# 📊 Real-Time Stock Dashboard

A sleek and interactive **real-time dashboard** for monitoring live stock prices, historical trends, and financial news. Built using **Streamlit**, **Altair**, and a local **MCP server**.

This project demonstrates how LLM-compatible servers (via Model Context Protocol) can power real-time visualizations.

---

![Dashboard Screenshot](screenshots/live-dash-demo.png)

---

## 🚀 Features

✅ Live stock price updates (auto-refreshing)<br>
✅ Interactive Altair charts with time-based zoom<br>
✅ Historical stock performance across multiple timeframes:
  - Today
  - Last Week
  - Last Month
  - Last 3 Months
  - Last Year  
✅ Local timezone conversion for all charts<br>
✅ 5-period moving average overlay<br>
✅ Weather widget + latest news headlines<br>
✅ Customizable refresh interval (10s, 15s, 30s)

---

## 📁 Project Structure

```

live-data-visualizer/
├── app.py                  # Main Streamlit app
├── mcp\_server/
│   └── server.py           # MCP server serving stock price tool
├── utils/
│   └── data\_fetcher.py     # API requests and data helpers
├── tests/
│   └── test\_fetcher.py     # Unit test for data fetch logic
├── screenshots/
│   └── live-dash-demo.png  # UI preview
├── setup\_env.bat           # (Windows) Virtualenv + install helper
├── start\_dashboard.bat     # (Windows) Start MCP + Streamlit app
├── requirements.txt        # Required Python packages
└── README.md               # You’re here!

````

---

## ⚙️ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/live-data-visualizer.git
cd live-data-visualizer
````

---

### 2. Install dependencies

Manual:

```bash
pip install -r requirements.txt
```

Or (Windows only):

```bash
setup_env.bat
```

---

### 3. Run the Dashboard

Option A — One-click launch (Windows):

```bash
start_dashboard.bat
```

Option B — Manual:

```bash
python mcp_server/server.py
streamlit run app.py
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory for custom configuration:

```
MCP_SERVER_URL=http://localhost:8000
WEATHER=your_openweather_api_key
```

---

## 📃 License

MIT License
Built using [Streamlit](https://streamlit.io), [FastAPI](https://fastapi.tiangolo.com), and [MCP](https://modelcontextprotocol.io)

![MIT License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?style=flat-square)