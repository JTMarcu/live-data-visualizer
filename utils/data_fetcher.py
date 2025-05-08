# utils/data_fetcher.py

import requests
import os
import pandas as pd
import feedparser
import yfinance as yf
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# --- Stock Functions ---

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
def fetch_opening_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d", interval="5m")
        if not hist.empty:
            return hist['Open'].iloc[0]
        else:
            raise ValueError("No opening price available.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch opening price for {symbol}: {str(e)}")

# --- Weather ---

@st.cache_data(ttl=600)
def fetch_weather(city="San Diego"):
    api_key = os.getenv("WEATHER")
    if not api_key:
        raise RuntimeError("Missing WEATHER API key in .env file.")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
    }

# --- News ---

@st.cache_data(ttl=600)
def fetch_stock_news(symbol):
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    articles = []

    for entry in feed.entries[:5]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
        })
    
    return articles
