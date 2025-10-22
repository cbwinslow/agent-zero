#!/usr/bin/env python3
"""
Certificate Transparency (crt.sh) MCP Server

Provides certificate transparency log search for subdomain enumeration and SSL certificate discovery.
"""

import asyncio
import json
import requests
from typing import Any, Dict, List
import sys

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class CertificateTransparency:
    """Certificate Transparency Log Search"""
    
    def __init__(self):
        self.base_url = "https://crt.sh"
    
    async def search_domain(self, domain: str) -> Dict[str, Any]:
        """Search certificate transparency logs for a domain"""
        try:
            params = {"q": f"%.{domain}", "output": "json"}
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                certs = response.json()
                
                # Extract unique subdomains
                subdomains = set()
                for cert in certs:
                    name_value = cert.get("name_value", "")
                    for subdomain in name_value.split("\n"):
                        subdomain = subdomain.strip()
                        if subdomain and "*" not in subdomain:
                            subdomains.add(subdomain)
                
                return {
                    "domain": domain,
                    "certificates_found": len(certs),
                    "unique_subdomains": sorted(list(subdomains)),
                    "status": "success"
                }
            else:
                return {
                    "domain": domain,
                    "error": f"HTTP {response.status_code}",
                    "status": "failed"
                }
                
        except requests.RequestException as e:
            return {
                "domain": domain,
                "error": str(e),
                "status": "error"
            }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "status": "error"
            }
    
    async def get_certificate_details(self, cert_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific certificate"""
        try:
            url = f"{self.base_url}/?id={cert_id}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return {
                    "certificate_id": cert_id,
                    "details": response.json(),
                    "status": "success"
                }
            else:
                return {
                    "certificate_id": cert_id,
                    "error": f"HTTP {response.status_code}",
                    "status": "failed"
                }
                
        except Exception as e:
            return {
                "certificate_id": cert_id,
                "error": str(e),
                "status": "error"
            }


# Create MCP server
server = Server("crtsh")
ct = CertificateTransparency()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available certificate transparency tools"""
    return [
        Tool(
            name="search_domain",
            description="Search certificate transparency logs for a domain to discover subdomains",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to search for (e.g., example.com)"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="get_certificate_details",
            description="Get detailed information about a specific certificate",
            inputSchema={
                "type": "object",
                "properties": {
                    "cert_id": {
                        "type": "string",
                        "description": "Certificate ID from crt.sh"
                    }
                },
                "required": ["cert_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    result = None
    
    if name == "search_domain":
        result = await ct.search_domain(arguments["domain"])
    elif name == "get_certificate_details":
        result = await ct.get_certificate_details(arguments["cert_id"])
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the crt.sh MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
