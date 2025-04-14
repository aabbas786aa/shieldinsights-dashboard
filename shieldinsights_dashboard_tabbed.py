
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🔐 ShieldInsights.ai – Simulated Integrations Dashboard")

# Simulate integrations data
def simulate_integrations_data():
    tools = ['CrowdStrike', 'Okta', 'Splunk']
    sample_size = 30
    data = {
        'record id': [f'R{i+1:03d}' for i in range(sample_size)],
        'description': np.random.choice([
            'Endpoint threat detected', 'IAM misconfiguration', 'Log anomaly detected',
            'Privilege escalation attempt', 'SSL certificate expired'
        ], sample_size),
        'severity': np.random.choice(['High', 'Medium', 'Low'], sample_size),
        'status': np.random.choice(['Open', 'In Progress', 'Resolved'], sample_size),
        'tool': np.random.choice(tools, sample_size),
        'team': np.random.choice(['SOC', 'IAM', 'Cloud'], sample_size),
        'ai recommendation': np.random.choice([
            'Enable MFA', 'Patch vulnerability', 'Investigate endpoint', 'Reconfigure IAM policy'
        ], sample_size),
        'risk_score': np.random.randint(60, 95, sample_size),
        'source': np.random.choice(tools, sample_size),
        'when': pd.date_range(start="2025-04-01", periods=sample_size, freq="D"),
    }
    return pd.DataFrame(data)

df = simulate_integrations_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "KPI Summary", "Remediation Timeline", "AI Insights", "KPI Dashboard", "Admin / Analyst"
])

with tab1:
    st.subheader("📊 KPI Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Open Issues", (df['status'] == 'Open').sum())
    col3.metric("Avg. Risk Score", int(df['risk_score'].mean()))

    fig = px.pie(df, names='tool', title='Data Breakdown by Tool')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🗓️ Remediation Timeline")
    fig = px.scatter(df, x="when", y="team", color="status", size="risk_score", hover_name="description")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("💡 AI-Generated Recommendations")
    for tool in df['tool'].unique():
        subset = df[df['tool'] == tool].head(5)
        st.markdown(f"**{tool}** – Top Recommendations:")
        st.dataframe(subset[['record id', 'description', 'ai recommendation']])

with tab4:
    st.subheader("📈 KPI Bar Chart")
    fig = px.bar(df, x="tool", y="risk_score", color="severity", barmode="group", title="Risk Score by Tool")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("🧠 Analyst View: Heatmap + Timeline")

    st.markdown("### Domain vs. Severity Heatmap")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.heatmap(df.pivot_table(index="team", columns="severity", aggfunc="size", fill_value=0), annot=True, cmap="YlGnBu", ax=ax3)
    st.pyplot(fig3)

    st.markdown("### Risk Score Timeline by Tool")
    fig4 = px.scatter(df, x="when", y="tool", size="risk_score", color="status")
    st.plotly_chart(fig4, use_container_width=True)
