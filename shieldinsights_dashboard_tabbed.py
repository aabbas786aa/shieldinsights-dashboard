import streamlit as st
import pandas as pd
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
    data_source = pd.read_excel(uploaded_file)
    st.sidebar.success("✅ File uploaded and loaded successfully.")
else:
    st.sidebar.warning("⚠️ Using preloaded sample data.")
data_source = get_api_data() if integration_mode.startswith("Risk Cognizance") else simulate_integrations_data()
import plotly.express as px
from datetime import datetime, timedelta
import random

st.title('ShieldInsights.ai – Real-Time Remediation Dashboard')

# Data source selection
data_source = st.radio('Select Data Source:', ['Upload Excel File', 'Use API (Simulated)'])

# Structured mock data generator
def generate_mock_data(n=30):
    domains = ['IAM', 'Cloud', 'Network', 'Endpoint']
    severities = ['Low', 'Medium', 'High']
    statuses = ['Open', 'In Progress', 'Resolved']
    teams = ['GRC', 'SOC', 'InfraSec']
    tools = ['CrowdStrike', 'SailPoint', 'Splunk']
    data = []
    for i in range(n):
        data.append({
            'Record ID': f'RID-{1000 + i}',
            'Description': f'Task {i}',
            'Severity': random.choice(severities),
            'Status': random.choice(statuses),
            'Team': random.choice(teams),
            'Tool': random.choice(tools),
            'Start Date': (datetime.today() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d'),
            'Due Date': (datetime.today() + timedelta(days=random.randint(3, 15))).strftime('%Y-%m-%d')
        })
    return pd.DataFrame(data)

# Load data
data_source = None
if data_source == 'Upload Excel File':
    uploaded_file = st.file_uploader('Upload Excel File', type=['xlsx'])
    if uploaded_file:
        data_source = pd.read_excel(uploaded_file)
    else:
        data_source = generate_mock_data()
else:
    data_source = generate_mock_data()

# Show data table
st.subheader('📋 Remediation Tasks')
st.dataframe(data_source)

# --------- ADVANCED FILTERS BLOCK ---------
st.markdown("### 🧰 Advanced Filters")
colA, colB, colC = st.columns(3)
selected_status = colA.multiselect("Filter by Status", options=sorted(data_source['Status'].dropna().unique()), default=sorted(data_source['Status'].dropna().unique()))
selected_severity = colB.multiselect("Filter by Severity", options=sorted(data_source['Severity'].dropna().unique()), default=sorted(data_source['Severity'].dropna().unique()))
selected_team = colC.multiselect("Filter by Team", options=sorted(data_source['Team'].dropna().unique()), default=sorted(data_source['Team'].dropna().unique()))

data_source = data_source[
    data_source['Status'].isin(selected_status) &
    data_source['Severity'].isin(selected_severity) &
    data_source['Team'].isin(selected_team)
].copy()

# ------------------ Dashboard Tabs ------------------
tabs = st.tabs(["Overview", "Timeline", "Insights", "KPI Dashboard", "Admin / Analyst"])

with tabs[0]:
    st.subheader("🗂 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(data_source))
    col2.metric("Open", (data_source['Status'] == 'Open').sum())
    col3.metric("Resolved", (data_source['Status'] == 'Resolved').sum())

    st.dataframe(data_source)

with tabs[1]:
    st.subheader("📅 Remediation Timeline")
    if 'Start Date' in data_source.columns and 'Due Date' in data_source.columns:
        data_source['Start Date'] = pd.to_datetime(data_source['Start Date'], errors='coerce')
        data_source['Due Date'] = pd.to_datetime(data_source['Due Date'], errors='coerce')
        fig = px.timeline(data_source, x_start='Start Date', x_end='Due Date', y='Description', color='Status')
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(fig, use_container_width=True)


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
            if row.get('severity') == 'High': base += 30
            elif row.get('severity') == 'Medium': base += 15
            if row.get('status') == 'Open': base += 10
            elif row.get('status') == 'In Progress': base += 5
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

# ---------------- Admin/Analyst Dashboard ----------------

# ---------------- Admin/Analyst Dashboard (Seaborn with Fallback) ----------------
import matplotlib.pyplot as plt
import seaborn as sns

with tabs[4]:
    st.subheader("📌 Admin / Analyst Dashboard")
    if data_source is not None and not data_source.empty:
        fallback_data_source = data_source.copy()
        import numpy as np
        import random
        from datetime import datetime, timedelta

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

# Keep original df reference for legacy code blocks if needed
df = data_source
