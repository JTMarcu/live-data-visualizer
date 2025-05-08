# utils/data_fetcher.py

import requests
import os
from dotenv import load_dotenv
import yfinance as yf
import streamlit as st

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

def fetch_stock_price(symbol="RIVN"):
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/get_stock_price/invoke",
            json={"symbol": symbol}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch stock price for {symbol}: {str(e)}")

def fetch_company_name(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info.get("shortName", symbol)
    except Exception:
        return symbol

@st.cache_data(ttl=600)
def fetch_historical_data(symbol, period="1d", interval="5m"):
    stock = yf.Ticker(symbol)

    attempts = 2
    for attempt in range(attempts):
        hist = stock.history(period=period, interval=interval)
        if not hist.empty:
            break
        if attempt < attempts - 1:
            import time
            time.sleep(1)  # Retry after short wait
    else:
        raise RuntimeError(f"Failed to fetch historical data for {symbol} after {attempts} attempts.")

    hist.reset_index(inplace=True)
    hist['timestamp'] = hist['Datetime'] if 'Datetime' in hist else hist['Date']
    return hist[['timestamp', 'Close']]

@st.cache_data(ttl=600)
def fetch_previous_close(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d", interval="1d")
        return hist['Close'].iloc[-2]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch previous close for {symbol}: {str(e)}")
