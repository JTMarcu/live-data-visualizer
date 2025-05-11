# app.py

import streamlit as st
from modules.stock_dashboard import display_stock_dashboard
from utils.data_fetcher import fetch_weather, fetch_stock_news
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Real-Time Dashboard", layout="wide")

# Sidebar
with st.sidebar:
    st.header("Settings")

    st.subheader("Stock Options")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN",
        help="Use commas to separate multiple stock symbols (e.g., AAPL,GOOGL)"
    ).upper().replace(" ", "").split(",")

    st.subheader("Weather")
    city = st.text_input("City:", "San Diego", help="City used for weather forecast")

    st.subheader("Auto Refresh")
    refresh_interval = st.selectbox("Interval (seconds):", (10, 15, 30), index=1)

# Auto-refresh trigger
count = st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Tab layout
tabs = st.tabs([
    "📊 Live Dashboard",
    "📈 Stocks",
    "🌤 Weather",
    "📰 News"
])

# Live Dashboard Tab
with tabs[0]:
    cols = st.columns([2, 1])

    with cols[0]:  # Left: Stocks
        display_stock_dashboard(stock_symbols, key_suffix="live")

    with cols[1]:  # Right: Weather + News
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

# Stocks Tab
with tabs[1]:
    display_stock_dashboard(stock_symbols, key_suffix="stocks")

# Weather Tab
with tabs[2]:
    try:
        weather = fetch_weather(city)
        st.subheader(f"Weather in {weather['city']}")
        st.image(f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png", width=80)
        st.metric(label="Temp", value=f"{weather['temperature']}°F")
        st.caption(weather['description'])
    except Exception as e:
        st.error(f"Weather error: {e}")

# News Tab
with tabs[3]:
    for symbol in stock_symbols:
        st.subheader(f"📰 News for {symbol}")
        try:
            news = fetch_stock_news(symbol)
            for article in news:
                st.markdown(f"- [{article['title']}]({article['link']})", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Failed to fetch news for {symbol}: {e}")
