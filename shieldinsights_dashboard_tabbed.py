import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import random
from datetime import datetime, timedelta

# ---------------- AI Recommendations Column ----------------
def generate_ai_recommendation(row):
    if row["Severity"] == "High" and row["Status"] != "Resolved":
        return "🚨 Immediate action required. Prioritize within 48h."
    elif row["Tool"] == "CrowdStrike" and row["Status"] == "Open":
        return "⚠️ Review CrowdStrike playbook for endpoint remediation."
    elif row["Team"] == "GRC":
        return "📄 Validate against latest compliance checklists."
    elif row["Status"] == "In Progress":
        return "⏳ Continue monitoring. Verify ETA with team lead."
    else:
        return "✅ No critical insight. Proceed as planned."

import matplotlib as mpl
from io import BytesIO
import streamlit.components.v1 as components

# ------------------ Dark Mode Chart Styling ------------------
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

# ------------------ Streamlit Setup ------------------
st.set_page_config(layout="wide")
st.title("ShieldInsights.ai – Real-Time Remediation Dashboard")

# ------------------ Custom CSS for KPI Cards ------------------
custom_css = """
<style>
.kpi-card {
    border-radius: 10px;
    padding: 20px;
    margin: 10px;
    background-color: #2a2a2a;
    color: white;
}
.kpi-card.green {
    border: 3px solid #4CAF50;
}
.kpi-card.red {
    border: 3px solid #F44336;
}
.kpi-card.blue {
    border: 3px solid #2196F3;
}
.kpi-card.orange {
    border: 3px solid #FF9800;
}
.kpi-icon {
    font-size: 50px;
    margin-bottom: 10px;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Function to create a KPI card
def kpi_card(title, value, icon, color):
    card_html = f"""
    <div class="kpi-card {color}">
        <div class="kpi-icon">{icon}</div>
        <h3>{title}</h3>
        <h1>{value}</h1>
    </div>
    """
    components.html(card_html, height=200)

# ------------------ Data Source Selection ------------------
data_source = st.radio("Select Data Source:", ["Upload Excel File", "Use API (Simulated)"])

# ------------------ Generate Structured Mock Data ------------------
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

# ------------------ Simulated API Logic ------------------
def get_api_data():
    data = generate_structured_mock_data(num_rows=3)
    if len(data) < 10:
        enriched_data = generate_structured_mock_data(num_rows=30)
        st.warning("Fewer than 10 rows retrieved from API — generating additional entries for visual completeness.")
        return enriched_data
    return data

# ------------------ Load Data ------------------
df = None
if data_source == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload Remediation Excel File", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df['when'] = pd.to_datetime(df['when'], errors='coerce')
else:
    df = get_api_data()

# ------------------ If Data is Loaded ------------------
if df is not None:
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 KPI Summary", 
        "📈 Drill-Down Dashboard", 
        "📉 Analyst Dashboard", 
        "📋 Remediation Table", 
        "🧠 AI Insights"
    ])

    # Tab 1 – KPI
    with tab1:
        st.subheader("KPI Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            kpi_card("Total Issues", len(df), "📊", "blue")
        with col2:
            kpi_card("Completed", df['status'].str.lower().eq('completed').sum(), "✅", "green")
        with col3:
            kpi_card("High Severity Open", len(df[(df['severity'].str.lower() == 'high') & (df['status'].str.lower() != 'completed')]), "⚠️", "red")
        with col4:
            kpi_card("Overdue", len(df[(df['status'].str.lower() != 'completed') & (df['when'] < pd.Timestamp.today())]), "⏰", "orange")

    # Filters
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

    # Tab 2 – Drill-Down
    with tab2:
        st.subheader("Status Distribution")
        pie_fig = px.pie(filtered_df, names='status', title='Status Distribution', hole=0.3)
        st.plotly_chart(pie_fig)

        drill_status = st.selectbox("Drill Down into Status:", filtered_df['status'].unique())
        df_drilled = filtered_df[filtered_df['status'] == drill_status]

        st.subheader(f"Domain vs. Severity for Status: {drill_status}")
        bar_fig = px.bar(df_drilled, x='domain', color='severity', barmode='group')
        st.plotly_chart(bar_fig)

        st.subheader(f"Remediation Items for Status: {drill_status}")
        st.dataframe(df_drilled[['record_id', 'domain', 'severity', 'status', 'who', 'when', 'action', 'recommendation']])

    # Tab 3 – Analyst Dashboard
    with tab3:
        st.subheader("Severity by Domain Heatmap")
        fig_heatmap, ax_heatmap = plt.subplots(figsize=(8, 5))
        pivot = pd.crosstab(filtered_df['domain'], filtered_df['severity'])
        sns.heatmap(pivot, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5, linecolor='gray', ax=ax_heatmap, cbar_kws={'label': 'Count'})
        ax_heatmap.set_title("Severity by Domain Heatmap", fontsize=14, fontweight='bold')
        ax_heatmap.tick_params(axis='x', rotation=45)
        ax_heatmap.tick_params(axis='y', rotation=0)
        st.pyplot(fig_heatmap)

        st.subheader("Timeline of Remediation Issues")
        fig_scatter, ax_scatter = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=filtered_df,
            x='when',
            y='domain',
            hue='status',
            style='severity',
            palette='deep',
            s=100,
            ax=ax_scatter
        )
        ax_scatter.set_title("Issue Timeline by Domain and Status", fontsize=14, fontweight='bold')
        ax_scatter.set_xlabel("Due Date")
        ax_scatter.set_ylabel("Domain")
        ax_scatter.grid(True, linestyle='--', linewidth=0.5)

        # Rotate the x-axis labels and change their format
        ax_scatter.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b %d'))
        plt.setp(ax_scatter.xaxis.get_majorticklabels(), rotation=45, ha="right")

        st.pyplot(fig_scatter)

    # Tab 4 – Table
    with tab4:
        st.subheader("Filtered Remediation Table")
        st.dataframe(filtered_df)

        def export_excel(data):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button("Download Filtered Data", data=export_excel(filtered_df), file_name="filtered_remediation.xlsx")

    # Tab 5 – AI Insights
    with tab5:
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

with tabs[5]:
    st.markdown("## 📅 Remediation Timeline")
    if "Start Date" in filtered_data.columns and "Due Date" in filtered_data.columns:
        try:
            timeline_data = filtered_data.copy()
            timeline_data["Start Date"] = pd.to_datetime(timeline_data["Start Date"], errors='coerce')
            timeline_data["Due Date"] = pd.to_datetime(timeline_data["Due Date"], errors='coerce')
            timeline_data = timeline_data.dropna(subset=["Start Date", "Due Date"])

            if not timeline_data.empty:
                fig = px.timeline(
                    timeline_data,
                    x_start="Start Date",
                    x_end="Due Date",
                    y="Description",
                    color="Status",
                    title="Remediation Timeline",
                    template="plotly_dark"
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid start/end dates available for timeline visualization.")
        except Exception as e:
            st.error(f"Error generating timeline: {e}")
    else:
        st.warning("Please ensure your dataset includes 'Start Date' and 'Due Date' columns.")
