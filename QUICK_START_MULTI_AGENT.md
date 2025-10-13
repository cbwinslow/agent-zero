# Multi-Agent Memory System - Quick Setup Guide

This guide will help you quickly set up and start using the new multi-agent memory management system.

## Quick Start

### 1. Configure Environment

Copy the example environment file and configure it:

```bash
cp example.env .env
```

Edit `.env` and add your API keys:

```env
# OpenRouter (recommended for multi-model access)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Or use other providers
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Enable multi-agent mode
MULTI_AGENT_ENABLED=true
MEMORY_MCP_ENABLED=true
```

### 2. Run Setup Script

```bash
python setup_memory_mcp.py
```

This will:
- Configure the Memory MCP server
- Verify agent profiles are set up
- Check all required files are present

### 3. Start Agent Zero

#### Using Docker (Recommended)

```bash
cd docker/run
docker-compose up -d
```

This starts:
- Agent Zero main container (port 50080)
- Memory MCP Server container (port 3001)

#### Without Docker

```bash
python run_ui.py
```

In a separate terminal, start the Memory MCP server:

```bash
python run_memory_mcp.py
```

### 4. Verify Setup

Open Agent Zero in your browser: `http://localhost:50080`

Test the multi-agent system:

```
Research the latest trends in AI and create a summary report with code examples
```

The system will automatically:
- Use the researcher agent to gather information
- Use the analyst agent to analyze trends
- Use the developer agent to create code examples
- Synthesize all results into a comprehensive report

## Available Features

### 1. Memory Management

Save and retrieve memories:
```
Save this decision to memory: Use PostgreSQL for the database
```

Search memories:
```
What database decisions have we made?
```

### 2. Knowledge Base

Store knowledge in organized areas:
- **main**: General knowledge
- **fragments**: Code snippets and templates
- **solutions**: Solved problems
- **instruments**: Tool descriptions

### 3. Multi-Agent Tasks

Delegate to specialized agents:
```
Use multiple agents to:
1. Research best practices for REST APIs
2. Plan the architecture
3. Implement a basic API
4. Test and document it
```

### 4. Agent Profiles

Available specialized agents:
- **researcher**: Information gathering
- **developer**: Software development
- **analyst**: Data analysis
- **planner**: Project planning
- **executor**: Task execution

## Configuration Options

### Environment Variables

```env
# Memory MCP Server
MEMORY_MCP_HOST=localhost
MEMORY_MCP_PORT=3001
MEMORY_MCP_ENABLED=true

# Multi-Agent System
MULTI_AGENT_ENABLED=true
MAX_SUB_AGENTS=5
SUB_AGENT_PROFILES=researcher,developer,analyst
AGENT_COORDINATION_STRATEGY=adaptive

# Memory Settings
MEMORY_COMPRESSION_THRESHOLD=0.9
MEMORY_MAX_SIZE=10000
```

### MCP Servers

The Memory MCP server is automatically added to your settings. You can also configure it manually in the Agent Zero UI under Settings > MCP Servers.

## Common Use Cases

### Use Case 1: Research and Development

```
I need to build a task scheduler application.
Research existing solutions, plan the architecture, and implement a prototype.
```

The system will:
1. Research task scheduler patterns (researcher)
2. Plan the architecture (planner)
3. Implement the prototype (developer)

### Use Case 2: Data Analysis Project

```
Analyze our user behavior data and provide recommendations for improving engagement.
```

The system will:
1. Analyze the data (analyst)
2. Identify patterns (analyst)
3. Create recommendations (analyst)

### Use Case 3: Complex Integration

```
Research the Stripe API, plan the integration, and implement payment processing.
```

The system will:
1. Research Stripe API (researcher)
2. Plan integration approach (planner)
3. Implement payment flow (developer)
4. Test the implementation (executor)

## Troubleshooting

### Memory MCP Server Not Starting

Check if the port is already in use:
```bash
lsof -i :3001
```

Change the port in `.env`:
```env
MEMORY_MCP_PORT=3002
```

### Multi-Agent Not Working

Verify it's enabled:
```bash
grep MULTI_AGENT_ENABLED .env
```

Should show:
```
MULTI_AGENT_ENABLED=true
```

### Agent Profiles Missing

Re-run the setup script:
```bash
python setup_memory_mcp.py
```

### Docker Issues

Restart the containers:
```bash
cd docker/run
docker-compose down
docker-compose up -d
```

View logs:
```bash
docker logs agent-zero
docker logs agent-zero-memory-mcp
```

## Advanced Usage

### Custom Agent Profiles

Create a new agent profile:

```bash
mkdir agents/my-custom-agent
```

Create `agents/my-custom-agent/_context.md`:
```markdown
# My Custom Agent

You are specialized in X, Y, Z...
```

Add to configuration:
```env
SUB_AGENT_PROFILES=my-custom-agent,researcher,developer
```

### Memory Organization

Organize memories by project:
```python
# Save project-specific memory
await memory.save_memory(
    content="Project X uses microservices architecture",
    metadata={
        "project": "project-x",
        "area": "solutions",
        "importance": "high"
    }
)

# Search project-specific memories
results = await memory.search_memories(
    query="architecture decisions",
    filter='project == "project-x"'
)
```

### Programmatic Access

Use the multi-agent coordinator directly:

```python
from python.helpers.multi_agent_coordinator import (
    MultiAgentCoordinator,
    AgentTask,
    CoordinationStrategy
)

coordinator = MultiAgentCoordinator(context, max_agents=5)

tasks = [
    AgentTask(agent_profile="researcher", message="Research topic X"),
    AgentTask(agent_profile="analyst", message="Analyze findings"),
]

results = await coordinator.coordinate(tasks, CoordinationStrategy.SEQUENTIAL)
```

## Next Steps

1. Read the [full documentation](docs/multi_agent_memory_system.md)
2. Explore [agent profiles](agents/)
3. Check out [example prompts](prompts/)
4. Join the community for support

## Resources

- **Documentation**: `/docs/multi_agent_memory_system.md`
- **Configuration**: `example.env`
- **Agent Profiles**: `/agents/`
- **Setup Script**: `setup_memory_mcp.py`
- **Docker Compose**: `docker/run/docker-compose.yml`

## Support

For issues or questions:
- GitHub Issues: [github.com/cbwinslow/agent-zero/issues](https://github.com/cbwinslow/agent-zero/issues)
- Documentation: Check `/docs/` folder
- Examples: See `docs/multi_agent_memory_system.md`

---

Happy building with Agent Zero's multi-agent memory system! 🚀
