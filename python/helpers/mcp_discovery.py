"""
MCP Server Discovery Module

This module provides functionality to discover MCP servers from multiple sources:
- npm registry (@modelcontextprotocol/* packages)
- GitHub repositories (with mcp-server topics)
- Docker Hub (images with mcp tags)
"""

import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path

class MCPServerDiscovery:
    """Discover MCP servers from various sources"""
    
    # Cache settings
    CACHE_FILE = "conf/mcp_servers_registry.json"
    CACHE_DURATION = timedelta(hours=24)  # Cache for 24 hours
    
    # API endpoints
    NPM_REGISTRY_URL = "https://registry.npmjs.org"
    GITHUB_API_URL = "https://api.github.com"
    DOCKER_HUB_URL = "https://hub.docker.com/v2"
    
    def __init__(self, cache_file: Optional[str] = None):
        """Initialize the discovery module"""
        self.cache_file = cache_file or self.CACHE_FILE
        self.cache_data = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached discovery data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is still valid
                    cache_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                    if datetime.now() - cache_time < self.CACHE_DURATION:
                        return data
            except Exception as e:
                print(f"Error loading cache: {e}")
        return {'timestamp': '2000-01-01', 'servers': []}
    
    def _save_cache(self, data: Dict[str, Any]):
        """Save discovery data to cache"""
        try:
            # Ensure the directory exists
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def discover_npm_servers(self) -> List[Dict[str, Any]]:
        """Discover MCP servers from npm registry"""
        servers = []
        
        try:
            # Search for @modelcontextprotocol packages
            search_url = f"{self.NPM_REGISTRY_URL}/-/v1/search"
            params = {
                'text': 'scope:modelcontextprotocol',
                'size': 250
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json()
                
                for pkg in results.get('objects', []):
                    package = pkg.get('package', {})
                    name = package.get('name', '')
                    
                    # Only include server packages
                    if 'server' in name.lower():
                        server_info = {
                            'name': name.replace('@modelcontextprotocol/', ''),
                            'full_name': name,
                            'source': 'npm',
                            'type': 'stdio',
                            'description': package.get('description', ''),
                            'version': package.get('version', ''),
                            'command': 'npx',
                            'args': ['-y', name],
                            'homepage': package.get('links', {}).get('homepage', ''),
                            'repository': package.get('links', {}).get('repository', ''),
                            'npm_url': f"https://www.npmjs.com/package/{name}",
                            'downloads': package.get('downloads', 0),
                            'enabled': False
                        }
                        servers.append(server_info)
            
            # Also search for other mcp-server packages
            params = {
                'text': 'keywords:mcp-server',
                'size': 100
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json()
                
                for pkg in results.get('objects', []):
                    package = pkg.get('package', {})
                    name = package.get('name', '')
                    
                    # Skip if already added
                    if any(s['full_name'] == name for s in servers):
                        continue
                    
                    server_info = {
                        'name': name.split('/')[-1],  # Get just the package name
                        'full_name': name,
                        'source': 'npm',
                        'type': 'stdio',
                        'description': package.get('description', ''),
                        'version': package.get('version', ''),
                        'command': 'npx',
                        'args': ['-y', name],
                        'homepage': package.get('links', {}).get('homepage', ''),
                        'repository': package.get('links', {}).get('repository', ''),
                        'npm_url': f"https://www.npmjs.com/package/{name}",
                        'downloads': package.get('downloads', 0),
                        'enabled': False
                    }
                    servers.append(server_info)
                    
        except Exception as e:
            print(f"Error discovering npm servers: {e}")
        
        return servers
    
    def discover_github_servers(self, github_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover MCP servers from GitHub repositories"""
        servers = []
        
        try:
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            # Search for repositories with mcp-server topic
            search_url = f"{self.GITHUB_API_URL}/search/repositories"
            
            # Search for multiple queries
            queries = [
                'topic:mcp-server',
                'topic:model-context-protocol',
                'mcp server in:name,description',
            ]
            
            for query in queries:
                params = {
                    'q': query,
                    'sort': 'stars',
                    'per_page': 50
                }
                
                response = requests.get(search_url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    results = response.json()
                    
                    for repo in results.get('items', []):
                        full_name = repo.get('full_name', '')
                        
                        # Skip if already added
                        if any(s.get('github_repo') == full_name for s in servers):
                            continue
                        
                        server_info = {
                            'name': repo.get('name', ''),
                            'full_name': full_name,
                            'source': 'github',
                            'type': 'unknown',  # Need to check repo for type
                            'description': repo.get('description', ''),
                            'github_repo': full_name,
                            'github_url': repo.get('html_url', ''),
                            'stars': repo.get('stargazers_count', 0),
                            'language': repo.get('language', ''),
                            'topics': repo.get('topics', []),
                            'last_updated': repo.get('updated_at', ''),
                            'enabled': False
                        }
                        servers.append(server_info)
                        
        except Exception as e:
            print(f"Error discovering GitHub servers: {e}")
        
        return servers
    
    def discover_docker_servers(self) -> List[Dict[str, Any]]:
        """Discover MCP servers from Docker Hub"""
        servers = []
        
        try:
            # Search Docker Hub for MCP servers
            search_url = f"{self.DOCKER_HUB_URL}/search/repositories"
            
            queries = ['mcp', 'mcp-server', 'model-context-protocol']
            
            for query in queries:
                params = {
                    'query': query,
                    'page_size': 50
                }
                
                response = requests.get(search_url, params=params, timeout=10)
                if response.status_code == 200:
                    results = response.json()
                    
                    for repo in results.get('results', []):
                        repo_name = repo.get('repo_name', '')
                        
                        # Skip if already added
                        if any(s.get('docker_image') == repo_name for s in servers):
                            continue
                        
                        server_info = {
                            'name': repo_name.split('/')[-1],
                            'full_name': repo_name,
                            'source': 'docker',
                            'type': 'docker',
                            'description': repo.get('short_description', ''),
                            'docker_image': repo_name,
                            'docker_url': f"https://hub.docker.com/r/{repo_name}",
                            'stars': repo.get('star_count', 0),
                            'pulls': repo.get('pull_count', 0),
                            'last_updated': repo.get('last_updated', ''),
                            'enabled': False
                        }
                        servers.append(server_info)
                        
        except Exception as e:
            print(f"Error discovering Docker servers: {e}")
        
        return servers
    
    def discover_all(self, github_token: Optional[str] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Discover MCP servers from all sources"""
        
        # Check cache first
        if not force_refresh:
            cache_time = datetime.fromisoformat(self.cache_data.get('timestamp', '2000-01-01'))
            if datetime.now() - cache_time < self.CACHE_DURATION:
                return self.cache_data.get('servers', [])
        
        all_servers = []
        
        print("Discovering MCP servers from npm...")
        npm_servers = self.discover_npm_servers()
        all_servers.extend(npm_servers)
        print(f"Found {len(npm_servers)} npm servers")
        
        print("Discovering MCP servers from GitHub...")
        github_servers = self.discover_github_servers(github_token)
        all_servers.extend(github_servers)
        print(f"Found {len(github_servers)} GitHub servers")
        
        print("Discovering MCP servers from Docker Hub...")
        docker_servers = self.discover_docker_servers()
        all_servers.extend(docker_servers)
        print(f"Found {len(docker_servers)} Docker servers")
        
        # Sort by popularity (stars/downloads)
        all_servers.sort(key=lambda x: x.get('stars', x.get('downloads', x.get('pulls', 0))), reverse=True)
        
        # Save to cache
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'servers': all_servers,
            'count': len(all_servers)
        }
        self._save_cache(cache_data)
        self.cache_data = cache_data
        
        return all_servers
    
    def get_server_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific server by name"""
        servers = self.cache_data.get('servers', [])
        for server in servers:
            if server.get('name') == name or server.get('full_name') == name:
                return server
        return None
    
    def search_servers(self, query: str, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for servers by query string"""
        servers = self.cache_data.get('servers', [])
        results = []
        
        query_lower = query.lower()
        
        for server in servers:
            # Filter by source if specified
            if source and server.get('source') != source:
                continue
            
            # Search in name, description, and topics
            if (query_lower in server.get('name', '').lower() or
                query_lower in server.get('description', '').lower() or
                any(query_lower in topic.lower() for topic in server.get('topics', []))):
                results.append(server)
        
        return results
    
    def generate_server_config(self, server: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Agent Zero configuration for a server"""
        config = {
            'name': server.get('name', ''),
            'description': server.get('description', ''),
            'enabled': False
        }
        
        source = server.get('source', '')
        
        if source == 'npm':
            config.update({
                'type': 'stdio',
                'command': server.get('command', 'npx'),
                'args': server.get('args', []),
            })
        elif source == 'docker':
            config.update({
                'type': 'stdio',
                'command': 'docker',
                'args': ['run', '-i', '--rm', server.get('docker_image', '')],
            })
        elif source == 'github':
            # For GitHub repos, we need to provide instructions
            config['notes'] = f"Clone from {server.get('github_url', '')} and follow setup instructions"
        
        return config


def discover_mcp_servers(github_token: Optional[str] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Convenience function to discover all MCP servers"""
    discovery = MCPServerDiscovery()
    return discovery.discover_all(github_token, force_refresh)
