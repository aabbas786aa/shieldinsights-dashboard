import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(layout='wide')
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
df = None
if data_source == 'Upload Excel File':
    uploaded_file = st.file_uploader('Upload Excel File', type=['xlsx'])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
    else:
        df = generate_mock_data()
else:
    df = generate_mock_data()

# Show data table
st.subheader('📋 Remediation Tasks')
st.dataframe(df)

# ------------------ Dashboard Tabs ------------------
tabs = st.tabs(["Overview", "Timeline", "Insights", "KPI Dashboard", "Admin / Analyst"])

with tabs[0]:
    st.subheader("🗂 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(df))
    col2.metric("Open", (df['Status'] == 'Open').sum())
    col3.metric("Resolved", (df['Status'] == 'Resolved').sum())

    st.dataframe(df)

with tabs[1]:
    st.subheader("📅 Remediation Timeline")
    if 'Start Date' in df.columns and 'Due Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        fig = px.timeline(df, x_start='Start Date', x_end='Due Date', y='Description', color='Status')
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
    if df is not None and not df.empty:
        df['AI Recommendation'] = df.apply(generate_ai_recommendation, axis=1)
        st.dataframe(df[['Record ID', 'Description', 'Severity', 'Status', 'Tool', 'Team', 'AI Recommendation']])
    else:
        st.warning("No data available for AI insights.")

with tabs[3]:
    st.subheader("📊 KPI Dashboard")
    if df is not None and not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", len(df))
        col2.metric("Open", (df['Status'] == 'Open').sum())
        col3.metric("Resolved", (df['Status'] == 'Resolved').sum())

        st.markdown("### Severity Distribution")
        severity_counts = df['Severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig = px.bar(severity_counts, x='Severity', y='Count', color='Severity', title='Severity Breakdown')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for KPI analysis.")

# ---------------- Admin/Analyst Dashboard ----------------

# ---------------- Admin/Analyst Dashboard (Seaborn Enhanced) ----------------
import matplotlib.pyplot as plt
import seaborn as sns

with tabs[4]:
    st.subheader("📌 Admin / Analyst Dashboard")
    if df is not None and not df.empty:
        filtered_df = df.copy()
        if 'domain' in filtered_df.columns and 'severity' in filtered_df.columns:
            st.subheader("Domain vs. Severity Heatmap")
            heatmap_data = filtered_df.groupby(['domain', 'severity']).size().unstack(fill_value=0)
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlGnBu', ax=ax3)
            st.pyplot(fig3)

        if 'when' in filtered_df.columns and 'domain' in filtered_df.columns:
            st.subheader("Remediation Timeline")
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=filtered_df, x='when', y='domain', hue='status', style='severity', ax=ax4)
            ax4.set_xlabel("Target Date")
            ax4.set_ylabel("Domain")
            st.pyplot(fig4)
    else:
        st.warning("No data available for enhanced admin visuals.")
