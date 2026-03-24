"""
core/requirement_checker.py
Rule-based first pass + Gemini LLM enhancement.
"""
from __future__ import annotations
import re
from typing import Optional
from .llm_client import LLMClient

AMBIGUOUS_TERMS = {
    "fast", "quickly", "slow", "efficient", "user-friendly", "easy", "simple",
    "intuitive", "flexible", "scalable", "robust", "reliable", "seamless",
    "sufficient", "adequate", "appropriate", "reasonable", "minimal", "maximum",
    "as needed", "as required", "as appropriate", "etc", "and so on", "various",
    "some", "several", "many", "few", "most", "often", "sometimes", "usually",
    "generally", "typically", "approximately", "about", "around", "nearly",
    "soon", "timely", "promptly", "real-time", "near real-time",
}

SEVERITY_WEIGHTS = {
    "fast": "HIGH", "real-time": "HIGH", "near real-time": "HIGH",
    "user-friendly": "HIGH", "intuitive": "HIGH",
    "sufficient": "MEDIUM", "adequate": "MEDIUM", "appropriate": "MEDIUM",
    "flexible": "MEDIUM", "scalable": "MEDIUM", "robust": "MEDIUM",
    "reasonable": "MEDIUM", "minimal": "MEDIUM",
    "soon": "LOW", "timely": "LOW", "sometimes": "LOW", "often": "LOW",
}

COMPLIANCE_UNSAFE = {
    "tbd", "to be determined", "to be defined", "n/a", "unknown", "unclear",
    "placeholder", "future work", "out of scope for now", "see above",
    "see below", "refer to", "if applicable", "when necessary",
    "at the discretion", "as per", "depending on",
}

REWRITE_TEMPLATES = {
    "fast":          "shall complete within [X ms] under [Y] concurrent users",
    "quickly":       "shall respond within [X] seconds",
    "user-friendly": "shall allow a new user to complete [task] within [X] minutes without training",
    "intuitive":     "shall score >= [X] on a usability test with [N] participants",
    "sufficient":    "shall provide at least [X] [unit] of [resource]",
    "adequate":      "shall meet [specific criterion] measured by [metric]",
    "appropriate":   "shall conform to [specific standard or criterion]",
    "flexible":      "shall support [specific variation] without code changes",
    "scalable":      "shall maintain [metric] when load increases from [X] to [Y]",
    "robust":        "shall remain available during [specific failure scenario]",
    "reliable":      "shall achieve [X]% uptime measured over [period]",
    "real-time":     "shall update within [X] ms of [triggering event]",
    "near real-time":"shall update within [X] seconds of [triggering event]",
    "soon":          "shall complete within [X] business days",
    "timely":        "shall complete within [X] hours/days as defined in [SLA]",
    "seamless":      "shall complete [transition] without user-visible interruption",
    "reasonable":    "shall satisfy [specific measurable threshold]",
    "minimal":       "shall use no more than [X] [unit] of [resource]",
}

CONTRADICTION_PAIRS = [
    (r"\bmust\s+always\b",   r"\bmay\s+not\b|\bshall\s+not\b"),
    (r"\bshall\s+support\b", r"\bshall\s+not\s+support\b"),
    (r"\bmandatory\b",       r"\boptional\b"),
    (r"\brequired\b",        r"\bnot\s+required\b"),
    (r"\bprohibited\b",      r"\ballowed\b|\bpermitted\b"),
]


class RequirementChecker:
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm

    def analyze(self, requirements: list[dict]) -> dict:
        ambiguous          = []
        vague_compliance   = []
        consistency_issues = []

        texts = [
            (r.get("id", f"REQ-{i+1}"), r.get("text", ""))
            for i, r in enumerate(requirements)
        ]

        for req_id, text in texts:
            found_ambig = self._find_ambiguous_terms(text)
            if found_ambig:
                severity = max(
                    (SEVERITY_WEIGHTS.get(t, "LOW") for t in found_ambig),
                    key=lambda s: {"HIGH": 2, "MEDIUM": 1, "LOW": 0}[s],
                )
                rule_suggestion = self._build_rule_suggestion(text, found_ambig)
                llm_rewrite     = None
                llm_explanation = None
                if self.llm:
                    llm_rewrite     = self.llm.rewrite_requirement(text, found_ambig)
                    llm_explanation = self.llm.explain_ambiguity(text, found_ambig)

                ambiguous.append({
                    "id":              req_id,
                    "text":            text,
                    "ambiguous_words": found_ambig,
                    "severity":        severity,
                    "suggestion":      llm_rewrite or rule_suggestion,
                    "explanation":     llm_explanation or self._rule_explanation(found_ambig),
                    "llm_enhanced":    llm_rewrite is not None,
                })

            found_vague = self._find_compliance_vagueness(text)
            if found_vague:
                vague_compliance.append({
                    "Requirement ID": req_id,
                    "Text":           text[:80] + ("..." if len(text) > 80 else ""),
                    "Vague Phrases":  ", ".join(found_vague),
                })

        consistency_issues = self._check_consistency(texts)

        return {
            "ambiguous":          ambiguous,
            "vague_compliance":   vague_compliance,
            "consistency_issues": consistency_issues,
            "total_analyzed":     len(texts),
        }

    def _find_ambiguous_terms(self, text: str) -> list[str]:
        lower = text.lower()
        return [t for t in AMBIGUOUS_TERMS
                if re.search(r"\b" + re.escape(t) + r"\b", lower)]

    def _find_compliance_vagueness(self, text: str) -> list[str]:
        lower = text.lower()
        return [p for p in COMPLIANCE_UNSAFE if p in lower]

    def _build_rule_suggestion(self, text: str, ambig_terms: list[str]) -> str:
        suggestion = text
        for term in ambig_terms:
            template = REWRITE_TEMPLATES.get(term)
            if template:
                pattern    = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
                suggestion = pattern.sub(f"[{template}]", suggestion, count=1)
                break
        return suggestion

    def _rule_explanation(self, terms: list[str]) -> str:
        return (
            f"The term(s) '{', '.join(terms)}' are subjective and cannot be measured. "
            "Without a specific, quantifiable criterion no pass/fail test can be written."
        )

    def _check_consistency(self, texts: list[tuple]) -> list[dict]:
        issues = []
        for i, (id_a, text_a) in enumerate(texts):
            for id_b, text_b in texts[i + 1:]:
                for pat_a, pat_b in CONTRADICTION_PAIRS:
                    if (re.search(pat_a, text_a, re.IGNORECASE) and
                            re.search(pat_b, text_b, re.IGNORECASE)):
                        llm_detail = None
                        if self.llm:
                            llm_detail = self.llm.analyze_consistency(text_a, text_b)
                        issues.append({
                            "req_a":  id_a,
                            "req_b":  id_b,
                            "text_a": text_a,
                            "text_b": text_b,
                            "detail": llm_detail or (
                                f"Possible contradiction: '{pat_a}' vs '{pat_b}'."
                            ),
                        })
                        break
        return issues
