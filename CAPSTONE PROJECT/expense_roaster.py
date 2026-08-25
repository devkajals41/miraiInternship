import streamlit as st
import pandas as pd
import os
import json
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------
# Page Configurations & CSS Theme Injection
# ---------------------------------------------------------

st.set_page_config(
    page_title="Expense Roaster",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Full color theme matching the reference image:
# - Deep vivid blue sidebar (#1E40AF)
# - Hot-pink primary accent (#EC4899)
# - Lavender-blue main content background (#EEF2FF)
# - Pure white neumorphic cards
# - Navy dark text (#0F172A)
st.markdown("""
<style>
    /* ── Global Page & Main Content Background ── */
    .stApp {
        background-color: #EEF2FF;
    }

    /* ── Sidebar: Deep Blue Theme ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #E0E7FF !important;
    }
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #BFDBFE !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #3B5BA7 !important;
    }
    /* Fix: Input fields inside the dark sidebar must have dark text on white bg */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="datepicker"] input,
    [data-testid="stSidebar"] [data-testid="stDateInputField"] input {
        color: #0F172A !important;
        background-color: #ffffff !important;
    }
    /* The outer date input box wrapper */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="datepicker"],
    [data-testid="stSidebar"] [data-testid="stDateInputField"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    /* Placeholder text inside sidebar inputs */
    [data-testid="stSidebar"] input::placeholder {
        color: #94A3B8 !important;
    }
    /* Multiselect tags and dropdown text */
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #0F172A !important;
        background-color: #ffffff !important;
    }
    /* Slider value text */
    [data-testid="stSidebar"] [data-testid="stTickBar"] * {
        color: #BFDBFE !important;
    }
    /* Sidebar button → pink accent */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #EC4899 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #DB2777 !important;
    }

    /* ── Main Area White Card Containers ── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #E0E7FF !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 24px rgba(37, 99, 235, 0.07) !important;
    }

    /* ── Tabs: Pink active indicator ── */
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #EC4899 !important;
        border-bottom: 3px solid #EC4899 !important;
        font-weight: 700 !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        color: #64748B !important;
        font-weight: 600 !important;
    }

    /* ── Primary Action Buttons: Pink ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #DB2777 0%, #BE185D 100%) !important;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.45) !important;
    }

    /* ── Form Submit Button: Pink ── */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35) !important;
    }

    /* ── Metric Values: Navy Bold ── */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #64748B !important;
    }

    /* ── Info / Success / Warning / Error Boxes ── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    /* ── Brand Header ── */
    .brand-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        color: #1E3A8A;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }
    .brand-accent {
        color: #EC4899;
    }
    .brand-subtitle {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }

    /* ── Section Titles ── */
    .section-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        color: #1E3A8A;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #E0E7FF;
    }

    /* ── Sidebar Header Label ── */
    .sidebar-header {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 800;
        font-size: 1.05rem;
        color: #FFFFFF;
        letter-spacing: 1px;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    /* ── Dataframe / Data Editor ── */
    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        border-radius: 12px !important;
        border: 1px solid #E0E7FF !important;
    }

    /* ── Expander headers ── */
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #1E3A8A !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Gemini Client Setup
# ---------------------------------------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

# On Streamlit Cloud, secrets are stored via st.secrets — fall back to it if .env is not present
if not gemini_api_key:
    try:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        gemini_api_key = None

if not gemini_api_key:
    st.error("🔑 **GEMINI_API_KEY is missing!** Add it to your `.env` file (local) or Streamlit Cloud Secrets (deployed).")
    st.stop()

client = genai.Client(api_key=gemini_api_key)

# ---------------------------------------------------------
# Session State Initialization (prevents UI refresh loss)
# ---------------------------------------------------------

if "expense_data" not in st.session_state:
    st.session_state.expense_data = None

if "manual_expenses" not in st.session_state:
    st.session_state.manual_expenses = []

if "roast_result" not in st.session_state:
    st.session_state.roast_result = None

# List of standard categories for select boxes
standard_categories = [
    "Food Delivery", "Eating Out", "Essentials", "Shopping", 
    "Subscriptions", "Transport", "Entertainment", "Bills", 
    "Personal Care", "Education", "Health"
]

# ---------------------------------------------------------
# Custom HTML/CSS Card Renderers (Aesthetic Alignment)
# ---------------------------------------------------------

def render_metric_card(label, value, delta=None, delta_direction="up", is_bad_behavior=False):
    """Renders a clean, neumorphic-style metric card with customizable delta colors."""
    delta_html = ""
    if delta:
        if is_bad_behavior:
            color = "#EF4444" if delta_direction == "up" else "#10B981"
        else:
            color = "#10B981" if delta_direction == "up" else "#EF4444"
        arrow = "↑" if delta_direction == "up" else "↓"
        delta_html = f'<div style="color: {color}; font-size: 0.85rem; font-weight: 600; margin-top: 4px; display: flex; align-items: center; gap: 2px;">{arrow} {delta}</div>'
    
    card_html = f"""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); height: 100%;">
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">{label}</div>
        <div style="color: #0f172a; font-size: 1.8rem; font-weight: 700; line-height: 1.1;">{value}</div>
        {delta_html}
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

def render_badge_card(title, value, color_hex):
    """Renders a clean summary info block with a custom pastel background accent."""
    card_html = f"""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border-top: 4px solid {color_hex}; text-align: center;">
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">{title}</div>
        <div style="color: #0F172A; font-size: 1.8rem; font-weight: 800;">{value}</div>
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Controls (Only display if data is loaded)
# ---------------------------------------------------------

if st.session_state.expense_data is not None:
    st.sidebar.markdown('<div class="sidebar-header">Master Settings</div>', unsafe_allow_html=True)
    
    # Reset button to allow loading new data files
    if st.sidebar.button("🔄 Clear & Ingest New Data", use_container_width=True):
        st.session_state.expense_data = None
        st.session_state.manual_expenses = []
        st.session_state.roast_result = None
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    
    # Monthly budget slider
    monthly_budget = st.sidebar.slider(
        "Monthly Budget Limit (₹)",
        min_value=5000,
        max_value=120000,
        value=25000,
        step=1000
    )

    # Date range filters based on data boundaries
    dates_in_data = sorted(st.session_state.expense_data['Date'].unique())
    start_date, end_date = st.sidebar.date_input(
        "Select Date Scope",
        value=(dates_in_data[0], dates_in_data[-1]),
        min_value=dates_in_data[0],
        max_value=dates_in_data[-1]
    )

    # Category filters
    all_categories = sorted(st.session_state.expense_data['Category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Categories Filter",
        options=all_categories,
        default=all_categories
    )

    # Apply all reactive filters to the core dataset
    filtered_df = st.session_state.expense_data[
        (st.session_state.expense_data['Date'] >= start_date) &
        (st.session_state.expense_data['Date'] <= end_date) &
        (st.session_state.expense_data['Category'].isin(selected_categories))
    ]

# ---------------------------------------------------------
# Main Page Render Logic
# ---------------------------------------------------------

st.markdown('<div class="brand-title">Expense <span class="brand-accent">Roaster</span></div>', unsafe_allow_html=True)

# EMPTY STATE: Ingest Data Screen
if st.session_state.expense_data is None:
    st.markdown('<div class="brand-subtitle">Treatment-ready personal finance metrics & dynamic AI roasts</div>', unsafe_allow_html=True)
    
    # Card-like layout for data setup
    st.info("💡 **Welcome to Expense Roaster.** To begin, please upload a transaction CSV or input records manually.")
    
    # User Input Workflow Tabs — CSV upload and manual entry only
    tab_upload, tab_manual = st.tabs(["📤 Upload Expenses CSV", "✏️ Manually Enter Expenses"])
    
    with tab_upload:
        st.markdown('<div class="section-title">Upload Transaction Data</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Select your CSV file (Expected Columns: Date, Item, Category, Amount, Payment_Method)",
            type=["csv"]
        )
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                uploaded_df['Date'] = pd.to_datetime(uploaded_df['Date']).dt.date
                st.session_state.expense_data = uploaded_df
                st.success("Expenses successfully imported!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to read CSV. Check column naming format: {str(e)}")

    with tab_manual:
        st.markdown('<div class="section-title">Manual Ingestion Console</div>', unsafe_allow_html=True)
        
        # Form to add entries individually without triggering visual updates constantly
        with st.form("manual_item_form"):
            col_date, col_item, col_cat = st.columns(3)
            with col_date:
                m_date = st.date_input("Date")
            with col_item:
                m_item = st.text_input("Item Description", placeholder="e.g. Starbucks Latte")
            with col_cat:
                m_category = st.selectbox("Category", options=standard_categories)
                
            col_amt, col_pay, col_btn = st.columns(3)
            with col_amt:
                m_amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            with col_pay:
                m_payment = st.selectbox("Payment Method", options=["UPI", "Credit Card", "Debit Card", "Cash"])
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                add_submitted = st.form_submit_button("Add Record", use_container_width=True)
                
            if add_submitted:
                if m_item.strip() == "":
                    st.warning("Please supply an item description.")
                else:
                    st.session_state.manual_expenses.append({
                        "Date": m_date,
                        "Item": m_item,
                        "Category": m_category,
                        "Amount": m_amount,
                        "Payment_Method": m_payment
                    })
                    st.success(f"Added '{m_item}' to transaction pool.")
        
        # If there are active manual expenses, show them
        if st.session_state.manual_expenses:
            st.markdown('<div class="section-title">Pending Session Transactions</div>', unsafe_allow_html=True)
            pending_df = pd.DataFrame(st.session_state.manual_expenses)
            st.dataframe(pending_df, use_container_width=True, hide_index=True)
            
            # Button to finalize and compile the manual data
            if st.button("Proceed & Analyze Manual Data", use_container_width=True, type="primary"):
                st.session_state.expense_data = pending_df
                st.rerun()



# MAIN DASHBOARD PANEL (Runs only if data exists in session)
else:
    st.markdown(f'<div class="brand-subtitle">AI-Driven Financial Habit Analysis • <b>{start_date.strftime("%B %d")} to {end_date.strftime("%B %d, %Y")}</b></div>', unsafe_allow_html=True)

    # Calculate metrics
    total_spent = filtered_df['Amount'].sum()
    num_transactions = len(filtered_df)
    avg_per_day = total_spent / max((end_date - start_date).days, 1)

    # Categories analysis
    category_totals = filtered_df.groupby('Category')['Amount'].sum()
    worst_category = category_totals.idxmax() if not category_totals.empty else "None"
    worst_category_amount = category_totals.max() if not category_totals.empty else 0

    # Budget delta
    budget_delta = total_spent - monthly_budget
    delta_str = f"₹{abs(budget_delta):,.0f} " + ("Over Budget" if budget_delta > 0 else "Under Budget")

    # ---------------------------------------------------------
    # Premium KPI Metric Cards
    # ---------------------------------------------------------
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        render_metric_card("Total Spending", f"₹{total_spent:,.0f}")
        
    with kpi_col2:
        render_metric_card(
            label="Budget Variance", 
            value=f"₹{monthly_budget:,.0f} Goal", 
            delta=delta_str,
            delta_direction="up" if budget_delta > 0 else "down",
            is_bad_behavior=True
        )
        
    with kpi_col3:
        render_metric_card(
            label="Biggest Pit Category", 
            value=worst_category, 
            delta=f"₹{worst_category_amount:,.0f} spent",
            delta_direction="up",
            is_bad_behavior=True
        )
        
    with kpi_col4:
        render_metric_card("Daily Spending Rate", f"₹{avg_per_day:,.0f}/day")

    # ---------------------------------------------------------
    # Plotly Data Visualizations (Refined Pastel Colors)
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">Analytics Engine</div>', unsafe_allow_html=True)

    # Chart color palette directly extracted from reference image:
    # Pink (#EC4899), Blue (#60A5FA), Yellow (#FBBF24), Lavender (#A78BFA), Green (#34D399), Coral (#F87171)
    ref_palette = ['#EC4899', '#60A5FA', '#FBBF24', '#A78BFA', '#34D399', '#F87171', '#38BDF8', '#FB923C']

    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        with st.container(border=True):
            st.markdown("**Category Distribution**")
            # Donut chart for spending distribution
            donut_df = filtered_df.groupby('Category')['Amount'].sum().reset_index()
            fig_donut = px.pie(
                donut_df, 
                values='Amount', 
                names='Category', 
                hole=0.55,
                color_discrete_sequence=ref_palette
            )
            fig_donut.update_traces(
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}",
                textfont_size=12,
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(t=15, b=15, l=15, r=15),
                height=290,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", size=11, color="#1E293B")
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with viz_col2:
        with st.container(border=True):
            st.markdown("**Daily Spend Burn Rate**")
            # Daily trends bar chart — pink bars matching reference accent
            daily_df = filtered_df.groupby('Date')['Amount'].sum().reset_index()
            daily_df['Date'] = daily_df['Date'].apply(lambda x: x.strftime('%b %d'))
            fig_bar = px.bar(
                daily_df,
                x='Date',
                y='Amount',
                color_discrete_sequence=['#EC4899']  # Hot pink from reference
            )
            fig_bar.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(t=15, b=15, l=15, r=15),
                height=290,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", size=11, color="#1E293B"),
                hovermode="x"
            )
            fig_bar.update_traces(
                hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}",
                marker_line_width=0,
                marker_opacity=0.9
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # payment method split
    with st.container(border=True):
        st.markdown("**Payment Method Share Over Time**")
        pay_df = filtered_df.groupby(['Date', 'Payment_Method'])['Amount'].sum().reset_index()
        pay_df['Date'] = pay_df['Date'].apply(lambda x: x.strftime('%b %d'))
        fig_pay = px.bar(
            pay_df,
            x='Date',
            y='Amount',
            color='Payment_Method',
            color_discrete_sequence=['#EC4899', '#60A5FA', '#FBBF24', '#34D399']  # Pink, Blue, Yellow, Green from reference
        )
        fig_pay.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(t=15, b=15, l=15, r=15),
            height=260,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="sans-serif", size=11, color="#1E293B"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_pay, use_container_width=True)

    # ---------------------------------------------------------
    # In-Session Data Grid Editor
    # ---------------------------------------------------------
    with st.expander("📝 Review & Edit Transactions Table", expanded=False):
        st.caption("Double-click any category or value cell below to adjust your transactions in real-time.")
        st.session_state.expense_data = st.data_editor(
            st.session_state.expense_data.sort_values('Date', ascending=False).reset_index(drop=True),
            use_container_width=True,
            num_rows="dynamic"
        )

    # ---------------------------------------------------------
    # Phase 3: AI Roast Master (Interactive st.form)
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">The Roast Engine</div>', unsafe_allow_html=True)

    # Prepare string summary for Gemini ingestion
    def get_structured_summary_text(data, budget):
        total = data['Amount'].sum()
        cat_agg = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_purchases = data.nlargest(5, 'Amount')[['Date', 'Item', 'Category', 'Amount']]
        
        sum_str = f"Monthly Spending Target: ₹{budget:,}\n"
        sum_str += f"Actual Expenditure: ₹{total:,.0f}\n"
        sum_str += f"Budget Standing: {'OVER BUDGET by ₹' + str(int(total - budget)) if total > budget else 'UNDER BUDGET by ₹' + str(int(budget - total))}\n\n"
        sum_str += "Spending per Category:\n" + cat_agg.to_string() + "\n\n"
        sum_str += "Top 5 Purchases:\n" + top_purchases.to_string(index=False)
        return sum_str

    formatted_summary = get_structured_summary_text(filtered_df, monthly_budget)

    # Form to trigger the Roast call intentionally
    with st.form("ai_roast_form"):
        st.markdown("Proceed to compile the data summary and query the AI Roast Engine.")
        
        # Displaying the Data Bridge preview inside the form for review
        with st.expander("🔗 Data Bridge Preview (Text submitted to Gemini)", expanded=False):
            st.code(formatted_summary, language="text")
            
        roast_triggered = st.form_submit_button("🔥 Fire Up the Roast Master", use_container_width=True)
        if roast_triggered:
            st.session_state.roast_requested = True

    # Define system instruction with structured schema parameters
    system_instruction = """
    You are "The Roast Master", a brutally honest, personal finance coach who roasts the user's spending data.
    
    You must return a JSON response matching this schema:
    {
        "grade": "Letter grade (A+ through F) grading their financial discipline",
        "savings_potential": "Estimated amount they can save next month (e.g. ₹4,500)",
        "roast_feedback": "A paragraph containing a direct, witty, and humorous roast of their biggest spending leaks",
        "recovery_steps": [
            "Actionable recovery step 1 with a concrete real-world replacement alternative",
            "Actionable recovery step 2 with a concrete real-world replacement alternative",
            "Actionable recovery step 3 with a concrete real-world replacement alternative"
        ],
        "avatar_prompt": "A short, descriptive prompt (max 20 words) depicting their financial state for image generation. Keep style consistent: 3d claymation style, pastel color scheme, soft lighting, minimalist clean background."
    }
    """

    @st.cache_data
    def fetch_expense_roast(summary_str):
        try:
            prompt = f"""
            Analyze the user's spending metrics and output a JSON matching the requested structure:
            {summary_str}
            """
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "grade": types.Schema(type=types.Type.STRING),
                            "savings_potential": types.Schema(type=types.Type.STRING),
                            "roast_feedback": types.Schema(type=types.Type.STRING),
                            "recovery_steps": types.Schema(
                                type=types.Type.ARRAY,
                                items=types.Schema(type=types.Type.STRING)
                            ),
                            "avatar_prompt": types.Schema(type=types.Type.STRING)
                        },
                        required=["grade", "savings_potential", "roast_feedback", "recovery_steps", "avatar_prompt"]
                    )
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "grade": "N/A",
                "savings_potential": "₹0",
                "roast_feedback": f"Could not communicate with the AI model: {str(e)}",
                "recovery_steps": ["Check your API key settings."],
                "avatar_prompt": "a broken key, simple clean layout, pastel background"
            }

    # Fetch roast
    if st.session_state.roast_requested:
        with st.spinner("🔥 Analysis in progress..."):
            st.session_state.roast_result = fetch_expense_roast(formatted_summary)
            st.session_state.roast_requested = False

    # Clean markdown formatting text helper
    def clean_text_formatting(text):
        if not isinstance(text, str):
            return text
        return text.replace('\\\\n', '\n').replace('\\n', '\n')

    # Display Roast Result Cards
    if st.session_state.roast_result:
        res = st.session_state.roast_result
        
        # Display Banners based on budget status
        if total_spent > monthly_budget:
            st.error(f"🚨 **Budget Limit Exceeded!** Total spending is ₹{total_spent - monthly_budget:,.0f} above your target goal.")
        else:
            st.success(f"🎉 **Under Budget!** Total spending is ₹{monthly_budget - total_spent:,.0f} below your limit.")

        # Roast & Avatar display columns
        col_feedback, col_avatar = st.columns([5, 3])

        with col_feedback:
            # Side-by-side Roast Summary badges
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                render_badge_card("Health Rating", res.get("grade", "C"), "#C084FC")
            with col_b2:
                render_badge_card("Savings Potential", res.get("savings_potential", "₹0"), "#A7F3D0")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("### 🗣️ Roast Assessment")
                st.write(clean_text_formatting(res.get("roast_feedback", "")))
                
                st.markdown("### 🛠️ Savings Action Steps")
                for step in res.get("recovery_steps", []):
                    st.markdown(f"- {clean_text_formatting(step)}")

        with col_avatar:
            with st.container(border=True):
                st.markdown("### ~_~ MOOOOOD")
                
                # Fetch Pollinations image based on prompt
                av_prompt = clean_text_formatting(res.get("avatar_prompt", "a dollar bill, pastel colors"))
                encoded_prompt = urllib.parse.quote(av_prompt)
                
                # Use total spent to seed the image so it changes only if dataset changes
                seed_val = int(total_spent)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed={seed_val}"
                
                # Render avatar image cleanly as a pure visual element without prompt description / filename
                st.image(image_url, use_container_width=True)
                st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.85rem; font-style: italic;'>AI-generated representation of your financial footprint</p>", unsafe_allow_html=True)
