import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(layout='wide')

# ---------------- Integration Mode Toggle ----------------
def get_api_data():
    # Placeholder: Replace with actual Risk Cognizance API call
    return df.copy() if 'df' in globals() else pd.DataFrame()

    def simulate_integrations_data():
        simulated = df.copy() if 'df' in globals() else pd.DataFrame()
        if not simulated.empty:
            simulated['tool'] = simulated['tool'] if 'tool' in simulated.columns else 'CrowdStrike'
            simulated['source'] = simulated['tool'].apply(lambda t: 'CrowdStrike' if 'cloud' in t.lower() else ('Okta' if 'iam' in t.lower() else 'Splunk'))
            simulated['risk_score'] = simulated['severity'].apply(lambda s: 90 if s=='High' else (70 if s=='Medium' else 50))
        return simulated

    integration_mode = st.sidebar.radio("Select Integration Mode:",
    ["Risk Cognizance API (Current MVP)", "Simulated Integrations"])


# ---------- FILE UPLOAD BLOCK ----------
    uploaded_file = st.sidebar.file_uploader("📂 Upload Your Remediation File", type=["xlsx"])
    if uploaded_file:
        st.title('ShieldInsights.ai – Real-Time Remediation Dashboard')
        preview_df = pd.read_excel(uploaded_file).dropna().head(5)
        st.write(preview_df)
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

# Load data
# Show data table
    st.subheader('📋 Remediation Tasks')
    st.dataframe(data_source)

# --------- ADVANCED FILTERS BLOCK ---------
    st.markdown("### 🧰 Advanced Filters")
    colA, colB, colC = st.columns(3)
    selected_status = colA.multiselect("Filter by Status", options=sorted(data_source['Status'].dropna().unique()), default=sorted(data_source['Status'].dropna().unique()))
    selected_severity = colB.multiselect("Filter by Severity", options=sorted(data_source['Severity'].dropna().unique()), default=sorted(data_source['Severity'].dropna().unique()))
    selected_team = colC.multiselect("Filter by Team", options=sorted(data_source['Team'].dropna().unique()), default=sorted(data_source['Team'].dropna().unique()))

# ------------------ Dashboard Tabs ------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    'Overview',
    'KPI Dashboard',
    'Analyst Dashboard',
    'Remediation Table',
    '🧠 AI-Powered Insights (GPT-4)'
    ])

# -------------------- AI-Powered Insights (GPT-4) --------------------
    with tab5:
        st.markdown('''This module uses OpenAI GPT-4 to generate remediation guidance based on your filtered data.''')
        import openai
        client = openai.OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

        required_columns = {'Description', 'Severity', 'Domain'}
        if required_columns.issubset(data_source.columns):
            preview_df = data_source[['Description', 'Severity', 'Domain']].dropna().head(5)
            for i, row in preview_df.iterrows():
                prompt = f"""
                Given the following issue:
                Description: {row['Description']}
                Severity: {row['Severity']}
                Domain: {row['Domain']}
            
                Suggest a detailed remediation plan from a security best practices perspective.
                """
                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a cybersecurity expert providing remediation advice."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    insight = response.choices[0].message.content
                    st.markdown(f"### 🔍 Insight for: `{row['Description'][:50]}...`")
                    st.success(insight)
                except Exception as e:
                    st.error(f"Error from OpenAI: {e}")
    else:
        st.warning("⚠️ Required columns ('Description', 'Severity', 'Domain') not found in the data. Please upload a valid remediation file.")
    st.subheader("📌 Admin / Analyst Dashboard")
    if data_source is not None and not data_source.empty:
    if 'domain' not in data_source.columns:
    data_source['domain'] = np.random.choice(['IAM', 'Cloud', 'Network', 'Data'], size=len(data_source))
    if 'severity' not in data_source.columns:
    data_source['severity'] = np.random.choice(['Low', 'Medium', 'High'], size=len(data_source))
    if 'status' not in data_source.columns:
    data_source['status'] = np.random.choice(['Open', 'In Progress', 'Resolved'], size=len(data_source))
    if 'when' not in data_source.columns:
    data_source['when'] = [datetime.today() + timedelta(days=random.randint(-5, 10)) for _ in range(len(data_source))]

    st.subheader("Domain vs. Severity Heatmap")
    heatmap_data = data_source.groupby(['domain', 'severity']).size().unstack(fill_value=0)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    st.pyplot(fig3)

    st.subheader("Remediation Timeline")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.set_xlabel("Target Date")
    ax4.set_ylabel("Domain")
    st.pyplot(fig4)
    else:
    st.warning("No data available for enhanced admin visuals.")

# Keep original df reference for legacy code blocks if needed
    df = data_source


# -------------------- AI-Powered Insights (GPT-4) --------------------
    st.markdown('''This module uses OpenAI GPT-4 to generate remediation guidance based on your filtered data.''')
import openai

    required_columns = {'Description', 'Severity', 'Domain'}
    if required_columns.issubset(data_source.columns):
    preview_df = data_source[['Description', 'Severity', 'Domain']].dropna().head(5)
    for i, row in preview_df.iterrows():
    prompt = f"""
    Given the following issue:
    Description: {row['Description']}
    Severity: {row['Severity']}
    Domain: {row['Domain']}

    Suggest a detailed remediation plan from a security best practices perspective.
    """
    try:
    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
    {"role": "system", "content": "You are a cybersecurity expert providing remediation advice."},
    {"role": "user", "content": prompt}
    ]
    )
    insight = response.choices[0].message.content
    st.markdown(f"### 🔍 Insight for: `{row['Description'][:50]}...`")
    st.success(insight)
    except Exception as e:
    st.error(f"Error from OpenAI: {e}")
    else:
    st.warning("⚠️ Required columns ('Description', 'Severity', 'Domain') not found in the data. Please upload a valid remediation file.")
