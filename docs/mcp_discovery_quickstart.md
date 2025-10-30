# MCP Server Discovery - Quick Start

This guide helps you quickly get started with the new MCP Server Discovery feature in Agent Zero.

## What is MCP Server Discovery?

MCP Server Discovery allows Agent Zero to automatically find and configure Model Context Protocol (MCP) servers from multiple sources:

- **npm Registry**: Official and community MCP servers (100+ servers)
- **GitHub**: Open-source MCP server repositories
- **Docker Hub**: Containerized MCP servers (149+ images)

## Quick Start (3 Steps)

### Step 1: Open Discovery Interface

1. Start Agent Zero
2. Go to **Settings** (⚙️ icon)
3. Click **MCP Servers Configuration**
4. Click the **🔍 Discover Servers** button

### Step 2: Find a Server

Use the discovery interface to find servers:

- **Search**: Type keywords like "github", "database", "slack"
- **Filter by Source**: Select npm, GitHub, or Docker Hub
- **Sort**: By popularity, name, or date

Popular servers to try:
- `server-github` - GitHub API integration
- `server-filesystem` - File system access
- `server-brave-search` - Web search
- `server-puppeteer` - Browser automation
- `server-postgres` - PostgreSQL database

### Step 3: Add Server

1. Click on a server card to view details
2. Review the description, popularity, and requirements
3. Click **➕ Copy Configuration**
4. Paste the configuration into the JSON editor
5. Change `"enabled": false` to `"enabled": true`
6. Click **Apply now**
7. The server will start automatically!

## Example: Adding GitHub Integration

Here's a complete example of adding the GitHub MCP server:

1. **Open Discovery**: Settings → MCP Servers Configuration → 🔍 Discover Servers
2. **Search**: Type "github" in the search box
3. **Select**: Click on "server-github" (📦 npm)
4. **View Details**: Review the description and features
5. **Copy Config**: Click "➕ Copy Configuration"
6. **Paste**: In the MCP Servers JSON editor, paste between the existing servers
7. **Add Token**: Update the configuration:
   ```json
   {
     "name": "GitHub",
     "description": "GitHub API integration for issues, PRs, repositories, and code search",
     "type": "stdio",
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-github"],
     "env": {
       "GITHUB_TOKEN": "ghp_your_token_here"
     },
     "enabled": true
   }
   ```
8. **Apply**: Click "Apply now"
9. **Verify**: Check the server status shows "connected" with green indicator

## Configuration Format

All discovered servers generate configurations in this format:

```json
{
  "name": "server-name",
  "description": "What the server does",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "package-name"],
  "env": {
    "API_KEY": "your-key-here"
  },
  "enabled": false,
  "notes": "Additional information"
}
```

## Common Server Types

### npm Servers (Node.js)
- Run with `npx` (no installation needed)
- Example: `@modelcontextprotocol/server-*`
- Most common and easiest to use

### Docker Servers
- Run as containers
- Command: `docker run -i --rm image-name`
- Good for isolation and complex dependencies

### GitHub Repositories
- Need to be cloned and built
- Follow the repository's README for setup
- Often provide unique or experimental features

## Tips for Success

1. **Start with Official Servers**: npm/@modelcontextprotocol servers are well-tested
2. **Check Requirements**: Some servers need API keys or credentials
3. **Read Descriptions**: Understand what each server does before enabling
4. **Enable One at a Time**: Test each server individually
5. **Monitor Resources**: Some servers may use more memory or CPU
6. **Use Search Wisely**: Filter by source to find specific types of servers

## Environment Variables

Many servers require API keys or tokens. Add these to your `.env` file:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here

# Brave Search
BRAVE_API_KEY=your_api_key

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-token

# PostgreSQL
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Troubleshooting

### Server Won't Start
- Check that required dependencies are installed (node, docker, etc.)
- Verify environment variables are set correctly
- Look at the server log (click "Log" button in status view)

### Server Shows Error
- Read the error message in the server status
- Check the server's documentation for requirements
- Verify API tokens are valid and have correct permissions

### Discovery Returns No Servers
- Click the 🔄 Refresh button to force cache update
- Check internet connection
- Try filtering by specific source (npm usually works best)

### Configuration Not Working
- Ensure JSON is valid (use the "Reformat" button)
- Check for missing commas between server entries
- Verify all quotes are properly closed

## Next Steps

After adding your first servers:

1. **Test the Tools**: Try using the new tools in a chat
2. **Explore More**: Browse the full catalog of 250+ servers
3. **Combine Servers**: Use multiple servers together for complex workflows
4. **Create Custom**: Consider creating your own MCP server
5. **Share**: Tell the community about useful server combinations

## Popular Server Combinations

### Web Developer Stack
- server-github (code management)
- server-filesystem (file access)
- server-puppeteer (browser testing)
- server-git (version control)

### Data Analysis Stack
- server-postgres (database queries)
- server-filesystem (data files)
- server-brave-search (research)

### DevOps Stack
- server-kubernetes (cluster management)
- server-docker (container operations)
- server-github (CI/CD)
- server-slack (notifications)

## Learn More

- [Full MCP Discovery Documentation](./mcp_discovery.md)
- [MCP Setup Guide](./mcp_setup.md)
- [MCP Servers Configuration Guide](./mcp_servers_guide.md)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

---

**Ready to expand your Agent Zero's capabilities? Start discovering servers now!**
