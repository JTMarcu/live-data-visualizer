import streamlit as st
from utils.data_fetcher import fetch_stock_price
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=10000, key="datarefresh")

st.title("Real-Time Stock Dashboard")

# Initialize session state
if "stock_prices" not in st.session_state:
    st.session_state.stock_prices = {}
if "last_stock_symbols" not in st.session_state:
    st.session_state.last_stock_symbols = []

# Sidebar input
with st.sidebar:
    st.header("Stock Settings")
    stock_symbols = st.text_input(
        "Enter stock symbols (comma-separated):",
        value="RIVN,TSLA,COST"
    ).upper().replace(" ", "").split(",")

# Detect stock change
if st.session_state.last_stock_symbols != stock_symbols:
    st.session_state.stock_prices = {symbol: [] for symbol in stock_symbols}
    st.session_state.last_stock_symbols = stock_symbols

# Fetch prices for each stock
for symbol in stock_symbols:
    try:
        stock_result = fetch_stock_price(symbol=symbol)
        if "price" in stock_result:
            st.session_state.stock_prices.setdefault(symbol, []).append(stock_result["price"])
    except Exception as e:
        st.error(f"Exception fetching {symbol}: {str(e)}")

# Plot each stock
# Smarter two-column layout, preserving order
for i in range(0, len(stock_symbols), 2):
    cols = st.columns(2)
    for idx in range(2):
        if i + idx < len(stock_symbols):
            symbol = stock_symbols[i + idx]
            with cols[idx]:
                st.subheader(f"Live {symbol} Stock Price")
                if st.session_state.stock_prices.get(symbol):
                    st.line_chart(st.session_state.stock_prices[symbol])