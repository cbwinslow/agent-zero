# OSINT and Security Tools Guide

## Overview

Agent Zero now includes comprehensive OSINT (Open Source Intelligence) and security testing capabilities through integrated tools and MCP servers.

## OSINT Tools Included

### Network Reconnaissance

#### Nmap
- **Description**: Network scanning and port discovery
- **Usage**: Via OSINT toolkit or Nmap MCP server
- **Example**: `"Scan ports 1-1000 on target.example.com"`

#### Masscan
- **Description**: Ultra-fast port scanner
- **Usage**: Direct command or via code execution
- **Example**: `"Use masscan to scan 192.168.1.0/24"`

#### Amass
- **Description**: Network mapping and subdomain discovery
- **Usage**: Via OSINT toolkit
- **Example**: `"Use Amass to discover subdomains for example.com"`

#### Subfinder
- **Description**: Fast subdomain discovery tool
- **Usage**: Via OSINT toolkit
- **Example**: `"Enumerate subdomains for target.com using subfinder"`

### Email & Contact Discovery

#### theHarvester
- **Description**: Email harvesting from public sources
- **Location**: `/opt/theHarvester`
- **Usage**: Via OSINT toolkit
- **Example**: `"Harvest emails for example.com"`

#### Hunter.io
- **Description**: Email finder and verification (API-based)
- **Usage**: Via Hunter MCP server
- **Requires**: HUNTER_API_KEY environment variable

### Domain & DNS Intelligence

#### WHOIS Lookup
- **Description**: Domain registration information
- **Usage**: Via OSINT toolkit or WHOIS MCP server
- **Example**: `"Perform WHOIS lookup on example.com"`

#### Certificate Transparency (crt.sh)
- **Description**: SSL/TLS certificate discovery for subdomain enumeration
- **Usage**: Via crt.sh MCP server or OSINT toolkit
- **Example**: `"Search certificate logs for example.com"`

#### DNS Enumeration
- **Description**: Enumerate DNS records (A, AAAA, MX, NS, TXT, SOA)
- **Usage**: Via OSINT toolkit
- **Example**: `"Enumerate DNS records for example.com"`

### Social Media Intelligence

#### Sherlock
- **Description**: Username search across 300+ social media platforms
- **Location**: `/opt/sherlock`
- **Usage**: Via OSINT toolkit
- **Example**: `"Search for username 'johndoe' across social media"`

#### Social Media OSINT
- **Platforms**: Twitter, LinkedIn, Instagram, Facebook, Reddit
- **Usage**: Via OSINT toolkit social_media_search method
- **Example**: `"Search Twitter for mentions of 'company XYZ'"`

### Web Reconnaissance

#### HTTPx
- **Description**: HTTP probe tool with tech detection
- **Usage**: Via OSINT toolkit
- **Example**: `"Probe HTTP services on discovered subdomains"`

#### GoBuster
- **Description**: Directory and file brute forcing
- **Usage**: Via OSINT toolkit
- **Example**: `"Perform directory enumeration on https://example.com"`

#### WPScan
- **Description**: WordPress security scanner
- **Usage**: Via OSINT toolkit
- **Example**: `"Scan WordPress site at https://example.com"`

#### Nikto
- **Description**: Web server vulnerability scanner
- **Usage**: Via OSINT toolkit
- **Example**: `"Scan web server at example.com for vulnerabilities"`

### Vulnerability Assessment

#### Nuclei
- **Description**: Vulnerability scanner with template engine
- **Usage**: Via OSINT toolkit
- **Example**: `"Run Nuclei scan on https://example.com"`

#### SQLMap
- **Description**: SQL injection detection and exploitation
- **Usage**: Direct command or code execution
- **Example**: `"Test URL for SQL injection vulnerabilities"`

### Threat Intelligence

#### Shodan
- **Description**: Search engine for Internet-connected devices
- **Usage**: Via Shodan MCP server
- **Requires**: SHODAN_API_KEY environment variable
- **Example**: `"Search Shodan for Apache servers in specific country"`

#### Censys
- **Description**: Search for hosts and certificates
- **Usage**: Via Censys MCP server
- **Requires**: CENSYS_API_ID and CENSYS_API_SECRET
- **Example**: `"Search Censys for SSL certificates for example.com"`

#### VirusTotal
- **Description**: Malware scanning and threat intelligence
- **Usage**: Via VirusTotal MCP server
- **Requires**: VIRUSTOTAL_API_KEY
- **Example**: `"Check URL reputation on VirusTotal"`

#### Have I Been Pwned
- **Description**: Data breach checking
- **Usage**: Via HIBP MCP server
- **Requires**: HIBP_API_KEY
- **Example**: `"Check if email@example.com has been in data breaches"`

#### SecurityTrails
- **Description**: Historical DNS and WHOIS data
- **Usage**: Via SecurityTrails MCP server
- **Requires**: SECURITYTRAILS_API_KEY
- **Example**: `"Get historical DNS records for example.com"`

