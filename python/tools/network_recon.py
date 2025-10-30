import asyncio
import json
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class NetworkRecon(Tool):
    """
    Network reconnaissance tool for scanning and discovering network assets.
    Supports various scanning techniques including port scanning, service detection,
    and host discovery using nmap and scapy.
    """

    async def execute(self, **kwargs):
        """
        Execute network reconnaissance operations.
        
        Supported operations:
        - port_scan: Scan ports on target hosts
        - host_discovery: Discover live hosts on network
        - service_detection: Detect services and versions
        - os_detection: Detect operating system
        """
        
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        target = self.args.get("target", "")
        
        if not target:
            return Response(
                message=self.agent.read_prompt(
                    "fw.tool_error.md",
                    error="Target is required for network reconnaissance"
                ),
                break_loop=False
            )
        
        # Security check: Warn about legal implications
        warning_msg = """
⚠️  WARNING: Network scanning should only be performed on networks and systems 
you own or have explicit permission to test. Unauthorized scanning may be illegal.
"""
        PrintStyle(font_color="red", padding=True).print(warning_msg)
        
        if operation == "port_scan":
            response = await self.port_scan(target)
        elif operation == "host_discovery":
            response = await self.host_discovery(target)
        elif operation == "service_detection":
            response = await self.service_detection(target)
        elif operation == "os_detection":
            response = await self.os_detection(target)
        elif operation == "quick_scan":
            response = await self.quick_scan(target)
        else:
            response = self.agent.read_prompt(
                "fw.tool_error.md",
                error=f"Unknown operation: {operation}"
            )
        
        return Response(message=response, break_loop=False)
    
    async def port_scan(self, target: str) -> str:
        """Scan ports on target using nmap"""
        ports = self.args.get("ports", "1-1000")
        
        code = f"""
import nmap
import json

try:
    nm = nmap.PortScanner()
    result = nm.scan('{target}', '{ports}', arguments='-sV')
    
    output = {{
        'scan_info': result.get('nmap', {{}}).get('scaninfo', {{}}),
        'hosts': {{}}
    }}
    
    for host in result.get('scan', {{}}).keys():
        host_info = result['scan'][host]
        output['hosts'][host] = {{
            'state': host_info.get('status', {{}}).get('state', 'unknown'),
            'protocols': {{}}
        }}
        
        for proto in host_info.get('tcp', {{}}).keys():
            port_info = host_info['tcp'][proto]
            output['hosts'][host]['protocols'][proto] = {{
                'state': port_info.get('state', 'unknown'),
                'name': port_info.get('name', 'unknown'),
                'product': port_info.get('product', ''),
                'version': port_info.get('version', '')
            }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f"Error during port scan: {{str(e)}}")
"""
        
        # Execute using code execution tool
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
    
    async def host_discovery(self, target: str) -> str:
        """Discover live hosts on network"""
        code = f"""
import nmap
import json

try:
    nm = nmap.PortScanner()
    result = nm.scan(hosts='{target}', arguments='-sn')
    
    hosts = []
    for host in result.get('scan', {{}}).keys():
        host_info = result['scan'][host]
        hosts.append({{
            'ip': host,
            'hostname': host_info.get('hostnames', [{{}}])[0].get('name', ''),
            'state': host_info.get('status', {{}}).get('state', 'unknown'),
            'reason': host_info.get('status', {{}}).get('reason', '')
        }})
    
    output = {{
        'total_hosts': len(hosts),
        'hosts': hosts
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f"Error during host discovery: {{str(e)}}")
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
    
    async def service_detection(self, target: str) -> str:
        """Detect services and versions"""
        code = f"""
import nmap
import json

try:
    nm = nmap.PortScanner()
    result = nm.scan('{target}', arguments='-sV --version-intensity 5')
    
    services = []
    for host in result.get('scan', {{}}).keys():
        host_info = result['scan'][host]
        for proto in ['tcp', 'udp']:
            if proto in host_info:
                for port, port_info in host_info[proto].items():
                    services.append({{
                        'host': host,
                        'port': port,
                        'protocol': proto,
                        'state': port_info.get('state', 'unknown'),
                        'service': port_info.get('name', 'unknown'),
                        'product': port_info.get('product', ''),
                        'version': port_info.get('version', ''),
                        'extrainfo': port_info.get('extrainfo', '')
                    }})
    
    output = {{
        'total_services': len(services),
        'services': services
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f"Error during service detection: {{str(e)}}")
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
    
    async def os_detection(self, target: str) -> str:
        """Detect operating system"""
        code = f"""
import nmap
import json

try:
    nm = nmap.PortScanner()
    result = nm.scan('{target}', arguments='-O')
    
    os_info = []
    for host in result.get('scan', {{}}).keys():
        host_info = result['scan'][host]
        if 'osmatch' in host_info:
            for os_match in host_info['osmatch']:
                os_info.append({{
                    'host': host,
                    'name': os_match.get('name', 'unknown'),
                    'accuracy': os_match.get('accuracy', 0),
                    'line': os_match.get('line', 0)
                }})
    
    output = {{
        'os_detections': os_info
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f"Error during OS detection: {{str(e)}}")
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
    
    async def quick_scan(self, target: str) -> str:
        """Perform a quick scan with basic information"""
        code = f"""
import nmap
import json

try:
    nm = nmap.PortScanner()
    result = nm.scan('{target}', arguments='-F')  # Fast scan
    
    output = {{
        'scan_time': result.get('nmap', {{}}).get('scanstats', {{}}).get('elapsed', ''),
        'hosts': {{}}
    }}
    
    for host in result.get('scan', {{}}).keys():
        host_info = result['scan'][host]
        output['hosts'][host] = {{
            'state': host_info.get('status', {{}}).get('state', 'unknown'),
            'open_ports': []
        }}
        
        if 'tcp' in host_info:
            for port, port_info in host_info['tcp'].items():
                if port_info.get('state') == 'open':
                    output['hosts'][host]['open_ports'].append({{
                        'port': port,
                        'service': port_info.get('name', 'unknown')
                    }})
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f"Error during quick scan: {{str(e)}}")
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
            type="network_recon",
            heading=f"icon://radar {self.agent.agent_name}: Network Reconnaissance - {self.args.get('operation', 'unknown')}",
            content="",
            kvps=self.args,
        )
