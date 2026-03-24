"""
core/llm_client.py
Gemini API wrapper using google-generativeai SDK.
Model: gemini-1.5-flash (free tier, fast, capable)
Falls back gracefully if no API key is configured.
"""
from __future__ import annotations
import os
import time
from typing import Optional

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

MODEL_NAME = "gemini-1.5-flash"

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT:        HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH:        HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:  HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:  HarmBlockThreshold.BLOCK_NONE,
} if GENAI_AVAILABLE else {}

GENERATION_CONFIG = {
    "temperature":      0.3,
    "top_p":            0.9,
    "max_output_tokens": 300,
} if GENAI_AVAILABLE else {}


class LLMClient:
    """
    Thin wrapper around Gemini 1.5 Flash.
    Every public method returns None on failure so callers
    fall back to their rule-based result seamlessly.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.enabled = bool(key and GENAI_AVAILABLE)
        self.model   = None

        if self.enabled:
            try:
                genai.configure(api_key=key)
                self.model = genai.GenerativeModel(
                    model_name        = MODEL_NAME,
                    generation_config = GENERATION_CONFIG,
                    safety_settings   = SAFETY_SETTINGS,
                )
            except Exception:
                self.enabled = False

    # ── public API ────────────────────────────────────────────────────────────

    def rewrite_requirement(self, req_text: str, ambiguous_terms: list[str]) -> Optional[str]:
        """Return a testable rewrite of req_text."""
        prompt = (
            "You are a senior software quality engineer specialising in requirements engineering.\n"
            f"Rewrite the following requirement so it is specific, measurable, and testable.\n"
            f"Replace every vague term ({', '.join(ambiguous_terms)}) with a concrete, "
            "quantifiable criterion (include example numbers/thresholds in brackets).\n"
            "Return ONLY the rewritten requirement. No preamble, no explanation.\n\n"
            f"Original requirement: {req_text}"
        )
        return self._generate(prompt, max_tokens=200)

    def explain_ambiguity(self, req_text: str, terms: list[str]) -> Optional[str]:
        """Return a short QA-focused explanation of why the terms are problematic."""
        prompt = (
            "You are a QA engineer reviewing software requirements.\n"
            f"Explain in 1-2 sentences why the term(s) '{', '.join(terms)}' in the following "
            "requirement make it impossible to write a pass/fail test.\n"
            "Be direct and practical. No bullet points, no preamble.\n\n"
            f"Requirement: {req_text}"
        )
        return self._generate(prompt, max_tokens=120)

    def summarize_bug_cluster(self, category: str, bug_titles: list[str]) -> Optional[str]:
        """Return a 2-sentence insight about a recurring defect cluster."""
        titles_str = "\n".join(f"- {t}" for t in bug_titles[:8])
        prompt = (
            "You are a software quality analyst.\n"
            f"The following defect titles all belong to the category '{category}':\n"
            f"{titles_str}\n\n"
            "In exactly 2 sentences: (1) describe the likely root-cause pattern, "
            "(2) suggest one concrete remediation action for the team.\n"
            "No bullet points. No preamble."
        )
        return self._generate(prompt, max_tokens=160)

    def generate_release_rationale(self, scores: dict, findings: list[dict]) -> Optional[str]:
        """Return a professional release-readiness paragraph."""
        findings_str = "\n".join(
            f"- [{f['severity']}] {f['title']}: {f['detail']}" for f in findings[:5]
        )
        prompt = (
            "You are a QA manager writing a release readiness summary for senior stakeholders.\n"
            f"Quality scores — overall: {scores['overall']}/100 | "
            f"requirement clarity: {scores['requirement_clarity']}/100 | "
            f"test coverage: {scores['test_coverage']}/100 | "
            f"bug risk: {scores['bug_risk']}/100.\n\n"
            f"Key findings:\n{findings_str}\n\n"
            "Write a 3-4 sentence release readiness paragraph. "
            "Be factual, concise, and professional. No bullet points."
        )
        return self._generate(prompt, max_tokens=220)

    def analyze_consistency(self, req_a: str, req_b: str) -> Optional[str]:
        """Return a one-sentence explanation of the potential contradiction."""
        prompt = (
            "You are a requirements analyst.\n"
            "Do the following two requirements contradict each other? "
            "Explain in one sentence why or why not.\n\n"
            f"Requirement A: {req_a}\n"
            f"Requirement B: {req_b}"
        )
        return self._generate(prompt, max_tokens=100)

    def suggest_test_case(self, req_text: str) -> Optional[str]:
        """Suggest a concrete Given/When/Then test case for an uncovered requirement."""
        prompt = (
            "You are a QA engineer.\n"
            "Write one concrete, executable test case in Given/When/Then format for:\n"
            f"{req_text}\n\n"
            "Return ONLY the test case. No explanation, no preamble."
        )
        return self._generate(prompt, max_tokens=160)

    def assess_release_risk(self, scores: dict, findings: list[dict]) -> Optional[str]:
        """Return a short go/no-go verdict with reasoning."""
        high = sum(1 for f in findings if f.get("severity") == "HIGH")
        prompt = (
            "You are a release manager.\n"
            f"Overall quality score: {scores['overall']}/100. "
            f"High-severity findings: {high}. "
            f"Test coverage score: {scores['test_coverage']}/100.\n\n"
            "Give a one-sentence go/no-go release verdict with your primary reason."
        )
        return self._generate(prompt, max_tokens=80)

    # ── internal ──────────────────────────────────────────────────────────────

    def _generate(self, prompt: str, max_tokens: int = 200, retries: int = 2) -> Optional[str]:
        if not self.enabled or self.model is None:
            return None

        # Temporarily override max tokens for this call
        local_config = dict(GENERATION_CONFIG)
        local_config["max_output_tokens"] = max_tokens

        for attempt in range(retries + 1):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=local_config,
                )
                if response.text:
                    return response.text.strip()
                return None
            except Exception as exc:
                err = str(exc).lower()
                if ("quota" in err or "rate" in err or "429" in err) and attempt < retries:
                    time.sleep(2 ** (attempt + 1))
                    continue
                # Resource exhausted on free tier — wait longer
                if "resource_exhausted" in err and attempt < retries:
                    time.sleep(5)
                    continue
                return None
        return None
