#!/usr/bin/env python3
"""
FastAPI server that interfaces with the MCP weather server
"""
import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

app = FastAPI(title="Weather MCP Frontend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class WeatherRequest(BaseModel):
    location: str

class WeatherResponse(BaseModel):
    location: str
    data: Dict[Any, Any]
    success: bool
    error: str = None

class MCPClient:
    """MCP client manager"""
    def __init__(self):
        self.session = None
        self.read = None
        self.write = None
        self.client_context = None

    async def connect(self):
        """Connect to the MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.main"],
            )
            
            self.client_context = stdio_client(server_params)
            self.read, self.write = await self.client_context.__aenter__()
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            return True
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the MCP server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.client_context:
                await self.client_context.__aexit__(None, None, None)
        except Exception as e:
            print(f"Error disconnecting: {e}")

    async def get_weather(self, location: str) -> Dict[Any, Any]:
        """Get weather data for a location"""
        if not self.session:
            raise Exception("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool("get_current_weather", {"location": location})
            
            # Parse the result content
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON
                        weather_data = json.loads(content.text)
                        return weather_data
                    except json.JSONDecodeError:
                        # If not JSON, return as text
                        return {"message": content.text}
                else:
                    return {"message": str(content)}
            else:
                return {"message": "No weather data received"}
                
        except Exception as e:
            raise Exception(f"Failed to get weather: {str(e)}")

# Global MCP client
mcp_client = MCPClient()

@app.on_event("startup")
async def startup_event():
    """Connect to MCP server on startup"""
    print("Connecting to MCP server...")
    success = await mcp_client.connect()
    if success:
        print("✅ Connected to MCP server")
    else:
        print("❌ Failed to connect to MCP server")

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MCP server on shutdown"""
    await mcp_client.disconnect()
    print("Disconnected from MCP server")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather MCP Frontend</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                width: 100%;
                text-align: center;
            }
            
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
                font-weight: 300;
            }
            
            .search-container {
                margin-bottom: 30px;
                position: relative;
            }
            
            input[type="text"] {
                width: 100%;
                padding: 15px 20px;
                font-size: 18px;
                border: 2px solid #e0e0e0;
                border-radius: 50px;
                outline: none;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.9);
            }
            
            input[type="text"]:focus {
                border-color: #667eea;
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
            }
            
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
                min-width: 150px;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }
            
            .weather-card {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border-radius: 20px;
                padding: 30px;
                margin-top: 30px;
                text-align: left;
                display: none;
            }
            
            .weather-card.show {
                display: block;
            }
            
            .location {
                font-size: 2em;
                margin-bottom: 10px;
            }
            
            .datetime {
                font-size: 1.1em;
                opacity: 0.8;
                margin-bottom: 20px;
            }
            
            .weather-main {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .temperature {
                font-size: 3.5em;
                margin-right: 20px;
            }
            
            .condition {
                font-size: 1.5em;
            }
            
            .weather-details {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            
            .detail-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
            }
            
            .detail-item h3 {
                font-size: 0.9em;
                opacity: 0.8;
                margin-bottom: 5px;
            }
            
            .detail-item p {
                font-size: 1.2em;
            }
            
            .error-message {
                background: linear-gradient(135deg, #f44336, #d32f2f);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Weather Forecast</h1>
            <div class="search-container">
                <input type="text" id="location" placeholder="Enter city name..." />
                <button onclick="getWeather()">Get Weather</button>
            </div>
            
            <div class="weather-card" id="weatherCard">
                <div class="location" id="locationName"></div>
                <div class="datetime" id="dateTime"></div>
                <div class="weather-main">
                    <div class="temperature" id="temperature"></div>
                    <div class="condition" id="condition"></div>
                </div>
                <div class="weather-details">
                    <div class="detail-item">
                        <h3>Feels Like</h3>
                        <p id="feelsLike"></p>
                    </div>
                    <div class="detail-item">
                        <h3>Humidity</h3>
                        <p id="humidity"></p>
                    </div>
                    <div class="detail-item">
                        <h3>Wind</h3>
                        <p id="wind"></p>
                    </div>
                    <div class="detail-item">
                        <h3>Precipitation</h3>
                        <p id="precipitation"></p>
                    </div>
                </div>
            </div>
            
            <div class="error-message" id="errorMessage"></div>
        </div>

        <script>
            async function getWeather() {
                const location = document.getElementById('location').value;
                if (!location) {
                    showError('Please enter a location');
                    return;
                }

                try {
                    const response = await fetch('/weather', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ location }),
                    });

                    const data = await response.json();
                    
                    if (!data.success) {
                        showError(data.error || 'Failed to get weather data');
                        return;
                    }

                    displayWeather(data.data);
                } catch (error) {
                    showError('Failed to fetch weather data');
                }
            }

            function displayWeather(data) {
                const location = data.location;
                const current = data.current;
                
                // Update location and time
                document.getElementById('locationName').textContent = `${location.name}, ${location.country}`;
                document.getElementById('dateTime').textContent = `Last updated: ${current.last_updated}`;
                
                // Update temperature and condition
                document.getElementById('temperature').textContent = `${current.temp_c}°C`;
                document.getElementById('condition').textContent = current.condition.text;
                
                // Update details
                document.getElementById('feelsLike').textContent = `${current.feelslike_c}°C`;
                document.getElementById('humidity').textContent = `${current.humidity}%`;
                document.getElementById('wind').textContent = `${current.wind_kph} km/h`;
                document.getElementById('precipitation').textContent = `${current.precip_mm} mm`;
                
                // Show the weather card
                document.getElementById('weatherCard').classList.add('show');
                document.getElementById('errorMessage').style.display = 'none';
            }

            function showError(message) {
                const errorElement = document.getElementById('errorMessage');
                errorElement.textContent = message;
                errorElement.style.display = 'block';
                document.getElementById('weatherCard').classList.remove('show');
            }

            // Allow Enter key to trigger search
            document.getElementById('location').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    getWeather();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """Get weather data for a location"""
    try:
        weather_data = await mcp_client.get_weather(request.location)
        return WeatherResponse(
            location=request.location,
            data=weather_data,
            success=True
        )
    except Exception as e:
        return WeatherResponse(
            location=request.location,
            data={},
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mcp_connected": mcp_client.session is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)