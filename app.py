# app.py

import streamlit as st
from utils.data_fetcher import fetch_stock_price, fetch_company_name, fetch_historical_data, fetch_previous_close
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import datetime
import altair as alt

# Sidebar
with st.sidebar:
    st.header("Stock Settings")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN"
    ).upper().replace(" ", "").split(",")

    timeframe = st.selectbox(
        "Select timeframe to view:",
        ("Last 1 Hour", "Last 1 Day", "Last 5 Days", "Last 1 Month", "Last 3 Months")
    )

    refresh_interval = st.selectbox(
        "Refresh Interval (seconds):",
        (5, 10, 30),
        index=1
    )

count = st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

st.title("Real-Time Stock Dashboard")

# Session state
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

def prepare_dataframe(data_list, timeframe_selection):
    df = pd.DataFrame(data_list)

    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=len(df), freq='7S')
        df['price'] = df[0]
        df = df[['timestamp', 'price']]

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    now = pd.Timestamp.now(tz="UTC")

    if timeframe_selection == "Last 1 Hour":
        cutoff = now - pd.Timedelta(hours=1)
    else:
        cutoff = now - pd.Timedelta(days=1)

    df = df[df.index >= cutoff]
    return df

def get_dynamic_historical_data(symbol, timeframe_selection):
    if timeframe_selection == "Last 1 Day":
        period = "1d"
        interval = "5m"
    elif timeframe_selection == "Last 5 Days":
        period = "5d"
        interval = "15m"
    elif timeframe_selection == "Last 1 Month":
        period = "1mo"
        interval = "1d"
    elif timeframe_selection == "Last 3 Months":
        period = "3mo"
        interval = "1d"
    else:
        period = "1d"
        interval = "5m"

    with st.spinner(f"Fetching {symbol} historical data..."):
        try:
            df = fetch_historical_data(symbol, period=period, interval=interval)
            if df.empty:
                st.warning(f"No historical data available for {symbol}.")
                return pd.DataFrame()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            df.rename(columns={"Close": "price"}, inplace=True)
            return df
        except Exception as e:
            st.error(f"Failed to fetch historical data for {symbol}: {e}")
            return pd.DataFrame()

def display_stock_data(symbol, company_name, timeframe_selection):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Last Updated: {now}")

    if timeframe_selection == "Last 1 Hour":
        if st.session_state.stock_prices.get(symbol):
            df = prepare_dataframe(st.session_state.stock_prices[symbol], timeframe_selection)
        else:
            df = pd.DataFrame()
    else:
        df = get_dynamic_historical_data(symbol, timeframe_selection)

    if not df.empty:
        df['moving_avg'] = df['price'].rolling(window=5).mean()

        latest_price = round(df['price'].iloc[-1], 2)
        previous_price = round(df['price'].iloc[-2], 2) if len(df) > 1 else latest_price
        price_delta = round(latest_price - previous_price, 2)

        previous_close = st.session_state.previous_closes.get(symbol, latest_price)
        daily_delta = round(latest_price - previous_close, 2)
        daily_percent_change = round((daily_delta / previous_close) * 100, 2) if previous_close else 0

        # Metrics
        st.metric(
            label="Current Price",
            value=f"${latest_price:,.2f}",
            delta=""
        )

        # Changes
        day_arrow = "▲" if daily_delta >= 0 else "▼"
        day_color = "green" if daily_delta >= 0 else "red"
        instant_arrow = "▲" if price_delta >= 0 else "▼"
        instant_color = "green" if price_delta >= 0 else "red"

        change_markdown = f"""
        <div style='font-size:20px;'>
            <span style='color:{day_color}; font-weight:bold;'>{day_arrow} ${daily_delta:+.2f} ({daily_percent_change:+.2f}%)</span>
            &nbsp;&nbsp;
            <span style='color:{instant_color}; font-weight:bold;'>{instant_arrow} {price_delta:+.2f}</span>
        </div>
        """

        st.markdown(change_markdown, unsafe_allow_html=True)

        # Altair Chart
        base = alt.Chart(df.reset_index()).encode(
            x=alt.X('timestamp:T', axis=alt.Axis(title=None))
        )

        price_line = base.mark_line(
            color='yellow',
            strokeWidth=2
        ).encode(
            y=alt.Y('price:Q', scale=alt.Scale(zero=False)),
            tooltip=['timestamp:T', 'price:Q']
        )

        moving_avg_line = base.mark_line(
            color='orange',
            strokeDash=[5, 5],
            strokeWidth=1.5,
            opacity=0.6
        ).encode(
            y='moving_avg:Q',
            tooltip=['timestamp:T', 'moving_avg:Q']
        )

        combined_chart = (price_line + moving_avg_line).interactive()

        st.altair_chart(combined_chart, use_container_width=True)

    else:
        st.warning("No data available for this timeframe.")

# Plotting
if len(stock_symbols) == 1:
    symbol = stock_symbols[0]
    company_name = st.session_state.company_names.get(symbol, symbol)
    st.markdown(f"""
        <div style="font-size:20px; font-weight:bold;">Live Stock Price</div>
        <div style="font-size:16px; color:gray;">{company_name}</div>
    """, unsafe_allow_html=True)
    display_stock_data(symbol, company_name, timeframe)
else:
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
