# Real-Time Data Dashboard (In Development)

A Python-based real-time data dashboard that integrates with the Model Context Protocol (MCP) to fetch and visualize live data streams. This project showcases the seamless integration of LLMs with external data sources, providing dynamic insights through an interactive dashboard.

## Features

* **Real-Time Data Visualization**: Stream and display live data updates.
* **MCP Integration**: Connects with MCP servers to fetch contextual data.
* **Interactive UI**: User-friendly interface for data exploration.
* **Modular Architecture**: Easily extendable components for scalability.

##  Technologies Used

* **Frontend**: [Streamlit](https://streamlit.io/) for interactive dashboards.
* **Backend**: Python with [FastAPI](https://fastapi.tiangolo.com/) for API development.
* **Data Handling**: [Pandas](https://pandas.pydata.org/) for data manipulation.
* **MCP Integration**: [mcp-python-sdk](https://github.com/modelcontextprotocol/python-sdk) for MCP client/server communication.

## Screenshots

![Dashboard Overview](link_to_screenshot1)
*Figure 1: Overview of the real-time dashboard interface.*

![Live Data Stream](link_to_screenshot2)
*Figure 2: Live data streaming and visualization.*

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/JTMarcu/real-time-data-dashboard.git
   cd real-time-data-dashboard
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   streamlit run app.py
   ```

##  Configuration

* **MCP Server URL**: Set the MCP server endpoint in the `config.py` file.
* **API Keys**: Store any necessary API keys in a `.env` file.
* **Data Sources**: Configure data source endpoints in the `data_sources.py` module.

## Usage

Once the application is running:

1. Navigate to `http://localhost:8501` in your web browser.
2. Use the sidebar to select data streams or adjust visualization parameters.
3. Monitor real-time data updates and interact with the dashboard components.

## Testing

To run the test suite:

```bash
pytest tests/
```

Ensure all tests pass to validate the functionality of the application components.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

* [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
* [Streamlit](https://streamlit.io/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Pandas](https://pandas.pydata.org/)

---
