
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

st.set_page_config(layout="wide")

# Integration mode selector
integration_mode = st.sidebar.radio("Select Integration Mode:", ["Risk Cognizance API (Current MVP)", "Simulated Integrations"])

# Mock functions
def get_api_data():
    try:
        return df.copy() if 'df' in globals() else pd.DataFrame()
    except:
        return pd.DataFrame()

def simulate_integrations_data():
    sample_size = 30
    tools = ['CrowdStrike', 'Okta', 'Splunk']
    severities = ['High', 'Medium', 'Low']
    statuses = ['Open', 'In Progress', 'Resolved']
    descriptions = ['Endpoint threat detected', 'IAM misconfiguration', 'Anomaly in logs', 'Privilege escalation risk']
    data = {
        'record id': [f'R-{i+1:03d}' for i in range(sample_size)],
        'description': np.random.choice(descriptions, sample_size),
        'severity': np.random.choice(severities, sample_size),
        'status': np.random.choice(statuses, sample_size),
        'tool': np.random.choice(tools, sample_size),
        'team': np.random.choice(['SOC', 'IAM', 'Infra'], sample_size),
        'ai recommendation': np.random.choice([
            'Enable MFA', 'Patch known vulnerabilities', 'Review IAM policies', 'Investigate anomalies'], sample_size),
        'risk_score': np.random.randint(60, 96, sample_size),
        'source': np.random.choice(tools, sample_size)
    }
    df_sim = pd.DataFrame(data)
    df_sim.columns = [col.lower().strip() for col in df_sim.columns]
    return df_sim

# Load data
data_source = get_api_data() if integration_mode.startswith("Risk Cognizance") else simulate_integrations_data()

if data_source is not None and not data_source.empty:
    st.title("ShieldInsights.ai - Unified Dashboard")

    tab1, tab2, tab3 = st.tabs(["KPI Summary", "Detailed View", "AI Insights"])

    with tab1:
        st.subheader("KPI Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(data_source))
        if "status" in data_source.columns:
            col2.metric("Open", (data_source["status"] == "Open").sum())
            col3.metric("Resolved", (data_source["status"] == "Resolved").sum())

        if integration_mode == "Simulated Integrations":
            st.markdown("### 🔍 Simulated Tool Breakdown")
            if "source" in data_source.columns:
                fig = px.pie(data_source, names='source', title='Data Distribution by Integration Source')
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 🔎 Risk Scores by Integration")
            if "source" in data_source.columns and "risk_score" in data_source.columns:
                fig_bar = px.bar(data_source, x='source', y='risk_score', color='source',
                                 barmode='group', title='Average Risk Scores by Integration')
                st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("📊 Detailed Data View")
        st.dataframe(data_source)

    with tab3:
        st.subheader("💡 AI-Generated Insights")
        if "source" in data_source.columns:
            for tool in data_source["source"].unique():
                subset = data_source[data_source["source"] == tool]
                st.markdown(f"**{tool}** Recommendations:")
                st.dataframe(subset[["record id", "description", "ai recommendation"]].head(5))
