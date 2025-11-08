# Hacking Tools Quick Start Guide

This guide provides quick examples to get you started with Agent Zero's hacking and OSINT tools.

## Prerequisites

1. Ensure Docker image is rebuilt with hacking tools:
   ```bash
   docker build -t agent0ai/agent-zero .
   ```

2. Install Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set API keys in `.env`:
   ```bash
   SHODAN_API_KEY=your_key_here
   CENSYS_API_ID=your_id_here
   CENSYS_API_SECRET=your_secret_here
   ```

## Quick Examples

### Network Reconnaissance

**Example 1: Quick scan of a host**
```
User: "Scan 192.168.1.1 for open ports"

Agent Response:
- Uses network_recon tool with quick_scan operation
- Shows open ports and basic services
```

**Example 2: Discover all hosts on network**
```
User: "Find all live hosts on 192.168.1.0/24 network"

Agent Response:
- Uses network_recon tool with host_discovery operation
- Lists all active IP addresses with hostnames
```

**Example 3: Deep service detection**
```
User: "Identify all services running on 192.168.1.10"

Agent Response:
- Uses network_recon tool with service_detection operation
- Shows detailed service versions and products
```

### OSINT Operations

**Example 1: Subdomain discovery**
```
User: "Find all subdomains for example.com"

Agent Response:
- Uses osint_tool with subdomain_enum operation
- Lists discovered subdomains with IPs
```

**Example 2: DNS reconnaissance**
```
User: "Get all DNS records for example.com"

Agent Response:
- Uses osint_tool with dns_lookup operation
- Shows A, AAAA, MX, NS, TXT, SOA records
```

**Example 3: Domain information**
```
User: "Get WHOIS information for example.com"

Agent Response:
- Uses osint_tool with whois_lookup operation
- Shows registration details, nameservers, etc.
```

**Example 4: Shodan search (requires API key)**
```
User: "Search Shodan for Apache servers in New York"

Agent Response:
- Uses osint_tool with shodan_search operation
- Shows internet-connected devices matching query
```

### Server Orchestration

**Example 1: Execute command on remote server**
```
User: "Check disk space on server1.example.com"

Agent Response:
- Uses server_orchestration with ssh_execute
- Connects via SSH and runs df -h command
```

**Example 2: Parallel execution**
```
User: "Get uptime from all production servers"

Agent Response:
- Uses server_orchestration with parallel_execute
- Runs uptime command on all servers simultaneously
```

**Example 3: File transfer**
```
User: "Upload config.json to /etc/app/ on server1.example.com"

Agent Response:
- Uses server_orchestration with file_transfer
- Transfers file via SFTP
```

### Web Security Testing

**Example 1: Security header analysis**
```
User: "Check security headers on https://example.com"

Agent Response:
- Uses web_exploit with header_analysis
- Shows present and missing security headers
```

**Example 2: Directory enumeration**
```
User: "Find hidden directories on https://example.com"

Agent Response:
- Uses web_exploit with dir_enum
- Discovers common paths like /admin, /api, etc.
```

**Example 3: SSL/TLS assessment**
```
User: "Check SSL configuration on https://example.com"

Agent Response:
- Uses web_exploit with ssl_test
- Shows certificate details, protocol, cipher suite
```

**Example 4: Basic vulnerability detection**
```
User: "Test https://example.com/search?q=test for XSS"

Agent Response:
- Uses web_exploit with xss_test
- Checks if payloads are reflected in response
```

### Cryptography Operations

**Example 1: Identify hash type**
```
User: "What type of hash is 5d41402abc4b2a76b9719d911017c592?"

Agent Response:
- Uses crypto_tool with hash_identify
- Identifies as MD5 (128-bit, 32 characters)
```

**Example 2: Encode/decode data**
```
User: "Encode 'hello world' to base64"

Agent Response:
- Uses crypto_tool with encode operation
- Returns: aGVsbG8gd29ybGQ=
```

**Example 3: Generate hashes**
```
User: "Generate SHA-256 hash of 'password123'"

Agent Response:
- Uses crypto_tool with generate_hash
- Shows hash: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
```

**Example 4: Password strength analysis**
```
User: "How strong is the password 'MyP@ssw0rd123'?"

Agent Response:
- Uses crypto_tool with password_strength
- Shows score, characteristics, recommendations
```

## Advanced Scenarios

### Scenario 1: Complete reconnaissance workflow
```
User: "Perform full reconnaissance on my test domain testdomain.com"

Agent Workflow:
1. DNS lookup to get IP addresses
2. WHOIS lookup for domain info
3. Subdomain enumeration
4. Port scan on main IP
5. Service detection on open ports
6. Web security header analysis
7. SSL certificate check
8. Summary report with findings
```

### Scenario 2: Multi-server management
```
User: "Deploy update.sh to 5 servers and execute it"

Agent Workflow:
1. Test SSH connections to all servers
2. Transfer update.sh via SFTP
3. Execute script in parallel
4. Collect results from each server
5. Report success/failure status
```

### Scenario 3: Security assessment
```
User: "Assess security of https://testsite.example.com"

Agent Workflow:
1. Header security analysis
2. SSL/TLS configuration check
3. Directory enumeration
4. Basic SQL injection tests
5. XSS vulnerability detection
6. Generate security report
7. Provide remediation recommendations
```

## Tips for Best Results

1. **Be Specific**: Provide clear targets and operations
2. **Authorization**: Always mention "my" or "test" to indicate you have permission
3. **API Keys**: Set environment variables for Shodan/Censys for best results
4. **Credentials**: Use SSH keys instead of passwords for server operations
5. **Iteration**: Agent can chain multiple tools for complex workflows
6. **Safety**: Agent will warn before potentially dangerous operations

## Common Issues

### "nmap not found"
- Solution: Rebuild Docker image to install system tools

### "API key required"
- Solution: Set SHODAN_API_KEY or CENSYS_API_ID in .env file

### "Connection refused"
- Solution: Check firewall rules and network connectivity

### "Permission denied"
- Solution: Verify SSH credentials and user permissions

## Legal Reminder

⚠️ **ALWAYS**:
- Get written authorization before testing
- Test only on systems you own or have permission for
- Follow responsible disclosure for vulnerabilities
- Keep audit logs of all activities

❌ **NEVER**:
- Test systems without permission
- Use these tools maliciously
- Share findings publicly without authorization
- Ignore local laws and regulations

## Getting Help

- Full documentation: [docs/HACKING_TOOLS.md](./HACKING_TOOLS.md)
- Report issues: https://github.com/agent0ai/agent-zero/issues
- Join community: https://discord.gg/B8KZKNsPpj

## Next Steps

1. Try the examples above in your environment
2. Read the full documentation for advanced features
3. Create custom workflows combining multiple tools
4. Extend tools with your own specialized operations
5. Share your experience with the community

Happy (ethical) hacking! 🔐
