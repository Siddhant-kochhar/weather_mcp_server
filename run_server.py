#!/usr/bin/env python3
"""
Simple script to run the FastAPI server
"""
import uvicorn
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("🚀 Starting Weather MCP Frontend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌤️  Open your browser and go to the URL above!")
    print("⛔ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "src.fastapi_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )