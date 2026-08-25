# 💻 LIFE-OS WELLBEING DASHBOARD

```text
================================================================================
  _      _  __        ___   ____  
 | |    (_)/ _|      / _ \ / ___| 
 | |    | | |_ _____| | | | \___ \ 
 | |___ | |  _|_____| |_| |  ___) |
 |_____||_|_|       \___/ |____/ 
                                  
 DIGITAL WELLBEING ENGINE // COACH-AEGIS VER 3.5
================================================================================
```

> Aegis is running...
> Reading user screen time profiles...
> Initializing brutal-but-fair feedback algorithms...

`Life-OS` is a professional digital wellbeing dashboard built with **Streamlit**, **Pandas**, and the **Gemini 3.5 Flash API**. It tracks your daily screen time habits, aggregates them across categories, and feeds them into **Aegis**—a brutal-but-fair lifestyle coach that doesn't hold back. To visualize your behavior, the system renders a dynamic, AI-generated **Guilt-Trip Avatar** (via Pollinations.ai) representing your productivity level.

---

## 🛠️ System Architecture & Stack

```text
[CSV Data Pipeline] ──> [Pandas Aggregation Engine] ──> [Streamlit SaaS UI]
                                                             │
[Pollinations Avatar API] <─── [Gemini AI Coach Engine] <─────┘
```

- **Frontend/Dashboard:** Streamlit (v1.59.1)
- **Data Processor:** Pandas (v3.0.3)
- **AI Brain:** google-genai SDK (v2.12.1) + Gemini 3.5 Flash
- **Image Engine:** Pollinations.ai API
- **Configuration:** Python-dotenv

---

## 📥 Setup & Installation

```bash
# 1. Clone this repository and enter directory
$ git clone <your-repo-link>
$ cd miraiIntern

# 2. Setup your virtual environment
$ python -m venv venv
$ venv\Scripts\activate      # On Windows
$ source venv/bin/activate   # On macOS/Linux

# 3. Install required dependencies
$ pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file with your API key:
$ echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

*Note: Your `.env` file contains sensitive API keys and is excluded from source control via `.gitignore`.*

---

## 🚀 Running the System

To boot up the dashboard locally:

```bash
$ streamlit run life_os_app.py
```

---

## 🧠 Core Features & Phase Deliverables

- **Phase 1: Data Pipeline:** Synthesized 14 days of realistic app usage data across 5 distinct categories (`Coding`, `Social Media`, `Entertainment`, `Education`, `Productivity`). Loaded using pandas with robust caching.
- **Phase 2: SaaS UI Command Center:**
  - Sidebar for date filtering and setting screen time boundaries.
  - KPI metric cards indicating screen time duration, most used app, and dynamic target deltas (`delta_color="inverse"`).
  - Clean stacked bar charts detailing daily usage categories over 14 days.
- **Phase 3: AI Integration:** Integrates Gemini to analyze daily habits, outputting a custom JSON format with lifestyle reviews and real-world replacements.
- **Phase 4: Guilt-Trip Avatar (Innovation):** Extracts the AI's creative prompt and renders a matching avatar generated via Pollinations.ai. The avatar is seeded to the day's date, keeping it stable but highly personalized.
