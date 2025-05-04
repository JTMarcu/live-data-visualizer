# tests/test_fetcher.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_fetcher import fetch_live_data

def test_fetch_live_data_returns_dict():
    """Test that fetch_live_data returns a dictionary with keys 'timestamp' and 'value'."""
    data = fetch_live_data()
    assert isinstance(data, dict)
    assert "timestamp" in data
    assert "value" in data
