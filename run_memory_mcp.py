#!/usr/bin/env python3
"""
Standalone Memory MCP Server for Agent Zero
Run this to start the memory management MCP server
"""

import sys
import os
import asyncio

# Add parent directory to path to import agent zero modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from python.helpers.memory_mcp_server import memory_mcp
from python.helpers import dotenv
from python.helpers.print_style import PrintStyle

# Load environment variables
dotenv.load_dotenv()

_PRINTER = PrintStyle(italic=True, font_color="cyan", padding=True)


def main():
    """Main entry point for the memory MCP server"""
    
    _PRINTER.print("=" * 60)
    _PRINTER.print("Agent Zero - Memory Management MCP Server")
    _PRINTER.print("=" * 60)
    
    # Get configuration from environment
    host = os.getenv("MEMORY_MCP_HOST", "localhost")
    port = int(os.getenv("MEMORY_MCP_PORT", "3001"))
    
    _PRINTER.print(f"Starting server on {host}:{port}")
    _PRINTER.print("Press Ctrl+C to stop the server")
    _PRINTER.print("=" * 60)
    
    try:
        # Run the MCP server
        memory_mcp.run(host=host, port=port, transport="stdio")
    except KeyboardInterrupt:
        _PRINTER.print("\nShutting down memory MCP server...")
    except Exception as e:
        _PRINTER.print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
