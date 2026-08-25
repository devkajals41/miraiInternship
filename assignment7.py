import streamlit as st
import pandas as pd
import os
import json
import urllib.parse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------
# Page Configuration & Clean Setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="Life-OS Wellbeing Dashboard",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Inject minimal, clean styles to optimize spacing and font readability
st.markdown("""
<style>
    /* Clean Title styling */
    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    /* Ensure the metric cards look clean and simple */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #0f172a;
    }
    
    /* Metric label styling */
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# Retrieve API key and instantiate the Google GenAI Client
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("🔑 **GEMINI_API_KEY is missing!** Please configure it in your `.env` file.")
    st.stop()

client = genai.Client(api_key=gemini_api_key)

# ---------------------------------------------------------
# Phase 1: Data Pipeline
# ---------------------------------------------------------

@st.cache_data
def load_screentime_data():
    """
    Loads screen time data from screentime.csv, parses dates,
    and returns a clean, cached Pandas DataFrame.
    """
    csv_file = "screentime.csv"
    if not os.path.exists(csv_file):
        st.error(f"📂 Dataset `{csv_file}` not found. Please ensure it is present in the project directory.")
        st.stop()
    
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

# Load the screen time dataset
df = load_screentime_data()

# Unique dates for the filter dropdown
unique_dates = sorted(df['Date'].unique(), reverse=True)
# Human-friendly format for date selection
friendly_date_labels = {date: date.strftime('%A, %b %d, %Y') for date in unique_dates}

# ---------------------------------------------------------
# Phase 2: Sidebar Controls
# ---------------------------------------------------------

st.sidebar.title("⚙️ Life-OS Controls")
st.sidebar.markdown("Navigate days and configure screen time boundaries.")

# Dropdown selection for dates with human-friendly formatting
selected_date = st.sidebar.selectbox(
    "Select Day to Inspect",
    options=unique_dates,
    format_func=lambda d: friendly_date_labels[d],
    index=0
)

# Screen time limit slider
daily_goal_hours = st.sidebar.slider(
    "Daily Limit (Hours)",
    min_value=1.0,
    max_value=12.0,
    value=4.0,
    step=0.5,
    help="Define the maximum hours you want to spend on screens daily."
)
daily_goal_minutes = int(daily_goal_hours * 60)

# Filter dataset for the selected date
day_df = df[df['Date'] == selected_date]

# ---------------------------------------------------------
# Dashboard Main Layout & KPI Row
# ---------------------------------------------------------

# Main SaaS Header
st.markdown('<div class="app-title">Life-OS Wellbeing Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">Daily Screen Time Statistics & Holistic AI Coaching • <b>{selected_date.strftime("%A, %B %d, %Y")}</b></div>', unsafe_allow_html=True)

# Calculate metrics for the selected day
total_minutes = day_df['Minutes_Used'].sum()
total_hours_spent = total_minutes / 60

# Find most used app and its duration
if not day_df.empty:
    most_used_row = day_df.loc[day_df['Minutes_Used'].idxmax()]
    most_used_app_name = most_used_row['App_Name']
    most_used_app_minutes = most_used_row['Minutes_Used']
else:
    most_used_app_name = "None"
    most_used_app_minutes = 0

# Calculate delta value compared to the goal set by the user
delta_minutes = total_minutes - daily_goal_minutes

# Format total time string
total_time_str = f"{total_minutes // 60}h {total_minutes % 60}m"

# Delta format (positive is over limit, negative is under limit)
if delta_minutes > 0:
    delta_str = f"+{abs(delta_minutes)}m (Over Limit)"
else:
    delta_str = f"-{abs(delta_minutes)}m (Under Limit)"

# Render the KPI metrics using st.columns and st.container(border=True)
metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    with st.container(border=True):
        st.metric(
            label="⏱️ Total Screen Time Today",
            value=total_time_str
        )

# Fix truncation by placing the app name as the value and the duration as the delta
with metric_col2:
    with st.container(border=True):
        st.metric(
            label="📱 Most Used App",
            value=most_used_app_name,
            delta=f"{most_used_app_minutes}m used",
            delta_color="off" # neutral color to keep it clean
        )

with metric_col3:
    with st.container(border=True):
        # delta_color="inverse" makes positive (over limit) RED, and negative (under limit) GREEN
        st.metric(
            label="🎯 Target Limit vs. Actual",
            value=f"{daily_goal_hours}h Goal",
            delta=delta_str,
            delta_color="inverse"
        )

# ---------------------------------------------------------
# Visualizations: 14-Day Screen Time Trend
# ---------------------------------------------------------

st.subheader("📊 14-Day Screen Time Trends")

# Group data by Date and Category to show daily breakdowns
trend_df = df.groupby(['Date', 'Category'])['Minutes_Used'].sum().reset_index()

# Format Date as string YYYY-MM-DD for the chart to prevent auto-bucketing by date type
trend_df['Date'] = trend_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

# Render a stacked bar chart displaying Category breakdown over the 14 days
st.bar_chart(
    data=trend_df,
    x='Date',
    y='Minutes_Used',
    color='Category',
    use_container_width=True
)

# ---------------------------------------------------------
# Phase 3 & 4: AI Integration & Guilt-Trip Avatar
# ---------------------------------------------------------

st.subheader("🧠 Coach Aegis's Review")

# Function to aggregate daily usage into a clean text-based structure for Gemini
def prepare_day_summary_str(selected_day_df):
    """
    Aggregates day's app usage by category and lists individual apps.
    """
    category_summary = selected_day_df.groupby('Category')['Minutes_Used'].sum().reset_index()
    category_summary = category_summary.sort_values(by='Minutes_Used', ascending=False)
    
    app_details = selected_day_df[['App_Name', 'Category', 'Minutes_Used']].sort_values(by='Minutes_Used', ascending=False)
    
    summary_text = "CATEGORY SUMMARY:\n" + category_summary.to_string(index=False)
    summary_text += "\n\nAPP BREAKDOWN:\n" + app_details.to_string(index=False)
    return summary_text

# Format day's data
day_data_summary = prepare_day_summary_str(day_df)

# Clean markdown parser to fix literal backslash-n (\n) strings from JSON responses
def clean_markdown_content(text):
    if not isinstance(text, str):
        return text
    # Replace literal '\n' and '\\n' string representations with actual newline characters
    return text.replace('\\\\n', '\n').replace('\\n', '\n')

# Define instructions for Gemini acting as the life coach
system_instruction = """
You are "Aegis", a brutal-but-fair, direct, and holistic productivity and lifestyle coach.
You analyze screen time data and tell the user the hard truth about their digital habits. 
Do NOT just tell them to "use their phone less." 
You must analyze their category breakdown and suggest physical, real-world replacements for their wasted time.
For example, if they spent hours on social media or entertainment, suggest they reclaim that time for exercise, reading, cooking, or social outings.
If they spent a lot of time on coding or education, acknowledge their focus but remind them of balance, physical activity, and eye strain.

Write your coach response in standard Markdown using mixed-case (do not use all-caps for sections or headers, keep it looking clean and readable).

You must respond ONLY with a JSON object containing two fields:
1. "coach_response": A markdown formatted string containing your brutal-but-fair coaching feedback, breakdown analysis, and real-world replacement ideas. Use bullet points, bold text, and section headers (like '## The Brief', '## Reclaim Plan') for readability. Use an honest, sharp, yet motivating tone.
2. "avatar_prompt": A highly descriptive, short image prompt (max 30 words) that visualizes the user's screen time behavior for today. It will be passed to an image generator. 
- If they stayed under their goal (good day) or focused on Coding/Education: generate a positive, inspiring avatar prompt (e.g., "a disciplined zen warrior coding under a cherry blossom tree, 3d claymation style, vibrant colors").
- If they exceeded their goal (bad day) or wasted time on Social Media/Entertainment: generate a funny, mildly guilt-tripping avatar prompt (e.g., "a lazy zombie slouched on a couch staring at a glowing phone screen, 3d cartoon style, dark moody room").
- Make sure the style is consistent (e.g. "3d cartoon style" or "cyberpunk digital art").
"""

# Cached function to retrieve Gemini responses, preventing redundant API calls on UI updates
@st.cache_data
def fetch_coaching_and_avatar(date_str, total_mins, goal_mins, summary_str):
    try:
        prompt = f"""
        Here is the user's screen time data for {date_str}:
        Total Screen Time: {total_mins} minutes
        Daily Screen Time Goal: {goal_mins} minutes
        Screen Time Status: {"EXCEEDED GOAL by " + str(total_mins - goal_mins) + " minutes" if total_mins > goal_mins else "STAYED UNDER GOAL by " + str(goal_mins - total_mins) + " minutes"}

        {summary_str}

        Please analyze this data and generate your feedback and avatar prompt in JSON format.
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
                        "coach_response": types.Schema(type=types.Type.STRING),
                        "avatar_prompt": types.Schema(type=types.Type.STRING),
                    },
                    required=["coach_response", "avatar_prompt"]
                )
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        return {
            "coach_response": f"⚠️ **Failed to contact Coach Aegis:** {str(e)}\n\nPlease ensure your API connection and key are working correctly.",
            "avatar_prompt": "a rusty broken robot in a junkyard, cartoon style"
        }

