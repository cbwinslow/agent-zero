import asyncio
import json
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class OsintTool(Tool):
    """
    Open Source Intelligence (OSINT) gathering tool.
    Supports various OSINT operations including domain enumeration,
    subdomain discovery, email harvesting, and threat intelligence.
    """

    async def execute(self, **kwargs):
        """
        Execute OSINT operations.
        
        Supported operations:
        - shodan_search: Search Shodan for internet-connected devices
        - subdomain_enum: Enumerate subdomains for a domain
        - dns_lookup: Perform DNS lookups and queries
        - whois_lookup: Perform WHOIS lookups
        - email_harvest: Harvest emails from domain (requires API keys)
        - threat_intel: Get threat intelligence data
        """
        
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        target = self.args.get("target", "")
        
        if not target:
            return Response(
                message=self.agent.read_prompt(
                    "fw.tool_error.md",
                    error="Target is required for OSINT operations"
                ),
                break_loop=False
            )
        
        # Security/Ethics warning
        warning_msg = """
⚠️  OSINT ETHICS: Use OSINT tools responsibly and ethically. 
- Only gather publicly available information
- Respect privacy and data protection laws
- Obtain proper authorization before testing
"""
        PrintStyle(font_color="yellow", padding=True).print(warning_msg)
        
        if operation == "shodan_search":
            response = await self.shodan_search(target)
        elif operation == "subdomain_enum":
            response = await self.subdomain_enumeration(target)
        elif operation == "dns_lookup":
            response = await self.dns_lookup(target)
        elif operation == "whois_lookup":
            response = await self.whois_lookup(target)
        elif operation == "censys_search":
            response = await self.censys_search(target)
        elif operation == "passive_dns":
            response = await self.passive_dns(target)
        else:
            response = self.agent.read_prompt(
                "fw.tool_error.md",
                error=f"Unknown operation: {operation}"
            )
        
        return Response(message=response, break_loop=False)
    
    async def shodan_search(self, query: str) -> str:
        """Search Shodan for internet-connected devices"""
        api_key = self.args.get("api_key", "")
        
        code = f"""
import json
import os

try:
    api_key = "{api_key}" or os.getenv('SHODAN_API_KEY', '')
    
    if not api_key:
        print(json.dumps({{
            'error': 'SHODAN_API_KEY required. Set via environment variable or api_key parameter.'
        }}))
    else:
        import shodan
        api = shodan.Shodan(api_key)
        
        # Search Shodan
        results = api.search('{query}')
        
        output = {{
            'total': results.get('total', 0),
            'matches': []
        }}
        
        for result in results.get('matches', [])[:10]:  # Limit to 10 results
            output['matches'].append({{
                'ip': result.get('ip_str', ''),
                'port': result.get('port', 0),
                'organization': result.get('org', ''),
                'hostnames': result.get('hostnames', []),
                'location': {{
                    'country': result.get('location', {{}}).get('country_name', ''),
                    'city': result.get('location', {{}}).get('city', '')
                }},
                'data': result.get('data', '')[:200]  # Truncate data
            }})
        
        print(json.dumps(output, indent=2))
except ImportError:
    print(json.dumps({{'error': 'shodan library not installed. Run: pip install shodan'}}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def subdomain_enumeration(self, domain: str) -> str:
        """Enumerate subdomains for a domain"""
        code = f"""
import json
import dns.resolver
import requests
from bs4 import BeautifulSoup

