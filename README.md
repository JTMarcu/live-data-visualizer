# Real-Time Data Dashboard (In Development)

A Python-based real-time data dashboard that integrates with the Model Context Protocol (MCP) to fetch and visualize live data streams. This project showcases the seamless integration of LLMs with external data sources, providing dynamic insights through an interactive dashboard.

## Features

* **Real-Time Data Visualization**: Stream and display live data updates.
* **MCP Integration**: Connects with MCP servers to fetch contextual data.
* **Interactive UI**: User-friendly interface for data exploration.
* **Modular Architecture**: Easily extendable components for scalability.
* **One-Click Start**: Quickly launch both the MCP server and Streamlit dashboard with a single command.

## Technologies Used

* **Frontend**: [Streamlit](https://streamlit.io/) for interactive dashboards.
* **Backend**: Python with [FastAPI](https://fastapi.tiangolo.com/) for API development.
* **Data Handling**: [Pandas](https://pandas.pydata.org/) for data manipulation.
* **MCP Integration**: [mcp-python-sdk](https://github.com/modelcontextprotocol/python-sdk) for MCP client/server communication.

## Screenshots

*(Coming soon!)*

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/JTMarcu/live-data-visualizer.git
   cd live-data-visualizer
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

Create a `.env` file (or copy from `.env.example`) and set your MCP server URL:

```bash
MCP_SERVER_URL=http://localhost:8000
```

## Quick Start

To launch the MCP server and Streamlit dashboard together, run:

```bash
start_dashboard.bat
```

This will:

* Start the MCP server on `localhost:8000`
* Start the Streamlit app on `localhost:8501`
* Open two terminal windows automatically

✅ Make sure to activate your virtual environment and install dependencies first!

## Usage

Once the application is running:

1. Navigate to [http://localhost:8501](http://localhost:8501) in your web browser.
2. Click **Fetch Live Data** to retrieve real-time values from the MCP server.
3. Monitor live updates and explore the dashboard.

## Testing

To run the test suite:

```bash
pytest tests/
```

✅ Ensure your MCP server is running before executing tests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

* [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
* [Streamlit](https://streamlit.io/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Pandas](https://pandas.pydata.org/)