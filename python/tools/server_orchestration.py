import asyncio
import json
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class ServerOrchestration(Tool):
    """
    Server orchestration tool for managing and executing commands across multiple servers.
    Supports SSH connections, parallel execution, and distributed operations.
    """

    async def execute(self, **kwargs):
        """
        Execute server orchestration operations.
        
        Supported operations:
        - ssh_connect: Connect to remote server via SSH
        - ssh_execute: Execute command on remote server(s)
        - parallel_execute: Execute commands in parallel across multiple servers
        - file_transfer: Transfer files to/from servers
        - tunnel_create: Create SSH tunnel
        """
        
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        
        if operation == "ssh_execute":
            response = await self.ssh_execute()
        elif operation == "parallel_execute":
            response = await self.parallel_execute()
        elif operation == "file_transfer":
            response = await self.file_transfer()
        elif operation == "tunnel_create":
            response = await self.tunnel_create()
        elif operation == "test_connection":
            response = await self.test_connection()
        else:
            response = self.agent.read_prompt(
                "fw.tool_error.md",
                error=f"Unknown operation: {operation}"
            )
        
        return Response(message=response, break_loop=False)
    
    async def ssh_execute(self) -> str:
        """Execute command on remote server via SSH"""
        host = self.args.get("host", "")
        username = self.args.get("username", "")
        password = self.args.get("password", "")
        key_file = self.args.get("key_file", "")
        command = self.args.get("command", "")
        port = self.args.get("port", "22")
        
        if not host or not username or not command:
            return "Error: host, username, and command are required"
        
        code = f"""
import json
import paramiko
import io

try:
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect
    connect_kwargs = {{
        'hostname': '{host}',
        'port': {port},
        'username': '{username}',
    }}
    
    if '{key_file}':
        connect_kwargs['key_filename'] = '{key_file}'
    elif '{password}':
        connect_kwargs['password'] = '{password}'
    
    ssh.connect(**connect_kwargs)
    
    # Execute command
    stdin, stdout, stderr = ssh.exec_command('{command}')
    
    output = {{
        'host': '{host}',
        'command': '{command}',
        'stdout': stdout.read().decode('utf-8', errors='ignore'),
        'stderr': stderr.read().decode('utf-8', errors='ignore'),
        'exit_status': stdout.channel.recv_exit_status()
    }}
    
    ssh.close()
    
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
    
    async def parallel_execute(self) -> str:
        """Execute commands in parallel across multiple servers"""
        servers = self.args.get("servers", [])  # List of server configs
        command = self.args.get("command", "")
        
        if not servers or not command:
            return "Error: servers list and command are required"
        
        # Convert servers list to string representation for code
        servers_str = str(servers).replace("'", "\\'")
        
        code = f"""
import json
import paramiko
import threading
from queue import Queue

def execute_on_server(server_config, command, results_queue):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {{
            'hostname': server_config['host'],
            'port': server_config.get('port', 22),
            'username': server_config['username'],
        }}
        
        if 'key_file' in server_config:
            connect_kwargs['key_filename'] = server_config['key_file']
        elif 'password' in server_config:
            connect_kwargs['password'] = server_config['password']
        
        ssh.connect(**connect_kwargs)
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        result = {{
            'host': server_config['host'],
            'success': True,
            'stdout': stdout.read().decode('utf-8', errors='ignore'),
            'stderr': stderr.read().decode('utf-8', errors='ignore'),
            'exit_status': stdout.channel.recv_exit_status()
        }}
        
        ssh.close()
        results_queue.put(result)
    except Exception as e:
        results_queue.put({{
            'host': server_config.get('host', 'unknown'),
            'success': False,
            'error': str(e)
        }})

