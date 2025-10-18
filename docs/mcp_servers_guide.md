# MCP Servers Configuration Guide

This guide explains how to configure and use the available Model Context Protocol (MCP) servers with Agent Zero.

## Available MCP Servers

Agent Zero comes with pre-configured support for numerous MCP servers. You can enable them by editing the `conf/mcp_servers_available.json` file and setting `"enabled": true` for the servers you want to use.

### Core Servers

#### Memory Manager (Built-in)
**Status**: Enabled by default

The Memory Manager is Agent Zero's built-in MCP server for managing memories, knowledge base, and agent rules with semantic search capabilities.

**Configuration**: Already configured and running.

### Development & Git

#### Filesystem
**Description**: Access and manage files and directories with advanced search capabilities.

**Setup**:
```json
"enabled": true,
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir1", "/path/to/allowed/dir2"]
```

Configure allowed directories in the `args` array for security.

#### Git
**Description**: Git operations including status, diff, commit, and repository management.

**Setup**:
```json
"enabled": true
```

Must be run within a Git repository.

#### GitHub
**Description**: GitHub API integration for issues, PRs, repositories, and code search.

**Setup**:
1. Get a GitHub Personal Access Token from https://github.com/settings/tokens
2. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

**Capabilities**:
- Create, read, update issues
- Manage pull requests
- Search repositories and code
- Fork repositories
- Manage branches

#### GitLab
**Description**: GitLab API integration for issues, merge requests, and repository management.

**Setup**:
1. Get a GitLab Personal Access Token from your GitLab instance
2. Add to `.env`:
   ```
   GITLAB_TOKEN=glpat-your_token_here
   GITLAB_URL=https://gitlab.com  # or your GitLab instance URL
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

**Capabilities**:
- Create, read, update issues
- Manage merge requests
- Repository management
- Project operations

### Databases

#### PostgreSQL
**Description**: PostgreSQL database queries and schema inspection.

**Setup**:
1. Add connection string to `.env`:
   ```
   POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/dbname
   ```
2. Enable in config:
   ```json
   "enabled": true
   ```

**Capabilities**:
- Execute SQL queries
- Inspect database schema
- Manage tables and data

#### SQLite
**Description**: SQLite database queries and management.

**Setup**:
```json
"enabled": true,
"args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/your/database.db"]
```

Configure the database path in the `args` array.

### Search & Web

#### Brave Search
**Description**: Web search using Brave Search API.

**Setup**:
1. Get a Brave Search API key from https://brave.com/search/api/
2. Add to `.env`:
   ```
   BRAVE_API_KEY=your_api_key_here
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

#### Puppeteer
**Description**: Browser automation and web scraping.

**Setup**:
```json
"enabled": true
```

Provides headless browser automation for web scraping and testing.

### Cloud Services

#### Google Drive
**Description**: Access and manage Google Drive files and folders.

**Setup**:
1. Create a Google Cloud service account and download credentials JSON
2. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

#### AWS Knowledge Base
**Description**: Query AWS knowledge bases and documents.

**Setup**:
1. Add AWS credentials to `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```
2. Enable in config:
   ```json
   "enabled": true
   ```

### Communication

#### Slack
**Description**: Send messages and interact with Slack workspaces.

**Setup**:
1. Create a Slack bot and get the bot token
2. Add to `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

### Container Orchestration

#### Docker
**Description**: Docker container management and operations.

**Setup**:
```json
"enabled": true
```

Requires Docker installed and running on the system.

**Capabilities**:
- Manage containers (start, stop, remove)
- Image management
- Network operations
- Volume management

#### Kubernetes
**Description**: Kubernetes cluster management and operations.

**Setup**:
1. Ensure kubectl is installed
2. Add to `.env`:
   ```
   KUBECONFIG=/path/to/kubeconfig
   ```
3. Enable in config:
   ```json
   "enabled": true
   ```

### Utilities

#### Sequential Thinking
**Description**: Enhanced reasoning through structured thought processes.

**Setup**:
```json
"enabled": true
```

Provides prompts and tools for step-by-step reasoning and problem-solving.

#### Everything Search (Windows Only)
**Description**: Fast file search using Everything search engine.

**Setup**:
1. Install Everything search engine on Windows
2. Enable in config:
   ```json
   "enabled": true
   ```

## How to Enable MCP Servers

1. **Edit Configuration**:
   Open `conf/mcp_servers_available.json` and set `"enabled": true` for desired servers.

2. **Set Environment Variables**:
   Add required credentials and configuration to your `.env` file.

3. **Restart Agent Zero**:
   The servers will be initialized on startup.

## Security Considerations

- **Filesystem Server**: Only allow access to necessary directories
- **Database Servers**: Use read-only credentials when possible
- **API Tokens**: Store tokens securely in `.env`, never commit them
- **Network Access**: Consider firewall rules for external services

## Troubleshooting

### Server Won't Start

1. Check that all required environment variables are set
2. Verify the server command is installed (e.g., `npx` for Node-based servers)
3. Check the server logs in the Agent Zero logs directory

### Permission Errors

- Ensure the Agent Zero process has necessary permissions
- For filesystem access, verify directory permissions
- For databases, check user credentials and permissions

### Connection Issues

- Verify API tokens are valid and not expired
- Check network connectivity to external services
- Ensure firewall rules allow necessary connections

## Creating Custom MCP Servers

You can create custom MCP servers for your specific needs. See the [MCP documentation](https://modelcontextprotocol.io/) for details on implementing custom servers.

To add a custom server:

1. Add its configuration to `conf/mcp_servers_available.json`
2. Set any required environment variables in `.env`
3. Enable the server and restart Agent Zero

## Examples

### Example: Enabling GitHub Integration

```bash
# In .env
GITHUB_TOKEN=ghp_abc123...
```

```json
// In conf/mcp_servers_available.json
"github": {
  "enabled": true
}
```

### Example: Enabling PostgreSQL

```bash
# In .env
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/mydb
```

```json
// In conf/mcp_servers_available.json
"postgres": {
  "enabled": true
}
```

### Example: Multiple Servers

```bash
# In .env
GITHUB_TOKEN=ghp_...
GITLAB_TOKEN=glpat-...
BRAVE_API_KEY=...
SLACK_BOT_TOKEN=xoxb-...
```

```json
// In conf/mcp_servers_available.json
"github": { "enabled": true },
"gitlab": { "enabled": true },
"brave-search": { "enabled": true },
"slack": { "enabled": true }
```

## Best Practices

1. **Start Small**: Enable only the servers you need
2. **Use Environment Variables**: Never hardcode credentials
3. **Monitor Usage**: Check server logs for issues
4. **Update Regularly**: Keep MCP servers updated via `npx -y`
5. **Test Configuration**: Test servers individually before enabling multiple
6. **Document Custom Configs**: Note any custom configurations you make

## Support

For issues with specific MCP servers, refer to:
- Agent Zero documentation: `/docs`
- MCP protocol: https://modelcontextprotocol.io/
- Individual server repositories on GitHub

For Agent Zero-specific MCP integration issues, check the troubleshooting guide or file an issue on the Agent Zero repository.
