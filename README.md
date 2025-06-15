# Weather MCP Server

A weather information server built with FastAPI and MCP (Machine Conversation Protocol) that provides weather data through a beautiful web interface.

## Features

- 🌤️ Real-time weather information
- 🎨 Modern, responsive web interface
- 🔄 Asynchronous API endpoints
- 🔒 Secure API key management
- 🚀 Fast and efficient data delivery

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd weather_mcp_server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## Running the Server

1. Start the server:
```bash
python run_server.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

- `src/`
  - `fastapi_server.py` - Frontend server with web UI
  - `mcp_server.py` - MCP server implementation
  - `main.py` - Entry point for MCP server
  - `weather_tools.py` - Weather API integration
  - `config.py` - Configuration management
- `run_server.py` - Server startup script
- `requirements.txt` - Project dependencies

## API Endpoints

- `GET /` - Web interface
- `POST /weather` - Get weather data
- `GET /health` - Health check endpoint

## License

MIT License
