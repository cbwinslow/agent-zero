# MCP Server Configuration Guide

## Quick Start

### Step 1: Enable MCP Servers

Edit `conf/mcp_servers_available.json` to enable the servers you want to use:

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Step 2: Set Up API Keys

Add your API keys to `.env` file:

```bash
# Copy example.env to .env
cp example.env .env

# Edit .env and add your keys
GITHUB_TOKEN=ghp_your_token_here
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_virustotal_key
```

### Step 3: Restart Agent Zero

```bash
# If using Docker
docker restart agent-zero

# If running locally
python run_ui.py
```

## VS Code Integration

### Export from VS Code

1. Open VS Code settings (Ctrl+,)
2. Search for "MCP"
3. Copy your MCP configuration
4. Paste into `conf/mcp_servers_vscode.json`

### Import to VS Code

1. Copy `conf/mcp_servers_vscode.json`
2. Open VS Code settings
3. Paste into MCP configuration section
4. Restart VS Code

## Configuration Workflow

### 1. Basic Setup

For general development and GitHub integration:

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "git": {
      "enabled": true
    },
    "filesystem": {
      "enabled": true
    }
  }
}
```

### 2. OSINT Setup

For security research and reconnaissance:

```json
{
  "mcpServers": {
    "osint-toolkit": {
      "enabled": true
    },
    "nmap": {
      "enabled": true
    },
    "shodan": {
      "enabled": true,
      "env": {
        "SHODAN_API_KEY": "${SHODAN_API_KEY}"
      }
    },
    "virustotal": {
      "enabled": true,
      "env": {
        "VIRUSTOTAL_API_KEY": "${VIRUSTOTAL_API_KEY}"
      }
    }
  }
}
```

### 3. Cloud & DevOps Setup

For infrastructure management:

```json
{
  "mcpServers": {
    "docker": {
      "enabled": true
    },
    "kubernetes": {
      "enabled": true,
      "env": {
        "KUBECONFIG": "${KUBECONFIG}"
      }
    },
    "aws-kb": {
      "enabled": true,
      "env": {
        "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
        "AWS_REGION": "${AWS_REGION}"
      }
    }
  }
}
```

### 4. Full Stack Development

For comprehensive development work:

```json
{
  "mcpServers": {
    "github": {"enabled": true, "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}},
    "gitlab": {"enabled": true, "env": {"GITLAB_TOKEN": "${GITLAB_TOKEN}"}},
    "postgres": {"enabled": true, "env": {"POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"}},
    "redis": {"enabled": true, "env": {"REDIS_URL": "${REDIS_URL}"}},
    "docker": {"enabled": true},
    "linear": {"enabled": true, "env": {"LINEAR_API_KEY": "${LINEAR_API_KEY}"}},
    "slack": {"enabled": true, "env": {"SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"}}
  }
}
```

## API Key Management

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** (quarterly recommended)
4. **Use least privilege** - give keys minimum required permissions
5. **Monitor usage** - watch for unusual API usage patterns

### Key Storage Options

#### Option 1: .env File (Development)

```bash
# .env
GITHUB_TOKEN=ghp_...
SHODAN_API_KEY=...
```

#### Option 2: System Environment (Production)

```bash
# ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_..."
export SHODAN_API_KEY="..."
```

#### Option 3: Docker Secrets (Container)

```yaml
# docker-compose.yml
services:
  agent-zero:
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - SHODAN_API_KEY=${SHODAN_API_KEY}
```

#### Option 4: Secret Manager (Enterprise)

Use AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault for production deployments.

## MCP Server Categories

### Core Infrastructure

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| filesystem | File operations | No |
| git | Git operations | No |
| shell | Shell commands | No |
| time | Time operations | No |

### Code Hosting

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| github | GitHub API | GITHUB_TOKEN |
| gitlab | GitLab API | GITLAB_TOKEN |
| azure-devops | Azure DevOps | AZURE_DEVOPS_TOKEN |

### Databases

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| postgres | PostgreSQL | CONNECTION_STRING |
| mysql | MySQL | CONNECTION_STRING |
| mongodb | MongoDB | MONGODB_URI |
| redis | Redis | REDIS_URL |
| sqlite | SQLite | No (file path) |

### OSINT & Security

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| osint-toolkit | Comprehensive OSINT | No |
| nmap | Network scanning | No |
| crt-sh | Certificate logs | No |
| shodan | Device search | SHODAN_API_KEY |
| censys | Infrastructure search | CENSYS_API_ID/SECRET |
| virustotal | Malware analysis | VIRUSTOTAL_API_KEY |
| haveibeenpwned | Breach checking | HIBP_API_KEY |
| securitytrails | DNS history | SECURITYTRAILS_API_KEY |
| ipinfo | IP geolocation | IPINFO_TOKEN |
| hunter | Email finder | HUNTER_API_KEY |

### Cloud & DevOps

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| docker | Container management | No |
| kubernetes | K8s operations | KUBECONFIG |
| aws-kb | AWS Knowledge Base | AWS credentials |

### Communication

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| slack | Slack integration | SLACK_BOT_TOKEN |

### Project Management

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| linear | Linear PM | LINEAR_API_KEY |
| jira | Jira integration | JIRA credentials |
| asana | Asana PM | ASANA_ACCESS_TOKEN |
| notion | Notion workspace | NOTION_TOKEN |

### Search & Research

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| brave-search | Web search | BRAVE_API_KEY |
| web-search | Multi-provider search | No |
| arxiv | Academic papers | No |
| youtube-transcript | Video transcripts | No |

### Monitoring

| Server | Purpose | Auth Required |
|--------|---------|--------------|
| sentry | Error tracking | SENTRY_DSN |

## Troubleshooting

### Server Won't Start

**Problem**: MCP server fails to start

**Solutions**:
1. Check if required command is installed (`npx`, `python`)
2. Verify API keys are set correctly
3. Check server logs in Agent Zero UI
4. Ensure environment variables are loaded

### Authentication Errors

**Problem**: "Unauthorized" or "Invalid API key"

**Solutions**:
1. Verify API key is correct
2. Check if key has expired
3. Ensure key has required permissions
4. Verify environment variable name matches exactly

### Rate Limiting

**Problem**: "Too many requests" or "Rate limit exceeded"

**Solutions**:
1. Check API usage limits
2. Implement exponential backoff
3. Upgrade to paid API tier
4. Use multiple API keys with rotation

### Configuration Errors

**Problem**: Server not appearing in Agent Zero

**Solutions**:
1. Verify JSON syntax in config file
2. Check `enabled: true` is set
3. Restart Agent Zero after config changes
4. Check logs for configuration parsing errors

## Advanced Configuration

### Custom MCP Server Paths

Override default paths in configuration:

```json
{
  "mcpServers": {
    "custom-server": {
      "command": "python",
      "args": ["/custom/path/to/server.py"],
      "enabled": true
    }
  }
}
```

### Environment-Specific Configs

Use different configs for different environments:

```bash
# Development
cp conf/mcp_servers_dev.json conf/mcp_servers_available.json

# Production
cp conf/mcp_servers_prod.json conf/mcp_servers_available.json
```

### Conditional Server Loading

Load servers based on conditions:

```json
{
  "mcpServers": {
    "development-only": {
      "enabled": "${DEV_MODE}",
      "command": "npx",
      "args": ["-y", "dev-server"]
    }
  }
}
```

## Testing MCP Servers

### Test Individual Server

```bash
# Test GitHub server
agent: Test GitHub MCP server by getting my repositories

# Test OSINT server
agent: Test OSINT toolkit by performing a WHOIS lookup on example.com
```

### Verify All Servers

```bash
# In Agent Zero
agent: List all available MCP servers and their status
```

### Debug Mode

Enable debug logging for MCP servers:

```bash
# In .env
MCP_DEBUG=true
MCP_LOG_LEVEL=debug
```

## Performance Optimization

### Minimize Enabled Servers

Only enable servers you actively use to reduce startup time and memory usage.

### Cache API Responses

Configure caching for frequently accessed data:

```json
{
  "mcpServers": {
    "github": {
      "cache": {
        "enabled": true,
        "ttl": 3600
      }
    }
  }
}
```

### Connection Pooling

For database servers, configure connection pooling:

```json
{
  "mcpServers": {
    "postgres": {
      "pool": {
        "min": 2,
        "max": 10
      }
    }
  }
}
```

## Migration Guide

### Migrating from VS Code

1. Export VS Code MCP settings
2. Save to `conf/mcp_servers_vscode.json`
3. Convert environment variable format if needed
4. Test each server individually
5. Update `.env` with required keys

### Upgrading Configurations

When upgrading Agent Zero:

1. Backup current configuration
2. Review new server additions in `conf/mcp_servers_available.json`
3. Merge your custom settings
4. Test configuration
5. Update API keys if needed

## Best Practices

1. **Start Small**: Enable only essential servers initially
2. **Test Incrementally**: Test each server before adding another
3. **Document Usage**: Keep notes on which servers you use and why
4. **Regular Audits**: Review enabled servers monthly
5. **Monitor Costs**: Track API usage and associated costs
6. **Security First**: Rotate keys, use least privilege, monitor access
7. **Version Control**: Keep configs in version control (without secrets)
8. **Backup Settings**: Backup working configurations regularly

## Getting Help

- **Documentation**: See [OSINT & Security Guide](./osint_and_security.md)
- **Discord**: https://discord.gg/B8KZKNsPpj
- **GitHub Issues**: https://github.com/agent0ai/agent-zero/issues
- **Community**: https://www.skool.com/agent-zero
