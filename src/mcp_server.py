from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio
import json
from .weather_tools import get_current_weather

# Create the MCP server
app = Server("weather-server")

# FIRST: Register your tool so AI agents can discover it
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_current_weather",
            description="Get current weather information for a specific location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, state, or country (e.g., 'Delhi', 'Mumbai', 'New York')"
                    }
                },
                "required": ["location"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "get_current_weather":
        # Step 1: Extract location from arguments
        if "location" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Location parameter is required"
            )]
        
        location = arguments["location"]
        
        # Step 2: Call our weather function
        try:
            weather_data = await get_current_weather(location)
            
            # Step 3: Handle errors from weather API
            if "error" in weather_data:
                return [types.TextContent(
                    type="text", 
                    text=f"Weather API Error: {weather_data['error']}"
                )]
            
            # Step 4: Format the response (MOVED INSIDE try block)
            formatted_weather = json.dumps(weather_data, indent=2)
            return [types.TextContent(
                type="text",
                text=formatted_weather
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]