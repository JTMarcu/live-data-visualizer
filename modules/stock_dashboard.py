# modules/stock_dashboard.py

import streamlit as st
import pandas as pd
import datetime
import altair as alt
import yfinance as yf
from utils.data_fetcher import fetch_company_name, fetch_opening_price, fetch_stock_price

@st.cache_data(ttl=600)
def get_dynamic_historical_data(symbol, timeframe_selection):
    try:
        ticker = yf.Ticker(symbol)

        if timeframe_selection == "Today":
            df = ticker.history(period="1d", interval="5m")
        elif timeframe_selection == "Last Week":
            df = ticker.history(period="7d", interval="15m")
        elif timeframe_selection == "Last Month":
            df = ticker.history(period="1mo", interval="1d")
        elif timeframe_selection == "Last 3 Months":
            df = ticker.history(period="3mo", interval="1d")
        elif timeframe_selection == "Last Year":
            df = ticker.history(period="1y", interval="1wk")
        else:
            df = ticker.history(period="1d", interval="5m")

        if df.empty:
            st.warning(f"No historical data available for {symbol}.")
            return pd.DataFrame()

        df.reset_index(inplace=True)
        if "Date" in df.columns:
            df.rename(columns={"Date": "timestamp"}, inplace=True)
        elif "Datetime" in df.columns:
            df.rename(columns={"Datetime": "timestamp"}, inplace=True)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        df.rename(columns={"Close": "price"}, inplace=True)
        return df

    except Exception as e:
        st.error(f"Failed to fetch historical data for {symbol}: {e}")
        return pd.DataFrame()

