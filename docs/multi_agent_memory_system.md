# Multi-Agent Memory System for Agent Zero

This guide explains the new multi-agent memory management system that enables Agent Zero to work with specialized sub-agents and maintain a comprehensive knowledge base.

## Overview

The multi-agent memory system consists of three main components:

1. **Memory MCP Server** - A dedicated MCP server for managing memories, knowledge, and rules
2. **Multi-Agent Coordinator** - A system for coordinating multiple specialized agents
3. **Specialized Agent Profiles** - Pre-configured agent profiles for different roles

## Memory MCP Server

The Memory MCP Server provides a centralized API for managing:
- **Memories**: Store and retrieve conversational memories in the vector database
- **Knowledge Base**: Organize knowledge into areas (main, fragments, solutions, instruments)
- **Agent Rules**: Define behavioral rules for different agent profiles
- **Memory Compression**: Consolidate and compress memories to reduce redundancy

### Available Tools

#### Memory Management
- `save_memory` - Save a memory with optional metadata
- `search_memories` - Search memories using semantic similarity
- `delete_memories` - Delete memories by query or IDs
- `compress_memories` - Compress and consolidate memories

#### Knowledge Base
- `save_knowledge` - Save knowledge to a specific area
- `get_knowledge` - Retrieve knowledge entries

#### Agent Rules
- `save_agent_rule` - Save or update agent behavioral rules
- `get_agent_rules` - Get all rules for an agent profile

### Configuration

Configure the Memory MCP Server in your `.env` file:

```env
# Memory MCP Server
MEMORY_MCP_HOST=localhost
MEMORY_MCP_PORT=3001
MEMORY_MCP_ENABLED=true

# Memory Settings
MEMORY_COMPRESSION_THRESHOLD=0.9
MEMORY_MAX_SIZE=10000
KNOWLEDGE_AUTO_IMPORT=true
KNOWLEDGE_DEFAULT_AREA=main
```

### Running the Memory MCP Server

#### Standalone Mode
```bash
python run_memory_mcp.py
```

#### Docker Compose Mode
The Memory MCP Server is automatically started when using docker-compose:

```bash
cd docker/run
docker-compose up -d
```

This starts both the main Agent Zero container and the Memory MCP Server container.

## Multi-Agent System

The multi-agent system allows Agent Zero to delegate tasks to specialized sub-agents, each optimized for specific types of work.

### Available Agent Profiles

#### 1. Researcher
- **Role**: Information gathering and analysis
- **Best for**: Research tasks, fact-finding, literature reviews
- **Skills**: Search, analysis, source validation

#### 2. Developer
- **Role**: Software development and technical implementation
- **Best for**: Coding, debugging, technical solutions
- **Skills**: Programming, testing, documentation

#### 3. Analyst
- **Role**: Data analysis and strategic insights
- **Best for**: Data analysis, pattern recognition, recommendations
- **Skills**: Statistical analysis, visualization, reporting

#### 4. Planner
- **Role**: Planning and coordination
- **Best for**: Project planning, task breakdown, workflow design
- **Skills**: Strategic planning, resource allocation, risk management

#### 5. Executor
- **Role**: Task execution and implementation
- **Best for**: Running commands, implementing solutions, automation
- **Skills**: Execution, validation, reporting

### Coordination Strategies

The multi-agent coordinator supports three coordination strategies:

1. **Sequential** - Agents work one after another
   - Use when: Tasks have clear dependencies
   - Example: Research → Plan → Develop → Test

2. **Parallel** - Agents work simultaneously
   - Use when: Tasks are independent
   - Example: Multiple research topics, parallel coding tasks

3. **Adaptive** (Recommended) - Automatically choose based on task structure
   - Use when: Complex tasks with mixed dependencies
   - Example: Some tasks can run in parallel, others must wait

### Configuration

Configure the multi-agent system in your `.env` file:

```env
# Multi-Agent System
MULTI_AGENT_ENABLED=true
MAX_SUB_AGENTS=5
SUB_AGENT_PROFILES=researcher,developer,analyst
AGENT_COORDINATION_STRATEGY=adaptive
```

### Using Multi-Agent Delegation

You can use the multi-agent system through the `multi_agent_delegation` tool:

```python
# Example usage in agent conversation
await agent.use_tool(
    "multi_agent_delegation",
    task_description="Research the latest AI trends and create a summary report",
    agent_profiles="researcher,analyst",
    coordination_strategy="sequential"
)
```

Or let the agent automatically decompose tasks:

```python
# Agent will automatically select appropriate profiles
await agent.use_tool(
    "multi_agent_delegation",
    task_description="Build a web scraper to collect product prices and analyze the data",
    # profiles will be auto-selected based on task
)
```

## OpenRouter Integration

OpenRouter is pre-configured and ready to use. It provides access to multiple LLM providers through a unified API.

### Setup

