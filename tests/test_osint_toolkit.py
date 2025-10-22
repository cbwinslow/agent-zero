"""
Tests for OSINT Toolkit Tool
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestOSINTToolkitStructure(unittest.TestCase):
    """Test OSINT toolkit structure and imports"""
    
    def test_osint_toolkit_imports(self):
        """Test that OSINT toolkit can be imported"""
        try:
            from python.tools.osint_toolkit import OSINTToolkit
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import OSINTToolkit: {e}")
    
    def test_osint_toolkit_has_required_methods(self):
        """Test that OSINTToolkit has all required methods"""
        from python.tools.osint_toolkit import OSINTToolkit
        
        required_methods = [
            '_subdomain_enum',
            '_email_harvest',
            '_port_scan',
            '_username_search',
            '_whois_lookup',
            '_certificate_search',
            '_vulnerability_scan',
            '_dns_enum',
            '_web_recon',
            '_social_media_search'
        ]
        
        for method in required_methods:
            self.assertTrue(
                hasattr(OSINTToolkit, method),
                f"OSINTToolkit missing method: {method}"
            )


class TestOSINTMCPServers(unittest.TestCase):
    """Test OSINT MCP servers structure"""
    
    def test_osint_server_exists(self):
        """Test that OSINT MCP server file exists"""
        server_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'python',
            'mcp_servers',
            'osint_server.py'
        )
        self.assertTrue(
            os.path.exists(server_path),
            "OSINT MCP server file does not exist"
        )
    
    def test_nmap_server_exists(self):
        """Test that Nmap MCP server file exists"""
        server_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'python',
            'mcp_servers',
            'nmap_server.py'
        )
        self.assertTrue(
            os.path.exists(server_path),
            "Nmap MCP server file does not exist"
        )
    
    def test_crtsh_server_exists(self):
        """Test that crt.sh MCP server file exists"""
        server_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'python',
            'mcp_servers',
            'crtsh_server.py'
        )
        self.assertTrue(
            os.path.exists(server_path),
            "crt.sh MCP server file does not exist"
        )


class TestMCPConfiguration(unittest.TestCase):
    """Test MCP server configuration"""
    
    def test_mcp_servers_available_config_exists(self):
        """Test that MCP servers configuration file exists"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'conf',
            'mcp_servers_available.json'
        )
        self.assertTrue(
            os.path.exists(config_path),
            "MCP servers configuration file does not exist"
        )
    
    def test_mcp_servers_vscode_config_exists(self):
        """Test that VS Code compatible MCP config exists"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'conf',
            'mcp_servers_vscode.json'
        )
        self.assertTrue(
            os.path.exists(config_path),
            "VS Code MCP configuration file does not exist"
        )
    
    def test_mcp_config_structure(self):
        """Test MCP configuration file structure"""
        import json
        
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'conf',
            'mcp_servers_available.json'
        )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('mcpServers', config)
        self.assertIsInstance(config['mcpServers'], dict)
        
        # Test some required OSINT servers
        osint_servers = [
            'osint-toolkit',
            'nmap',
            'crt-sh',
            'whois',
            'shodan'
        ]
        
        for server in osint_servers:
            self.assertIn(
                server,
                config['mcpServers'],
                f"Missing OSINT server: {server}"
            )
    
    def test_osint_servers_have_required_fields(self):
        """Test that OSINT servers have required configuration fields"""
        import json
        
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'conf',
            'mcp_servers_available.json'
        )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check a sample OSINT server
        nmap_config = config['mcpServers'].get('nmap')
        self.assertIsNotNone(nmap_config, "Nmap server not in configuration")
        
        required_fields = ['name', 'description', 'type', 'command', 'args']
        for field in required_fields:
            self.assertIn(
                field,
                nmap_config,
                f"Nmap server missing field: {field}"
            )


class TestDocumentation(unittest.TestCase):
    """Test documentation files"""
    
    def test_osint_documentation_exists(self):
        """Test that OSINT documentation exists"""
        doc_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'docs',
            'osint_and_security.md'
        )
        self.assertTrue(
            os.path.exists(doc_path),
            "OSINT and Security documentation does not exist"
        )
    
    def test_osint_installation_script_exists(self):
        """Test that OSINT tools installation script exists"""
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'docker',
            'base',
            'fs',
            'ins',
            'install_osint_tools.sh'
        )
        self.assertTrue(
            os.path.exists(script_path),
            "OSINT tools installation script does not exist"
        )
    
    def test_osint_installation_script_executable(self):
        """Test that OSINT installation script is executable"""
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'docker',
            'base',
            'fs',
            'ins',
            'install_osint_tools.sh'
        )
        
        if os.path.exists(script_path):
            # Check if file starts with shebang
            with open(script_path, 'r') as f:
                first_line = f.readline()
                self.assertTrue(
                    first_line.startswith('#!/bin/bash'),
                    "OSINT installation script missing shebang"
                )


class TestGitHubIntegration(unittest.TestCase):
    """Test GitHub integration tool"""
    
    def test_github_integration_tool_exists(self):
        """Test that GitHub integration tool exists"""
        tool_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'python',
            'tools',
            'github_integration.py'
        )
        self.assertTrue(
            os.path.exists(tool_path),
            "GitHub integration tool does not exist"
        )
    
    def test_github_api_helper_exists(self):
        """Test that GitHub API helper exists"""
        helper_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'python',
            'helpers',
            'github_api.py'
        )
        self.assertTrue(
            os.path.exists(helper_path),
            "GitHub API helper does not exist"
        )


class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration"""
    
    def test_example_env_has_osint_keys(self):
        """Test that example.env includes OSINT API keys"""
        env_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'example.env'
        )
        
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Check for OSINT-related environment variables
        osint_vars = [
            'SHODAN_API_KEY',
            'VIRUSTOTAL_API_KEY',
            'CENSYS_API_ID',
            'HUNTER_API_KEY',
            'IPINFO_TOKEN'
        ]
        
        for var in osint_vars:
            self.assertIn(
                var,
                content,
                f"example.env missing OSINT variable: {var}"
            )


if __name__ == "__main__":
    unittest.main()
