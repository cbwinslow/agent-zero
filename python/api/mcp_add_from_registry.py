from python.helpers.api import ApiHandler, Request, Response
from typing import Any
from python.helpers.mcp_discovery import MCPServerDiscovery
from python.helpers.mcp_handler import MCPConfig
import json


class McpAddFromRegistry(ApiHandler):
    """API endpoint for adding a discovered MCP server to the configuration"""
    
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        """
        Add a discovered server to the Agent Zero MCP configuration
        
        Input parameters:
        - server_name: str (required) - Name or full name of the server to add
        - enabled: bool (optional) - Whether to enable the server immediately (default: False)
        - custom_config: dict (optional) - Custom configuration overrides
        """
        
        try:
            server_name = input.get('server_name')
            if not server_name:
                return {
                    'success': False,
                    'error': 'server_name is required'
                }
            
            enabled = input.get('enabled', False)
            custom_config = input.get('custom_config', {})
            
            # Get the server from the registry
            discovery = MCPServerDiscovery()
            server = discovery.get_server_by_name(server_name)
            
            if not server:
                # Try to refresh and search again
                discovery.discover_all(force_refresh=True)
                server = discovery.get_server_by_name(server_name)
                
                if not server:
                    return {
                        'success': False,
                        'error': f'Server "{server_name}" not found in registry'
                    }
            
            # Generate configuration for the server
            config = discovery.generate_server_config(server)
            
            # Apply custom configuration
            config.update(custom_config)
            
            # Set enabled status
            config['enabled'] = enabled
            
            # Add metadata for tracking
            config['source'] = server.get('source', 'unknown')
            config['registry_entry'] = True
            
            return {
                'success': True,
                'server': server,
                'config': config,
                'message': f'Server "{server_name}" configuration generated. Add this to your MCP servers configuration.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
