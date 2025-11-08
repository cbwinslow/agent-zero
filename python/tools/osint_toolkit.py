"""
OSINT Toolkit Tool

This tool provides comprehensive OSINT capabilities including:
- Domain reconnaissance
- Email harvesting
- Subdomain enumeration
- Social media profiling
- Network scanning
- Vulnerability assessment
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import subprocess
import os
import json
import re
from typing import Optional, List, Dict, Any


class OSINTToolkit(Tool):
    """
    Tool for Open Source Intelligence (OSINT) operations.
    
    Supported methods:
    - subdomain_enum: Enumerate subdomains for a domain
    - email_harvest: Harvest email addresses from a domain
    - port_scan: Scan ports on a target
    - username_search: Search for username across social media
    - whois_lookup: Perform WHOIS lookup
    - certificate_search: Search certificate transparency logs
    - vulnerability_scan: Scan for vulnerabilities
    - dns_enum: Enumerate DNS records
    - web_recon: Perform web reconnaissance
    - social_media_search: Search social media for information
    """
    
    async def execute(self, **kwargs):
        """
        Execute the OSINT toolkit tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        method = self.args.get("method", "subdomain_enum")
        
        # Route to appropriate method
        if method == "subdomain_enum":
            return await self._subdomain_enum(**kwargs)
        elif method == "email_harvest":
            return await self._email_harvest(**kwargs)
        elif method == "port_scan":
            return await self._port_scan(**kwargs)
        elif method == "username_search":
            return await self._username_search(**kwargs)
        elif method == "whois_lookup":
            return await self._whois_lookup(**kwargs)
        elif method == "certificate_search":
            return await self._certificate_search(**kwargs)
        elif method == "vulnerability_scan":
            return await self._vulnerability_scan(**kwargs)
        elif method == "dns_enum":
            return await self._dns_enum(**kwargs)
        elif method == "web_recon":
            return await self._web_recon(**kwargs)
        elif method == "social_media_search":
            return await self._social_media_search(**kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: subdomain_enum, email_harvest, port_scan, username_search, whois_lookup, certificate_search, vulnerability_scan, dns_enum, web_recon, social_media_search",
                break_loop=False
            )
    
    async def _subdomain_enum(self, **kwargs):
        """Enumerate subdomains using various tools"""
        domain = self.args.get("domain")
        tool = self.args.get("tool", "subfinder")  # subfinder, sublist3r, amass
        
        if not domain:
            return Response(
                message="Please specify 'domain' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Subdomain Enumeration for {domain}\n\n"
            
            if tool == "subfinder" and os.path.exists("/usr/local/bin/subfinder"):
                result = subprocess.run(
                    ["subfinder", "-d", domain, "-silent"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0 and result.stdout:
                    subdomains = result.stdout.strip().split("\n")
                    message += f"**Tool**: Subfinder\n"
                    message += f"**Subdomains Found**: {len(subdomains)}\n\n"
                    for subdomain in subdomains[:50]:  # Limit to 50
                        message += f"- {subdomain}\n"
                    if len(subdomains) > 50:
                        message += f"\n... and {len(subdomains) - 50} more\n"
                else:
                    message += "No subdomains found or tool error\n"
                    
            elif tool == "sublist3r" and os.path.exists("/opt/Sublist3r"):
                message += f"**Tool**: Sublist3r\n"
                message += f"Run: `python3 /opt/Sublist3r/sublist3r.py -d {domain}`\n"
                
            elif tool == "amass" and os.path.exists("/usr/local/bin/amass"):
                result = subprocess.run(
                    ["amass", "enum", "-passive", "-d", domain],
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                
                if result.returncode == 0 and result.stdout:
                    subdomains = result.stdout.strip().split("\n")
                    message += f"**Tool**: Amass\n"
                    message += f"**Subdomains Found**: {len(subdomains)}\n\n"
                    for subdomain in subdomains[:50]:
                        message += f"- {subdomain}\n"
                    if len(subdomains) > 50:
                        message += f"\n... and {len(subdomains) - 50} more\n"
                else:
                    message += "No subdomains found or tool error\n"
            else:
                message += f"Tool '{tool}' not available. Available tools: subfinder, sublist3r, amass\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Subdomain Enumeration",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except subprocess.TimeoutExpired:
            error_msg = f"Subdomain enumeration timed out for {domain}"
            PrintStyle(font_color="yellow", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
        except Exception as e:
            error_msg = f"Failed to enumerate subdomains: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _email_harvest(self, **kwargs):
        """Harvest email addresses from a domain"""
        domain = self.args.get("domain")
        
        if not domain:
            return Response(
                message="Please specify 'domain' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Email Harvesting for {domain}\n\n"
            
            if os.path.exists("/opt/theHarvester"):
                message += f"**Tool**: theHarvester\n"
                message += f"Run: `python3 /opt/theHarvester/theHarvester.py -d {domain} -b all`\n\n"
                
                # Common email patterns
                message += "**Common Email Patterns**:\n"
                patterns = [
                    f"info@{domain}",
                    f"contact@{domain}",
                    f"admin@{domain}",
                    f"support@{domain}",
                    f"sales@{domain}",
                    f"security@{domain}",
                    f"webmaster@{domain}",
                    f"postmaster@{domain}"
                ]
                for pattern in patterns:
                    message += f"- {pattern}\n"
            else:
                message += "theHarvester not installed\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Email Harvesting",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to harvest emails: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _port_scan(self, **kwargs):
        """Perform port scanning"""
        target = self.args.get("target")
        ports = self.args.get("ports", "1-1000")
        scan_type = self.args.get("scan_type", "quick")  # quick, full, service
        
        if not target:
            return Response(
                message="Please specify 'target' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Port Scan for {target}\n\n"
            
            if os.path.exists("/usr/bin/nmap"):
                if scan_type == "quick":
                    cmd = ["nmap", "-F", "--open", target]
                elif scan_type == "full":
                    cmd = ["nmap", "-p", ports, "--open", target]
                elif scan_type == "service":
                    cmd = ["nmap", "-sV", "-p", ports, target]
                else:
                    cmd = ["nmap", "-F", "--open", target]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    message += f"**Scan Type**: {scan_type}\n\n"
                    message += "```\n"
                    message += result.stdout
                    message += "\n```\n"
                else:
                    message += f"Scan failed: {result.stderr}\n"
            else:
                message += "Nmap not installed\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Port Scan",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except subprocess.TimeoutExpired:
            error_msg = f"Port scan timed out for {target}"
            PrintStyle(font_color="yellow", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
        except Exception as e:
            error_msg = f"Failed to perform port scan: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _username_search(self, **kwargs):
        """Search for username across social media platforms"""
        username = self.args.get("username")
        
        if not username:
            return Response(
                message="Please specify 'username' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Username Search: {username}\n\n"
            
            if os.path.exists("/opt/sherlock"):
                message += f"**Tool**: Sherlock\n"
                message += f"Run: `python3 /opt/sherlock/sherlock/sherlock.py {username}`\n\n"
            
            # List of platforms to check
            platforms = [
                ("Twitter", f"https://twitter.com/{username}"),
                ("GitHub", f"https://github.com/{username}"),
                ("Instagram", f"https://instagram.com/{username}"),
                ("LinkedIn", f"https://linkedin.com/in/{username}"),
                ("Reddit", f"https://reddit.com/user/{username}"),
                ("Medium", f"https://medium.com/@{username}"),
                ("YouTube", f"https://youtube.com/@{username}"),
                ("TikTok", f"https://tiktok.com/@{username}")
            ]
            
            message += "**Platforms to Check**:\n"
            for platform, url in platforms:
                message += f"- {platform}: {url}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Username Search",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to search username: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _whois_lookup(self, **kwargs):
        """Perform WHOIS lookup"""
        domain = self.args.get("domain")
        
        if not domain:
            return Response(
                message="Please specify 'domain' parameter",
                break_loop=False
            )
        
        try:
            result = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            message = f"# WHOIS Lookup: {domain}\n\n"
            if result.returncode == 0:
                message += "```\n"
                message += result.stdout
                message += "\n```\n"
            else:
                message += f"Lookup failed: {result.stderr}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="WHOIS Lookup",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except subprocess.TimeoutExpired:
            error_msg = f"WHOIS lookup timed out for {domain}"
            PrintStyle(font_color="yellow", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
        except Exception as e:
            error_msg = f"Failed to perform WHOIS lookup: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _certificate_search(self, **kwargs):
        """Search certificate transparency logs"""
        domain = self.args.get("domain")
        
        if not domain:
            return Response(
                message="Please specify 'domain' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Certificate Transparency Search: {domain}\n\n"
            message += f"**crt.sh URL**: https://crt.sh/?q=%.{domain}\n\n"
            message += "This will show all SSL/TLS certificates issued for this domain and its subdomains.\n"
            message += "Useful for subdomain discovery.\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Certificate Search",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to search certificates: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _vulnerability_scan(self, **kwargs):
        """Perform vulnerability scanning"""
        target = self.args.get("target")
        scan_type = self.args.get("scan_type", "basic")
        
        if not target:
            return Response(
                message="Please specify 'target' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Vulnerability Scan: {target}\n\n"
            
            if os.path.exists("/usr/local/bin/nuclei"):
                message += f"**Tool**: Nuclei\n"
                message += f"Run: `nuclei -u {target}`\n\n"
            
            if os.path.exists("/usr/bin/nikto"):
                message += f"**Tool**: Nikto (web server scanner)\n"
                message += f"Run: `nikto -h {target}`\n\n"
            
            if os.path.exists("/usr/bin/nmap"):
                message += f"**Tool**: Nmap with vuln scripts\n"
                message += f"Run: `nmap --script vuln {target}`\n\n"
            
            message += "**Note**: Vulnerability scanning should only be performed on systems you own or have explicit permission to test.\n"
            
            PrintStyle(font_color="yellow", padding=True).print(message)
            self.agent.context.log.log(
                type="warning",
                heading="Vulnerability Scan",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to perform vulnerability scan: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _dns_enum(self, **kwargs):
        """Enumerate DNS records"""
        domain = self.args.get("domain")
        
        if not domain:
            return Response(
                message="Please specify 'domain' parameter",
                break_loop=False
            )
        
        try:
            message = f"# DNS Enumeration: {domain}\n\n"
            
            record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]
            
            for record_type in record_types:
                result = subprocess.run(
                    ["dig", "+short", domain, record_type],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    message += f"**{record_type} Records**:\n"
                    message += "```\n"
                    message += result.stdout
                    message += "```\n\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="DNS Enumeration",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to enumerate DNS: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _web_recon(self, **kwargs):
        """Perform web reconnaissance"""
        target = self.args.get("target")
        
        if not target:
            return Response(
                message="Please specify 'target' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Web Reconnaissance: {target}\n\n"
            
            if os.path.exists("/usr/local/bin/httpx"):
                message += f"**Tool**: HTTPx\n"
                message += f"Run: `echo {target} | httpx -silent -title -tech-detect -status-code`\n\n"
            
            if os.path.exists("/usr/bin/gobuster"):
                message += f"**Tool**: GoBuster (directory enumeration)\n"
                message += f"Run: `gobuster dir -u {target} -w /usr/share/wordlists/dirb/common.txt`\n\n"
            
            if os.path.exists("/usr/bin/wpscan"):
                message += f"**Tool**: WPScan (WordPress scanner)\n"
                message += f"Run: `wpscan --url {target}`\n\n"
            
            message += "**Manual Checks**:\n"
            message += f"- robots.txt: {target}/robots.txt\n"
            message += f"- sitemap.xml: {target}/sitemap.xml\n"
            message += f"- .git directory: {target}/.git/\n"
            message += f"- Security headers: Use securityheaders.com\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Web Reconnaissance",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to perform web reconnaissance: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _social_media_search(self, **kwargs):
        """Search social media for information"""
        query = self.args.get("query")
        platform = self.args.get("platform", "all")
        
        if not query:
            return Response(
                message="Please specify 'query' parameter",
                break_loop=False
            )
        
        try:
            message = f"# Social Media Search: {query}\n\n"
            
            if platform == "all" or platform == "twitter":
                message += f"**Twitter/X**: https://twitter.com/search?q={query.replace(' ', '%20')}\n"
            
            if platform == "all" or platform == "linkedin":
                message += f"**LinkedIn**: https://www.linkedin.com/search/results/all/?keywords={query.replace(' ', '%20')}\n"
            
            if platform == "all" or platform == "facebook":
                message += f"**Facebook**: https://www.facebook.com/search/top?q={query.replace(' ', '%20')}\n"
            
            if platform == "all" or platform == "instagram":
                message += f"**Instagram**: https://www.instagram.com/explore/tags/{query.replace(' ', '')}/\n"
            
            if platform == "all" or platform == "reddit":
                message += f"**Reddit**: https://www.reddit.com/search/?q={query.replace(' ', '%20')}\n"
            
            message += "\n**OSINT Tools for Social Media**:\n"
            if os.path.exists("/opt/spiderfoot"):
                message += "- SpiderFoot: `python3 /opt/spiderfoot/sf.py`\n"
            
            message += "- Social Analyzer: Available via pip (social-analyzer)\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Social Media Search",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to search social media: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
