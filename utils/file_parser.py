"""
utils/file_parser.py
Parse uploaded files into the internal list-of-dicts format.
"""
from __future__ import annotations
import io
import csv
import pandas as pd
import streamlit as st


def parse_uploaded_file(uploaded_file, artifact_type: str) -> list[dict]:
    """
    artifact_type: 'requirements' | 'test_cases' | 'bugs'
    Returns a list of dicts with at least {'id': ..., 'text': ...}
    """
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        elif name.endswith(".txt"):
            raw  = uploaded_file.read().decode("utf-8", errors="ignore")
            rows = [line.strip() for line in raw.splitlines() if line.strip()]
            df   = pd.DataFrame({"text": rows})
        else:
            st.warning(f"Unsupported file format: {name}")
            return []

        return _normalise(df, artifact_type)

    except Exception as exc:
        st.error(f"Could not parse {name}: {exc}")
        return []


def _normalise(df: pd.DataFrame, artifact_type: str) -> list[dict]:
    """Map whatever columns exist to {id, text, ...}."""
    df.columns = [c.strip().lower() for c in df.columns]

    # id column
    id_col = next((c for c in df.columns if c in ("id", "req_id", "tc_id", "bug_id", "#")), None)

    # text column
    text_candidates = {
        "requirements": ["text", "description", "requirement", "statement", "title"],
        "test_cases":   ["text", "description", "title", "test_case", "test case", "steps"],
        "bugs":         ["text", "description", "title", "summary", "bug_summary"],
    }
    text_col = next(
        (c for c in text_candidates.get(artifact_type, ["text", "description", "title"]) if c in df.columns),
        df.columns[0] if len(df.columns) > 0 else None,
    )

    records = []
    for i, row in df.iterrows():
        rec = {k: v for k, v in row.items()}
        rec["id"]   = str(row[id_col])   if id_col   else f"{artifact_type.upper()[:3]}-{i+1:03d}"
        rec["text"] = str(row[text_col]) if text_col else ""
        records.append(rec)

    return records
