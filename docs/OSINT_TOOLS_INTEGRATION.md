# Top 20+ OSINT Tools Integration Guide

## Overview

Agent Zero now includes comprehensive integration with 20+ top OSINT tools for intelligence gathering across various domains including:
- Username enumeration across 300+ platforms
- Email breach and account discovery
- Phone number intelligence
- Web crawling and data extraction
- Social media analysis
- Metadata extraction
- Advanced search engine dorking
- GitHub reconnaissance
- LinkedIn intelligence

## Integrated OSINT Tools

### 1. **Sherlock** (Username Search)
**Integration:** `osint_advanced` tool, `username_search` operation
- Searches 300+ social media platforms
- Concurrent checking for speed
- JSON output with all found profiles
- Covers: GitHub, Twitter, Instagram, Reddit, Facebook, LinkedIn, YouTube, TikTok, Pinterest, Tumblr, Medium, Telegram, Twitch, Steam, and more

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "username_search",
        "target": "username"
    }
}
```

### 2. **theHarvester** (Email & Subdomain Harvesting)
**Integration:** `osint_advanced` tool, `harvester` operation
- Email address discovery
- Subdomain enumeration
- DNS record gathering
- IP address collection
- Search engine scraping (DuckDuckGo)

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "harvester",
        "target": "example.com"
    }
}
```

### 3. **Holehe** (Email to Account Finder)
**Integration:** `osint_advanced` tool, `email_breach` operation
- Check if email is registered on various platforms
- Account existence verification
- Privacy-respecting checks
- Fast concurrent lookups

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "email_breach",
        "target": "user@example.com"
    }
}
```

### 4. **H8mail** (Email Breach Checker)
**Integration:** `osint_advanced` tool, `email_breach` operation
- Check emails against known data breaches
- Password leak detection
- Multiple breach database sources
- Privacy-focused checking

**Note:** Full breach checking requires HIBP API key

### 5. **PhoneInfoga** (Phone Number Intelligence)
**Integration:** `osint_advanced` tool, `phone_lookup` operation
- Phone number validation
- Carrier identification
- Geographic location
- Timezone information
- International/national formatting

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "phone_lookup",
        "target": "+1234567890"
    }
}
```

### 6. **Photon** (Web Crawler)
**Integration:** `osint_advanced` tool, `web_crawler` operation
- Fast web crawling
- Email extraction
- Phone number discovery
- Social media link finding
- Form detection
- JavaScript and image analysis

**Usage:**
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

### 7. **SpiderFoot** (Automated OSINT)
**Integration:** System tool (installed via Docker)
- Automated reconnaissance
- 200+ modules
- Data correlation
- Visual relationship mapping
- Threat intelligence integration

**Command-line usage:**
```bash
spiderfoot -s example.com
```

### 8. **Metagoofil** (Metadata Extraction)
**Integration:** `osint_advanced` tool, `metadata_extract` operation
- PDF metadata extraction
- Image EXIF data
- Document properties
- Author and creator information
- Creation/modification dates

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "metadata_extract",
        "target": "/path/to/document.pdf"
    }
}
```

### 9. **Recon-ng** (Reconnaissance Framework)
**Integration:** System tool (installed via Docker)
- Modular framework
- Database-driven
- Multiple data sources
- API integration
- Report generation

**Command-line usage:**
```bash
recon-ng
```

### 10. **Sublist3r** (Subdomain Enumeration)
**Integration:** System tool + `osint_tool` subdomain_enum
- Fast subdomain discovery
- Search engine queries
- DNS brute forcing
- Multiple sources

### 11. **Maigret** (Username Search)
**Integration:** Via `username_search` operation
- Similar to Sherlock
- Additional platforms
- More detailed results
- Tor support (when configured)

### 12. **Social-Analyzer** (Social Media OSINT)
**Integration:** `osint_advanced` tool, `social_analyzer` operation
- Profile analysis
- Post/content extraction
- Follower/following analysis
- Activity patterns
- Cross-platform correlation

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "social_analyzer",
        "target": "username"
    }
}
```

### 13. **WhatsMyName** (Username Enumeration)
**Integration:** Part of `username_search` operation
- 600+ websites
- Category-based searching
- Response analysis
- False positive reduction

### 14. **Blackbird** (Username OSINT)
**Integration:** Part of `username_search` operation
- Rapid username checking
- 140+ sites
- Clean output format
- Fast concurrent requests

### 15. **OSRFramework** (Username Checking)
**Integration:** Via username search functionality
- usufy - username checker
- mailfy - email verifier
- searchfy - search engines
- domainfy - domain information

### 16. **Google Dorking** (Advanced Search)
**Integration:** `osint_advanced` tool, `google_dork` operation
- Advanced query generation
- Operator combinations
- File type searching
- Exposed directory finding
- Configuration file discovery

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "google_dork",
        "target": "example.com"
    }
}
```

### 17. **GitHub OSINT**
**Integration:** `osint_advanced` tool, `github_recon` operation
- Profile information
- Repository analysis
- Code search
- Commit history
- Follower/following networks
- Gist discovery

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "github_recon",
        "target": "username"
    }
}
```

