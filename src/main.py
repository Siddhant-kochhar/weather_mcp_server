import asyncio
from mcp.server.stdio import stdio_server
from .mcp_server import app
from .config import validate_config

async def main():
    """Main entry point for the MCP server"""
    
    # Validate configuration before starting
    validate_config()
    
    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())