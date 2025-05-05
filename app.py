import streamlit as st
from utils.data_fetcher import fetch_live_data
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
count = st_autorefresh(interval=5000, key="datarefresh")

st.title("Real-Time Data Dashboard")

# Initialize session state to store values
if "live_values" not in st.session_state:
    st.session_state.live_values = []

try:
    result = fetch_live_data()
    st.session_state.live_values.append(result["value"])
    st.success("Data fetched successfully!")
except Exception as e:
    st.error(f"Exception occurred: {str(e)}")

# Plot the live data
if st.session_state.live_values:
    st.line_chart(st.session_state.live_values)
