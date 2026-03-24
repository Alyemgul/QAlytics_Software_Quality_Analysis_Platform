"""
core/bug_analyzer.py
Rule-based bug clustering + Gemini-powered insights.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Optional
from .llm_client import LLMClient

BUG_CATEGORIES = {
    "Authentication & Login":   ["login", "logout", "auth", "password", "token", "session", "credential", "oauth", "sso"],
    "UI / Frontend":            ["ui", "button", "display", "screen", "render", "layout", "style", "css", "page", "modal", "dialog", "form"],
    "Performance":              ["slow", "timeout", "latency", "performance", "memory", "cpu", "hang", "freeze", "lag", "speed"],
    "Data / Database":          ["data", "database", "db", "sql", "query", "insert", "update", "delete", "migration", "null", "corrupt", "deadlock", "connection"],
    "API / Integration":        ["api", "endpoint", "rest", "http", "request", "response", "integration", "webhook", "payload"],
    "Validation / Input":       ["validation", "input", "field", "required", "format", "invalid", "error message", "constraint"],
    "Sensor / Hardware":        ["sensor", "hardware", "device", "driver", "firmware", "gpio", "uart", "i2c", "spi", "calibration", "channel", "threshold"],
    "File / Upload":            ["file", "upload", "download", "attachment", "export", "import", "csv", "pdf"],
    "Notification / Email":     ["notification", "email", "alert", "sms", "push", "message"],
    "Configuration / Settings": ["config", "setting", "configuration", "environment", "env", "flag", "toggle", "parameter"],
    "Security":                 ["security", "vulnerability", "xss", "injection", "csrf", "privilege", "permission", "access"],
    "Crash / Exception":        ["crash", "exception", "traceback", "stack trace", "unhandled", "null pointer", "error 500"],
}


def _text_of(bug: dict) -> str:
    parts = [
        bug.get("title", ""),
        bug.get("description", ""),
        bug.get("summary", ""),
        bug.get("component", ""),
    ]
    return " ".join(str(p) for p in parts).lower()


class BugAnalyzer:
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm

    def analyze(self, bugs: list[dict]) -> dict:
        if not bugs:
            return {"clusters": [], "category_counts": {}}

        category_bugs: dict[str, list[str]] = defaultdict(list)

        for bug in bugs:
            text  = _text_of(bug)
            label = bug.get("title", bug.get("id", ""))[:60]
            matched = False
            for cat, keywords in BUG_CATEGORIES.items():
                if any(kw in text for kw in keywords):
                    category_bugs[cat].append(label)
                    matched = True
                    break
            if not matched:
                category_bugs["Uncategorized"].append(label)

        clusters = []
        for cat, examples in sorted(category_bugs.items(), key=lambda x: -len(x[1])):
            llm_summary = None
            if self.llm and len(examples) >= 1:
                llm_summary = self.llm.summarize_bug_cluster(cat, examples)

            rule_summary = (
                f"Recurring defects in {cat.lower()} area detected across {len(examples)} report(s). "
                f"Review related code paths and add regression tests."
            )

            clusters.append({
                "category":     cat,
                "count":        len(examples),
                "summary":      llm_summary or rule_summary,
                "examples":     examples[:5],
                "llm_enhanced": llm_summary is not None,
            })

        category_counts = {c["category"]: c["count"] for c in clusters}

        return {
            "clusters":        clusters,
            "category_counts": category_counts,
        }
