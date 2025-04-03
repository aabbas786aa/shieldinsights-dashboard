
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from datetime import datetime, timedelta
import matplotlib as mpl
from io import BytesIO
import plotly.express as px

# -----------------------------------
# Dark Theme Setup
# -----------------------------------
dark_theme_style = {
    "axes.facecolor": "#1e1e1e",
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "figure.facecolor": "#1e1e1e",
    "grid.color": "#444444",
    "text.color": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.titlecolor": "white",
    "font.size": 11,
    "legend.edgecolor": "white",
    "legend.facecolor": "#2a2a2a",
}
mpl.rcParams.update(dark_theme_style)
sns.set_style("darkgrid")

st.set_page_config(layout="wide")
st.title("ShieldInsights.ai – Real-Time Remediation Dashboard")

# -----------------------------------
# Data Source Selector
# -----------------------------------
data_source = st.radio("Select Data Source:", ["Upload Excel File", "Use API (Simulated)"])

# -----------------------------------
# Mock Data Generator
# -----------------------------------
def generate_structured_mock_data(num_rows=30):
    domains = ["IAM", "Cloud Security", "Network", "Endpoint", "GRC", "Data Protection"]
    severities = ["Low", "Medium", "High", "Critical"]
    statuses = ["Not Started", "In Progress", "Completed"]
    recommendations = [
        "Implement centralized logging for privileged access.",
        "Patch known vulnerabilities in internet-facing systems.",
        "Disable unused admin accounts.",
        "Apply least privilege across IAM roles.",
        "Encrypt data at rest and in transit.",
        "Enforce MFA on all high-risk accounts."
    ]
    actions = [
        "Review access logs weekly.",
        "Patch all critical CVEs within 7 days.",
        "Run quarterly account audits.",
        "Limit access to production environments.",
        "Set encryption policies in cloud storage.",
        "Enable conditional access policies."
    ]
    teams = ["CloudOps", "IAM Team", "Network Security", "GRC Team", "SOC Team"]
    tools = ["SailPoint", "Qualys", "CrowdStrike", "Azure Defender", "Splunk", "Tenable"]
    impacts = ["High", "Moderate", "Critical", "Low"]
    tracking = ["On Track", "Delayed", "Pending Approval"]

    mock_rows = []
    for i in range(num_rows):
        mock_rows.append({
            "record_id": f"SIM-{1000+i}",
            "domain": random.choice(domains),
            "status": random.choice(statuses),
            "severity": random.choice(severities),
            "recommendation": random.choice(recommendations),
            "action": random.choice(actions),
            "who": random.choice(teams),
            "when": datetime.today() + timedelta(days=random.randint(-15, 45)),
            "status_tracking": random.choice(tracking),
            "risk_impact": random.choice(impacts),
            "source_tool": random.choice(tools)
        })
    return pd.DataFrame(mock_rows)

# -----------------------------------
# API Simulation and Enrichment
# -----------------------------------
def get_api_data():
    data = generate_structured_mock_data(num_rows=3)
    if len(data) < 10:
        enriched_data = generate_structured_mock_data(num_rows=30)
        st.warning("Fewer than 10 rows retrieved from API — generating additional entries for visual completeness.")
        return enriched_data
    return data

# -----------------------------------
# Data Loading Logic
# -----------------------------------
df = None
if data_source == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload Remediation Excel File", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df['when'] = pd.to_datetime(df['when'], errors='coerce')
else:
    df = get_api_data()

# -----------------------------------
# Dashboard Rendering
# -----------------------------------
if df is not None:
    # Filters Sidebar
    st.sidebar.header("Filters")
    severity_filter = st.sidebar.multiselect("Severity", df['severity'].dropna().unique())
    status_filter = st.sidebar.multiselect("Status", df['status'].dropna().unique())
    team_filter = st.sidebar.multiselect("Team", df['who'].dropna().unique())
    tool_filter = st.sidebar.multiselect("Source Tool", df['source_tool'].dropna().unique())
    start_date = st.sidebar.date_input("Start Due Date", value=None)
    end_date = st.sidebar.date_input("End Due Date", value=None)

    filtered_df = df.copy()
    if severity_filter:
        filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if team_filter:
        filtered_df = filtered_df[filtered_df['who'].isin(team_filter)]
    if tool_filter:
        filtered_df = filtered_df[filtered_df['source_tool'].isin(tool_filter)]
    if start_date:
        filtered_df = filtered_df[filtered_df['when'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['when'] <= pd.to_datetime(end_date)]

    tab1, tab2, tab3, tab4 = st.tabs(["📊 KPI Summary", "📈 Dashboards", "📋 Remediation Table", "🧠 AI Insights"])

    with tab1:
        st.subheader("KPI Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Issues", len(filtered_df))
        col2.metric("Completed", filtered_df['status'].str.lower().eq('completed').sum())
        col3.metric("High Severity Open", len(filtered_df[(filtered_df['severity'].str.lower() == 'high') & (filtered_df['status'].str.lower() != 'completed')]))
        col4.metric("Overdue", len(filtered_df[(filtered_df['status'].str.lower() != 'completed') & (filtered_df['when'] < pd.Timestamp.today())]))

    with tab2:
        st.subheader("Remediation Status Distribution")
        pie_fig = px.pie(filtered_df, names='status', title='Status Distribution', hole=0.3)
        st.plotly_chart(pie_fig)

        drilldown_status = st.selectbox("Drill down into Status:", filtered_df['status'].unique())
        df_drilled = filtered_df[filtered_df['status'] == drilldown_status]

        st.subheader(f"Domain vs. Severity for Status: {drilldown_status}")
        bar_fig = px.bar(df_drilled, x='domain', color='severity', barmode='group')
        st.plotly_chart(bar_fig)

        st.subheader(f"Remediation Items for Status: {drilldown_status}")
        st.dataframe(df_drilled[['record_id', 'domain', 'severity', 'status', 'who', 'when', 'action', 'recommendation']])

    with tab3:
        st.subheader("Filtered Remediation Table")
        st.dataframe(filtered_df)

        def export_excel(data):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button("Download Filtered Data", data=export_excel(filtered_df), file_name="filtered_remediation.xlsx")

    with tab4:
        st.subheader("AI-Generated Insights")
        insights = []
        high_sev_open = filtered_df[(filtered_df['severity'].str.lower() == 'high') & (filtered_df['status'].str.lower() != 'completed')]
        if not high_sev_open.empty:
            insights.append(f"There are {len(high_sev_open)} high severity issues still open.")

        overdue = filtered_df[(filtered_df['status'].str.lower() != 'completed') & (filtered_df['when'] < pd.Timestamp.today())]
        if not overdue.empty:
            insights.append(f"{len(overdue)} items are overdue across {overdue['domain'].nunique()} domains.")

        if not filtered_df['who'].isna().all():
            top_team = filtered_df['who'].value_counts().idxmax()
            insights.append(f"The '{top_team}' team owns the most items.")

        if 'source_tool' in filtered_df.columns and not filtered_df['source_tool'].isna().all():
            top_tool = filtered_df['source_tool'].value_counts().idxmax()
            insights.append(f"The top reporting tool is '{top_tool}'.")

        for i, insight in enumerate(insights, 1):
            st.markdown(f"**{i}. {insight}**")