try:
    servers = {servers_str}
    command = '{command}'
    
    results_queue = Queue()
    threads = []
    
    # Start threads for each server
    for server in servers:
        thread = threading.Thread(
            target=execute_on_server,
            args=(server, command, results_queue)
        )
        thread.start()
        threads.append(thread)
    
    # Wait for all threads
    for thread in threads:
        thread.join(timeout=30)
    
    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    
    output = {{
        'total_servers': len(servers),
        'command': command,
        'results': results
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
    
    async def file_transfer(self) -> str:
        """Transfer files to/from remote servers"""
        host = self.args.get("host", "")
        username = self.args.get("username", "")
        password = self.args.get("password", "")
        key_file = self.args.get("key_file", "")
        local_path = self.args.get("local_path", "")
        remote_path = self.args.get("remote_path", "")
        direction = self.args.get("direction", "upload")  # upload or download
        port = self.args.get("port", "22")
        
        if not all([host, username, local_path, remote_path]):
            return "Error: host, username, local_path, and remote_path are required"
        
        code = f"""
import json
import paramiko

try:
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect
    connect_kwargs = {{
        'hostname': '{host}',
        'port': {port},
        'username': '{username}',
    }}
    
    if '{key_file}':
        connect_kwargs['key_filename'] = '{key_file}'
    elif '{password}':
        connect_kwargs['password'] = '{password}'
    
    ssh.connect(**connect_kwargs)
    
    # Create SFTP client
    sftp = ssh.open_sftp()
    
    if '{direction}' == 'upload':
        sftp.put('{local_path}', '{remote_path}')
        message = f"Uploaded {{'{local_path}'}} to {{'{remote_path}'}}"
    else:
        sftp.get('{remote_path}', '{local_path}')
        message = f"Downloaded {{'{remote_path}'}} to {{'{local_path}'}}"
    
    sftp.close()
    ssh.close()
    
    output = {{
        'host': '{host}',
        'success': True,
        'message': message
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
    
    async def tunnel_create(self) -> str:
        """Create SSH tunnel"""
        host = self.args.get("host", "")
        username = self.args.get("username", "")
        password = self.args.get("password", "")
        key_file = self.args.get("key_file", "")
        local_port = self.args.get("local_port", "")
        remote_host = self.args.get("remote_host", "localhost")
        remote_port = self.args.get("remote_port", "")
        ssh_port = self.args.get("ssh_port", "22")
        
        if not all([host, username, local_port, remote_port]):
            return "Error: host, username, local_port, and remote_port are required"
        
        return f"""
SSH Tunnel Configuration:
- SSH Server: {host}:{ssh_port}
- Local Port: {local_port}
- Remote Host: {remote_host}
- Remote Port: {remote_port}

To create this tunnel manually, use:
ssh -L {local_port}:{remote_host}:{remote_port} {username}@{host} -p {ssh_port}

Note: SSH tunnels require persistent connections. Consider using screen/tmux or 
running the tunnel in a separate session for production use.
"""
    
    async def test_connection(self) -> str:
        """Test SSH connection to server"""
        host = self.args.get("host", "")
        username = self.args.get("username", "")
        password = self.args.get("password", "")
        key_file = self.args.get("key_file", "")
        port = self.args.get("port", "22")
        
        if not host or not username:
            return "Error: host and username are required"
        
        code = f"""
import json
import paramiko

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connect_kwargs = {{
        'hostname': '{host}',
        'port': {port},
        'username': '{username}',
    }}
    
    if '{key_file}':
        connect_kwargs['key_filename'] = '{key_file}'
    elif '{password}':
        connect_kwargs['password'] = '{password}'
    
    ssh.connect(**connect_kwargs, timeout=10)
    
    # Test basic command
    stdin, stdout, stderr = ssh.exec_command('echo "Connection successful"')
    test_output = stdout.read().decode('utf-8')
    
    ssh.close()
    
    output = {{
        'host': '{host}',
        'port': {port},
        'success': True,
        'message': 'Connection successful',
        'test_output': test_output.strip()
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{
        'host': '{host}',
        'port': {port},
        'success': False,
        'error': str(e)
    }}))
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
            type="server_orchestration",
            heading=f"icon://server {self.agent.agent_name}: Server Orchestration - {self.args.get('operation', 'unknown')}",
            content="",
            kvps=self.args,
        )
