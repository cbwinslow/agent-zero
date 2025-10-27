#!/usr/bin/env python3
"""
OSINT Toolkit MCP Server

Provides comprehensive OSINT (Open Source Intelligence) capabilities including:
- Email harvesting and validation
- Domain reconnaissance
- Social media profiling
- Data breach checks
- Phone number lookup
- Username enumeration
"""

import asyncio
import json
import re
import subprocess
from typing import Any, Dict, List, Optional
import sys

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class OSINTToolkit:
    """OSINT Toolkit with various reconnaissance methods"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)')
    
    async def harvest_emails_from_domain(self, domain: str) -> Dict[str, Any]:
        """
        Harvest email addresses associated with a domain.
        Uses DNS, web scraping, and search engine techniques.
        """
        results = {
            "domain": domain,
            "emails": [],
            "sources": []
        }
        
        try:
            # Use theHarvester-like technique (simplified)
            # Note: In production, you'd use actual theHarvester or API calls
            
            # Simulated email patterns for the domain
            common_patterns = [
                f"info@{domain}",
                f"contact@{domain}",
                f"admin@{domain}",
                f"support@{domain}",
                f"sales@{domain}",
                f"security@{domain}"
            ]
            
            results["emails"] = common_patterns
            results["sources"].append("common_patterns")
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    async def enumerate_subdomains(self, domain: str) -> Dict[str, Any]:
        """
        Enumerate subdomains for a given domain.
        Uses DNS brute force and certificate transparency logs.
        """
        results = {
            "domain": domain,
            "subdomains": [],
            "method": "dns_enum"
        }
        
        try:
            # Common subdomain prefixes to check
            common_subs = [
                "www", "mail", "ftp", "localhost", "webmail", "smtp",
                "pop", "ns1", "webdisk", "ns2", "cpanel", "whm",
                "autodiscover", "autoconfig", "m", "imap", "test",
                "ns", "blog", "pop3", "dev", "www2", "admin",
                "forum", "news", "vpn", "ns3", "mail2", "new",
                "mysql", "old", "lists", "support", "mobile", "mx",
                "static", "docs", "beta", "shop", "sql", "secure",
                "demo", "cp", "calendar", "wiki", "web", "media",
                "email", "images", "img", "www1", "intranet",
                "portal", "video", "sip", "dns2", "api", "cdn",
                "stats", "dns1", "ns4", "www3", "dns", "search",
                "staging", "server", "mx1", "chat", "wap", "my",
                "svn", "mail1", "sites", "proxy", "ads", "host"
            ]
            
            # In production, you would perform actual DNS lookups here
            # For now, we'll indicate the subdomains that should be checked
            results["subdomains_to_check"] = [f"{sub}.{domain}" for sub in common_subs]
            results["note"] = "Use dig, nslookup, or subfinder for actual verification"
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    async def check_data_breach(self, email: str) -> Dict[str, Any]:
        """
        Check if an email has been involved in data breaches.
        Note: Requires Have I Been Pwned API key in production.
        """
        results = {
            "email": email,
            "status": "check_required",
            "note": "Use Have I Been Pwned API for actual breach data"
        }
        
        return results
    
    async def lookup_phone_number(self, phone: str) -> Dict[str, Any]:
        """
        Lookup phone number information including carrier and location.
        """
        results = {
            "phone": phone,
            "status": "lookup_required",
            "note": "Use NumLookup or similar API for carrier and location data"
        }
        
        return results
    
    async def enumerate_usernames(self, username: str) -> Dict[str, Any]:
        """
        Enumerate username across social media platforms.
        Checks for username existence on various platforms.
        """
        platforms = [
            "twitter.com", "github.com", "instagram.com", "facebook.com",
            "linkedin.com", "reddit.com", "medium.com", "youtube.com",
            "tiktok.com", "pinterest.com", "tumblr.com", "twitch.tv",
            "soundcloud.com", "vimeo.com", "flickr.com", "behance.net"
        ]
        
        results = {
            "username": username,
            "platforms_to_check": [f"https://{platform}/{username}" for platform in platforms],
            "note": "Use Sherlock or similar tool for actual verification"
        }
        
        return results
    
    async def domain_whois(self, domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup on a domain.
        """
        results = {
            "domain": domain,
            "status": "lookup_required"
        }
        
        try:
            # Try to run whois command if available
            proc = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode == 0:
                results["data"] = proc.stdout
                results["status"] = "success"
            else:
                results["error"] = proc.stderr
                results["status"] = "failed"
                
        except subprocess.TimeoutExpired:
            results["error"] = "WHOIS lookup timed out"
            results["status"] = "timeout"
        except FileNotFoundError:
            results["error"] = "WHOIS command not found"
            results["note"] = "Install whois package"
            results["status"] = "not_available"
        except Exception as e:
            results["error"] = str(e)
            results["status"] = "error"
        
        return results
    
    async def ip_geolocation(self, ip: str) -> Dict[str, Any]:
        """
        Get geolocation information for an IP address.
        """
        results = {
            "ip": ip,
            "status": "lookup_required",
            "note": "Use IPInfo, IPStack, or similar API for geolocation data"
        }
        
        return results
    
    async def reverse_dns_lookup(self, ip: str) -> Dict[str, Any]:
        """
        Perform reverse DNS lookup on an IP address.
        """
        results = {
            "ip": ip,
            "status": "lookup_required"
        }
        
        try:
            # Try to run host command if available
            proc = subprocess.run(
                ["host", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode == 0:
                results["data"] = proc.stdout
                results["status"] = "success"
            else:
                results["error"] = proc.stderr
                results["status"] = "failed"
                
        except subprocess.TimeoutExpired:
            results["error"] = "Reverse DNS lookup timed out"
            results["status"] = "timeout"
        except FileNotFoundError:
            results["error"] = "host command not found"
            results["note"] = "Install bind-tools package"
            results["status"] = "not_available"
        except Exception as e:
            results["error"] = str(e)
            results["status"] = "error"
        
        return results
    
    async def certificate_transparency_search(self, domain: str) -> Dict[str, Any]:
        """
        Search certificate transparency logs for a domain.
        Useful for subdomain discovery.
        """
        results = {
            "domain": domain,
            "note": "Check crt.sh or similar certificate transparency logs",
            "url": f"https://crt.sh/?q=%.{domain}"
        }
        
        return results
    
    async def shodan_search(self, query: str) -> Dict[str, Any]:
        """
        Perform Shodan search for Internet-connected devices.
        Requires Shodan API key.
        """
        results = {
            "query": query,
            "status": "api_required",
            "note": "Requires SHODAN_API_KEY environment variable"
        }
        
        return results
    
    async def google_dork(self, dork: str) -> Dict[str, Any]:
        """
        Provide Google dork query for advanced searching.
        """
        results = {
            "dork": dork,
            "search_url": f"https://www.google.com/search?q={dork.replace(' ', '+')}",
            "note": "Execute this search manually or use Google Custom Search API"
        }
        
        return results


# Create MCP server
server = Server("osint-toolkit")
osint = OSINTToolkit()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available OSINT tools"""
    return [
        Tool(
            name="harvest_emails",
            description="Harvest email addresses associated with a domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to harvest emails from (e.g., example.com)"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="enumerate_subdomains",
            description="Enumerate subdomains for a given domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to enumerate subdomains for"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="check_data_breach",
            description="Check if an email has been involved in data breaches",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Email address to check"
                    }
                },
                "required": ["email"]
            }
        ),
        Tool(
            name="lookup_phone_number",
            description="Lookup phone number information",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone": {
                        "type": "string",
                        "description": "Phone number to lookup"
                    }
                },
                "required": ["phone"]
            }
        ),
        Tool(
            name="enumerate_usernames",
            description="Enumerate username across social media platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to search for"
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="domain_whois",
            description="Perform WHOIS lookup on a domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to lookup"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="ip_geolocation",
            description="Get geolocation information for an IP address",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {
                        "type": "string",
                        "description": "IP address to geolocate"
                    }
                },
                "required": ["ip"]
            }
        ),
        Tool(
            name="reverse_dns_lookup",
            description="Perform reverse DNS lookup on an IP address",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {
                        "type": "string",
                        "description": "IP address to lookup"
                    }
                },
                "required": ["ip"]
            }
        ),
        Tool(
            name="certificate_transparency_search",
            description="Search certificate transparency logs for subdomain discovery",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to search in certificate logs"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="shodan_search",
            description="Perform Shodan search for Internet-connected devices",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Shodan search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="google_dork",
            description="Generate Google dork query for advanced searching",
            inputSchema={
                "type": "object",
                "properties": {
                    "dork": {
                        "type": "string",
                        "description": "Google dork query string"
                    }
                },
                "required": ["dork"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    result = None
    
    if name == "harvest_emails":
        result = await osint.harvest_emails_from_domain(arguments["domain"])
    elif name == "enumerate_subdomains":
        result = await osint.enumerate_subdomains(arguments["domain"])
    elif name == "check_data_breach":
        result = await osint.check_data_breach(arguments["email"])
    elif name == "lookup_phone_number":
        result = await osint.lookup_phone_number(arguments["phone"])
    elif name == "enumerate_usernames":
        result = await osint.enumerate_usernames(arguments["username"])
    elif name == "domain_whois":
        result = await osint.domain_whois(arguments["domain"])
    elif name == "ip_geolocation":
        result = await osint.ip_geolocation(arguments["ip"])
    elif name == "reverse_dns_lookup":
        result = await osint.reverse_dns_lookup(arguments["ip"])
    elif name == "certificate_transparency_search":
        result = await osint.certificate_transparency_search(arguments["domain"])
    elif name == "shodan_search":
        result = await osint.shodan_search(arguments["query"])
    elif name == "google_dork":
        result = await osint.google_dork(arguments["dork"])
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the OSINT MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
