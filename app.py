import streamlit as st
from utils.data_fetcher import fetch_live_data, fetch_stock_price
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
count = st_autorefresh(interval=5000, key="datarefresh")

st.title("Real-Time Data Dashboard")

# Initialize session state
if "live_values" not in st.session_state:
    st.session_state.live_values = []
if "stock_prices" not in st.session_state:
    st.session_state.stock_prices = []

# Fetch random value
try:
    result = fetch_live_data()
    st.session_state.live_values.append(result["value"])
except Exception as e:
    st.error(f"Exception occurred (random data): {str(e)}")

# Fetch stock price (e.g., RIVN)
try:
    stock_result = fetch_stock_price(symbol="RIVN")
    if "price" in stock_result:
        st.session_state.stock_prices.append(stock_result["price"])
except Exception as e:
    st.error(f"Exception occurred (stock data): {str(e)}")

# Plot random values
st.subheader("Live Random Values")
if st.session_state.live_values:
    st.line_chart(st.session_state.live_values)

# Plot stock prices
st.subheader("Live Rivian Stock Price")
if st.session_state.stock_prices:
    st.line_chart(st.session_state.stock_prices)
