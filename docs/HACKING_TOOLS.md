# Hacking Tools and OSINT Libraries - Documentation

## Overview

Agent Zero now includes comprehensive hacking and OSINT (Open Source Intelligence) capabilities, enabling it to perform security assessments, reconnaissance, and distributed server operations.

## ⚠️ Legal and Ethical Warning

**CRITICAL: These tools are for authorized security testing ONLY.**

- Only use on systems you own or have explicit written permission to test
- Unauthorized access to computer systems is ILLEGAL in most jurisdictions
- Violators may face criminal charges, fines, and imprisonment
- Always obtain proper authorization before conducting any security testing
- Follow responsible disclosure practices when vulnerabilities are found

## Installed Tools

### Network Reconnaissance
- **nmap**: Network exploration and security auditing
- **masscan**: High-speed port scanner
- **netcat**: TCP/IP swiss army knife
- **tcpdump**: Network packet analyzer

### Web Application Security
- **nikto**: Web server scanner
- **dirb/dirbuster**: Directory brute forcing
- **sqlmap**: SQL injection testing
- **wpscan**: WordPress security scanner

### Password & Hash Analysis
- **hashcat**: Advanced password recovery
- **john**: John the Ripper password cracker
- **hydra**: Network logon cracker

### OSINT & Information Gathering
- **whois**: Domain information lookup
- **dnsutils**: DNS query tools
- **Shodan API**: Internet-connected device search (requires API key)
- **Censys API**: Internet asset search (requires API key)
- **theHarvester**: Email and subdomain harvesting
- **Recon-ng**: Web reconnaissance framework
- **Sublist3r**: Subdomain enumeration
- **Metagoofil**: Metadata extraction
- **SpiderFoot**: Automated OSINT collection
- **Holehe**: Email to account finder
- **H8mail**: Email breach checking
- **PhoneInfoga**: Phone number intelligence

### Server Orchestration
- **paramiko**: SSH library for Python
- **fabric**: Remote execution and deployment
- **ansible**: IT automation (optional)

## New Agent Tools

### 1. network_recon

Perform network reconnaissance and scanning operations.

**Operations:**
- `port_scan`: Scan ports on target hosts
- `host_discovery`: Discover live hosts on network
- `service_detection`: Detect services and versions
- `os_detection`: Detect operating system
- `quick_scan`: Fast scan with basic information

**Example:**
```python
{
    "tool_name": "network_recon",
    "tool_args": {
        "operation": "port_scan",
        "target": "192.168.1.1",
        "ports": "1-1000"
    }
}
```

### 2. osint_tool

Gather open source intelligence from public sources.

**Operations:**
- `shodan_search`: Search Shodan for internet-connected devices
- `subdomain_enum`: Enumerate subdomains for a domain
- `dns_lookup`: Perform DNS lookups and queries
- `whois_lookup`: Perform WHOIS lookups
- `censys_search`: Search Censys database
- `passive_dns`: Perform passive DNS resolution

**Example:**
```python
{
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "subdomain_enum",
        "target": "example.com"
    }
}
```

### 3. server_orchestration

Manage and execute commands across multiple servers simultaneously.

**Operations:**
- `ssh_execute`: Execute command on remote server
- `parallel_execute`: Execute commands in parallel across multiple servers
- `file_transfer`: Transfer files to/from servers
- `tunnel_create`: Create SSH tunnel
- `test_connection`: Test SSH connection

**Example:**
```python
{
    "tool_name": "server_orchestration",
    "tool_args": {
        "operation": "parallel_execute",
        "servers": [
            {"host": "server1.com", "username": "admin", "password": "pass1"},
            {"host": "server2.com", "username": "admin", "key_file": "/path/key"}
        ],
        "command": "df -h"
    }
}
```

### 4. web_exploit

Web application security testing and vulnerability assessment.

**Operations:**
- `dir_enum`: Directory and file enumeration
- `sql_test`: SQL injection testing (detection only)
- `xss_test`: Cross-site scripting testing
- `header_analysis`: HTTP header security analysis
- `ssl_test`: SSL/TLS configuration testing
- `web_crawl`: Web application crawling

**Example:**
```python
{
    "tool_name": "web_exploit",
    "tool_args": {
        "operation": "header_analysis",
        "target": "https://example.com"
    }
}
```

### 5. crypto_tool

Cryptography and hash analysis tool.

**Operations:**
- `hash_identify`: Identify hash type based on length and format
- `encode`: Encode text (base64, hex, URL encoding)
- `decode`: Decode encoded text
- `generate_hash`: Generate hashes (MD5, SHA-1, SHA-256, SHA-512)
- `password_strength`: Analyze password strength and provide recommendations
- `hash_crack`: Attempt to crack hash using common wordlist (demo only)

**Example:**
```python
{
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "hash_identify",
        "hash": "5d41402abc4b2a76b9719d911017c592"
    }
}
```

### 6. osint_advanced

**NEW** - Advanced OSINT tool with 20+ integrated frameworks for comprehensive intelligence gathering.

