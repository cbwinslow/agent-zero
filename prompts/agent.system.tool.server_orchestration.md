### server_orchestration

manage and execute commands across multiple servers
perform distributed operations via SSH
select "operation" arg: "ssh_execute" "parallel_execute" "file_transfer" "tunnel_create" "test_connection"
specify connection details: "host" "username" "password" or "key_file"
for parallel_execute: provide "servers" list with server configs
output: JSON with execution results
usage:

1. ssh execute single command

~~~json
{
    "thoughts": [
        "Need to execute command on remote server...",
        "Using SSH to connect...",
    ],
    "headline": "Executing command on remote server",
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "ssh_execute",
        "host": "192.168.1.10",
        "username": "admin",
        "password": "secret",
        "command": "uptime",
        "port": "22"
    }
}
~~~

2. parallel execution on multiple servers

~~~json
{
    "thoughts": [
        "Need to run command on multiple servers...",
        "Using parallel execution...",
    ],
    "headline": "Executing command in parallel across servers",
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "parallel_execute",
        "servers": [
            {"host": "server1.com", "username": "admin", "password": "pass1"},
            {"host": "server2.com", "username": "admin", "key_file": "/path/to/key"}
        ],
        "command": "df -h"
    }
}
~~~

3. file transfer

~~~json
{
    "thoughts": [
        "Need to transfer file to server...",
        "Using SFTP...",
    ],
    "headline": "Transferring file to remote server",
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "file_transfer",
        "host": "192.168.1.10",
        "username": "admin",
        "password": "secret",
        "local_path": "/local/file.txt",
        "remote_path": "/remote/file.txt",
        "direction": "upload"
    }
}
~~~

4. test connection

~~~json
{
    "thoughts": [
        "Need to verify SSH connectivity...",
        "Testing connection...",
    ],
    "headline": "Testing SSH connection to server",
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "test_connection",
        "host": "192.168.1.10",
        "username": "admin",
        "password": "secret"
    }
}
~~~

5. create tunnel

~~~json
{
    "thoughts": [
        "Need SSH tunnel for port forwarding...",
        "Creating tunnel configuration...",
    ],
    "headline": "Setting up SSH tunnel",
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "tunnel_create",
        "host": "192.168.1.10",
        "username": "admin",
        "password": "secret",
        "local_port": "8080",
        "remote_host": "localhost",
        "remote_port": "80"
    }
}
~~~
