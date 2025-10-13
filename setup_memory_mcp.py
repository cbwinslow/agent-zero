#!/usr/bin/env python3
"""
Setup script for Memory MCP Server integration
Adds the memory MCP server to the Agent Zero settings
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from python.helpers import settings, files
from python.helpers.print_style import PrintStyle

_PRINTER = PrintStyle(italic=True, font_color="green", padding=True)


def setup_memory_mcp_server():
    """Add memory MCP server to settings if not already present"""
    
    _PRINTER.print("=" * 60)
    _PRINTER.print("Setting up Memory MCP Server Integration")
    _PRINTER.print("=" * 60)
    
    # Load current settings
    current_settings = settings.get_settings()
    
    # Parse existing MCP servers
    mcp_servers_str = current_settings.get("mcp_servers", "[]")
    
    try:
        # Try to parse as Python literal first
        import ast
        mcp_servers = ast.literal_eval(mcp_servers_str) if mcp_servers_str else []
    except:
        try:
            # Fall back to JSON parsing
            mcp_servers = json.loads(mcp_servers_str) if mcp_servers_str else []
        except:
            _PRINTER.print("Warning: Could not parse existing MCP servers config")
            mcp_servers = []
    
    # Check if memory server already exists
    has_memory_server = any(
        server.get("name") == "memory-manager" 
        for server in mcp_servers
    )
    
    if has_memory_server:
        _PRINTER.print("Memory MCP server already configured")
        return True
    
    # Add memory MCP server configuration
    memory_server_config = {
        "name": "memory-manager",
        "description": "Agent Zero Memory Management - Manages memories, knowledge, and rules",
        "type": "stdio",
        "command": "python",
        "args": [
            files.get_abs_path("run_memory_mcp.py")
        ],
        "env": {
            "MEMORY_MCP_HOST": os.getenv("MEMORY_MCP_HOST", "localhost"),
            "MEMORY_MCP_PORT": os.getenv("MEMORY_MCP_PORT", "3001")
        }
    }
    
    mcp_servers.append(memory_server_config)
    
    # Convert back to string for settings
    mcp_servers_str = str(mcp_servers)
    
    # Update settings
    try:
        settings.set_setting("mcp_servers", mcp_servers_str)
        _PRINTER.print("✓ Memory MCP server added to settings")
        _PRINTER.print(f"  Server: memory-manager")
        _PRINTER.print(f"  Command: python {files.get_abs_path('run_memory_mcp.py')}")
        return True
    except Exception as e:
        _PRINTER.print(f"✗ Error updating settings: {e}")
        return False


def verify_setup():
    """Verify the setup was successful"""
    _PRINTER.print("\nVerifying setup...")
    
    checks = []
    
    # Check if memory MCP server script exists
    mcp_script = files.get_abs_path("run_memory_mcp.py")
    if os.path.exists(mcp_script):
        checks.append(("Memory MCP server script", True))
    else:
        checks.append(("Memory MCP server script", False))
    
    # Check if memory MCP helper exists
    mcp_helper = files.get_abs_path("python/helpers/memory_mcp_server.py")
    if os.path.exists(mcp_helper):
        checks.append(("Memory MCP server helper", True))
    else:
        checks.append(("Memory MCP server helper", False))
    
    # Check if multi-agent coordinator exists
    coordinator = files.get_abs_path("python/helpers/multi_agent_coordinator.py")
    if os.path.exists(coordinator):
        checks.append(("Multi-agent coordinator", True))
    else:
        checks.append(("Multi-agent coordinator", False))
    
    # Check if agent profiles exist
    profiles = ["researcher", "developer", "analyst", "planner", "executor"]
    for profile in profiles:
        profile_dir = files.get_abs_path("agents", profile)
        if os.path.exists(profile_dir):
            checks.append((f"Agent profile: {profile}", True))
        else:
            checks.append((f"Agent profile: {profile}", False))
    
    # Print results
    _PRINTER.print("\nSetup verification:")
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        _PRINTER.print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Main setup function"""
    try:
        # Setup memory MCP server
        setup_success = setup_memory_mcp_server()
        
        # Verify setup
        verify_success = verify_setup()
        
        _PRINTER.print("\n" + "=" * 60)
        if setup_success and verify_success:
            _PRINTER.print("✓ Memory MCP Server setup completed successfully!")
            _PRINTER.print("\nNext steps:")
            _PRINTER.print("1. Configure your .env file with API keys")
            _PRINTER.print("2. Enable multi-agent mode: MULTI_AGENT_ENABLED=true")
            _PRINTER.print("3. Restart Agent Zero to load the new configuration")
            _PRINTER.print("4. Use the multi_agent_delegation tool in your conversations")
        else:
            _PRINTER.print("✗ Setup completed with some issues")
            _PRINTER.print("Please check the errors above and try again")
        _PRINTER.print("=" * 60)
        
        return 0 if (setup_success and verify_success) else 1
        
    except Exception as e:
        _PRINTER.print(f"\n✗ Setup failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
