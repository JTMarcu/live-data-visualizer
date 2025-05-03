# mcp_server/server.py

from mcp.server.fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("LiveDataServer")

# Define a tool
@mcp.tool()
def get_live_data():
    from datetime import datetime
    import random

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "value": random.randint(0, 100)
    }

# Instead of app = mcp.app, do this:
from fastapi import FastAPI

app = FastAPI()

@app.post("/tools/get_live_data/invoke")
async def invoke_tool():
    return get_live_data()