1. Get an API key from [OpenRouter](https://openrouter.ai/)
2. Add it to your `.env` file:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

3. Configure OpenRouter in the Agent Zero settings UI:
   - Provider: OpenRouter
   - Model: Choose from available models (e.g., `anthropic/claude-3.5-sonnet`)

### Benefits of OpenRouter

- **Multiple Providers**: Access models from OpenAI, Anthropic, Google, Meta, and more
- **Unified API**: Single API key for all providers
- **Cost-Effective**: Competitive pricing across providers
- **Fallback Support**: Automatic failover between providers
- **Usage Tracking**: Built-in usage analytics

## Memory Management Best Practices

### 1. Organize Knowledge by Area

- **main**: General knowledge and facts
- **fragments**: Code snippets, templates, reusable components
- **solutions**: Solved problems and their solutions
- **instruments**: Tool descriptions and usage examples

### 2. Use Metadata Effectively

When saving memories, add relevant metadata:

```python
await memory.insert_text(
    "Important project decision: Use microservices architecture",
    metadata={
        "area": "solutions",
        "project": "web-app",
        "importance": "high",
        "tags": ["architecture", "decision"]
    }
)
```

### 3. Regular Memory Compression

Periodically compress memories to:
- Remove duplicates
- Consolidate similar information
- Maintain database performance

```python
await memory_mcp.compress_memories(
    memory_subdir="default",
    threshold=0.9
)
```

### 4. Use Filters for Specific Searches

```python
# Search only in solutions area
results = await memory_mcp.search_memories(
    query="database optimization",
    filter='area == "solutions"',
    limit=10
)
```

## Agent Configuration Files

Each agent profile can have custom configuration files in its directory:

```
agents/
├── researcher/
│   ├── _context.md      # Profile description
│   └── rules.json       # Custom rules
├── developer/
│   ├── _context.md
│   └── rules.json
├── analyst/
│   └── _context.md
├── planner/
│   └── _context.md
└── executor/
    └── _context.md
```

### Creating Custom Agent Profiles

1. Create a new directory in `agents/`:
   ```bash
   mkdir agents/my-custom-agent
   ```

2. Create `_context.md` with the agent's role and behavior:
   ```markdown
   # My Custom Agent Profile
   
   You are specialized in...
   ```

3. Optionally, create `rules.json` for specific behavioral rules:
   ```json
   {
     "rule1": {
       "content": "Always validate inputs",
       "updated_at": "2024-01-01 12:00:00"
     }
   }
   ```

4. Use the profile in your configuration or tool calls:
   ```env
   SUB_AGENT_PROFILES=my-custom-agent,researcher,developer
   ```

## Docker Compose Setup

The updated docker-compose.yml includes the Memory MCP Server:

```yaml
services:
  agent-zero:
    container_name: agent-zero
    image: agent0ai/agent-zero:latest
    volumes:
      - ./agent-zero:/a0
    ports:
      - "50080:80"
    environment:
      - MEMORY_MCP_HOST=memory-mcp
      - MEMORY_MCP_PORT=3001
    depends_on:
      - memory-mcp

  memory-mcp:
    container_name: agent-zero-memory-mcp
    image: agent0ai/agent-zero:latest
    volumes:
      - ./agent-zero:/a0
    ports:
      - "3001:3001"
    command: ["python", "/a0/run_memory_mcp.py"]
```

## Troubleshooting

### Memory MCP Server Not Connecting

1. Check if the server is running:
   ```bash
   docker ps | grep memory-mcp
   ```

2. Check server logs:
   ```bash
   docker logs agent-zero-memory-mcp
   ```

3. Verify environment variables:
   ```bash
   echo $MEMORY_MCP_HOST
   echo $MEMORY_MCP_PORT
   ```

### Multi-Agent Tasks Not Executing

1. Verify multi-agent is enabled:
   ```env
   MULTI_AGENT_ENABLED=true
   ```

2. Check agent profile directories exist:
   ```bash
   ls -la agents/
   ```

3. Review agent logs for coordination errors

### Memory Search Not Finding Results

1. Check similarity threshold (lower = more results):
   ```python
   threshold=0.6  # Try lower values
   ```

2. Verify memory subdir:
   ```python
   memory_subdir="default"  # Use correct subdir
   ```

3. Check if memories were saved:
   ```python
   # List all memories
   results = await memory.search_memories(
       query="",
       threshold=0.0,
       limit=100
   )
   ```

## Examples

### Example 1: Research and Development Workflow

```python
# Complex task requiring multiple agents
task = """
Research the best practices for building a REST API,
then create a implementation plan,
and finally implement a basic API with authentication.
"""

result = await agent.use_tool(
    "multi_agent_delegation",
    task_description=task,
    agent_profiles="researcher,planner,developer",
    coordination_strategy="sequential"
)
```

### Example 2: Parallel Data Analysis

```python
# Multiple independent analysis tasks
task = """
Analyze user behavior data, sales trends, and website performance metrics
to identify opportunities for improvement.
"""

result = await agent.use_tool(
    "multi_agent_delegation",
    task_description=task,
    agent_profiles="analyst,analyst,analyst",
    coordination_strategy="parallel"
)
```

### Example 3: Using Memory MCP Server

```python
# Save project decisions
await memory_mcp.save_memory(
    content="Decided to use PostgreSQL for the main database",
    metadata={
        "area": "solutions",
        "project": "web-app",
        "category": "architecture"
    }
)

# Later, retrieve decisions
results = await memory_mcp.search_memories(
    query="database choice for web-app",
    filter='project == "web-app" and area == "solutions"',
    limit=5
)
```

## Future Enhancements

Planned improvements for the multi-agent memory system:

1. **Advanced Task Decomposition** - LLM-based task analysis and decomposition
2. **Agent Learning** - Agents learn from past executions
3. **Dynamic Agent Creation** - Create specialized agents on-demand
4. **Memory Hierarchies** - Multi-level memory organization
5. **Cross-Agent Knowledge Sharing** - Agents share insights automatically
6. **Performance Metrics** - Track agent performance and optimize
7. **Conflict Resolution** - Handle conflicting agent outputs
8. **Resource Management** - Intelligent resource allocation across agents

## Contributing

To add new agent profiles or improve the memory system:

1. Create your agent profile in `agents/`
2. Test with the multi-agent coordinator
3. Document your profile's capabilities
4. Submit a pull request

## Support

For issues or questions:
- GitHub Issues: [cbwinslow/agent-zero](https://github.com/cbwinslow/agent-zero)
- Documentation: [docs/](../docs/)
- Community: Join our Discord server
