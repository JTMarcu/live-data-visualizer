# app.py

import streamlit as st
import pandas as pd
import datetime
import altair as alt
import yfinance as yf
from utils.data_fetcher import fetch_stock_price, fetch_company_name, fetch_previous_close
from streamlit_autorefresh import st_autorefresh

# Sidebar
with st.sidebar:
    st.header("Stock Settings")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN"
    ).upper().replace(" ", "").split(",")

    timeframe = st.selectbox(
        "Select timeframe to view:",
        ("Last Hour", "Last Day", "Last Week", "Last Month", "Last 3 Months", "Last Year")
    )

    refresh_interval = st.selectbox(
        "Refresh Interval (seconds):",
        (5, 10, 30),
        index=1
    )

count = st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

st.title("Real-Time Stock Dashboard")

# Session State
if "stock_prices" not in st.session_state:
    st.session_state.stock_prices = {}
if "last_stock_symbols" not in st.session_state:
    st.session_state.last_stock_symbols = []
if "company_names" not in st.session_state:
    st.session_state.company_names = {}
if "previous_closes" not in st.session_state:
    st.session_state.previous_closes = {}

# Detect stock change
if st.session_state.last_stock_symbols != stock_symbols:
    st.session_state.stock_prices = {symbol: [] for symbol in stock_symbols}
    st.session_state.last_stock_symbols = stock_symbols
    st.session_state.company_names = {}
    st.session_state.previous_closes = {}

# Fetch prices
for symbol in stock_symbols:
    try:
        stock_result = fetch_stock_price(symbol=symbol)
        if "price" in stock_result and "timestamp" in stock_result:
            st.session_state.stock_prices.setdefault(symbol, []).append({
                "timestamp": stock_result["timestamp"],
                "price": stock_result["price"]
            })
            if symbol not in st.session_state.company_names:
                st.session_state.company_names[symbol] = fetch_company_name(symbol)
            if symbol not in st.session_state.previous_closes:
                st.session_state.previous_closes[symbol] = fetch_previous_close(symbol)
    except Exception as e:
        st.error(f"Exception fetching {symbol}: {str(e)}")

# Prepare Dataframe for "Last Hour"
def prepare_realtime_dataframe(data_list, timeframe_selection):
    df = pd.DataFrame(data_list)
    if 'timestamp' not in df.columns:
        return pd.DataFrame()

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    now = pd.Timestamp.now(tz="UTC")

    if timeframe_selection == "Last Hour":
        cutoff = now - pd.Timedelta(hours=1)
    elif timeframe_selection == "Last Day":
        cutoff = now - pd.Timedelta(days=1)
    elif timeframe_selection == "Last Week":
        cutoff = now - pd.Timedelta(days=7)
    else:
        cutoff = now - pd.Timedelta(days=1)

    df = df[df.index >= cutoff]

    return df

# Fetch historical data
def get_historical_data(symbol, timeframe_selection):
    today = datetime.datetime.utcnow()
    stock = yf.Ticker(symbol)

    if timeframe_selection == "Last Day":
        df = stock.history(period="1d", interval="5m")
    elif timeframe_selection == "Last Week":
        df = stock.history(period="7d", interval="15m")
    elif timeframe_selection == "Last Month":
        start = today - datetime.timedelta(days=30)
        df = stock.history(start=start, end=today, interval="1d")
    elif timeframe_selection == "Last 3 Months":
        start = today - datetime.timedelta(days=90)
        df = stock.history(start=start, end=today, interval="1d")
    elif timeframe_selection == "Last Year":
        start = today - datetime.timedelta(days=365)
        df = stock.history(start=start, end=today, interval="1wk")
    else:
        df = stock.history(period="1d", interval="5m")

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()
    df.rename(columns={"Date": "timestamp"}, inplace=True)

    return df

# Display Chart
def display_stock_data(symbol, company_name, timeframe_selection):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Last Updated: {now}")

    if timeframe_selection == "Last Hour":
        df = prepare_realtime_dataframe(st.session_state.stock_prices.get(symbol, []), timeframe_selection)
    else:
        df = get_historical_data(symbol, timeframe_selection)

    if df.empty:
        st.warning(f"No data available for {symbol}.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Localize timestamps
    if df['timestamp'].dt.tz is None or df['timestamp'].dt.tz is pd.NaT:
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
    local_tz = datetime.datetime.now().astimezone().tzinfo
    df['timestamp'] = df['timestamp'].dt.tz_convert(local_tz)

    if timeframe_selection in ["Last Hour", "Last Day", "Last Week"]:
        df['time_label'] = df['timestamp'].dt.strftime('%b %d %H:%M')
    else:
        df['time_label'] = df['timestamp'].dt.strftime('%b %d')

    # Columns
    if 'price' not in df.columns and 'Close' in df.columns:
        df['price'] = df['Close']

    df['moving_avg'] = df['price'].rolling(window=5, min_periods=1).mean()

    # Plot
    base = alt.Chart(df).encode(
        x=alt.X('time_label:N', axis=alt.Axis(title="Time", labelAngle=-45, labelOverlap=True))
    )

    price_line = base.mark_line(
        color='yellow',
        strokeWidth=2
    ).encode(
        y=alt.Y('price:Q', title='Price ($)', scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip('timestamp:T', title='Timestamp'),
            alt.Tooltip('price:Q', title='Price ($)')
        ]
    )

    moving_avg_line = base.mark_line(
        color='orange',
        strokeDash=[5, 5],
        opacity=0.7
    ).encode(
        y='moving_avg:Q'
    )

    combined_chart = (price_line + moving_avg_line).properties(
        width=800, height=400
    ).interactive(bind_x="pan", bind_y="zoom")

    st.altair_chart(combined_chart, use_container_width=True)

# Main Plotting
if len(stock_symbols) == 1:
    symbol = stock_symbols[0]
    company_name = st.session_state.company_names.get(symbol, symbol)
    st.markdown(f"<div style='font-size:20px; font-weight:bold;'>Live Stock Price</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:16px; color:gray;'>{company_name}</div>", unsafe_allow_html=True)
    display_stock_data(symbol, company_name, timeframe)
else:
    for i in range(0, len(stock_symbols), 2):
        cols = st.columns(2)
        for idx in range(2):
            if i + idx < len(stock_symbols):
                symbol = stock_symbols[i + idx]
                company_name = st.session_state.company_names.get(symbol, symbol)
                with cols[idx]:
                    st.markdown(f"<div style='font-size:20px; font-weight:bold;'>Live Stock Price</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:16px; color:gray;'>{company_name}</div>", unsafe_allow_html=True)
                    display_stock_data(symbol, company_name, timeframe)