# Get coaching insights and avatar prompt
with st.spinner("🧠 Consulting Coach Aegis..."):
    insights = fetch_coaching_and_avatar(
        date_str=str(selected_date),
        total_mins=total_minutes,
        goal_mins=daily_goal_minutes,
        summary_str=day_data_summary
    )

# Extract insights and clean any escaped newlines
coach_feedback = clean_markdown_content(insights.get("coach_response", "No feedback generated."))
avatar_prompt = clean_markdown_content(insights.get("avatar_prompt", "a simple drawing of a phone, cartoon style"))

# Display banner based on goal status
if total_minutes > daily_goal_minutes:
    exceeded_by = total_minutes - daily_goal_minutes
    if exceeded_by >= 120:
        st.error(f"🚨 **Goal Exceeded:** You went over your daily screen time goal by **{exceeded_by // 60}h {exceeded_by % 60}m**.")
    else:
        st.warning(f"⚠️ **Goal Exceeded:** You went over your screen time budget by **{exceeded_by} minutes** today.")
else:
    under_by = daily_goal_minutes - total_minutes
    st.success(f"🎉 **Goal Met:** You stayed **{under_by // 60}h {under_by % 60}m** under your screen time limit today. Keep it up!")

# Render Coach verdict and Avatar side-by-side using simple, clean columns
col_verdict, col_avatar = st.columns([5, 3])

with col_verdict:
    with st.container(border=True):
        st.markdown(coach_feedback)

with col_avatar:
    with st.container(border=True):
        st.markdown("### 🤖 Daily Avatar")
        
        # Generate image URL from Pollinations.ai (using day of the month as seed to keep images stable per day)
        day_seed = int(pd.to_datetime(selected_date).strftime('%d'))
        encoded_avatar_prompt = urllib.parse.quote(avatar_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_avatar_prompt}?width=512&height=512&nologo=true&seed={day_seed}"
        
        # Render avatar image on the dashboard
        st.image(
            image_url,
            use_container_width=True
        )
