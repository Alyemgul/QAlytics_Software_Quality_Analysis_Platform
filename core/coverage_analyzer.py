"""
core/coverage_analyzer.py
Jaccard-similarity requirement-to-test mapper + Gemini test case suggestions.
"""
from __future__ import annotations
import re
from typing import Optional
from .llm_client import LLMClient


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-z]{3,}\b", text.lower()))


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


COVERAGE_THRESHOLD = 0.12


class CoverageAnalyzer:
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm

    def analyze(self, requirements: list[dict], test_cases: list[dict]) -> dict:
        req_list = [
            (r.get("id", f"REQ-{i+1}"), r.get("text", ""))
            for i, r in enumerate(requirements)
        ]
        tc_list = [
            (t.get("id", f"TC-{i+1}"),
             t.get("text", t.get("description", t.get("title", ""))))
            for i, t in enumerate(test_cases)
        ]

        req_tokens = [(rid, rtxt, _tokenize(rtxt)) for rid, rtxt in req_list]
        tc_tokens  = [(tid, ttxt, _tokenize(ttxt)) for tid, ttxt in tc_list]

        covered_ids = set()
        covered_tc  = set()
        mapping     = {}

        for rid, rtxt, rtok in req_tokens:
            matches = []
            for tid, ttxt, ttok in tc_tokens:
                score = _jaccard(rtok, ttok)
                if score >= COVERAGE_THRESHOLD:
                    matches.append((tid, score))
                    covered_tc.add(tid)
            if matches:
                covered_ids.add(rid)
                mapping[rid] = [m[0] for m in sorted(matches, key=lambda x: -x[1])]

        gaps = []
        for rid, rtxt, _ in req_tokens:
            if rid not in covered_ids:
                # LLM suggests a test case for uncovered requirement
                suggested_tc = None
                if self.llm:
                    suggested_tc = self.llm.suggest_test_case(rtxt)
                gaps.append({
                    "req_id":        rid,
                    "req_text":      rtxt,
                    "suggested_tc":  suggested_tc,
                    "llm_enhanced":  suggested_tc is not None,
                })

        orphan_tests = [
            {"tc_id": tid, "tc_text": ttxt[:80]}
            for tid, ttxt, _ in tc_tokens
            if tid not in covered_tc
        ]

        return {
            "covered_count":   len(covered_ids),
            "uncovered_count": len(gaps),
            "coverage_map":    mapping,
            "gaps":            gaps,
            "orphan_tests":    orphan_tests,
        }
