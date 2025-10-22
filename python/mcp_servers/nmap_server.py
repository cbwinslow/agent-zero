#!/usr/bin/env python3
"""
Nmap MCP Server

Provides network scanning and port discovery capabilities using Nmap.
"""

import asyncio
import json
import subprocess
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
import sys

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class NmapScanner:
    """Nmap scanner with various scan types"""
    
    def __init__(self):
        self.nmap_available = self._check_nmap()
    
    def _check_nmap(self) -> bool:
        """Check if nmap is installed"""
        try:
            subprocess.run(["nmap", "--version"], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    async def quick_scan(self, target: str) -> Dict[str, Any]:
        """Perform a quick scan of top 100 ports"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-F", "--open", target],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "target": target,
                "scan_type": "quick",
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def port_scan(self, target: str, ports: str = "1-1000") -> Dict[str, Any]:
        """Scan specific ports on a target"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-p", ports, "--open", target],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            return {
                "target": target,
                "scan_type": "port_scan",
                "ports": ports,
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def service_detection(self, target: str, ports: str = "1-1000") -> Dict[str, Any]:
        """Detect services and versions on open ports"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-sV", "-p", ports, target],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "target": target,
                "scan_type": "service_detection",
                "ports": ports,
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def os_detection(self, target: str) -> Dict[str, Any]:
        """Detect operating system of target (requires root)"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-O", target],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            return {
                "target": target,
                "scan_type": "os_detection",
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed",
                "note": "May require root privileges for accurate results"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def vulnerability_scan(self, target: str) -> Dict[str, Any]:
        """Run vulnerability detection scripts"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "--script", "vuln", target],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "target": target,
                "scan_type": "vulnerability_scan",
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def aggressive_scan(self, target: str) -> Dict[str, Any]:
        """Perform aggressive scan (OS detection, version detection, script scanning, traceroute)"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-A", target],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "target": target,
                "scan_type": "aggressive",
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed",
                "note": "Aggressive scan may be detected by IDS/IPS"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "target": target}
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def ping_sweep(self, network: str) -> Dict[str, Any]:
        """Discover live hosts on a network"""
        if not self.nmap_available:
            return {
                "error": "Nmap not installed",
                "note": "Install nmap package: apt-get install nmap"
            }
        
        try:
            proc = subprocess.run(
                ["nmap", "-sn", network],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            return {
                "network": network,
                "scan_type": "ping_sweep",
                "output": proc.stdout,
                "status": "success" if proc.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out", "network": network}
        except Exception as e:
            return {"error": str(e), "network": network}


# Create MCP server
server = Server("nmap-scanner")
scanner = NmapScanner()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Nmap scanning tools"""
    return [
        Tool(
            name="quick_scan",
            description="Quick scan of top 100 ports on target",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="port_scan",
            description="Scan specific ports on a target",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    },
                    "ports": {
                        "type": "string",
                        "description": "Port range (e.g., 1-1000, 80,443, or 1-65535)",
                        "default": "1-1000"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="service_detection",
            description="Detect services and versions on open ports",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    },
                    "ports": {
                        "type": "string",
                        "description": "Port range to scan",
                        "default": "1-1000"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="os_detection",
            description="Detect operating system of target (requires root)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="vulnerability_scan",
            description="Run vulnerability detection scripts on target",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="aggressive_scan",
            description="Perform aggressive scan with OS detection, version detection, scripts, and traceroute",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or hostname"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="ping_sweep",
            description="Discover live hosts on a network",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {
                        "type": "string",
                        "description": "Network range (e.g., 192.168.1.0/24)"
                    }
                },
                "required": ["network"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    result = None
    
    if name == "quick_scan":
        result = await scanner.quick_scan(arguments["target"])
    elif name == "port_scan":
        result = await scanner.port_scan(
            arguments["target"],
            arguments.get("ports", "1-1000")
        )
    elif name == "service_detection":
        result = await scanner.service_detection(
            arguments["target"],
            arguments.get("ports", "1-1000")
        )
    elif name == "os_detection":
        result = await scanner.os_detection(arguments["target"])
    elif name == "vulnerability_scan":
        result = await scanner.vulnerability_scan(arguments["target"])
    elif name == "aggressive_scan":
        result = await scanner.aggressive_scan(arguments["target"])
    elif name == "ping_sweep":
        result = await scanner.ping_sweep(arguments["network"])
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the Nmap MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
