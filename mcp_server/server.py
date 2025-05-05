# mcp_server/server.py

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request
import yfinance as yf
from datetime import datetime
import random

# Create the FastMCP server
mcp = FastMCP("LiveDataServer")

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

@app.post("/tools/get_stock_price/invoke")
async def invoke_stock_price(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "RIVN")
    return get_stock_price(symbol)
