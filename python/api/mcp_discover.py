from python.helpers.api import ApiHandler, Request, Response
from typing import Any
from python.helpers.mcp_discovery import MCPServerDiscovery
import os


class McpDiscover(ApiHandler):
    """API endpoint for discovering MCP servers from various sources"""
    
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        """
        Discover MCP servers from npm, GitHub, and Docker Hub
        
        Input parameters:
        - force_refresh: bool (optional) - Force refresh of cached data
        - source: str (optional) - Filter by source (npm, github, docker)
        - query: str (optional) - Search query
        """
        
        try:
            force_refresh = input.get('force_refresh', False)
            source = input.get('source', None)
            query = input.get('query', '')
            
            # Get GitHub token from environment if available
            github_token = os.environ.get('GITHUB_TOKEN')
            
            # Initialize discovery
            discovery = MCPServerDiscovery()
            
            # Discover all servers
            servers = discovery.discover_all(github_token, force_refresh)
            
            # Filter by source if specified
            if source:
                servers = [s for s in servers if s.get('source') == source]
            
            # Search if query provided
            if query:
                servers = discovery.search_servers(query, source)
            
            return {
                'success': True,
                'servers': servers,
                'count': len(servers),
                'cached': not force_refresh
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
