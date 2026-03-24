"""
core/analyzer.py
Central orchestrator — wires LLM client into every sub-analyzer.
"""
from __future__ import annotations
from typing import Any, Optional

from .llm_client          import LLMClient
from .requirement_checker import RequirementChecker
from .coverage_analyzer   import CoverageAnalyzer
from .bug_analyzer        import BugAnalyzer


class QualityAnalyzer:

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.llm          = LLMClient(api_key=gemini_api_key)
        self.req_checker  = RequirementChecker(llm=self.llm)
        self.cov_analyzer = CoverageAnalyzer(llm=self.llm)
        self.bug_analyzer = BugAnalyzer(llm=self.llm)

    @property
    def llm_active(self) -> bool:
        return self.llm.enabled

    def run_full_analysis(
        self,
        requirements: list[dict],
        test_cases:   list[dict],
        bugs:         list[dict],
    ) -> dict[str, Any]:

        req_results = self.req_checker.analyze(requirements)
        cov_results = self.cov_analyzer.analyze(requirements, test_cases)
        bug_results = self.bug_analyzer.analyze(bugs)

        scores       = self._compute_scores(req_results, cov_results, bug_results,
                                            requirements, test_cases, bugs)
        key_findings = self._extract_key_findings(req_results, cov_results, bug_results)

        # LLM release rationale
        llm_rationale = None
        if self.llm.enabled:
            llm_rationale = self.llm.generate_release_rationale(scores, key_findings)

        llm_verdict = None
        if self.llm.enabled:
            llm_verdict = self.llm.assess_release_risk(scores, key_findings)

        release_risk = self._compute_release_risk(scores, key_findings,
                                                   llm_rationale, llm_verdict)

        return {
            "scores":                scores,
            "key_findings":          key_findings,
            "release_risk":          release_risk,
            "requirements_analysis": req_results,
            "coverage_analysis":     cov_results,
            "bug_analysis":          bug_results,
            "llm_active":            self.llm_active,
            "input_counts": {
                "requirements": len(requirements),
                "test_cases":   len(test_cases),
                "bugs":         len(bugs),
            },
        }

    # ── scoring ───────────────────────────────────────────────────────────────

    def _compute_scores(self, req_r, cov_r, bug_r, reqs, tcs, bugs) -> dict:
        total_reqs = max(len(reqs), 1)

        ambig_ratio   = len(req_r.get("ambiguous", []))          / total_reqs
        vague_ratio   = len(req_r.get("vague_compliance", []))   / total_reqs
        consist_ratio = len(req_r.get("consistency_issues", [])) / total_reqs
        req_score     = max(0, round(100 - ambig_ratio*50 - vague_ratio*25 - consist_ratio*25))

        covered   = cov_r.get("covered_count", 0)
        cov_score = round((covered / total_reqs) * 100)

        if not bugs:
            bug_score = 100
        else:
            clusters  = len(bug_r.get("clusters", []))
            high_bugs = sum(1 for b in bugs if str(b.get("severity", "")).upper() == "HIGH")
            penalty   = min(80, clusters * 8 + high_bugs * 5)
            bug_score = max(0, 100 - penalty)

        overall = round(req_score * 0.40 + cov_score * 0.35 + bug_score * 0.25)

        return {
            "overall":             overall,
            "requirement_clarity": req_score,
            "test_coverage":       cov_score,
            "bug_risk":            bug_score,
        }

    def _extract_key_findings(self, req_r, cov_r, bug_r) -> list[dict]:
        findings = []

        amb = req_r.get("ambiguous", [])
        if amb:
            findings.append({
                "title":    f"{len(amb)} ambiguous requirement(s) detected",
                "detail":   f"Vague terms found in {len(amb)} requirement(s). Testability is at risk.",
                "severity": "HIGH" if len(amb) > 5 else "MEDIUM",
            })

        gaps = cov_r.get("gaps", [])
        if gaps:
            findings.append({
                "title":    f"{len(gaps)} requirement(s) have no test mapping",
                "detail":   "These requirements are not covered by any known test case.",
                "severity": "HIGH" if len(gaps) > 3 else "MEDIUM",
            })

        clusters = bug_r.get("clusters", [])
        if clusters:
            top = clusters[0]
            findings.append({
                "title":    f"Recurring defect category: {top['category']}",
                "detail":   f"Appeared {top['count']} time(s). {top['summary']}",
                "severity": "HIGH" if top["count"] > 4 else "MEDIUM",
            })

        vague = req_r.get("vague_compliance", [])
        if vague:
            findings.append({
                "title":    f"{len(vague)} requirement(s) use compliance-unsafe wording",
                "detail":   "Too vague for safety-critical or audited systems.",
                "severity": "MEDIUM",
            })

        cons = req_r.get("consistency_issues", [])
        if cons:
            findings.append({
                "title":    f"{len(cons)} consistency issue(s) detected",
                "detail":   "Possible contradictions between requirement statements.",
                "severity": "MEDIUM",
            })

        if not findings:
            findings.append({
                "title":    "No critical issues found",
                "detail":   "All analyzed artifacts look clean.",
                "severity": "LOW",
            })

        return findings

    def _compute_release_risk(self, scores, findings, llm_rationale, llm_verdict) -> dict:
        overall       = scores["overall"]
        high_findings = sum(1 for f in findings if f.get("severity") == "HIGH")

        if overall < 50 or high_findings >= 2:
            level   = "HIGH"
            summary = "Multiple critical quality issues. Release not recommended without remediation."
        elif overall < 70 or high_findings == 1:
            level   = "MEDIUM"
            summary = "Some quality concerns present. Review flagged items before release."
        else:
            level   = "LOW"
            summary = "Quality indicators are acceptable. Minor items to address."

        return {
            "level":          level,
            "summary":        summary,
            "llm_rationale":  llm_rationale,
            "llm_verdict":    llm_verdict,
        }
