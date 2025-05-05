# mcp_server/server.py

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import yfinance as yf
from datetime import datetime
import random

# Create the FastMCP server
mcp = FastMCP("LiveDataServer")

# Define random data tool
def get_live_data():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "value": random.randint(0, 100)
    }

# Define stock price tool
def get_stock_price(symbol: str = "RIVN"):
    stock = yf.Ticker(symbol)
    todays_data = stock.history(period="1d")
    if todays_data.empty:
        return {"error": "No data found for symbol."}
    last_quote = todays_data["Close"].iloc[-1]
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "symbol": symbol,
        "price": round(last_quote, 2)
    }

# Instead of app = mcp.app
app = FastAPI()

@app.post("/tools/get_live_data/invoke")
async def invoke_tool():
    return get_live_data()

@app.post("/tools/get_stock_price/invoke")
async def invoke_stock_price():
    return get_stock_price()
