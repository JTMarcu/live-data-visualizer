# app.py

import streamlit as st
from utils.data_fetcher import fetch_live_data

st.title("Real-Time Data Dashboard")

if st.button("Fetch Live Data"):
    try:
        result = fetch_live_data()
        st.success("Data fetched successfully!")
        st.json(result)
    except Exception as e:
        st.error(f"Exception occurred: {str(e)}")
