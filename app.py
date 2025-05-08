# app.py

import streamlit as st
from modules.stock_dashboard import display_stock_dashboard
from utils.data_fetcher import fetch_weather, fetch_stock_news
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Real-Time Dashboard", layout="wide")
# Sidebar
with st.sidebar:
    st.header("Settings")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN"
    ).upper().replace(" ", "").split(",")

    city = st.text_input("City for weather:", "San Diego")
    refresh_interval = st.selectbox("Refresh Interval (seconds):", (10, 15, 30), index=1)

count = st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Tabs
tabs = st.tabs(["📈 Live Dashboard"])

with tabs[0]:
    cols = st.columns([2, 1])

    with cols[0]:  # Left side: Stock Dashboard
        display_stock_dashboard(stock_symbols)

    with cols[1]:  # Right side: Weather + News
        try:
            weather = fetch_weather(city)
            st.subheader(f"Weather in {weather['city']}")
            st.image(f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png", width=80)
            st.metric(label="Temp", value=f"{weather['temperature']}°F")
            st.caption(weather['description'])
        except Exception as e:
            st.error(f"Weather error: {e}")

        for symbol in stock_symbols:
            st.subheader(f"📰 News for {symbol}")
            try:
                news = fetch_stock_news(symbol)
                for article in news:
                    st.markdown(f"- [{article['title']}]({article['link']})", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Failed to fetch news for {symbol}: {e}")
