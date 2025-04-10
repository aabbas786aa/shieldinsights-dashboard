import streamlit as st

# Set page configuration
st.set_page_config(layout="wide")

import pandas as pd

# Placeholder for file upload
uploaded_file = st.sidebar.file_uploader("Upload your data file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load the uploaded file into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    
    # Render the severity filter only if the data is loaded
    severity_filter = st.sidebar.multiselect("Severity", df['severity'].dropna().unique())
else:
    # Display a message prompting the user to upload the file
    st.sidebar.warning("Please upload a data file to proceed.")
    
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import random
from datetime import datetime, timedelta
import matplotlib as mpl
from io import BytesIO
import streamlit.components.v1 as components

# ------------------ Theme Toggle ------------------
theme_option = st.sidebar.radio("Choose Theme", ["Dark", "Light"])
if theme_option == "Light":
    mpl.rcParams.update({
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "figure.facecolor": "white",
        "grid.color": "#cccccc",
        "text.color": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.titlecolor": "black",
        "font.size": 11,
        "legend.edgecolor": "black",
        "legend.facecolor": "#eaeaea",
    })
    sns.set_style("whitegrid")
else:
    mpl.rcParams.update({
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
    })
    sns.set_style("darkgrid")

# ------------------ Custom CSS for KPI Cards ------------------
custom_css = """
<style>
.kpi-card {
    border-radius: 10px;
    padding: 20px;
    margin: 10px;
    background-color: #2a2a2a;
    color: white;
    text-align: center;
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

# ------------------ Enhanced KPI Card Function ------------------
def kpi_card(title, value, icon, color, filter_query=None):
    card_html = f"""
    <div class="kpi-card {color}" style="cursor: pointer;">
        <div class="kpi-icon">{icon}</div>
        <h3>{title}</h3>
        <h1>{value}</h1>
    </div>
    """
    if filter_query and st.button("", key=title):
        st.session_state['filter'] = filter_query
    components.html(card_html, height=200)

# ------------------ RISK Cognizance Simulation Functions ------------------
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

def get_api_data():
    data = generate_structured_mock_data(num_rows=3)
    if len(data) < 10:
        enriched_data = generate_structured_mock_data(num_rows=30)
        st.warning("Fewer than 10 rows retrieved from RISK Cognizance API — generating additional entries for visual completeness.")
        return enriched_data
    return data

# ------------------ Simulated Integrations Functions ------------------
def simulate_tool_data(tool_name, num_events=10):
    events = []
    for i in range(num_events):
        events.append({
            "event_id": f"{tool_name[:2].upper()}-{random.randint(1000, 9999)}",
            "tool": tool_name,
            "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 120)),
            "event_type": random.choice(["Login", "Alert", "Anomaly"]),
            "severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "details": f"Simulated event from {tool_name}"
        })
    return pd.DataFrame(events)

def simulate_integrations_data():
    cs_data = simulate_tool_data("CrowdStrike", num_events=10)
    okta_data = simulate_tool_data("Okta", num_events=8)
    splunk_data = simulate_tool_data("Splunk", num_events=12)
    combined_df = pd.concat([cs_data, okta_data, splunk_data], ignore_index=True)
    # Normalize severity labels
    combined_df['severity'] = combined_df['severity'].str.lower().str.capitalize()
    # Deduplicate by event_id
    combined_df = combined_df.drop_duplicates(subset='event_id')
    # Enrichment: assign a risk score based on severity
    severity_mapping = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    combined_df['risk_score'] = combined_df['severity'].map(severity_mapping)
    combined_df['ai_insight'] = combined_df.apply(
        lambda row: f"Event {row['event_id']} is high risk. Immediate remediation recommended!" 
        if row['risk_score'] >= 3 else "Normal event", axis=1)
    return combined_df

# ------------------ Sidebar: Integration Mode Selection ------------------
integration_mode = st.sidebar.radio("Select Integration Mode:", 
    ["RISK Cognizance API (Current MVP)", "Simulated Integrations (CrowdStrike, Okta, Splunk)"])

# ------------------ Main Dashboard Title & Page Config ------------------
# st.set_page_config(layout="wide")
st.title("ShieldInsights.ai – Real-Time Remediation Dashboard")

# ------------------ Main Branch: RISK Cognizance vs. Simulated Integrations ------------------
if integration_mode == "RISK Cognizance API (Current MVP)":
    # RISK Cognizance Data Source Selection
    data_source_option = st.radio("Select Data Source:", ["Upload Excel File", "Use API (Simulated)"])
    df = None
    if data_source_option == "Upload Excel File":
        uploaded_file = st.file_uploader("Upload Remediation Excel File", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            df['when'] = pd.to_datetime(df['when'], errors='coerce')
    else:
        df = get_api_data()

    # Debug: Check if df is loaded correctly
    if df is None:
        st.error("Failed to load data")
    else:
        st.write("Data loaded successfully")
        st.write(df.head())  # Print the first few rows of df

    # Ensure df is not None before proceeding
    if df is not None:
        # Dashboard Tabs for RISK Cognizance
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 KPI Summary", 
            "📈 Drill-Down Dashboard", 
            "📉 Analyst Dashboard", 
            "📋 Remediation Table", 
            "🧠 AI Insights"
        ])

        # Tab 1 – KPI Summary
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
    
    # Sidebar Filters for RISK Cognizance Data
    st.sidebar.header("Filters")

    if df is not None:
        # Render filters only if df is loaded
        severity_filter = st.sidebar.multiselect("Severity", df['severity'].dropna().unique())
        status_filter = st.sidebar.multiselect("Status", df['status'].dropna().unique())
        
        #severity_filter = st.sidebar.multiselect("Severity", df['severity'].dropna().unique())
        #status_filter = st.sidebar.multiselect("Status", df['status'].dropna().unique())
        
        team_filter = st.sidebar.multiselect("Team", df['who'].dropna().unique())
        tool_filter = st.sidebar.multiselect("Source Tool", df['source_tool'].dropna().unique())
        start_date = st.sidebar.date_input("Start Due Date", value=None)
        end_date = st.sidebar.date_input("End Due Date", value=None)
    else:
        st.sidebar.warning("Please upload or load the data to apply filters.")
        
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
    
    # Tab 2 – Drill-Down Dashboard
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
        ax_scatter.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b %d'))
        plt.setp(ax_scatter.xaxis.get_majorticklabels(), rotation=45, ha="right")
        st.pyplot(fig_scatter)
    
    # Tab 4 – Remediation Table
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

else:
    # ---------- Simulated Integrations Mode ----------
    integrated_data = simulate_integrations_data()
    
    # ---------- Dashboard Tabs for Simulated Integrations ----------
    tab1_sim, tab2_sim, tab3_sim = st.tabs([
        "📊 KPI Summary", 
        "📈 Event Dashboard", 
        "🧠 AI Insights"
    ])
    
    # Tab 1 – KPI Summary for Simulated Integrations
    with tab1_sim:
        st.subheader("KPI Metrics - Simulated Integrations")
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("Total Events", len(integrated_data), "📊", "blue")
        with col2:
            high_risk_events = integrated_data[integrated_data['risk_score'] >= 3]
            kpi_card("High Risk Events", len(high_risk_events), "⚠️", "red")
        with col3:
            normal_events = integrated_data[integrated_data['risk_score'] < 3]
            kpi_card("Normal Events", len(normal_events), "✅", "green")
    
    # Tab 2 – Event Dashboard for Simulated Integrations
    with tab2_sim:
        st.subheader("Event Dashboard - Simulated Integrations")
        st.markdown("""
        This section visualizes the event data aggregated from CrowdStrike, Okta, and Splunk.
        """)
        fig_bar = px.bar(
            integrated_data, 
            x='tool', 
            color='severity', 
            title="Event Distribution by Tool and Severity",
            labels={"tool": "Security Tool", "severity": "Event Severity"}
        )
        st.plotly_chart(fig_bar)
        
        fig_timeline = px.scatter(
            integrated_data, 
            x='timestamp', 
            y='tool', 
            color='severity', 
            size='risk_score',
            hover_data=['event_id', 'event_type', 'ai_insight'],
            title="Timeline of Integrated Events"
        )
        st.plotly_chart(fig_timeline)
    
    # Tab 3 – AI Insights for Simulated Integrations
    with tab3_sim:
        st.subheader("AI-Generated Insights - Simulated Integrations")
        st.dataframe(integrated_data[['event_id', 'tool', 'timestamp', 'severity', 'risk_score', 'ai_insight']])
        st.markdown("### Summary of AI Insights")
        for idx, row in integrated_data.iterrows():
            st.markdown(f"**Event {row['event_id']} ({row['tool']})**: {row['ai_insight']}")
        st.markdown("### Download All Events")
        output = BytesIO()
        integrated_data.to_excel(output, index=False)
        st.download_button("Download All Events", data=output.getvalue(), file_name="integrated_events.xlsx")
        st.session_state["admin_logs"].append({"User Type": "Customer", "Action": "Downloaded all events", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.markdown("### Download Filtered Events")
        filtered_events = integrated_data[integrated_data['risk_score'] >= 3]
        output_filtered = BytesIO()
        filtered_events.to_excel(output_filtered, index=False)
        st.download_button("Download Filtered Events", data=output_filtered.getvalue(), file_name="filtered_events.xlsx")
        st.session_state["admin_logs"].append({"User Type": "Customer", "Action": "Downloaded filtered events", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.markdown("### Export Event Report")
        selected_event = st.selectbox("Select Event to Export", integrated_data['event_id'].unique())
        if st.button("Export Event Report"):
            event_report = integrated_data[integrated_data['event_id'] == selected_event]
            output_event = BytesIO()
            event_report.to_excel(output_event, index=False)
            st.download_button("Download Event Report", data=output_event.getvalue(), file_name=f"{selected_event}_report.xlsx")
            st.session_state["admin_logs"].append({"User Type": "Customer", "Action": f"Exported report: {selected_event}", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.markdown("### Engagement Timeline View")
        timeline_data = pd.DataFrame({
            "Milestone": ["Engagement Start", "Security Assessment", "Solution Design", "Implementation", "Testing", "Go Live"],
            "Start": ["2025-04-01", "2025-04-03", "2025-04-07", "2025-04-14", "2025-04-18", "2025-04-24"],
            "Finish": ["2025-04-02", "2025-04-06", "2025-04-13", "2025-04-17", "2025-04-23", "2025-04-30"],
            "Owner": ["ShieldNexus", "Vendor", "Joint", "Vendor", "Customer", "Customer"]
        })
        fig_timeline = px.timeline(
            timeline_data,
            x_start="Start",
            x_end="Finish",
            y="Milestone",
            color="Owner",
            title="Customer Project Timeline",
            template="plotly_dark"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.session_state["admin_logs"].append({"User Type": "Customer", "Action": "Viewed engagement timeline", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.markdown("### Export Engagement Report")
        selected_milestone = st.selectbox("Select Milestone to Export", timeline_data['Milestone'].unique())
        if st.button("Export Engagement Report"):
            milestone_report = timeline_data[timeline_data['Milestone'] == selected_milestone]
            output_milestone = BytesIO()
            milestone_report.to_excel(output_milestone, index=False)
            st.download_button("Download Engagement Report", data=output_milestone.getvalue(), file_name=f"{selected_milestone}_report.xlsx")
            st.session_state["admin_logs"].append({"User Type": "Customer", "Action": f"Exported report: {selected_milestone}", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.markdown("### Admin Logs")
        if "admin_logs" not in st.session_state:
            st.session_state["admin_logs"] = []
        admin_logs_df = pd.DataFrame(st.session_state["admin_logs"])
        st.dataframe(admin_logs_df)
        st.markdown("### User Feedback")
        feedback = st.text_area("Please provide your feedback:")
        if st.button("Submit Feedback"):
            st.session_state["admin_logs"].append({"User Type": "Customer", "Action": f"Feedback submitted: {feedback}", "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            st.success("Thank you for your feedback!")
        st.markdown("### User Engagement")
        engagement_data = pd.DataFrame(st.session_state["admin_logs"])
        engagement_data['Timestamp'] = pd.to_datetime(engagement_data['Timestamp'])
        engagement_data['Date'] = engagement_data['Timestamp'].dt.date
        engagement_data['Time'] = engagement_data['Timestamp'].dt.time
        engagement_data['Hour'] = engagement_data['Timestamp'].dt.hour
        engagement_data['Minute'] = engagement_data['Timestamp'].dt.minute
        engagement_data['Second'] = engagement_data['Timestamp'].dt.second
        engagement_data['Day'] = engagement_data['Timestamp'].dt.day
        engagement_data['Month'] = engagement_data['Timestamp'].dt.month
        engagement_data['Year'] = engagement_data['Timestamp'].dt.year
        engagement_data['Day of Week'] = engagement_data['Timestamp'].dt.day_name()
        engagement_data['Week of Year'] = engagement_data['Timestamp'].dt.isocalendar().week
        engagement_data['Quarter'] = engagement_data['Timestamp'].dt.quarter
        engagement_data['Is Weekend'] = engagement_data['Timestamp'].dt.dayofweek >= 5
        engagement_data['Is Weekday'] = engagement_data['Timestamp'].dt.dayofweek < 5
        engagement_data['Is Holiday'] = engagement_data['Timestamp'].dt.date.isin(pd.to_datetime(["2025-01-01", "2025-12-25"]).date)
        engagement_data['Is Workday'] = engagement_data['Is Weekend'] == False
        engagement_data['Is Non-Workday'] = engagement_data['Is Weekend'] == True
        engagement_data['Is Morning'] = engagement_data['Hour'] < 12
        engagement_data['Is Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Evening'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Night'] = engagement_data['Hour'] >= 0
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 22) & (engagement_data['Hour'] < 24)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 22)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 22) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Afternoon'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Evening'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Evening'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Night'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)
        engagement_data['Is Late Night'] = (engagement_data['Hour'] >= 18) & (engagement_data['Hour'] < 24)
        engagement_data['Is Early Morning'] = (engagement_data['Hour'] >= 0) & (engagement_data['Hour'] < 6)
        engagement_data['Is Late Morning'] = (engagement_data['Hour'] >= 6) & (engagement_data['Hour'] < 12)
        engagement_data['Is Early Afternoon'] = (engagement_data['Hour'] >= 12) & (engagement_data['Hour'] < 18)    
