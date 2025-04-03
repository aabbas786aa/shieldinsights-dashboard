
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO
import matplotlib as mpl

# Apply dark mode styling
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
st.title("ShieldInsights.ai - Interactive Dashboard")

uploaded_file = st.file_uploader("Upload your Excel remediation dataset", type=["xlsx"])

def export_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Filtered Data')
    return output.getvalue()

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['when'] = pd.to_datetime(df['when'], errors='coerce')

    # Sidebar Filters
    st.sidebar.header("Filter Remediation Data")
    severity_filter = st.sidebar.multiselect("Severity", df['severity'].dropna().unique())
    status_filter = st.sidebar.multiselect("Status", df['status'].dropna().unique())
    team_filter = st.sidebar.multiselect("Responsible Team", df['who'].dropna().unique())
    tool_filter = st.sidebar.multiselect("Source Tool", df['source_tool'].dropna().unique())
    start_date = st.sidebar.date_input("Start Due Date", value=None)
    end_date = st.sidebar.date_input("End Due Date", value=None)

    # Apply Filters
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

    # Tabs for layout
    tab1, tab2, tab3, tab4 = st.tabs(["📊 KPI Summary", "📈 Visual Dashboards", "📋 Remediation Table", "🧠 AI Insights"])

    # Tab 1: KPI Cards
    with tab1:
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Issues", len(filtered_df))
        col2.metric("Completed", filtered_df['status'].str.lower().eq('completed').sum())
        col3.metric("High Severity Open", len(filtered_df[(filtered_df['severity'].str.lower() == 'high') & (filtered_df['status'].str.lower() != 'completed')]))
        col4.metric("Overdue", len(filtered_df[(filtered_df['status'].str.lower() != 'completed') & (filtered_df['when'] < pd.Timestamp.today())]))

    # Tab 2: Dashboards
    with tab2:
        st.subheader("Remediation Status Distribution")
        fig1, ax1 = plt.subplots()
        filtered_df['status'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax1)
        ax1.set_ylabel('')
        st.pyplot(fig1)

        st.subheader("Severity Distribution")
        fig2, ax2 = plt.subplots()
        sns.countplot(data=filtered_df, x='severity', order=filtered_df['severity'].value_counts().index, ax=ax2)
        st.pyplot(fig2)

        st.subheader("Domain vs. Severity Heatmap")
        heatmap_data = filtered_df.groupby(['domain', 'severity']).size().unstack(fill_value=0)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlGnBu', ax=ax3)
        st.pyplot(fig3)

        st.subheader("Remediation Timeline")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=filtered_df, x='when', y='domain', hue='status', style='severity', ax=ax4)
        ax4.set_xlabel("Target Date")
        ax4.set_ylabel("Domain")
        st.pyplot(fig4)

    # Tab 3: Table and Export
    with tab3:
        st.subheader("Filtered Remediation Table")
        st.dataframe(filtered_df)

        st.download_button(
            label="Export Filtered Data to Excel",
            data=export_excel(filtered_df),
            file_name="filtered_remediation_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Tab 4: AI Insights
    with tab4:
        st.subheader("AI-Generated Insights")
        insights = []

        high_sev_open = filtered_df[(filtered_df['severity'].str.lower() == 'high') & (filtered_df['status'].str.lower() != 'completed')]
        if not high_sev_open.empty:
            insights.append(f"There are {len(high_sev_open)} high severity issues still open across {high_sev_open['domain'].nunique()} domains.")

        overdue = filtered_df[(filtered_df['status'].str.lower() != 'completed') & (filtered_df['when'] < pd.Timestamp.today())]
        if not overdue.empty:
            insights.append(f"{len(overdue)} remediation items are currently overdue. Top impacted domains: {', '.join(overdue['domain'].value_counts().head(3).index)}.")

        if 'who' in filtered_df.columns and not filtered_df['who'].isna().all():
            top_team = filtered_df['who'].value_counts().idxmax()
            team_issues = filtered_df[filtered_df['who'] == top_team]
            insights.append(f"The '{top_team}' team owns the most remediation items ({len(team_issues)}), with {team_issues['severity'].str.lower().eq('high').sum()} marked as High severity.")

        if 'source_tool' in filtered_df.columns and not filtered_df['source_tool'].isna().all():
            top_tool = filtered_df['source_tool'].value_counts().idxmax()
            tool_issues = filtered_df[filtered_df['source_tool'] == top_tool]
            insights.append(f"The tool generating the most issues is '{top_tool}' with {len(tool_issues)} items, {tool_issues['severity'].str.lower().eq('high').sum()} of which are High severity.")

        in_progress = filtered_df[(filtered_df['status'].str.lower() == 'in progress') & (filtered_df['when'] < pd.Timestamp.today())]
        if not in_progress.empty:
            insights.append(f"{len(in_progress)} issues are 'In Progress' but past their due dates, suggesting potential execution delays.")

        for i, insight in enumerate(insights, 1):
            st.markdown(f"**{i}. {insight}**")
