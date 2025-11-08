### network_recon

perform network reconnaissance and scanning operations
WARNING: only use on networks/systems you own or have permission to test
select "operation" arg: "port_scan" "host_discovery" "service_detection" "os_detection" "quick_scan"
specify "target" arg: IP address, hostname, or CIDR range
for port_scan: optional "ports" arg (default "1-1000")
output: JSON with scan results including open ports, services, versions
important: requires nmap to be installed on system
usage:

1. port scan

~~~json
{
    "thoughts": [
        "Need to scan target network...",
        "Using network_recon for port scanning...",
    ],
    "headline": "Scanning ports on target system",
    "tool_name": "network_recon",
    "tool_args": {
        "operation": "port_scan",
        "target": "192.168.1.1",
        "ports": "1-1000"
    }
}
~~~

2. host discovery

~~~json
{
    "thoughts": [
        "Need to find live hosts...",
        "Using host discovery...",
    ],
    "headline": "Discovering live hosts on network",
    "tool_name": "network_recon",
    "tool_args": {
        "operation": "host_discovery",
        "target": "192.168.1.0/24"
    }
}
~~~

3. service detection

~~~json
{
    "thoughts": [
        "Need to identify services...",
        "Using service detection...",
    ],
    "headline": "Detecting services and versions",
    "tool_name": "network_recon",
    "tool_args": {
        "operation": "service_detection",
        "target": "192.168.1.1"
    }
}
~~~

4. quick scan

~~~json
{
    "thoughts": [
        "Need quick overview...",
        "Using quick scan...",
    ],
    "headline": "Running quick network scan",
    "tool_name": "network_recon",
    "tool_args": {
        "operation": "quick_scan",
        "target": "192.168.1.1"
    }
}
~~~
