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

# ------------------ Dashboard Tabs ------------------
tabs = st.tabs([
    "Overview", "Timeline", "Insights", "KPI Dashboard", "Admin / Analyst", "🧠 AI-Powered Insights (GPT-4)"
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


157| ## -------------------- AI-Powered Insights (GPT-4o) --------------------
158| with tabs[5]:  # Ensure it integrates as a tab in the main code
159|     st.subheader("🧠 AI-Powered Insights (GPT-4o)")
160|     st.markdown('''This module uses OpenAI GPT-4o to generate remediation guidance based on your filtered data.''')
161| 
162|     import openai  # Ensure proper indentation for import statements
163|     client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
164| 
165|     required_columns = {'Description', 'Severity', 'Domain'}
166|     if required_columns.issubset(data_source.columns):  # Check if required columns exist
167|         preview_df = data_source[['Description', 'Severity', 'Domain']].dropna().head(5)  # Sample top 5 rows
168|         for i, row in preview_df.iterrows():
169|             # Create a GPT-4o prompt based on the row's data
170|             prompt = f"""
171|             Given the following issue:
172|             Description: {row['Description']}
173|             Severity: {row['Severity']}
174|             Domain: {row['Domain']}
175| 
176|             Suggest a detailed remediation plan from a security best practices perspective.
177|             """
178|             try:
179|                 # Make the API call to GPT-4o
180|                 response = client.chat.completions.create(
181|                     model="gpt-4o",
182|                     messages=[
183|                         {"role": "system", "content": "You are a cybersecurity expert providing remediation advice."},
184|                         {"role": "user", "content": prompt}
185|                     ]
186|                 )
187|                 # Extract and display the generated insight
188|                 insight = response.choices[0].message.content
189|                 st.markdown(f"### 🔍 Insight for: `{row['Description'][:50]}...`")
190|                 st.success(insight)
191|             except Exception as e:
192|                 st.error(f"Error from OpenAI: {e}")
193|     else:
194|         # Warn the user if required columns are not found
195|         st.warning("⚠️ Required columns ('Description', 'Severity', 'Domain') not found in the data. Please upload a valid remediation file.")
