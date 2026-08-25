# 🔥 Expense Roaster

> AI-powered personal finance dashboard that brutally roasts your spending habits.

---

## About

**Expense Roaster** is a production-quality Streamlit web application that lets users upload or manually enter their monthly expenses. The app processes the data with Pandas, generates interactive Plotly visualizations, and feeds the aggregated summary to **Google Gemini 3.5 Flash** — which acts as "The Roast Master," a savage but genuinely helpful personal finance coach.

A dynamic **Financial Avatar** (powered by Pollinations.ai) is generated based on the user's spending behavior — guilt-tripping overspenders and celebrating disciplined budgeters.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas |
| AI Engine | Google Gemini 3.5 Flash (via `google-genai` SDK) |
| Visualizations | Plotly Express |
| Image Generation | Pollinations.ai API |
| Config | python-dotenv / Streamlit Secrets |

---

## Features

- **Interactive Data Ingestion** — Upload a CSV or manually enter expenses through a clean form interface
- **KPI Metric Cards** — Total spending, budget variance, biggest money pit, daily burn rate
- **Plotly Charts** — Category donut chart, daily spend bars, payment method distribution
- **AI Roast Engine** — Gemini analyzes spending patterns and delivers a brutally honest financial assessment with a letter grade and actionable recovery steps
- **Financial Avatar** — AI-generated image representing the user's financial state
- **Session State** — No data loss on widget interactions
- **st.form** — API calls only trigger on explicit user action

---

## Setup

```bash
# Clone
git clone https://github.com/devkajals41/miraiInternship.git
cd miraiInternship

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run
streamlit run expense_roaster.py
```

---

## Architecture

```
┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  User Input      │────▶│  Pandas Engine   │────▶│  Streamlit UI    │
│  (CSV / Manual)  │     │  (Aggregation)   │     │  (KPIs + Charts) │
└──────────────────┘     └────────┬────────┘     └──────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  Gemini 3.5     │
                         │  Flash API      │
                         │  (Roast Master) │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Pollinations   │
                         │  Image API      │
                         └─────────────────┘
```

---

## Live Demo

🔗 [**View Live App**](https://devkajals41-miraiinternship-expense-roaster.streamlit.app)

---

**Built as a Capstone Project for MirAI School of Technology — Summer Internship 2026**
