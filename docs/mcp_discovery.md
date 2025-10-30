# MCP Server Discovery Guide

Agent Zero now includes an integrated MCP server discovery system that allows you to browse and install MCP servers from multiple sources including npm, GitHub, and Docker Hub.

## Overview

The MCP Server Discovery feature provides:

1. **Automatic Discovery**: Search and browse MCP servers from npm registry, GitHub repositories, and Docker Hub
2. **Easy Installation**: One-click configuration generation for discovered servers
3. **Rich Metadata**: View server descriptions, popularity metrics, and links
4. **Smart Filtering**: Search and filter by source, name, description, or topics
5. **Caching**: Discovered servers are cached for 24 hours for better performance

## Accessing the Discovery Interface

1. Open Agent Zero's Web UI
2. Go to **Settings** → **MCP Servers Configuration**
3. Click the **🔍 Discover Servers** button at the top of the page
4. The discovery interface will load with a list of available MCP servers

## Using the Discovery Interface

### Search and Filter

The discovery interface provides several ways to find servers:

- **Search Box**: Type keywords to search server names, descriptions, and topics
- **Source Filter**: Filter by source (All Sources, npm, GitHub, Docker Hub)
- **Sort Options**: 
  - **Sort by Popularity**: Shows most popular servers first (by stars/downloads)
  - **Sort by Name**: Alphabetical sorting
  - **Sort by Date**: Most recently updated first

### Server Information

Each server card displays:

- **Source Icon**: 📦 (npm), 🐙 (GitHub), or 🐳 (Docker Hub)
- **Name**: The server name
- **Description**: What the server does
- **Popularity Metrics**: 
  - Stars (for GitHub)
  - Downloads (for npm)
  - Pulls (for Docker Hub)
- **Language**: Programming language (for GitHub repositories)

### Adding a Server

1. Click on a server card to view detailed information
2. In the details modal, review:
   - Full description
   - Version information
   - Popularity metrics
   - Topics/keywords
   - Links to source repositories
3. Click **➕ Copy Configuration**
4. The server configuration is automatically copied to your clipboard
5. Close the modal and paste the configuration into the JSON editor
6. Set `"enabled": true` in the pasted configuration
7. Click **Apply now** to activate the server

## Discovery Sources

### npm Registry

The system searches for MCP servers in the npm registry by:

- Packages in the `@modelcontextprotocol` scope
- Packages with the `mcp-server` keyword

**npm servers** are typically Node.js-based and can be run using `npx`:

```json
{
  "name": "server-name",
  "description": "Server description",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-name"],
  "enabled": false
}
```

### GitHub Repositories

The system searches GitHub for:

- Repositories with the `mcp-server` topic
- Repositories with the `model-context-protocol` topic
- Repositories with "mcp server" in the name or description

**GitHub servers** may require cloning and building. The discovery system provides the repository URL for manual setup.

### Docker Hub

The system searches Docker Hub for:

- Images with "mcp" in the name
- Images with "mcp-server" tags
- Images with "model-context-protocol" in the description

**Docker servers** can be run as containers:

```json
{
  "name": "docker-server",
  "description": "Docker-based MCP server",
  "type": "stdio",
  "command": "docker",
  "args": ["run", "-i", "--rm", "image-name"],
  "enabled": false
}
```

## Cache Management

- Discovered servers are cached in `conf/mcp_servers_registry.json`
- Cache expires after 24 hours
- To force a refresh, click the **🔄 Refresh** button in the discovery interface
- The system will automatically refresh if cache is older than 24 hours

## API Endpoints

For programmatic access, the discovery system provides API endpoints:

### Discover Servers

```python
POST /api/mcp_discover
{
  "force_refresh": false,  # Optional: force cache refresh
  "source": "npm",         # Optional: filter by source (npm, github, docker)
  "query": "database"      # Optional: search query
}
```

Response:
```json
{
  "success": true,
  "servers": [...],
  "count": 100,
  "cached": true
}
```

### Add Server from Registry

```python
POST /api/mcp_add_from_registry
{
  "server_name": "@modelcontextprotocol/server-github",
  "enabled": false,
  "custom_config": {       # Optional: override defaults
    "args": ["-y", "@modelcontextprotocol/server-github", "--custom-arg"]
  }
}
```

Response:
```json
{
  "success": true,
  "server": {...},
  "config": {...},
  "message": "Server configuration generated"
}
```

## Popular MCP Servers

Here are some popular MCP servers available through the discovery system:

### Official Servers (npm/@modelcontextprotocol)

1. **server-filesystem**: File system access and management
2. **server-github**: GitHub API integration
3. **server-git**: Git repository operations
4. **server-gitlab**: GitLab integration
5. **server-postgres**: PostgreSQL database queries
6. **server-sqlite**: SQLite database access
7. **server-brave-search**: Web search via Brave
8. **server-slack**: Slack messaging integration
9. **server-puppeteer**: Browser automation
10. **server-kubernetes**: Kubernetes cluster management

### Community Servers

1. **agentic-flow**: Production-ready AI agent orchestration
2. **git-mcp-server**: Enhanced Git operations
3. **mcp-server-mysql**: MySQL database integration
4. **mcp-server-atlassian-bitbucket**: Bitbucket integration
5. **railway/mcp-server**: Railway platform integration
6. **codacy-mcp**: Code quality analysis

## Troubleshooting

### Discovery Returns No Results

1. Check your internet connection
2. Try clicking **🔄 Refresh** to force a cache refresh
3. Check browser console for errors
4. Verify the discovery API endpoint is accessible

### Cannot Add Server

1. Ensure you have clipboard permissions in your browser
2. Check that the server configuration is valid JSON
3. Verify required environment variables are set (e.g., GITHUB_TOKEN)
4. Check the server's documentation for prerequisites

### Server Fails to Start

1. For npm servers, ensure `node` and `npx` are installed
2. For Docker servers, ensure Docker is running
3. Check the server logs in the MCP Servers Configuration page
4. Verify environment variables and arguments are correct

## Best Practices

1. **Start Small**: Enable only the servers you need
2. **Check Requirements**: Read server documentation before enabling
3. **Test Incrementally**: Enable and test one server at a time
4. **Monitor Resources**: Some servers may consume significant resources
5. **Keep Updated**: Periodically refresh the discovery cache for new servers
6. **Read Documentation**: Each server may have specific setup requirements

## Security Considerations

1. **Verify Sources**: Only add servers from trusted sources
2. **Review Configurations**: Check server arguments and environment variables
3. **Limit Permissions**: For filesystem servers, specify minimal allowed paths
4. **Secure Credentials**: Store API tokens in environment variables, not in config
5. **Docker Isolation**: Docker-based servers run in isolated containers

## Contributing

To add your MCP server to the discovery system:

1. **For npm packages**: 
   - Publish to npm with `mcp-server` keyword
   - Use `@modelcontextprotocol` scope if official
   - Include clear description and documentation

2. **For GitHub repositories**:
   - Add `mcp-server` topic to your repository
   - Include comprehensive README
   - Add example configurations

3. **For Docker images**:
   - Tag images with "mcp" or "mcp-server"
   - Include clear description
   - Document required environment variables

## Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Agent Zero MCP Setup Guide](./mcp_setup.md)
- [Agent Zero MCP Servers Guide](./mcp_servers_guide.md)
- [Agent Zero Documentation](./README.md)

## Support

For issues with:
- **Discovery System**: File an issue on the Agent Zero repository
- **Specific MCP Servers**: Check the server's repository or npm package page
- **General MCP Questions**: See the MCP protocol documentation

---

Last updated: 2025-10-30
