import httpx
from typing import Dict, Any
from .config import WEATHER_API_KEY, WEATHER_API_BASE_URL

async def get_current_weather(location: str) -> Dict[str, Any]:
    """Get current weather for a given location"""
    
    if not location:
        return {"error": "Location parameter is required"}
    
    # Step 1: Parameters
    params = {
        "key": WEATHER_API_KEY,
        "q": location
    }
    
    # Step 2: Make the HTTP request
    url = f"{WEATHER_API_BASE_URL}/current.json"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            data = response.json()
            return data
    except httpx.TimeoutException:
        return {"error": "Request timed out. Please try again."}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"error": "Invalid API key. Please check your configuration."}
        elif e.response.status_code == 404:
            return {"error": f"Location '{location}' not found."}
        else:
            return {"error": f"HTTP error occurred: {str(e)}"}
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

