import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from core.analyzer import QualityAnalyzer
from core.report   import ReportGenerator
from utils.file_parser import parse_uploaded_file
from utils.sample_data import load_sample_data

# Load .env if present
load_dotenv()

st.set_page_config(
    page_title="QAlytics – Software Quality Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3, h4 { font-family: 'IBM Plex Mono', monospace; }
.stApp { background: #0d0f14; color: #e2e8f0; }
.metric-card {
    background: #161b27; border: 1px solid #2d3748;
    border-radius: 8px; padding: 1.2rem 1.5rem; margin-bottom: 0.75rem;
}
.risk-high   { border-left: 4px solid #f56565; }
.risk-medium { border-left: 4px solid #ed8936; }
.risk-low    { border-left: 4px solid #48bb78; }
.badge { display:inline-block; padding:2px 10px; border-radius:4px;
         font-size:.72rem; font-family:'IBM Plex Mono',monospace;
         font-weight:600; letter-spacing:.04em; }
.badge-high   { background:#742a2a; color:#fc8181; }
.badge-medium { background:#7b341e; color:#fbd38d; }
.badge-low    { background:#1c4532; color:#68d391; }
.badge-ai     { background:#1a365d; color:#90cdf4; }
.section-header {
    border-bottom:1px solid #2d3748; padding-bottom:.4rem; margin-top:2rem;
    color:#a0aec0; font-size:.78rem; letter-spacing:.15em;
    text-transform:uppercase; font-family:'IBM Plex Mono',monospace;
}
.ai-box {
    background:#0f1f38; border:1px solid #2b4b7a; border-radius:6px;
    padding:.9rem 1.1rem; margin-top:.5rem; color:#90cdf4;
    font-size:.9rem; line-height:1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["requirements", "test_cases", "bugs", "analysis_done", "results"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "analysis_done" else False

reporter = ReportGenerator()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 QAlytics")
    st.markdown("*Software Quality Analysis*")
    st.divider()

    # ── Gemini API Key ────────────────────────────────────────────────────────
    st.markdown("### 🤖 Gemini AI")
    env_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "API Key",
        value     = env_key,
        type      = "password",
        help      = "Get a free key at aistudio.google.com → Get API key",
        placeholder = "AIzaSy...",
    )

    if api_key:
        st.success("API key set — AI insights enabled")
    else:
        st.warning("No key — rule-based mode only")

    st.divider()

    # ── File Upload ───────────────────────────────────────────────────────────
    st.markdown("### Upload Artifacts")
    req_file = st.file_uploader("Requirements (.txt / .csv / .xlsx)", type=["txt","csv","xlsx"])
    tc_file  = st.file_uploader("Test Cases (.csv / .xlsx)",          type=["csv","xlsx"])
    bug_file = st.file_uploader("Bug Reports (.csv / .xlsx)",         type=["csv","xlsx"])

    st.divider()
    use_sample = st.button("▶  Load Sample Data",  use_container_width=True)
    run_button = st.button("⚡  Run Analysis",      use_container_width=True, type="primary")

    st.divider()
    st.caption("Your data never leaves your machine.\nAPI calls go directly to Google.")

# ── Load data ─────────────────────────────────────────────────────────────────
if use_sample:
    sample = load_sample_data()
    st.session_state.requirements = sample["requirements"]
    st.session_state.test_cases   = sample["test_cases"]
    st.session_state.bugs         = sample["bugs"]
    st.toast("Sample data loaded — 10 reqs · 15 tests · 20 bugs", icon="✅")

if req_file:
    st.session_state.requirements = parse_uploaded_file(req_file, "requirements")
if tc_file:
    st.session_state.test_cases   = parse_uploaded_file(tc_file,  "test_cases")
if bug_file:
    st.session_state.bugs         = parse_uploaded_file(bug_file, "bugs")

# ── Run analysis ──────────────────────────────────────────────────────────────
if run_button:
    if not st.session_state.requirements:
        st.warning("Please upload or load requirements first.")
    else:
        llm_note = "with Gemini AI" if api_key else "in rule-based mode"
        with st.spinner(f"Analyzing artifacts {llm_note} …"):
            analyzer = QualityAnalyzer(gemini_api_key=api_key or None)
            results  = analyzer.run_full_analysis(
                requirements = st.session_state.requirements,
                test_cases   = st.session_state.test_cases or [],
                bugs         = st.session_state.bugs       or [],
            )
            st.session_state.results       = results
            st.session_state.analysis_done = True

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# QAlytics")
st.markdown("##### LLM-Based Software Quality Analysis Platform")

if not st.session_state.analysis_done:
    st.info("👈 Upload your artifacts (or load sample data) and click **Run Analysis**.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Requirements**\n- Ambiguity detection\n- Clarity scoring\n- AI-powered rewrites\n- Compliance wording check")
    with col2:
        st.markdown("**Test Cases**\n- Coverage gap detection\n- Req-to-test mapping\n- AI test case suggestions\n- Orphan test alerts")
    with col3:
        st.markdown("**Bug Reports**\n- Trend clustering\n- Recurring pattern detection\n- AI root-cause insights\n- Release risk scoring")
    st.stop()

results = st.session_state.results
llm_on  = results.get("llm_active", False)

# LLM status banner
if llm_on:
    st.success("🤖 Gemini 1.5 Flash active — AI-enhanced analysis")
else:
    st.info("⚙️ Running in rule-based mode. Enter a Gemini API key for AI insights.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📝 Requirements",
    "🧪 Test Coverage",
    "🐛 Bug Trends",
    "📄 Full Report",
])

# ─ Tab 1: Dashboard ──────────────────────────────────────────────────────────
with tab1:
    st.markdown('<p class="section-header">Quality Scores</p>', unsafe_allow_html=True)
    scores = results["scores"]

    def score_color(s):
        if s >= 70: return "#48bb78"
        if s >= 45: return "#ed8936"
        return "#f56565"

    c1, c2, c3, c4 = st.columns(4)
    for col, label, key in [
        (c1, "OVERALL QUALITY",    "overall"),
        (c2, "REQ CLARITY",        "requirement_clarity"),
        (c3, "TEST COVERAGE",      "test_coverage"),
        (c4, "BUG RISK",           "bug_risk"),
    ]:
        v = scores[key]
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size:.72rem;color:#718096;font-family:'IBM Plex Mono',monospace;letter-spacing:.1em">{label}</div>
            <div style="font-size:2.4rem;font-weight:700;color:{score_color(v)};font-family:'IBM Plex Mono',monospace">{v}<span style="font-size:1rem">/100</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">Release Readiness</p>', unsafe_allow_html=True)
    risk       = results["release_risk"]
    risk_color = {"HIGH": "#f56565", "MEDIUM": "#ed8936", "LOW": "#48bb78"}.get(risk["level"], "#ed8936")

    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid {risk_color}">
        <div style="font-size:.72rem;color:#718096;font-family:'IBM Plex Mono',monospace;letter-spacing:.1em">RELEASE RISK</div>
        <div style="font-size:1.6rem;font-weight:700;color:{risk_color};font-family:'IBM Plex Mono',monospace">{risk['level']}</div>
        <div style="color:#a0aec0;margin-top:.3rem">{risk['summary']}</div>
    </div>""", unsafe_allow_html=True)

    if risk.get("llm_verdict"):
        st.markdown(f"""
        <div class="ai-box">
            🤖 <strong>AI Verdict:</strong> {risk['llm_verdict']}
        </div>""", unsafe_allow_html=True)

    if risk.get("llm_rationale"):
        with st.expander("📋 Full AI Release Rationale"):
            st.markdown(risk["llm_rationale"])

    st.markdown('<p class="section-header">Key Findings</p>', unsafe_allow_html=True)
    for finding in results["key_findings"]:
        sev   = finding.get("severity", "MEDIUM")
        badge = f'<span class="badge badge-{sev.lower()}">{sev}</span>'
        st.markdown(f"""
        <div class="metric-card risk-{sev.lower()}">
            {badge}&nbsp;&nbsp;<strong>{finding['title']}</strong>
            <div style="color:#a0aec0;margin-top:.3rem;font-size:.9rem">{finding['detail']}</div>
        </div>""", unsafe_allow_html=True)

# ─ Tab 2: Requirements ────────────────────────────────────────────────────────
with tab2:
    req_results = results.get("requirements_analysis", {})
    ambig       = req_results.get("ambiguous", [])

    st.markdown('<p class="section-header">Ambiguous Requirements</p>', unsafe_allow_html=True)
    if ambig:
        for item in ambig:
            ai_badge = ' <span class="badge badge-ai">AI</span>' if item.get("llm_enhanced") else ""
            with st.expander(f"⚠️ {item['id']} — {item['text'][:75]}…"):
                st.markdown(f"**Ambiguous terms:** `{', '.join(item['ambiguous_words'])}`")
                st.markdown(f"**Severity:** `{item['severity']}`")

                if item.get("explanation"):
                    st.markdown("**Why it matters:**")
                    if item.get("llm_enhanced"):
                        st.markdown(f'<div class="ai-box">🤖 {item["explanation"]}</div>', unsafe_allow_html=True)
                    else:
                        st.info(item["explanation"])

                if item.get("suggestion"):
                    st.markdown("**Suggested rewrite:**")
                    if item.get("llm_enhanced"):
                        st.markdown(f'<div class="ai-box">🤖 {item["suggestion"]}</div>', unsafe_allow_html=True)
                    else:
                        st.code(item["suggestion"], language=None)
    else:
        st.success("No ambiguous requirements found.")

    st.markdown('<p class="section-header">Compliance / Vagueness Flags</p>', unsafe_allow_html=True)
    vague = req_results.get("vague_compliance", [])
    if vague:
        st.dataframe(pd.DataFrame(vague), use_container_width=True, hide_index=True)
    else:
        st.success("No compliance-style vagueness detected.")

    st.markdown('<p class="section-header">Consistency Issues</p>', unsafe_allow_html=True)
    cons = req_results.get("consistency_issues", [])
    if cons:
        for issue in cons:
            with st.expander(f"⚡ {issue['req_a']} ↔ {issue['req_b']}"):
                st.markdown(f"**REQ A:** {issue.get('text_a', issue['req_a'])}")
                st.markdown(f"**REQ B:** {issue.get('text_b', issue['req_b'])}")
                if llm_on:
                    st.markdown(f'<div class="ai-box">🤖 {issue["detail"]}</div>', unsafe_allow_html=True)
                else:
                    st.warning(issue["detail"])
    else:
        st.success("No contradictions detected.")

# ─ Tab 3: Test Coverage ───────────────────────────────────────────────────────
with tab3:
    tc_results = results.get("coverage_analysis", {})
    c1, c2 = st.columns(2)
    c1.metric("Requirements with test mapping",    tc_results.get("covered_count", 0))
    c2.metric("Requirements with NO test mapping", tc_results.get("uncovered_count", 0))

    st.markdown('<p class="section-header">Coverage Gaps</p>', unsafe_allow_html=True)
    gaps = tc_results.get("gaps", [])
    if gaps:
        for g in gaps:
            with st.expander(f"⚠️ {g['req_id']} — No test case found"):
                st.markdown(f"**Requirement:** {g['req_text']}")
                if g.get("suggested_tc"):
                    st.markdown("**AI Suggested Test Case:**")
                    st.markdown(f'<div class="ai-box">🤖<br><pre style="color:#90cdf4;background:none;margin:0">{g["suggested_tc"]}</pre></div>',
                                unsafe_allow_html=True)
                elif not llm_on:
                    st.caption("Add a Gemini API key to get AI-generated test case suggestions.")
    else:
        st.success("All requirements appear to have test coverage.")

    st.markdown('<p class="section-header">Orphan Test Cases</p>', unsafe_allow_html=True)
    orphans = tc_results.get("orphan_tests", [])
    if orphans:
        st.dataframe(pd.DataFrame(orphans), use_container_width=True, hide_index=True)
    else:
        st.success("All test cases are mapped to requirements.")

# ─ Tab 4: Bug Trends ──────────────────────────────────────────────────────────
with tab4:
    bug_results = results.get("bug_analysis", {})

    st.markdown('<p class="section-header">Recurring Defect Clusters</p>', unsafe_allow_html=True)
    clusters = bug_results.get("clusters", [])
    if clusters:
        for cl in clusters:
            sev_class = "high" if cl["count"] > 4 else "medium" if cl["count"] > 2 else "low"
            ai_badge  = ' <span class="badge badge-ai">AI</span>' if cl.get("llm_enhanced") else ""
            with st.expander(f"{'🔴' if sev_class=='high' else '🟡'} {cl['category']} — {cl['count']} occurrence(s)"):
                if cl.get("llm_enhanced"):
                    st.markdown(f'<div class="ai-box">🤖 {cl["summary"]}</div>', unsafe_allow_html=True)
                else:
                    st.info(cl["summary"])
                if cl.get("examples"):
                    st.markdown("**Examples:**")
                    for ex in cl["examples"]:
                        st.markdown(f"- {ex}")
    else:
        st.info("No bug data provided.")

    st.markdown('<p class="section-header">Defect Distribution</p>', unsafe_allow_html=True)
    cat_data = bug_results.get("category_counts", {})
    if cat_data:
        df = pd.DataFrame(list(cat_data.items()), columns=["Category", "Count"])
        df = df.sort_values("Count", ascending=False)
        st.bar_chart(df.set_index("Category"))

# ─ Tab 5: Full Report ─────────────────────────────────────────────────────────
with tab5:
    report_md = reporter.generate_markdown_report(results)
    st.markdown(report_md)
    st.download_button(
        "⬇ Download Report (.md)",
        data          = report_md,
        file_name     = "quality_report.md",
        mime          = "text/markdown",
        use_container_width = True,
    )
