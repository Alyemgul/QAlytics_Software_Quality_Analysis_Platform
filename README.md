# QAlytics – Software Quality Analysis Platform

An LLM-powered tool for analyzing software artifacts and identifying quality risks.  
Uses **Gemini 1.5 Flash** (free tier) for AI-enhanced insights with a rule-based fallback.

---

## Features

| Feature | Rule-based | + Gemini AI |
|---|---|---|
| Ambiguity detection | ✅ keyword matching | ✅ + explanation of *why* it matters |
| Requirement rewrite | ✅ template-based | ✅ natural language rewrite |
| Test coverage mapping | ✅ Jaccard similarity | ✅ + suggested test case per gap |
| Bug clustering | ✅ keyword categories | ✅ + root-cause insight & fix suggestion |
| Consistency check | ✅ regex patterns | ✅ + plain-English contradiction explanation |
| Release risk | ✅ score-based | ✅ + AI rationale paragraph + go/no-go verdict |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/qalytics.git
cd qalytics
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

```bash
# Copy the example file
cp .env.example .env

# Open .env and paste your key
# GEMINI_API_KEY=AIzaSy...
```

Get a free key at: https://aistudio.google.com → **Get API key**

### 5. Run the app

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Demo Flow

1. Paste your Gemini API key in the sidebar (or it reads from `.env` automatically)
2. Click **▶ Load Sample Data** — loads 10 reqs, 15 test cases, 20 bugs
3. Click **⚡ Run Analysis**
4. Explore the 5 tabs:

| Tab | What you see |
|-----|-------------|
| 📊 Dashboard | 4 quality scores + release risk + AI verdict |
| 📝 Requirements | Ambiguous terms + AI explanations + AI rewrites |
| 🧪 Test Coverage | Gaps + AI-generated test cases per uncovered requirement |
| 🐛 Bug Trends | Clustered defects + AI root-cause summaries |
| 📄 Full Report | Downloadable Markdown report with all AI content |

---

## Input File Formats

| Artifact | Formats | Key Columns |
|---|---|---|
| Requirements | `.txt`, `.csv`, `.xlsx` | `id`, `text` |
| Test Cases | `.csv`, `.xlsx` | `id`, `text` / `title` / `description` |
| Bug Reports | `.csv`, `.xlsx` | `id`, `title`, `description`, `severity` |

Sample files: `data/samples/`

---

## Project Structure

```
qalytics/
├── app.py                        # Streamlit UI
├── requirements.txt
├── .env.example                  # Copy to .env and add your key
├── README.md
├── core/
│   ├── llm_client.py             # Gemini 1.5 Flash wrapper
│   ├── analyzer.py               # Main orchestrator
│   ├── requirement_checker.py    # Ambiguity + consistency engine
│   ├── coverage_analyzer.py      # Req-to-test mapper
│   ├── bug_analyzer.py           # Bug clustering
│   └── report.py                 # Markdown report generator
├── utils/
│   ├── file_parser.py            # .txt / .csv / .xlsx parser
│   └── sample_data.py            # Built-in demo dataset
└── data/samples/
    ├── requirements.csv
    ├── test_cases.csv
    └── bugs.csv
```

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** — UI
- **Google Gemini 1.5 Flash** — LLM (free tier)
- **google-generativeai** — official Python SDK
- **pandas** — data handling
- **python-dotenv** — API key management

---

## License

MIT
