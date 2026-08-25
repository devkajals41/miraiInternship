# 🔥 Capstone Project: Expense Roaster

```text
================================================================================
  _____ _            _____                                
 |_   _| |__   ___  | ____|_  ___ __   ___ _ __  ___  ___ 
   | | | '_ \ / _ \ |  _| \ \/ / '_ \ / _ \ '_ \/ __|/ _ \
   | | | | | |  __/ | |___ >  <| |_) |  __/ | | \__ \  __/
   |_| |_| |_|\___| |_____/_/\_\ .__/ \___|_| |_|___/\___|
                                |_|                        
  ____                  _            
 |  _ \ ___   __ _ ___| |_ ___ _ __ 
 | |_) / _ \ / _` / __| __/ _ \ '__|
 |  _ < (_) | (_| \__ \ ||  __/ |   
 |_| \_\___/ \__,_|___/\__\___|_|   

 ROAST-ENGINE VER 3.5 // FINANCIAL TRUTH MACHINE
================================================================================
```

This folder houses the **Expense Roaster** Streamlit application, a production-grade AI personal finance dashboard.

🔗 **[Live Deployed URL](https://miraiinternship-8vbgfann2wttqxgpymeiwm.streamlit.app)**

---

## 🏗️ Technical Pipeline & Design

The application links data ingestion, local pandas metrics aggregation, interactive Plotly charts, and structured LLM responses.

```mermaid
graph LR
    subgraph Input
        A1[CSV Upload] --> C[Pandas Engine]
        A2[Manual Form] --> C
    end

    subgraph Views
        C --> D1[KPI Cards]
        C --> D2[Plotly Charts]
        C --> D3[Interactive Data Editor]
    end

    subgraph AI Pipeline
        C --> E[Data Summary Builder]
        E --> F[Gemini 3.5 Flash]
        F --> G[JSON Parsed Roast]
        G --> H[Pollinations.ai Image API]
        H --> I[Financial Avatar Graphic]
    end

    classDef accent fill:#EC4899,stroke:#BE185D,stroke-width:2px,color:#fff;
    classDef card fill:#fff,stroke:#E0E7FF,stroke-width:2px,color:#0F172A;
    
    class C accent;
    class D1,D2,D3,G,I card;
```

---

## 📂 Folder Files

- **`expense_roaster.py`**: The core Streamlit application. Contains all page configs, custom CSS, data loaders, state variables, and logic connectors.
- **`expenses.csv`**: A 25-day synthetic financial mock log containing various categories.
- **`requirements.txt`**: Unpinned library configuration containing core dependencies for Streamlit Cloud.
- **`.gitignore`**: Directory-specific gitrules preventing API keys and cache folder configurations from leaking.

---

## 🛠️ Run Locally

1. Open your terminal and navigate to this folder:
   ```bash
   cd capstone_project
   ```

2. Make sure your virtual environment is active:
   ```bash
   # Windows
   ..\venv\Scripts\activate

   # macOS/Linux
   source ../venv/bin/activate
   ```

3. Launch the dashboard:
   ```bash
   streamlit run expense_roaster.py
   ```

---

**Built as the Capstone assignment for MirAI School of Technology summer session.**
