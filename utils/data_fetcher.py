# utils/data_fetcher.py

import requests
import os
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
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
            time.sleep(1)
    else:
        raise RuntimeError(f"Failed to fetch historical data for {symbol} after {attempts} attempts.")

    hist.reset_index(inplace=True)

    if 'Datetime' in hist.columns:
        hist = hist.rename(columns={"Datetime": "timestamp"})
    elif 'Date' in hist.columns:
        hist = hist.rename(columns={"Date": "timestamp"})

    hist['timestamp'] = pd.to_datetime(hist['timestamp'])

    # Only keep NYSE regular trading hours (Eastern Time)
    hist['timestamp'] = hist['timestamp'].dt.tz_convert('US/Eastern')

    # Detect market open and close (9:30 AM to 4:00 PM)
    minutes = hist['timestamp'].dt.hour * 60 + hist['timestamp'].dt.minute
    is_open_hours = (minutes >= 570) & (minutes <= 960)

    # Drop pre-market, post-market, weekends, holidays
    hist = hist[is_open_hours]

    # BONUS: drop any days with no trading volume (i.e., fully closed)
    if "Volume" in hist.columns:
        hist = hist[hist["Volume"] > 0]

    # Convert timestamps back to UTC
    hist['timestamp'] = hist['timestamp'].dt.tz_convert('UTC')

    return hist[['timestamp', 'Close']]

@st.cache_data(ttl=600)
def fetch_previous_close(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d", interval="1d")
        return hist['Close'].iloc[-2]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch previous close for {symbol}: {str(e)}")
