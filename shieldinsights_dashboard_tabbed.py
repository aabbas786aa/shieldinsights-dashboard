import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib as mpl
import random  # Missing import added

# Set page configuration
st.set_page_config(layout="wide")

# Placeholder for file upload
uploaded_file = st.sidebar.file_uploader("Upload your data file", type=["csv", "xlsx"])

if df is None or df.empty:
    st.warning("No data available. Please upload a valid dataset.")
    st.stop()  # Prevent further execution if no data
    
df = None
filtered_df = pd.DataFrame()  # Initialize as an empty DataFrame

# Validate uploaded file before processing
if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            
        # Additional check for required columns
        required_columns = ['when', 'domain', 'status', 'severity']
        if not set(required_columns).issubset(df.columns):
            st.error(f"Uploaded file is missing required columns: {', '.join(required_columns)}")
            st.stop()
        st.sidebar.success("File uploaded successfully!")

         # Validate if df is empty
    if df is None or df.empty:
        st.warning("No data available. Please upload a valid dataset.")
        st.stop()  # Prevent further execution if no data 
        
    #except Exception as e:
        #st.error(f"Error reading file: {e}")
       # st.stop()
else:
    st.sidebar.warning("Please upload a data file to proceed.")
    st.stop()

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

# ------------------ Data Validation ------------------
if df is not None:
    required_columns = ['when', 'domain', 'status', 'severity']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
    else:
        df['when'] = pd.to_datetime(df['when'], errors='coerce')  # Ensure dates are parsed correctly
        filtered_df = df.copy()

# ------------------ Filters ------------------
if not filtered_df.empty:
    st.sidebar.header("Filters")
    severity_filter = st.sidebar.multiselect("Severity", filtered_df['severity'].dropna().unique())
    status_filter = st.sidebar.multiselect("Status", filtered_df['status'].dropna().unique())
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    # Apply filters
    if severity_filter:
        filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if start_date:
        filtered_df = filtered_df[filtered_df['when'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['when'] <= pd.to_datetime(end_date)]

# ------------------ Tabs ------------------
tab1, tab2, tab3 = st.tabs(["📊 KPI Summary", "📈 Charts", "📋 Data Table"])

tab4, tab5 = st.tabs(["📊 Remediation Table", "🧠 AI Insights"])

with tab1:
    st.subheader("KPI Metrics")
    if not filtered_df.empty:
        total_issues = len(filtered_df)
        completed_issues = filtered_df['status'].str.lower().eq('completed').sum()
        high_severity = len(filtered_df[filtered_df['severity'].str.lower() == 'high'])
        overdue = len(filtered_df[filtered_df['when'] < datetime.now()])

        st.metric("Total Issues", total_issues)
        st.metric("Completed Issues", completed_issues)
        st.metric("High Severity", high_severity)
        st.metric("Overdue Issues", overdue)

with tab2:
    st.subheader("Charts")
    if not filtered_df.empty:
        pie_chart = px.pie(filtered_df, names='status', title="Status Distribution")
        st.plotly_chart(pie_chart)

with tab3:
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df)
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv_data, file_name="filtered_data.csv", mime="text/csv")

    # Tab 4 – Remediation Table
with tab4:
    st.subheader("Filtered Remediation Table")

    # Validate if filtered_df exists and is not empty
    if filtered_df.empty:
        st.warning("No data available for the remediation table. Adjust filters or upload a valid dataset.")
    else:
        # Display the filtered remediation data
        st.dataframe(filtered_df)

        # Export function for Excel
       def export_excel(data):
        if data.empty:
            return None
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False)
        return output.getvalue()

        # Download button for filtered data
        st.download_button(
            "Download Filtered Data",
            data=export_excel(filtered_df),
            file_name="filtered_remediation.xlsx"
        )

# Tab 5 – AI Insights
with tab5:
    st.subheader("AI-Generated Insights")

    if filtered_df.empty:
        st.warning("No data available for generating AI insights. Please upload a valid dataset or adjust filters.")
    else:
        insights = []

        # High-severity open issues
        if 'severity' in filtered_df.columns and 'status' in filtered_df.columns:
            high_sev_open = filtered_df[
                (filtered_df['severity'].str.lower() == 'high') &
                (filtered_df['status'].str.lower() != 'completed')
            ]
            if not high_sev_open.empty:
                insights.append(f"There are {len(high_sev_open)} high severity issues still open.")

        # Overdue issues
        if 'when' in filtered_df.columns:
            overdue = filtered_df[
                (filtered_df['status'].str.lower() != 'completed') &
                (filtered_df['when'] < pd.Timestamp.today())
            ]
            if not overdue.empty:
                insights.append(f"{len(overdue)} items are overdue across {overdue['domain'].nunique()} domains.")

        # Most active team
        if 'who' in filtered_df.columns and not filtered_df['who'].isna().all():
            top_team = filtered_df['who'].value_counts().idxmax()
            insights.append(f"The '{top_team}' team owns the most items.")

        # Top reporting tool
        if 'source_tool' in filtered_df.columns and not filtered_df['source_tool'].isna().all():
            top_tool = filtered_df['source_tool'].value_counts().idxmax()
            insights.append(f"The top reporting tool is '{top_tool}'.")

        # Display AI insights
        if insights:
            for i, insight in enumerate(insights, 1):
                st.markdown(f"**{i}. {insight}**")
        else:
            st.info("No actionable insights available for the current dataset.")

# Simulated Integrations Mode
if integration_mode == "Simulated Integrations (CrowdStrike, Okta, Splunk)":
    integrated_data = simulate_integrations_data()

    if integrated_data.empty:
        st.error("No data available from simulated integrations. Please check the simulation logic.")
    else:
        # Tabs for simulated integrations
        tab1_sim, tab2_sim, tab3_sim = st.tabs([
            "📊 KPI Summary",
            "📈 Event Dashboard",
            "🧠 AI Insights"
        ])

        # Tab 1 – KPI Summary
        with tab1_sim:
            st.subheader("KPI Metrics - Simulated Integrations")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Events", len(integrated_data))
            with col2:
                high_risk_events = integrated_data[integrated_data['risk_score'] >= 3]
                st.metric("High Risk Events", len(high_risk_events))
            with col3:
                normal_events = integrated_data[integrated_data['risk_score'] < 3]
                st.metric("Normal Events", len(normal_events))

        # Tab 2 – Event Dashboard
        with tab2_sim:
            st.subheader("Event Dashboard - Simulated Integrations")
            if not integrated_data.empty:
                # Bar chart for event distribution by tool and severity
                fig_bar = px.bar(
                    integrated_data,
                    x='tool',
                    color='severity',
                    title="Event Distribution by Tool and Severity",
                    labels={"tool": "Security Tool", "severity": "Event Severity"}
                )
                st.plotly_chart(fig_bar)

                # Timeline scatterplot
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
            else:
                st.warning("No event data available for visualization.")

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