#### IPInfo
- **Description**: IP geolocation and ASN lookup
- **Usage**: Via IPInfo MCP server
- **Requires**: IPINFO_TOKEN
- **Example**: `"Get geolocation for IP address 8.8.8.8"`

### OSINT Frameworks

#### Recon-ng
- **Description**: Web reconnaissance framework
- **Location**: `/opt/recon-ng`
- **Usage**: Interactive or scripted
- **Example**: `"Run Recon-ng module for domain intelligence"`

#### SpiderFoot
- **Description**: Automated OSINT collection
- **Location**: `/opt/spiderfoot`
- **Usage**: Web interface or API
- **Example**: `"Start SpiderFoot scan for target.com"`

## Using OSINT Toolkit in Agent Zero

### Basic Usage

The OSINT toolkit is available as a standard tool in Agent Zero:

```
agent: Use OSINT toolkit to enumerate subdomains for example.com
agent: Perform WHOIS lookup on example.com
agent: Search for username 'johndoe' across social media platforms
agent: Scan ports 80,443,8080 on target.example.com
```

### Advanced Workflows

#### Complete Domain Reconnaissance

```
1. WHOIS lookup
agent: Perform WHOIS lookup on target.com

2. Subdomain enumeration
agent: Enumerate subdomains for target.com using subfinder

3. Certificate transparency search
agent: Search certificate transparency logs for target.com

4. DNS enumeration
agent: Enumerate DNS records for discovered subdomains

5. Port scanning
agent: Scan common ports on discovered hosts

6. Web reconnaissance
agent: Perform web reconnaissance on active web servers
```

#### Email Intelligence Gathering

```
1. Email harvesting
agent: Harvest email addresses for company.com

2. Email validation
agent: Validate discovered email addresses using Hunter.io

3. Breach checking
agent: Check discovered emails for data breaches
```

#### Social Media Investigation

```
1. Username enumeration
agent: Search for username 'target_user' across social media

2. Social media profiling
agent: Search Twitter for mentions of 'company XYZ'

3. LinkedIn intelligence
agent: Search LinkedIn for employees of company XYZ
```

## Security Best Practices

### Legal and Ethical Considerations

1. **Authorization Required**: Only scan systems you own or have explicit written permission to test
2. **Respect Rate Limits**: Don't overwhelm targets with excessive requests
3. **Log Activities**: Maintain logs of all reconnaissance activities
4. **Data Handling**: Follow data protection regulations (GDPR, CCPA, etc.)
5. **Disclosure**: Report vulnerabilities responsibly

### Operational Security

1. **Use VPN/Proxy**: Route traffic through VPN for operational security
2. **Rotate IPs**: Use different IP addresses for different campaigns
3. **User Agent Strings**: Randomize or customize user agent strings
4. **Timing**: Introduce delays between requests to avoid detection
5. **Clean Up**: Remove traces and temporary files after operations

### API Key Security

1. **Never Commit Keys**: Don't commit API keys to version control
2. **Use Environment Variables**: Store keys in .env file or secrets manager
3. **Rotate Regularly**: Rotate API keys periodically
4. **Monitor Usage**: Track API usage for unauthorized access
5. **Principle of Least Privilege**: Use keys with minimum required permissions

## API Keys and Credentials

### Required Environment Variables

Add to `.env` file:

```bash
# OSINT & Security APIs
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_virustotal_key
HIBP_API_KEY=your_hibp_key
SECURITYTRAILS_API_KEY=your_securitytrails_key
CENSYS_API_ID=your_censys_id
CENSYS_API_SECRET=your_censys_secret
HUNTER_API_KEY=your_hunter_key
IPINFO_TOKEN=your_ipinfo_token

# General
GITHUB_TOKEN=your_github_token
```

### Obtaining API Keys

- **Shodan**: https://account.shodan.io/ (Free tier: 100 queries/month)
- **VirusTotal**: https://www.virustotal.com/gui/my-apikey (Free tier: 4 requests/min)
- **Have I Been Pwned**: https://haveibeenpwned.com/API/Key (Requires donation)
- **SecurityTrails**: https://securitytrails.com/corp/api (Free tier: 50 queries/month)
- **Censys**: https://search.censys.io/account/api (Free tier: 250 queries/month)
- **Hunter.io**: https://hunter.io/api (Free tier: 25 searches/month)
- **IPInfo**: https://ipinfo.io/signup (Free tier: 50k requests/month)

## Tool Reference

### OSINT Toolkit Methods

| Method | Description | Example |
|--------|-------------|---------|
| `subdomain_enum` | Enumerate subdomains | `method: subdomain_enum, domain: example.com` |
| `email_harvest` | Harvest email addresses | `method: email_harvest, domain: example.com` |
| `port_scan` | Scan network ports | `method: port_scan, target: example.com, ports: 1-1000` |
| `username_search` | Search username on social media | `method: username_search, username: johndoe` |
| `whois_lookup` | WHOIS domain lookup | `method: whois_lookup, domain: example.com` |
| `certificate_search` | Search certificate logs | `method: certificate_search, domain: example.com` |
| `vulnerability_scan` | Scan for vulnerabilities | `method: vulnerability_scan, target: example.com` |
| `dns_enum` | Enumerate DNS records | `method: dns_enum, domain: example.com` |
| `web_recon` | Web reconnaissance | `method: web_recon, target: https://example.com` |
| `social_media_search` | Search social media | `method: social_media_search, query: company name` |