try:
    subdomains_found = []
    
    # Common subdomain wordlist
    common_subdomains = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 
        'webdisk', 'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 
        'ns', 'test', 'dev', 'staging', 'admin', 'api', 'blog', 'forum',
        'shop', 'store', 'cdn', 'app', 'mobile', 'portal', 'vpn', 'remote'
    ]
    
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2
    
    for sub in common_subdomains:
        try:
            subdomain = f"{{sub}}.{domain}"
            answers = resolver.resolve(subdomain, 'A')
            ips = [str(rdata) for rdata in answers]
            subdomains_found.append({{
                'subdomain': subdomain,
                'ips': ips
            }})
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            pass
        except Exception as e:
            pass
    
    output = {{
        'domain': '{domain}',
        'total_found': len(subdomains_found),
        'subdomains': subdomains_found
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def dns_lookup(self, domain: str) -> str:
        """Perform comprehensive DNS lookups"""
        record_types = self.args.get("record_types", "A,AAAA,MX,NS,TXT,SOA").split(",")
        
        code = f"""
import json
import dns.resolver

try:
    dns_records = {{}}
    resolver = dns.resolver.Resolver()
    
    record_types = {record_types}
    
    for record_type in record_types:
        try:
            answers = resolver.resolve('{domain}', record_type.strip())
            dns_records[record_type] = [str(rdata) for rdata in answers]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            dns_records[record_type] = []
        except Exception as e:
            dns_records[record_type] = [f"Error: {{str(e)}}"]
    
    output = {{
        'domain': '{domain}',
        'records': dns_records
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def whois_lookup(self, domain: str) -> str:
        """Perform WHOIS lookup"""
        code = f"""
import json
import subprocess

try:
    result = subprocess.run(
        ['whois', '{domain}'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    output = {{
        'domain': '{domain}',
        'whois_data': result.stdout if result.returncode == 0 else result.stderr
    }}
    
    print(json.dumps(output, indent=2))
except subprocess.TimeoutExpired:
    print(json.dumps({{'error': 'WHOIS lookup timed out'}}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def censys_search(self, query: str) -> str:
        """Search Censys for internet assets"""
        api_id = self.args.get("api_id", "")
        api_secret = self.args.get("api_secret", "")
        
        code = f"""
import json
import os

try:
    api_id = "{api_id}" or os.getenv('CENSYS_API_ID', '')
    api_secret = "{api_secret}" or os.getenv('CENSYS_API_SECRET', '')
    
    if not api_id or not api_secret:
        print(json.dumps({{
            'error': 'CENSYS_API_ID and CENSYS_API_SECRET required'
        }}))
    else:
        from censys.search import CensysHosts
        
        h = CensysHosts(api_id, api_secret)
        results = h.search('{query}', per_page=10)
        
        output = {{
            'query': '{query}',
            'results': []
        }}
        
        for result in results():
            output['results'].append({{
                'ip': result.get('ip', ''),
                'services': result.get('services', []),
                'location': result.get('location', {{}}),
                'autonomous_system': result.get('autonomous_system', {{}})
            }})
        
        print(json.dumps(output, indent=2))
except ImportError:
    print(json.dumps({{'error': 'censys library not installed. Run: pip install censys'}}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def passive_dns(self, domain: str) -> str:
        """Perform passive DNS resolution"""
        code = f"""
import json
import dns.resolver
import socket

try:
    output = {{
        'domain': '{domain}',
        'ipv4': [],
        'ipv6': [],
        'reverse_dns': {{}}
    }}
    
    resolver = dns.resolver.Resolver()
    
    # IPv4 lookup
    try:
        answers = resolver.resolve('{domain}', 'A')
        output['ipv4'] = [str(rdata) for rdata in answers]
    except:
        pass
    
    # IPv6 lookup
    try:
        answers = resolver.resolve('{domain}', 'AAAA')
        output['ipv6'] = [str(rdata) for rdata in answers]
    except:
        pass
    
    # Reverse DNS for IPv4
    for ip in output['ipv4'][:5]:  # Limit to first 5
        try:
            hostname = socket.gethostbyaddr(ip)
            output['reverse_dns'][ip] = hostname[0]
        except:
            output['reverse_dns'][ip] = 'No PTR record'
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    def get_log_object(self):
        return self.agent.context.log.log(
            type="osint",
            heading=f"icon://search {self.agent.agent_name}: OSINT - {self.args.get('operation', 'unknown')}",
            content="",
            kvps=self.args,
        )
