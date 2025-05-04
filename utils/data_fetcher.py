# utils/data_fetcher.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

def fetch_live_data():
    try:
        response = requests.post(f"{MCP_SERVER_URL}/tools/get_live_data/invoke", json={})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch live data: {str(e)}")