**Operations:**
- `username_search`: Search username across 300+ social networks (Sherlock-style)
- `email_breach`: Check if email appears in data breaches (H8mail + Holehe)
- `phone_lookup`: Phone number intelligence (PhoneInfoga-style)
- `web_crawler`: Advanced web crawling for OSINT (Photon-style)
- `harvester`: Email and subdomain harvesting (theHarvester-style)
- `social_analyzer`: Comprehensive social media profile analysis
- `metadata_extract`: Extract metadata from documents (Metagoofil-style)
- `google_dork`: Generate advanced Google dork queries
- `github_recon`: GitHub profile and repository reconnaissance
- `linkedin_recon`: LinkedIn intelligence gathering guidance

**Example:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "username_search",
        "target": "johndoe"
    }
}
```

**Example:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "web_crawler",
        "target": "https://example.com",
        "max_depth": "2"
    }
}
```
        "operation": "header_analysis",
        "target": "https://example.com"
    }
}
```

## Python Libraries

The following Python libraries have been added to `requirements.txt`:

- **scapy**: Network packet manipulation
- **shodan**: Shodan API client
- **python-nmap**: Python wrapper for nmap
- **censys**: Censys API client
- **dnspython**: DNS toolkit
- **requests**: HTTP library
- **beautifulsoup4**: HTML/XML parser
- **pycryptodome**: Cryptographic functions
- **fabric**: Remote execution library
- **impacket**: Network protocols implementation
- **pwntools**: CTF and exploit development
- **pymetasploit3**: Metasploit RPC client

## Configuration

### API Keys

Set the following environment variables for enhanced OSINT capabilities:

```bash
# Shodan API
export SHODAN_API_KEY="your_shodan_api_key"

# Censys API
export CENSYS_API_ID="your_censys_id"
export CENSYS_API_SECRET="your_censys_secret"
```

Add these to your `.env` file:

```
SHODAN_API_KEY=your_shodan_api_key
CENSYS_API_ID=your_censys_id
CENSYS_API_SECRET=your_censys_secret
```

### SSH Configuration

For server orchestration, you can use:
- Password authentication
- Key-based authentication (recommended)
- SSH agent forwarding

## Usage Examples

### Example 1: Network Reconnaissance

```
User: "Scan my local network 192.168.1.0/24 and identify all live hosts"

Agent: Uses network_recon tool with host_discovery operation
Output: List of live hosts with IP addresses and hostnames
```

### Example 2: OSINT Gathering

```
User: "Find all subdomains for example.com"

Agent: Uses osint_tool with subdomain_enum operation
Output: List of discovered subdomains with IP addresses
```

### Example 3: Distributed Server Management

```
User: "Check disk space on all production servers"

Agent: Uses server_orchestration with parallel_execute operation
Output: Disk usage from all servers in parallel
```

### Example 4: Web Security Assessment

```
User: "Analyze the security headers of https://example.com"

Agent: Uses web_exploit with header_analysis operation
Output: Report of present and missing security headers
```

## Best Practices

1. **Always Get Authorization**: Never test systems without explicit permission
2. **Use Test Environments**: Practice on your own test environments first
3. **Rate Limiting**: Be mindful of scan rates to avoid overwhelming targets
4. **Logging**: Keep detailed logs of all security testing activities
5. **Responsible Disclosure**: If you find vulnerabilities, report them responsibly
6. **Stay Legal**: Know the laws in your jurisdiction regarding security testing

## Limitations

- SQL injection and XSS tests are detection-only (not exploitation)
- Some operations require additional API keys (Shodan, Censys)
- Network scanning requires appropriate network permissions
- Results should be verified manually for false positives
- Tools are educational and for authorized testing only

## Security Considerations

- All operations are logged for audit purposes
- Sensitive data (passwords, keys) should use environment variables
- Agent operates within Docker container for isolation
- Warning messages are displayed before potentially risky operations
- API keys should never be hardcoded in prompts

## Support and Resources

- Agent Zero Documentation: [docs/README.md](../docs/README.md)
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- SANS Penetration Testing: https://www.sans.org/penetration-testing/
- Bug Bounty Platforms: HackerOne, Bugcrowd, Intigriti

## Troubleshooting

**"nmap not found"**
- Ensure Docker image includes hacking tools installation script
- Rebuild Docker image with `install_hacking_tools.sh`

**"API key required"**
- Set appropriate environment variables in `.env` file
- Provide API key in tool arguments

**"Connection refused"**
- Check network connectivity
- Verify target is reachable
- Ensure firewall rules allow connections

**"Permission denied"**
- Verify SSH credentials
- Check file permissions for SSH keys
- Ensure user has sudo privileges if required

## Contributing

To add new hacking tools:

1. Add Python libraries to `requirements.txt`
2. Create new tool class in `python/tools/`
3. Add documentation prompt in `prompts/agent.system.tool.*.md`
4. Update Docker installation scripts if system packages needed
5. Test thoroughly in isolated environment
6. Document in this file

## License

These tools are provided for educational and authorized security testing purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations.
