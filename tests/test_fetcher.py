# tests/test_fetcher.py

import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_fetcher import fetch_stock_price

def test_fetch_stock_price_returns_valid_data():
    """Test that fetch_stock_price returns a dict with correct keys and types."""
    result = fetch_stock_price(symbol="RIVN")  # You could use a very common stock
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "timestamp" in result, "'timestamp' key missing"
    assert "price" in result, "'price' key missing"
    
    assert isinstance(result["timestamp"], str), "'timestamp' should be a string"
    assert isinstance(result["price"], (int, float)), "'price' should be a number"
