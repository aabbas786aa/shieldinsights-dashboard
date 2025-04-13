import streamlit as st
import pandas as pd
import plotly.express as px

st.title("ShieldInsights Remediation Dashboard")
data_source = st.sidebar.selectbox("Select Data Source", ["Upload Excel File", "API Simulated"])

if data_source == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload Remediation Data", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.DataFrame({
            'Description': ['Patch OpenSSL vulnerability', 'IAM policy audit', 'Firewall port review', 'Phishing simulation', 'SIEM tuning'],
            'Severity': ['High', 'Medium', 'Low', 'High', 'Medium'],
            'Status': ['Open', 'In Progress', 'Resolved', 'Open', 'In Progress'],
            'Team': ['InfraSec', 'GRC', 'Network', 'SOC', 'SOC'],
            'Tool': ['CrowdStrike', 'SailPoint', 'Palo Alto', 'Proofpoint', 'Splunk'],
            'Start Date': ['2025-04-01', '2025-04-02', '2025-04-03', '2025-04-04', '2025-04-05'],
            'Due Date': ['2025-04-07', '2025-04-09', '2025-04-06', '2025-04-10', '2025-04-12']
        })

# Example table to confirm loading
st.write("### Remediation Tasks")
st.dataframe(df)
