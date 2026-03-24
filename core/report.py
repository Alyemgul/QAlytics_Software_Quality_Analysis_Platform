"""
core/report.py
Generates a full Markdown quality report, incorporating LLM content where present.
"""
from __future__ import annotations
from datetime import datetime


class ReportGenerator:

    def generate_markdown_report(self, results: dict) -> str:
        now    = datetime.now().strftime("%Y-%m-%d %H:%M")
        scores = results["scores"]
        risk   = results["release_risk"]
        counts = results["input_counts"]
        reqs   = results["requirements_analysis"]
        cov    = results["coverage_analysis"]
        bugs   = results["bug_analysis"]
        llm_on = results.get("llm_active", False)

        lines = [
            "# Software Quality Analysis Report",
            f"**Generated:** {now}  ",
            f"**AI-Enhanced:** {'Yes — Gemini 1.5 Flash' if llm_on else 'No (rule-based only)'}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Metric | Score |",
            "|--------|-------|",
            f"| Overall Quality       | **{scores['overall']}/100** |",
            f"| Requirement Clarity   | {scores['requirement_clarity']}/100 |",
            f"| Test Coverage         | {scores['test_coverage']}/100 |",
            f"| Bug Risk              | {scores['bug_risk']}/100 |",
            "",
            f"**Release Risk Level:** `{risk['level']}`",
            f"> {risk['summary']}",
            "",
        ]

        if risk.get("llm_verdict"):
            lines += [
                f"**AI Verdict:** {risk['llm_verdict']}",
                "",
            ]

        if risk.get("llm_rationale"):
            lines += [
                "### Release Readiness (AI Analysis)",
                "",
                risk["llm_rationale"],
                "",
            ]

        lines += [
            "---",
            "",
            "## Input Summary",
            "",
            f"- Requirements analyzed: **{counts['requirements']}**",
            f"- Test cases analyzed:   **{counts['test_cases']}**",
            f"- Bug reports analyzed:  **{counts['bugs']}**",
            "",
            "---",
            "",
            "## Key Findings",
            "",
        ]

        for f in results["key_findings"]:
            lines.append(f"### [{f['severity']}] {f['title']}")
            lines.append(f"{f['detail']}")
            lines.append("")

        lines += [
            "---",
            "",
            "## Requirements Analysis",
            "",
            f"### Ambiguous Requirements ({len(reqs.get('ambiguous', []))})",
            "",
        ]

        for item in reqs.get("ambiguous", []):
            ai_badge = " *(AI-rewritten)*" if item.get("llm_enhanced") else " *(rule-based)*"
            lines.append(f"**{item['id']}** — Severity: `{item['severity']}`")
            lines.append(f"- **Original:** {item['text']}")
            lines.append(f"- **Ambiguous terms:** `{', '.join(item['ambiguous_words'])}`")
            lines.append(f"- **Why it matters:** {item.get('explanation', '')}")
            lines.append(f"- **Suggested rewrite{ai_badge}:** _{item['suggestion']}_")
            lines.append("")

        lines += [
            f"### Compliance / Vagueness Flags ({len(reqs.get('vague_compliance', []))})",
            "",
        ]
        for item in reqs.get("vague_compliance", []):
            lines.append(f"- **{item['Requirement ID']}**: {item['Vague Phrases']}")
        lines.append("")

        if reqs.get("consistency_issues"):
            lines += ["### Consistency Issues", ""]
            for issue in reqs["consistency_issues"]:
                lines.append(f"- **{issue['req_a']}** vs **{issue['req_b']}**: {issue['detail']}")
            lines.append("")

        lines += [
            "---",
            "",
            "## Test Coverage Analysis",
            "",
            f"- Covered requirements:   **{cov.get('covered_count', 0)}**",
            f"- Uncovered requirements: **{cov.get('uncovered_count', 0)}**",
            "",
            "### Coverage Gaps",
            "",
        ]
        for g in cov.get("gaps", []):
            lines.append(f"#### {g['req_id']}")
            lines.append(f"**Requirement:** {g['req_text']}")
            if g.get("suggested_tc"):
                lines.append(f"\n**AI Suggested Test Case:**\n\n```\n{g['suggested_tc']}\n```")
            lines.append("")

        lines += [
            "---",
            "",
            "## Bug Trend Analysis",
            "",
            "### Recurring Defect Categories",
            "",
        ]
        for cl in bugs.get("clusters", []):
            ai_badge = " *(AI insight)*" if cl.get("llm_enhanced") else ""
            lines.append(f"**{cl['category']}** — {cl['count']} occurrence(s){ai_badge}")
            lines.append(f"> {cl['summary']}")
            lines.append("")

        lines += [
            "---",
            "",
            "## Recommendations",
            "",
            "1. Rewrite all ambiguous requirements using testable, measurable criteria.",
            "2. Create test cases for every requirement currently marked as uncovered.",
            "3. Investigate the top recurring defect category and add regression tests.",
            "4. Review compliance-unsafe wording against project safety/audit guidelines.",
            "5. Re-run this analysis after each sprint to track quality improvement trends.",
            "",
            "---",
            "*Report generated by QAlytics — Software Quality Analysis Platform*",
        ]

        return "\n".join(lines)
