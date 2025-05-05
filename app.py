import streamlit as st
from utils.data_fetcher import fetch_stock_price
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=5000, key="datarefresh")

st.title("Real-Time Stock Dashboard")

# Initialize session state FIRST
if "stock_prices" not in st.session_state:
    st.session_state.stock_prices = []
if "last_stock_symbol" not in st.session_state:
    st.session_state.last_stock_symbol = None

# Sidebar input
with st.sidebar:
    st.header("Stock Settings")
    stock_symbol = st.text_input("Enter Stock Symbol:", value="RIVN").upper()

# Detect stock change
if st.session_state.last_stock_symbol != stock_symbol:
    st.session_state.stock_prices = []
    st.session_state.last_stock_symbol = stock_symbol

# Fetch stock price
try:
    stock_result = fetch_stock_price(symbol=stock_symbol)
    if "price" in stock_result:
        st.session_state.stock_prices.append(stock_result["price"])
except Exception as e:
    st.error(f"Exception occurred (stock data): {str(e)}")

# Plot stock prices
st.subheader(f"Live {stock_symbol} Stock Price")
if st.session_state.stock_prices:
    st.line_chart(st.session_state.stock_prices)