### Command Line Tools

Directly accessible via code execution tool:

```bash
# Nmap scans
nmap -sS -p 1-65535 target.com
nmap -sV -p 80,443 target.com
nmap --script vuln target.com

# Subfinder
subfinder -d example.com -silent

# Amass
amass enum -passive -d example.com

# theHarvester
python3 /opt/theHarvester/theHarvester.py -d example.com -b all

# Sherlock
python3 /opt/sherlock/sherlock/sherlock.py username

# Masscan
masscan -p1-65535 192.168.1.0/24 --rate=1000

# GoBuster
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt

# WPScan
wpscan --url https://example.com

# Nikto
nikto -h example.com

# Nuclei
nuclei -u https://example.com

# SQLMap
sqlmap -u "https://example.com/page?id=1" --batch
```

## Integration with GitHub

### Backup OSINT Results

Use GitHub integration tool to backup reconnaissance data:

```
agent: Backup OSINT results to GitHub repository myuser/osint-results
```

### Collaborative Intelligence

- Store findings in GitHub for team collaboration
- Use GitHub Issues to track discovered vulnerabilities
- Create knowledge base repositories with OSINT data

## Automation Examples

### Automated Reconnaissance Script

Create a comprehensive reconnaissance workflow:

```python
# Domain reconnaissance workflow
domains = ["target1.com", "target2.com", "target3.com"]

for domain in domains:
    # 1. WHOIS
    agent.execute_tool("osint_toolkit", method="whois_lookup", domain=domain)
    
    # 2. Subdomain enum
    agent.execute_tool("osint_toolkit", method="subdomain_enum", domain=domain)
    
    # 3. DNS enum
    agent.execute_tool("osint_toolkit", method="dns_enum", domain=domain)
    
    # 4. Certificate search
    agent.execute_tool("osint_toolkit", method="certificate_search", domain=domain)
    
    # 5. Email harvest
    agent.execute_tool("osint_toolkit", method="email_harvest", domain=domain)
```

### Continuous Monitoring

Set up scheduled tasks for ongoing monitoring:

```
agent: Create a scheduled task to monitor example.com for new subdomains daily
agent: Set up alerts for new certificates issued for example.com
agent: Monitor data breaches for company email addresses
```

## Reporting

### Generate OSINT Reports

```
agent: Generate a comprehensive OSINT report for target.com including:
- Domain information
- Discovered subdomains
- DNS records
- Open ports
- Email addresses
- Social media presence
```

### Export Results

- Export to JSON for programmatic access
- Generate Markdown reports for documentation
- Create CSV files for spreadsheet analysis
- Backup to GitHub for version control

## Troubleshooting

### Tool Not Found

If a tool is not available:
1. Check if Docker image is up to date
2. Rebuild Docker image: `docker build -t agent-zero .`
3. Verify tool installation in `/opt/` directory

### API Rate Limiting

If experiencing rate limits:
1. Check API usage quotas
2. Implement delays between requests
3. Upgrade to paid API tiers
4. Use multiple API keys with rotation

### Permission Errors

For tools requiring root:
1. Verify Docker container has necessary permissions
2. Use sudo for commands requiring elevated privileges
3. Check file permissions in `/opt/` directories

### Network Issues

If unable to reach targets:
1. Verify network connectivity
2. Check firewall rules
3. Ensure DNS resolution works
4. Try different network interfaces

## Additional Resources

- [OSINT Framework](https://osintframework.com/)
- [Kali Linux Tools](https://www.kali.org/tools/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Penetration Testing Execution Standard](http://www.pentest-standard.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Responsible Disclosure

When discovering vulnerabilities:

1. **Document Findings**: Record all details including steps to reproduce
2. **Assess Severity**: Rate vulnerability using CVSS or similar framework
3. **Contact Organization**: Reach out through security contact or bug bounty program
4. **Allow Time**: Give organization reasonable time to patch (typically 90 days)
5. **Coordinate Disclosure**: Work with organization on disclosure timing
6. **Public Disclosure**: Only disclose publicly after patch is available

## Legal Disclaimer

The OSINT and security tools in Agent Zero are provided for:
- Educational purposes
- Security research on owned systems
- Authorized penetration testing
- Compliance and security auditing

Users are responsible for ensuring their activities comply with:
- Local, state, and federal laws
- Computer Fraud and Abuse Act (CFAA) in the US
- Computer Misuse Act in the UK
- Equivalent laws in other jurisdictions

Unauthorized access to computer systems is illegal. Always obtain proper authorization before conducting security testing.
