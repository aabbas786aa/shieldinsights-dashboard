import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(layout='wide')

# ---------------- Integration Mode Toggle ----------------
def get_api_data():
    # Placeholder: Replace with actual Risk Cognizance API call
    return df.copy() if 'df' in globals() else pd.DataFrame()

def simulate_integrations_data():
    simulated = df.copy() if 'df' in globals() else pd.DataFrame()
    if not simulated.empty:
        simulated['tool'] = simulated['tool'] if 'tool' in simulated.columns else 'CrowdStrike'
        simulated['source'] = simulated['tool'].apply(
            lambda t: 'CrowdStrike' if 'cloud' in t.lower() else ('Okta' if 'iam' in t.lower() else 'Splunk'))
        simulated['risk_score'] = simulated['severity'].apply(lambda s: 90 if s == 'High' else (70 if s == 'Medium' else 50))
    return simulated

integration_mode = st.sidebar.radio("Select Integration Mode:",
                                    ["Risk Cognizance API (Current MVP)", "Simulated Integrations"])

# ---------- FILE UPLOAD BLOCK ----------
uploaded_file = st.sidebar.file_uploader("📂 Upload Your Remediation File", type=["xlsx"])
if uploaded_file:
    st.title('ShieldInsights.ai – Real-Time Remediation Dashboard')
    preview_df = pd.read_excel(uploaded_file).dropna().head(5)
    st.write(preview_df)

# Track changes in session state
if 'change_detected' not in st.session_state:
    st.session_state['change_detected'] = False

# Detect file upload changes
if uploaded_file:
    st.session_state['change_detected'] = True  # Set the change detection flag
    st.title('ShieldInsights.ai – Real-Time Remediation Dashboard')
    preview_df = pd.read_excel(uploaded_file).dropna().head(5)
    st.write(preview_df)

# Detect filter changes
if selected_status or selected_severity or selected_team:
    st.session_state['change_detected'] = True  # Set the change detection flag

def generate_mock_data(n=30):
    severities = ['High', 'Medium', 'Low']
    statuses = ['Open', 'Closed', 'In Progress']
    teams = ['Team A', 'Team B', 'Team C']
    tools = ['Tool X', 'Tool Y', 'Tool Z']
    domains = ['IAM', 'Network', 'Cloud', 'Endpoint']
    data = []
    for i in range(n):
        data.append({
            'Record ID': f'RID-{1000 + i}',
            'Description': f'Task {i}',
            'Severity': random.choice(severities),
            'Status': random.choice(statuses),
            'Team': random.choice(teams),
            'Tool': random.choice(tools),
            'Domain': random.choice(domains)
        })
    return pd.DataFrame(data)

# Initialize fallback data source
data_source = generate_mock_data()

# --------- ADVANCED FILTERS BLOCK ---------
st.markdown("### 🧰 Advanced Filters")
colA, colB, colC = st.columns(3)
selected_status = colA.multiselect(
    "Filter by Status",
    options=sorted(data_source['Status'].dropna().unique()),
    default=sorted(data_source['Status'].dropna().unique())
)
selected_severity = colB.multiselect(
    "Filter by Severity",
    options=sorted(data_source['Severity'].dropna().unique()),
    default=sorted(data_source['Severity'].dropna().unique())
)
selected_team = colC.multiselect(
    "Filter by Team",
    options=sorted(data_source['Team'].dropna().unique()),
    default=sorted(data_source['Team'].dropna().unique())
)

data_source = data_source[
    data_source['Status'].isin(selected_status) &
    data_source['Severity'].isin(selected_severity) &
    data_source['Team'].isin(selected_team)
].copy()

# Track changes in session state
if 'change_detected' not in st.session_state:
    st.session_state['change_detected'] = False

# Detect file upload changes
if uploaded_file:
    st.session_state['change_detected'] = True  # Set the change detection flag
    st.title('ShieldInsights.ai – Real-Time Remediation Dashboard')
    preview_df = pd.read_excel(uploaded_file).dropna().head(5)
    st.write(preview_df)

# Detect filter changes
if selected_status or selected_severity or selected_team:
    st.session_state['change_detected'] = True  # Set the change detection flag

# ------------------ Dashboard Tabs ------------------
tabs = st.tabs([
    "Overview", "Timeline", "Insights", "KPI Dashboard", "Admin / Analyst", "🧠 AI-Powered Insights (Enterprise GenAI)"
])