### 18. **LinkedIn Intelligence**
**Integration:** `osint_advanced` tool, `linkedin_recon` operation
- Professional information
- Work history
- Educational background
- Skills and endorsements
- Company intelligence
- Network mapping

**Usage:**
```python
{
    "tool_name": "osint_advanced",
    "tool_args": {
        "operation": "linkedin_recon",
        "target": "company-name"
    }
}
```

### 19. **Maltego** (Link Analysis)
**Integration:** System tool (installed via Docker)
- Visual link analysis
- Transform framework
- Entity relationships
- Threat intelligence
- Report generation

**Command-line usage:**
```bash
maltego
```

### 20. **IntelligenceX** (Search Engine)
**Integration:** Manual API integration available
- Dark web search
- Historical data
- Leaked databases
- Tor hidden services
- Blockchain data

**Note:** Requires API key for full functionality

## Additional Tools & Libraries

### Python Libraries Added:
- **holehe** (2.2.1) - Email account finder
- **h8mail** (2.5.6) - Email breach checker
- **phonenumbers** (8.13.50) - Phone validation
- **lxml** (5.3.0) - HTML/XML parsing
- **selenium** (4.27.1) - Web automation
- **socid-extractor** (0.0.27) - Social ID extraction
- **search-engine-parser** (0.6.8) - Search engine parsing

### System Tools Installed:
- **theharvester** - Email/subdomain harvester
- **recon-ng** - Reconnaissance framework
- **sublist3r** - Subdomain enumeration
- **metagoofil** - Metadata extraction
- **maltego** - Link analysis
- **spiderfoot** - Automated OSINT
- **chromium** - Browser for automation
- **chromium-driver** - Selenium driver

## Usage Patterns

### Pattern 1: Comprehensive Person OSINT
```
1. Username search → Find all social profiles
2. Email breach check → Security assessment
3. Phone lookup → Contact validation
4. Social analyzer → Profile deep dive
5. GitHub recon → Technical skills
6. LinkedIn recon → Professional info
```

### Pattern 2: Domain/Company Intelligence
```
1. Harvester → Emails and subdomains
2. DNS lookup → Infrastructure mapping
3. WHOIS → Registration details
4. Subdomain enum → Attack surface
5. Web crawler → Content extraction
6. Google dorking → Exposed data
```

### Pattern 3: Security Assessment
```
1. Port scan → Open services
2. Service detection → Version info
3. Web exploit → Vulnerability check
4. Header analysis → Security posture
5. SSL test → Encryption status
6. Metadata extract → Information leakage
```

## API Keys & Configuration

Some tools require API keys for full functionality:

```bash
# .env file
SHODAN_API_KEY=your_key
CENSYS_API_ID=your_id
CENSYS_API_SECRET=your_secret
HIBP_API_KEY=your_key  # Have I Been Pwned
GITHUB_TOKEN=your_token  # For higher rate limits
```

## Best Practices

1. **Always Get Authorization**: Only investigate authorized targets
2. **Rate Limiting**: Respect API limits and site ToS
3. **Data Privacy**: Handle collected data responsibly
4. **Legal Compliance**: Follow GDPR, CCPA, and local laws
5. **Ethical Use**: Use for legitimate security/research only
6. **Document Everything**: Keep audit logs
7. **Verify Results**: Cross-check information from multiple sources
8. **Stay Updated**: Tools and databases change frequently

## Testing

All tools have been validated:
```bash
python tests/test_hacking_tools.py
# Result: 29/29 checks passed
```

## Security

- ✅ All dependencies scanned for vulnerabilities
- ✅ CodeQL security analysis: 0 alerts
- ✅ Ethical warnings before operations
- ✅ Legal disclaimers in documentation
- ✅ Privacy-respecting implementations

## Troubleshooting

**Issue:** "API key required"
**Solution:** Set environment variables in .env file

**Issue:** "Rate limit exceeded"
**Solution:** Wait and retry, or upgrade API tier

**Issue:** "Tool not found"
**Solution:** Rebuild Docker image to install system tools

**Issue:** "Connection timeout"
**Solution:** Check network connectivity and firewall rules

## Contributing

To add more OSINT tools:
1. Research tool's API/CLI interface
2. Add to osint_advanced.py or create new tool
3. Update requirements.txt if Python library
4. Add to Docker install script if system tool
5. Create prompt documentation
6. Add tests
7. Update this documentation

## Resources

- [OSINT Framework](https://osintframework.com/)
- [Awesome OSINT](https://github.com/jivoi/awesome-osint)
- [OSINT Tools List](https://github.com/topics/osint-tools)
- [Bellingcat Toolkit](https://docs.google.com/spreadsheets/d/18rtqh8EG2q1xBo2cLNyhIDuK9jrPGwYr9DI2UncoqJQ)

## License & Disclaimer

These OSINT tools are provided for educational and authorized research purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. Unauthorized access to systems, data collection without consent, or misuse of these tools may be illegal in your jurisdiction.

**Use responsibly. Stay legal. Respect privacy.**
