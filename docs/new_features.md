# New Features and Enhancements

This document summarizes all the new features and enhancements added to Agent Zero.

## Table of Contents

1. [Error Tracking System](#error-tracking-system)
2. [Git Integration](#git-integration)
3. [Automatic Memory Monitoring](#automatic-memory-monitoring)
4. [MCP Servers](#mcp-servers)
5. [Theme System](#theme-system)
6. [New Tools](#new-tools)
7. [Configuration](#configuration)
8. [Quick Start](#quick-start)

---

## Error Tracking System

### Overview
A persistent error tracking system that logs all errors, categorizes them, and helps find solutions based on past occurrences.

### Features
- **Automatic Error Logging**: All errors are automatically logged with context
- **Categorization**: Errors are categorized (network, file_io, llm_api, tool_execution, etc.)
- **Solution Lookup**: Find solutions from previously resolved similar errors
- **Statistics**: View error frequency, resolution rates, and trends
- **Prevention Recommendations**: Get suggestions to prevent recurring errors

### Usage
```json
{
    "tool_name": "error_logs",
    "tool_args": {
        "method": "statistics"
    }
}
```

### Methods
- `statistics` - View overall error statistics
- `search` - Search errors by type or category
- `solutions` - Get solutions for specific errors
- `recommendations` - Get error prevention advice
- `resolve` - Mark an error as resolved with a solution

### File Location
Errors are stored in: `logs/error_tracker.json`

---

## Git Integration

### Overview
Comprehensive Git workflow support with full repository management capabilities.

### Features
- **Branch Management**: Create, checkout, list, and manage branches
- **Commit Operations**: Create commits with automatic staging
- **Push/Pull**: Sync with remote repositories
- **Diff Viewing**: View unstaged and staged changes
- **Conflict Detection**: Identify and list merge conflicts
- **Status Tracking**: Get detailed repository status

### Usage
```json
{
    "tool_name": "git_workflow",
    "tool_args": {
        "method": "status"
    }
}
```

### Methods
- `status` - Get repository status
- `info` - Get repository information
- `branch_create` - Create a new branch
- `branch_checkout` - Checkout an existing branch
- `branch_list` - List all branches
- `commit` - Create a commit
- `push` - Push to remote
- `pull` - Pull from remote
- `diff` - View changes
- `conflicts` - Check for merge conflicts

### GitHub/GitLab Integration
Use the GitHub and GitLab MCP servers for advanced operations:
- Create and manage issues
- Create and review pull requests/merge requests
- Search repositories
- Manage projects

---

## Automatic Memory Monitoring

### Overview
A background thread that monitors conversations and automatically manages memories.

### Features
- **Background Monitoring**: Runs on a separate thread using Ollama
- **Intelligent Classification**: Categorizes memories as short-term, long-term, episodic, semantic, or procedural
- **Importance Scoring**: Evaluates memory importance (0.0 to 1.0)
- **Automatic Organization**: Supports linear, hierarchical, parallel, and graph organization
- **Configurable Thresholds**: Customize what gets saved
- **TTL Management**: Short-term memories expire automatically

### Usage
```json
{
    "tool_name": "memory_monitor",
    "tool_args": {
        "method": "status"
    }
}
```

### Methods
- `start` - Start the memory monitor
- `stop` - Stop the memory monitor
- `status` - Get current status and statistics
- `short_term` - View short-term memories
- `pending` - View pending long-term memories
- `configure` - Update configuration

### Configuration
Set in `.env`:
```bash
MEMORY_MONITOR_ENABLED=true
MEMORY_MONITOR_MODEL=llama3.2:3b
MEMORY_IMPORTANCE_THRESHOLD=0.5
MEMORY_SHORT_TERM_TTL=3600
MEMORY_AUTO_SAVE=true
```

---

## MCP Servers

### Overview
Pre-configured Model Context Protocol servers for extended functionality.

### Available Servers (15+)

#### Development
- **filesystem** - File and directory management
- **git** - Git operations
- **github** - GitHub API integration
- **gitlab** - GitLab API integration

#### Databases
- **postgres** - PostgreSQL database queries
- **sqlite** - SQLite database management

#### Search & Web
- **brave-search** - Web search using Brave API
- **puppeteer** - Browser automation

#### Cloud Services
- **google-drive** - Google Drive integration
- **aws-kb** - AWS Knowledge Base

#### Communication
- **slack** - Slack workspace integration

#### Containers
- **docker** - Docker container management
- **kubernetes** - Kubernetes cluster operations

#### Utilities
- **sequential-thinking** - Enhanced reasoning
- **everything** - Fast file search (Windows)

### Configuration
See `conf/mcp_servers_available.json` for server configurations.

Detailed setup guide: [docs/mcp_servers_guide.md](./mcp_servers_guide.md)

---

## Theme System

### Overview
Customizable color themes for terminal output with 8 built-in themes.

### Built-in Themes
1. **dark** - Classic dark theme
2. **light** - Light theme for bright environments
3. **solarized_dark** - Solarized dark variant
4. **solarized_light** - Solarized light variant
5. **monokai** - Popular Monokai color scheme
6. **dracula** - Dark theme with pastel colors
7. **nord** - Arctic-inspired palette
8. **gruvbox** - Retro groove color scheme

### Features
- **Runtime Switching**: Change themes on the fly
- **Custom Themes**: Create and save custom color palettes
- **Export/Import**: Share themes with others
- **Per-Component Colors**: Customize individual UI elements
- **Style Preferences**: Control bold, italic, underline, padding

### Usage
```json
{
    "tool_name": "theme",
    "tool_args": {
        "method": "switch",
        "theme_name": "monokai"
    }
}
```

### Methods
- `list` - List available themes
- `current` - Show current theme
- `switch` - Switch to a different theme
- `colors` - Show color palette
- `export` - Export theme to file
- `import` - Import theme from file

### Configuration
Set in `.env`:
```bash
UI_THEME=dark
UI_BOLD_HEADINGS=true
UI_ITALIC_THOUGHTS=true
UI_UNDERLINE_LINKS=true
UI_PADDING_MESSAGES=true
UI_SHOW_TIMESTAMPS=false
```

---

## New Tools

### Summary of All New Tools

| Tool | Purpose | Methods |
|------|---------|---------|
| **error_logs** | Error tracking and management | statistics, search, solutions, recommendations, resolve |
| **git_workflow** | Git repository operations | status, info, branch_*, commit, push, pull, diff, conflicts |
| **memory_monitor** | Memory monitoring control | start, stop, status, short_term, pending, configure |
| **theme** | Theme and color management | list, current, switch, colors, export, import |

### Tool Documentation
Complete tools guide: [docs/tools_guide.md](./tools_guide.md)

---

## Configuration

### Environment Variables

All new features can be configured via `.env` file:

```bash
# Error Tracking
ERROR_TRACKING_ENABLED=true
ERROR_TRACKER_DB_PATH=logs/error_tracker.json

# Git Integration
GITHUB_TOKEN=ghp_your_token_here
GITLAB_TOKEN=glpat-your_token_here
GITLAB_URL=https://gitlab.com

# Memory Monitor
MEMORY_MONITOR_ENABLED=true
MEMORY_MONITOR_MODEL=llama3.2:3b
MEMORY_IMPORTANCE_THRESHOLD=0.5
MEMORY_SHORT_TERM_TTL=3600
MEMORY_AUTO_SAVE=true

# Theme
UI_THEME=dark
UI_BOLD_HEADINGS=true
UI_ITALIC_THOUGHTS=true
UI_UNDERLINE_LINKS=true
UI_PADDING_MESSAGES=true
UI_SHOW_TIMESTAMPS=false

# MCP Servers (as needed)
BRAVE_API_KEY=your_key_here
POSTGRES_CONNECTION_STRING=postgresql://...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
SLACK_BOT_TOKEN=xoxb-...
```

### Configuration Files

| File | Purpose |
|------|---------|
| `conf/mcp_servers_available.json` | MCP server configurations |
| `conf/theme.json` | User theme preferences |
| `logs/error_tracker.json` | Error tracking database |

---

## Quick Start

### 1. Enable Error Tracking

No configuration needed - it's automatic! View errors:

```json
{
    "tool_name": "error_logs",
    "tool_args": {"method": "statistics"}
}
```

### 2. Set Up Git Integration

Add your tokens to `.env`:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

Use Git operations:
```json
{
    "tool_name": "git_workflow",
    "tool_args": {
        "method": "status"
    }
}
```

### 3. Enable Memory Monitoring

Configure in `.env`:
```bash
MEMORY_MONITOR_ENABLED=true
MEMORY_MONITOR_MODEL=llama3.2:3b
```

Start the monitor:
```json
{
    "tool_name": "memory_monitor",
    "tool_args": {"method": "start"}
}
```

### 4. Configure MCP Servers

1. Choose servers from `conf/mcp_servers_available.json`
2. Set `"enabled": true` for desired servers
3. Add required credentials to `.env`
4. Restart Agent Zero

### 5. Customize Theme

Switch to a different theme:
```json
{
    "tool_name": "theme",
    "tool_args": {
        "method": "switch",
        "theme_name": "monokai"
    }
}
```

Or create a custom theme by exporting current, modifying colors, and importing.

---

## Benefits

### For Users
- **Better Error Handling**: Never lose track of errors and their solutions
- **Git Workflow**: Manage code repositories without leaving Agent Zero
- **Smart Memories**: Automatic memory management without manual intervention
- **Extended Capabilities**: Access to databases, cloud services, and more
- **Personalized Appearance**: Choose themes that match your preference

### For Developers
- **Comprehensive Documentation**: Every class and method is documented
- **Error Solutions**: Learn from past errors and their fixes
- **Git Integration**: Seamlessly work with version control
- **Extensible**: Easy to add new tools, themes, and MCP servers
- **Well-Structured**: Clean code with proper separation of concerns

---

## Documentation Links

- [Tools Guide](./tools_guide.md) - Complete reference for all tools
- [MCP Servers Guide](./mcp_servers_guide.md) - Setup and usage for MCP servers
- [Main README](../README.md) - Agent Zero overview
- [Installation Guide](./installation.md) - Installation instructions
- [Extensibility Guide](./extensibility.md) - Extending Agent Zero

---

## Troubleshooting

### Error Tracking Not Working
- Check that `ERROR_TRACKING_ENABLED=true` in `.env`
- Verify write permissions for `logs/` directory
- View error tracker database at `logs/error_tracker.json`

### Git Operations Failing
- Ensure you're in a valid Git repository
- Check Git is installed: `git --version`
- Verify credentials for GitHub/GitLab operations

### Memory Monitor Not Starting
- Verify Ollama is installed and running
- Check model exists: `ollama list`
- Pull model if needed: `ollama pull llama3.2:3b`
- Review monitor configuration in `.env`

### MCP Servers Not Available
- Verify `npx` is installed (for Node-based servers)
- Check required environment variables are set
- Review server logs in Agent Zero logs directory
- Ensure server is enabled in `mcp_servers_available.json`

### Theme Not Changing
- Verify theme name is correct (use `list` method)
- Check `conf/theme.json` was created
- Try restarting Agent Zero
- Export and review current theme configuration

---

## Future Enhancements

Potential future improvements:
- Advanced TUI with Rich/Textual library
- Machine learning-based memory classification
- Automated error recovery mechanisms
- More MCP server integrations
- Theme builder UI
- Memory consolidation algorithms
- Advanced Git workflow templates

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the documentation guides
3. Check existing GitHub issues
4. Create a new issue with details

---

## License

All enhancements follow the same license as Agent Zero.

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-18  
**Compatibility**: Agent Zero v0.9.6+