def display_stock_dashboard(stock_symbols, key_suffix=""):
    timeframe = st.selectbox(
        "Select timeframe to view:",
        ("Today", "Last Week", "Last Month", "Last 3 Months", "Last Year"),
        key=f"timeframe_select_{'_'.join(stock_symbols)}_{key_suffix}"
    )

    if "stock_prices" not in st.session_state:
        st.session_state.stock_prices = {}
    if "last_stock_symbols" not in st.session_state:
        st.session_state.last_stock_symbols = []
    if "company_names" not in st.session_state:
        st.session_state.company_names = {}
    if "opening_prices" not in st.session_state:
        st.session_state.opening_prices = {}

    # Clear history if stock list changes
    if st.session_state.last_stock_symbols != stock_symbols:
        st.session_state.stock_prices = {symbol: [] for symbol in stock_symbols}
        st.session_state.last_stock_symbols = stock_symbols
        st.session_state.company_names = {}
        st.session_state.opening_prices = {}

    MAX_HISTORY = 50

    for symbol in stock_symbols:
        try:
            stock_result = fetch_stock_price(symbol=symbol)
            if "price" in stock_result and "timestamp" in stock_result:
                st.session_state.stock_prices.setdefault(symbol, []).append({
                    "timestamp": stock_result["timestamp"],
                    "price": stock_result["price"]
                })
                st.session_state.stock_prices[symbol] = st.session_state.stock_prices[symbol][-MAX_HISTORY:]

                if symbol not in st.session_state.company_names:
                    st.session_state.company_names[symbol] = fetch_company_name(symbol)
                if symbol not in st.session_state.opening_prices:
                    st.session_state.opening_prices[symbol] = fetch_opening_price(symbol)
        except Exception as e:
            st.error(f"Exception fetching {symbol}: {str(e)}")

    def display_stock_data(symbol, company_name, timeframe_selection):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last Updated: {now}")

        with st.spinner(f"Fetching {symbol} {timeframe_selection} data..."):
            df = get_dynamic_historical_data(symbol, timeframe_selection)

        if not df.empty:
            df_plot = df.dropna(subset=["price"])

            if df_plot.empty:
                st.warning("No valid data to plot.")
                return

            try:
                if timeframe_selection in ["Today", "Last Week"]:
                    df_plot = df_plot.copy()
                    df_plot.index = df_plot.index.tz_convert('US/Eastern')
                    market_open = (df_plot.index.hour > 9) | ((df_plot.index.hour == 9) & (df_plot.index.minute >= 30))
                    market_close = (df_plot.index.hour < 16)
                    during_market_hours = market_open & market_close
                    df_plot = df_plot[during_market_hours]
                    df_plot.index = df_plot.index.tz_convert('UTC')

                local_tz = datetime.datetime.now().astimezone().tzinfo
                df_plot.index = df_plot.index.tz_convert(local_tz)

            except Exception as e:
                st.warning(f"Timezone conversion error: {e}")

            if df_plot.empty:
                st.warning("No market hours data to plot.")
                return

            if timeframe_selection in ["Last Month", "Last 3 Months", "Last Year"]:
                df_plot['time_label'] = df_plot.index.strftime('%b %d')
            else:
                df_plot['time_label'] = df_plot.index.strftime('%b %d %H:%M')

            df_plot['moving_avg'] = df_plot['price'].rolling(window=5, min_periods=1).mean()
            df_reset = df_plot.reset_index()

            latest_price = round(df_plot['price'].iloc[-1], 2)
            first_price = round(df_plot['price'].iloc[0], 2)
            timeframe_delta = round(latest_price - first_price, 2)
            timeframe_percent = round((timeframe_delta / first_price) * 100, 2) if first_price else 0
            timeframe_color = "green" if timeframe_delta >= 0 else "red"

            opening_price = st.session_state.opening_prices.get(symbol, latest_price)
            daily_delta = round(latest_price - opening_price, 2)
            daily_percent = round((daily_delta / opening_price) * 100, 2) if opening_price else 0
            daily_color = "green" if daily_delta >= 0 else "red"

            prev_close_delta = None
            try:
                hist_daily = yf.Ticker(symbol).history(period="2d", interval="1d")
                if len(hist_daily) >= 2:
                    prev_close = round(hist_daily["Close"].iloc[-2], 2)
                    prev_close_delta = round(latest_price - prev_close, 2)
                    prev_close_percent = round((prev_close_delta / prev_close) * 100, 2) if prev_close else 0
                    prev_close_color = "green" if prev_close_delta >= 0 else "red"
            except Exception as e:
                st.warning(f"Could not fetch previous close for {symbol}: {e}")

            st.markdown(f"<div style='font-size:24px; font-weight:bold; color:white;'>${latest_price:,.2f}</div>", unsafe_allow_html=True)

            if prev_close_delta is not None:
                st.markdown(f"<div style='font-size:16px; color:{prev_close_color};'>Since Previous Close: {prev_close_delta:+.2f} ({prev_close_percent:+.2f}%)</div>", unsafe_allow_html=True)

            st.markdown(f"<div style='font-size:16px; color:{daily_color};'>Since Open: {daily_delta:+.2f} ({daily_percent:+.2f}%)</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:16px; color:{timeframe_color};'>{timeframe_selection}: {timeframe_delta:+.2f} ({timeframe_percent:+.2f}%)</div>", unsafe_allow_html=True)

            x_axis = alt.X('time_label:N', axis=alt.Axis(title="Time (Local)", labelAngle=-45))
            base = alt.Chart(df_reset).encode(x=x_axis)

            price_line = base.mark_line(color='yellow', strokeWidth=2).encode(
                y=alt.Y('price:Q', title='Price ($)', scale=alt.Scale(zero=False)),
                tooltip=[alt.Tooltip('timestamp:T', title='Timestamp'), alt.Tooltip('price:Q', title='Price ($)')]
            )

            moving_avg_line = base.mark_line(
                color='orange', strokeDash=[5, 5], opacity=0.7
            ).encode(y='moving_avg:Q')

            combined_chart = (price_line + moving_avg_line).properties(
                title="Price & 5-Period Moving Avg"
            ).interactive()

            st.altair_chart(combined_chart, use_container_width=True)

        else:
            st.warning("No data available for this timeframe.")

    if len(stock_symbols) == 1:
        symbol = stock_symbols[0]
        company_name = st.session_state.company_names.get(symbol, symbol)
        st.markdown(f"<div style='font-size:20px; font-weight:bold;'>{company_name}</div>", unsafe_allow_html=True)
        display_stock_data(symbol, company_name, timeframe)
    else:
        for i in range(0, len(stock_symbols), 2):
            cols = st.columns(2)
            for idx in range(2):
                if i + idx < len(stock_symbols):
                    symbol = stock_symbols[i + idx]
                    company_name = st.session_state.company_names.get(symbol, symbol)
                    with cols[idx]:
                        st.markdown(f"<div style='font-size:20px; font-weight:bold;'>{company_name}</div>", unsafe_allow_html=True)
                        display_stock_data(symbol, company_name, timeframe)
