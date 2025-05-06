# app.py

import streamlit as st
from utils.data_fetcher import fetch_stock_price, fetch_company_name
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import datetime

# Sidebar inputs first
with st.sidebar:
    st.header("Stock Settings")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN"
    ).upper().replace(" ", "").split(",")

    timeframe = st.selectbox(
        "Select timeframe to view:",
        ("Last 1 Hour", "Last 1 Day", "Last 5 Days")
    )

    refresh_interval = st.selectbox(
        "Refresh Interval (seconds):",
        (5, 10, 30),
        index=1  # default to 10s
    )

# Auto-refresh every X seconds
count = st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

st.title("Real-Time Stock Dashboard")

# Initialize session state
if "stock_prices" not in st.session_state:
    st.session_state.stock_prices = {}
if "last_stock_symbols" not in st.session_state:
    st.session_state.last_stock_symbols = []
if "company_names" not in st.session_state:
    st.session_state.company_names = {}

# Detect stock change
if st.session_state.last_stock_symbols != stock_symbols:
    st.session_state.stock_prices = {symbol: [] for symbol in stock_symbols}
    st.session_state.last_stock_symbols = stock_symbols
    st.session_state.company_names = {}

# Fetch prices for each stock
for symbol in stock_symbols:
    try:
        stock_result = fetch_stock_price(symbol=symbol)
        if "price" in stock_result and "timestamp" in stock_result:
            st.session_state.stock_prices.setdefault(symbol, []).append({
                "timestamp": stock_result["timestamp"],
                "price": stock_result["price"]
            })
            # Fetch company name only once per symbol
            if symbol not in st.session_state.company_names:
                st.session_state.company_names[symbol] = fetch_company_name(symbol)
    except Exception as e:
        st.error(f"Exception fetching {symbol}: {str(e)}")

# Prepare DataFrame safely
def prepare_dataframe(data_list, timeframe_selection):
    df = pd.DataFrame(data_list)

    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=len(df), freq='7S')
        df['price'] = df[0]
        df = df[['timestamp', 'price']]

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    # Make "now" timezone-aware
    now = pd.Timestamp.now(tz="UTC")

    # Filter by timeframe
    if timeframe_selection == "Last 1 Hour":
        cutoff = now - pd.Timedelta(hours=1)
    elif timeframe_selection == "Last 1 Day":
        cutoff = now - pd.Timedelta(days=1)
    elif timeframe_selection == "Last 5 Days":
        cutoff = now - pd.Timedelta(days=5)
    else:
        cutoff = now - pd.Timedelta(days=5)

    df = df[df.index >= cutoff]
    return df

# Display function
def display_stock_data(symbol, company_name, timeframe_selection):
    if st.session_state.stock_prices.get(symbol):
        df = prepare_dataframe(st.session_state.stock_prices[symbol], timeframe_selection)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last Updated: {now}")

        # Add moving average
        df['moving_avg'] = df['price'].rolling(window=5).mean()

        st.line_chart(df[['price', 'moving_avg']])

        latest_price = df['price'].iloc[-1]
        previous_price = df['price'].iloc[-2] if len(df) > 1 else latest_price
        price_delta = latest_price - previous_price

        st.metric(
            label="Current Price",
            value=f"${latest_price:,.2f}",
            delta=f"${price_delta:+.2f}"
        )

# Plot each stock
if len(stock_symbols) == 1:
    # Single stock view
    symbol = stock_symbols[0]
    company_name = st.session_state.company_names.get(symbol, symbol)
    st.markdown(f"""
        <div style="font-size:20px; font-weight:bold;">Live Stock Price</div>
        <div style="font-size:16px; color:gray;">{company_name}</div>
    """, unsafe_allow_html=True)
    display_stock_data(symbol, company_name, timeframe)
else:
    # Multi-stock view
    for i in range(0, len(stock_symbols), 2):
        cols = st.columns(2)
        for idx in range(2):
            if i + idx < len(stock_symbols):
                symbol = stock_symbols[i + idx]
                company_name = st.session_state.company_names.get(symbol, symbol)
                with cols[idx]:
                    st.markdown(f"""
                        <div style="font-size:20px; font-weight:bold;">Live Stock Price</div>
                        <div style="font-size:16px; color:gray;">{company_name}</div>
                    """, unsafe_allow_html=True)
                    display_stock_data(symbol, company_name, timeframe)