with tabs[0]:
    st.subheader("🗂 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(data_source))
    col2.metric("Open", (data_source['Status'] == 'Open').sum())
    col3.metric("Resolved", (data_source['Status'] == 'Resolved').sum())
    st.dataframe(data_source)

with tabs[1]:
    st.subheader("📅 Remediation Timeline")
    
    # Check if the necessary columns exist in the data source
    if {'Start Date', 'Due Date', 'Description', 'Status'}.issubset(data_source.columns):
        # Convert columns to datetime and handle invalid entries
        data_source['Start Date'] = pd.to_datetime(data_source['Start Date'], errors='coerce')
        data_source['Due Date'] = pd.to_datetime(data_source['Due Date'], errors='coerce')

        # Filter out rows with invalid or missing dates
        valid_data = data_source.dropna(subset=['Start Date', 'Due Date'])

        if not valid_data.empty:
            # Create a timeline plot using Plotly
            fig = px.timeline(
                valid_data,
                x_start='Start Date',
                x_end='Due Date',
                y='Description',
                color='Status',
                title="Remediation Timeline"
            )
            fig.update_yaxes(autorange='reversed')  # Reverse the y-axis for better visualization
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid data available for the timeline. Please check 'Start Date' and 'Due Date' columns.")
    else:
        st.warning("Required columns ('Start Date', 'Due Date', 'Description', 'Status') are missing in the data source.")

# ------------------ AI Insights Generator ------------------
def generate_ai_recommendation(row):
    if row['Severity'] == 'High' and row['Status'] != 'Resolved':
        return '🚨 Immediate attention required.'
    elif row['Tool'] == 'CrowdStrike' and row['Status'] == 'Open':
        return '⚠️ Review endpoint configurations urgently.'
    elif row['Team'] == 'GRC':
        return '📄 Ensure compliance artifacts are updated.'
    elif row['Status'] == 'In Progress':
        return '⏳ Monitor progress and confirm ETA.'
    else:
        return '✅ Proceed as planned.'

with tabs[2]:
    st.subheader("🧠 AI-Generated Insights")
    if data_source is not None and not data_source.empty:
        # ---------------- Risk Scoring Logic ----------------
        def assign_risk_score(row):
            base = 50
            if row.get('Severity') == 'High': base += 30
            elif row.get('Severity') == 'Medium': base += 15
            if row.get('Status') == 'Open': base += 10
            elif row.get('Status') == 'In Progress': base += 5
            return min(base, 100)

        data_source['Risk Score'] = data_source.apply(assign_risk_score, axis=1)
        data_source['AI Recommendation'] = data_source.apply(generate_ai_recommendation, axis=1)
        st.dataframe(data_source[['Record ID', 'Description', 'Severity', 'Status', 'Tool', 'Team', 'Risk Score', 'AI Recommendation']])
    else:
        st.warning("No data available for AI insights.")

with tabs[3]:
    st.subheader("📊 KPI Dashboard")
    if data_source is not None and not data_source.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", len(data_source))
        col2.metric("Open", (data_source['Status'] == 'Open').sum())
        col3.metric("Resolved", (data_source['Status'] == 'Resolved').sum())

        st.markdown("### Severity Distribution")
        severity_counts = data_source['Severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig = px.bar(severity_counts, x='Severity', y='Count', color='Severity', title='Severity Breakdown')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for KPI analysis.")

with tabs[4]:
    st.subheader("📌 Admin / Analyst Dashboard")
    if data_source is not None and not data_source.empty:
        fallback_data_source = data_source.copy()

        if 'domain' not in fallback_data_source.columns:
            fallback_data_source['domain'] = np.random.choice(['IAM', 'Cloud', 'Network', 'Data'], size=len(fallback_data_source))
        if 'severity' not in fallback_data_source.columns:
            fallback_data_source['severity'] = np.random.choice(['Low', 'Medium', 'High'], size=len(fallback_data_source))
        if 'status' not in fallback_data_source.columns:
            fallback_data_source['status'] = np.random.choice(['Open', 'In Progress', 'Resolved'], size=len(fallback_data_source))
        if 'when' not in fallback_data_source.columns:
            fallback_data_source['when'] = [datetime.today() + timedelta(days=random.randint(-5, 10)) for _ in range(len(fallback_data_source))]

        st.subheader("Domain vs. Severity Heatmap")
        heatmap_data = fallback_data_source.groupby(['domain', 'severity']).size().unstack(fill_value=0)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlGnBu', ax=ax3)
        st.pyplot(fig3)

        st.subheader("Remediation Timeline")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=fallback_data_source, x='when', y='domain', hue='status', style='severity', ax=ax4)
        ax4.set_xlabel("Target Date")
        ax4.set_ylabel("Domain")
        st.pyplot(fig4)
    else:
        st.warning("No data available for enhanced admin visuals.")


# -------------------- AI-Powered Insights (GPT-4o) --------------------
with tabs[5]:  # AI-Powered Insights Tab
    st.subheader("🧠 AI-Powered Insights (Enterprise GenAI)")
    st.markdown('''This module uses Enterprise GenAI LLM to generate remediation guidance based on your filtered data.''')

    import openai  # Ensure proper indentation for import statements
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Check for required columns in the data
    required_columns = {'Description', 'Severity', 'Domain'}
    if required_columns.issubset(data_source.columns):  # Ensure the required columns exist
        preview_df = data_source[['Description', 'Severity', 'Domain']].dropna().head(5)  # Sample top 5 rows
        
        # Add a confirmation dialog to control GPT-4o execution
        change_detected = st.session_state.get('change_detected', False)  # Track changes in session state
        if change_detected:  # If a change is detected
            rerun_decision = st.radio(
                "The App has noticed a change to the data. Would you like to re-run the GenAI Insights?",
                ["Yes", "No"]
            )

            if rerun_decision == "Yes":
                # Reset change detection flag
                st.session_state['change_detected'] = False

                # Execute GPT-4o insights generation
                for i, row in preview_df.iterrows():
                    # Create a GPT-4o prompt based on the row's data
                    prompt = f"""
                    Given the following issue:
                    Description: {row['Description']}
                    Severity: {row['Severity']}
                    Domain: {row['Domain']}

                    Suggest a detailed remediation plan from a security best practices perspective.
                    """
                    try:
                        # Make the API call to GPT-4o
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a cybersecurity expert providing remediation advice."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        # Extract and display the generated insight
                        insight = response.choices[0].message.content
                        st.markdown(f"### 🔍 Insight for: `{row['Description'][:50]}...`")
                        st.success(insight)
                    except Exception as e:
                        st.error(f"Error from OpenAI: {e}")
            else:
                st.info("AI insights execution skipped.")
        else:
            st.info("No changes detected. Insights are up-to-date.")
    else:
        # Warn the user if required columns are not found
        st.warning("⚠️ Required columns ('Description', 'Severity', 'Domain') not found in the data. Please upload a valid remediation file.")on file.")
