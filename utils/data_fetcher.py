# utils/data_fetcher.py

import requests
import os
from dotenv import load_dotenv
import yfinance as yf

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
        return symbol  # fallback to symbol if fail

def fetch_historical_data(symbol, period="1d", interval="5m"):
    """
    Fetch historical stock data from Yahoo Finance.
    period: "1d", "5d", "1mo", "3mo", etc.
    interval: "1m", "5m", "15m", "1h", "1d", etc.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval=interval)
        hist.reset_index(inplace=True)
        hist['timestamp'] = hist['Datetime'] if 'Datetime' in hist else hist['Date']
        return hist[['timestamp', 'Close']]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data for {symbol}: {str(e)}")
