# Agent Zero Multi-Agent Memory System - Integration Guide

This guide explains how to integrate the multi-agent memory system into your Agent Zero workflows.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Integration Points](#integration-points)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Advanced Features](#advanced-features)
6. [Performance Tuning](#performance-tuning)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

The multi-agent memory system consists of three main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
│  (Web UI, CLI, API endpoints for user interaction)           │
└──────────────────────┬────────────────────────────────────────┘
                       │
┌──────────────────────┴────────────────────────────────────────┐
│                  Coordination Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Main Agent   │  │ Multi-Agent  │  │ Task         │       │
│  │ (Agent 0)    │──│ Coordinator  │──│ Decomposer   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────┬────────────────────────────────────────┘
                       │
┌──────────────────────┴────────────────────────────────────────┐
│               Specialized Agents Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Researcher│ │Developer │ │ Analyst  │ │ Planner  │ ...    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└──────────────────────┬────────────────────────────────────────┘
                       │
┌──────────────────────┴────────────────────────────────────────┐
│                  Memory & Storage Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Memory MCP   │  │ Vector DB    │  │ Knowledge    │       │
│  │ Server       │──│ (FAISS)      │──│ Base         │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Direct Tool Usage

Use the `multi_agent_delegation` tool in your agent conversations:

```python
# In an agent conversation
result = await agent.use_tool(
    "multi_agent_delegation",
    task_description="Your complex task here",
    agent_profiles="researcher,developer",
    coordination_strategy="adaptive"
)
```

### 2. Programmatic Integration

Use the coordinator directly in your Python code:

```python
from python.helpers.multi_agent_coordinator import (
    MultiAgentCoordinator,
    AgentTask,
    CoordinationStrategy
)

# Create coordinator
coordinator = MultiAgentCoordinator(context, max_agents=5)

# Define tasks
tasks = [
    AgentTask(
        agent_profile="researcher",
        message="Research machine learning frameworks",
        priority=1
    ),
    AgentTask(
        agent_profile="analyst",
        message="Compare the research findings",
        priority=2
    ),
]

# Execute
results = await coordinator.coordinate(
    tasks,
    CoordinationStrategy.SEQUENTIAL
)
```

### 3. Memory MCP Server Integration

Access the memory server through MCP tools:

```python
# Save a memory
await memory_mcp_tool(
    "save_memory",
    content="Important decision: Use PostgreSQL",
    metadata={"project": "web-app", "importance": "high"}
)

# Search memories
results = await memory_mcp_tool(
    "search_memories",
    query="database decisions",
    limit=10,
    threshold=0.7
)

# Compress memories
await memory_mcp_tool(
    "compress_memories",
    memory_subdir="default",
    threshold=0.9
)
```

## Configuration

### Environment Variables

Create a `.env` file with these settings:

```env
# LLM Providers
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

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
KNOWLEDGE_AUTO_IMPORT=true
```

### Agent Configuration in Settings UI

1. Open Agent Zero Settings
2. Navigate to "MCP Servers"
3. Add the memory server configuration:

```json
{
  "name": "memory-manager",
  "description": "Memory management server",
  "type": "stdio",
  "command": "python",
  "args": ["/path/to/run_memory_mcp.py"],
  "env": {
    "MEMORY_MCP_HOST": "localhost",
    "MEMORY_MCP_PORT": "3001"
  }
}
```

## Usage Examples

### Example 1: Research and Development Workflow

```python
# Complex development task with multiple phases
task = """
I need to build a REST API for user management.

Requirements:
1. Research best practices for REST API design
2. Plan the architecture and endpoints
3. Implement the API with authentication
4. Create comprehensive tests
5. Document the API
"""

result = await agent.use_tool(
    "multi_agent_delegation",
    task_description=task,
    agent_profiles="researcher,planner,developer,executor",
    coordination_strategy="sequential"
)

# The system will:
# 1. Researcher gathers REST API best practices
# 2. Planner designs architecture
# 3. Developer implements the API
# 4. Executor runs tests and creates documentation
```

### Example 2: Data Analysis Pipeline

```python
# Parallel data analysis
task = """
Analyze our Q4 data across three dimensions:
1. Customer behavior patterns
2. Sales trends by region
3. Product performance metrics

Create a consolidated report with recommendations.
"""

result = await agent.use_tool(
    "multi_agent_delegation",
    task_description=task,
    agent_profiles="analyst,analyst,analyst",
    coordination_strategy="parallel"
)

# Three analyst agents work in parallel, then results are synthesized
```

### Example 3: Memory Management

```python
# Save important project decisions
await memory_mcp.save_memory(
    content="Decided to use microservices architecture for scalability",
    metadata={
        "area": "solutions",
        "project": "web-platform",
        "category": "architecture",
        "importance": "critical",
        "date": "2024-01-15"
    }
)

# Later, retrieve context for new decisions
memories = await memory_mcp.search_memories(
    query="architecture decisions for web-platform",
    filter='project == "web-platform" and area == "solutions"',
    limit=5,
    threshold=0.75
)

# Use memories to inform new decisions
for memory in memories:
    print(f"Previous decision: {memory['content']}")
```

### Example 4: Knowledge Base Organization

```python
# Store code template in fragments
await memory_mcp.save_knowledge(
    content="""
# FastAPI Endpoint Template
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    # Implementation here
    pass
""",
    filename="fastapi_endpoint_template.md",
    area="fragments",
    knowledge_subdir="project-templates"
)

# Store solution for future reference
await memory_mcp.save_knowledge(
    content="""
# Solution: Rate Limiting in FastAPI

Problem: API was being overwhelmed with requests
Solution: Implemented token bucket rate limiter
Result: 99.9% uptime achieved

Implementation:
[code here]
""",
    filename="rate_limiting_solution.md",
    area="solutions"
)
```

## Advanced Features

### 1. Custom Agent Profiles

Create specialized agents for your domain:

```bash
# Create new profile directory
mkdir agents/security-expert

# Create context file
cat > agents/security-expert/_context.md << 'EOF'
# Security Expert Agent

You are a specialized security analyst focused on:
- Identifying security vulnerabilities
- Recommending security best practices
- Reviewing code for security issues
- Implementing security measures

Your analysis should be thorough and include:
- Threat assessment
- Risk evaluation
- Mitigation strategies
- Implementation guidance
EOF

# Use in configuration
echo "SUB_AGENT_PROFILES=security-expert,developer" >> .env
```

### 2. Task Dependencies

Define complex workflows with dependencies:

```python
tasks = [
    AgentTask(
        agent_profile="researcher",
        message="Research OAuth 2.0 implementation",
        priority=0,
        depends_on=[]
    ),
    AgentTask(
        agent_profile="planner",
        message="Plan OAuth integration architecture",
        priority=1,
        depends_on=["researcher_0"]  # Wait for research
    ),
    AgentTask(
        agent_profile="developer",
        message="Implement OAuth 2.0",
        priority=2,
        depends_on=["planner_1"]  # Wait for plan
    ),
]

results = await coordinator.coordinate(tasks, CoordinationStrategy.ADAPTIVE)
```

### 3. Memory Compression Strategies

Implement intelligent memory management:

```python
# Regular compression to maintain performance
async def compress_project_memories():
    # Compress old memories
    await memory_mcp.compress_memories(
        memory_subdir="project-memories",
        threshold=0.95,  # High threshold for safety
        max_results=500
    )
    
    # Archive very old memories to separate area
    old_memories = await memory_mcp.search_memories(
        query="",
        filter='timestamp < "2023-01-01"',
        limit=1000
    )
    
    # Move to archive
    for memory in old_memories:
        await memory_mcp.save_memory(
            content=memory["content"],
            metadata={**memory["metadata"], "archived": True},
            memory_subdir="archive"
        )
        await memory_mcp.delete_memories(ids=[memory["id"]])
```

### 4. Custom Coordination Strategies

Extend the coordinator with custom logic:

```python
class CustomCoordinator(MultiAgentCoordinator):
    async def execute_priority_based(self, tasks: List[AgentTask]):
        """Execute tasks based on priority scores"""
        # Sort by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        # Execute high priority first
        high_priority = [t for t in sorted_tasks if t.priority >= 2]
        low_priority = [t for t in sorted_tasks if t.priority < 2]
        
        results = {}
        
        # High priority in parallel
        if high_priority:
            results.update(await self.execute_parallel(high_priority))
        
        # Low priority sequentially
        if low_priority:
            results.update(await self.execute_sequential(low_priority))
        
        return results
```

## Performance Tuning

### 1. Optimize Memory Operations

```python
# Batch operations for efficiency
async def batch_save_memories(memories: List[Dict]):
    tasks = [
        memory_mcp.save_memory(
            content=m["content"],
            metadata=m["metadata"]
        )
        for m in memories
    ]
    return await asyncio.gather(*tasks)
```

### 2. Configure Resource Limits

```env
# Limit concurrent agents
MAX_SUB_AGENTS=3

# Adjust memory thresholds
MEMORY_COMPRESSION_THRESHOLD=0.85
MEMORY_MAX_SIZE=5000

# Configure search limits
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
```

### 3. Monitor Performance

```python
import time

async def monitored_coordination(coordinator, tasks):
    start = time.time()
    
    results = await coordinator.coordinate(tasks)
    
    duration = time.time() - start
    print(f"Coordination completed in {duration:.2f}s")
    print(f"Tasks processed: {len(results)}")
    print(f"Average per task: {duration/len(results):.2f}s")
    
    return results
```

## Troubleshooting

### Issue: Memory MCP Server Not Responding

**Symptoms**: Timeouts when accessing memory functions

**Solutions**:
1. Check server status: `docker ps | grep memory-mcp`
2. View logs: `docker logs agent-zero-memory-mcp`
3. Restart server: `docker-compose restart memory-mcp`
4. Check port availability: `netstat -an | grep 3001`

### Issue: Multi-Agent Tasks Failing

**Symptoms**: Agents not executing or returning errors

**Solutions**:
1. Verify profiles exist: `ls agents/`
2. Check environment variable: `echo $MULTI_AGENT_ENABLED`
3. Review agent logs for errors
4. Reduce `MAX_SUB_AGENTS` if resource constrained

### Issue: Memory Compression Taking Too Long

**Symptoms**: Compression operations timeout

**Solutions**:
1. Reduce `max_results` parameter
2. Increase `threshold` to process fewer memories
3. Run compression during low-usage periods
4. Use incremental compression

### Issue: Docker Compose Network Issues

**Symptoms**: Services can't communicate

**Solutions**:
1. Check network: `docker network ls`
2. Verify service names in compose file
3. Use service names for communication (not localhost)
4. Restart entire stack: `docker-compose down && docker-compose up -d`

## Best Practices

### 1. Memory Organization

- Use consistent metadata schemas
- Tag memories with project identifiers
- Set importance levels for filtering
- Regular compression schedules

### 2. Agent Coordination

- Start with adaptive strategy
- Use sequential for dependent tasks
- Use parallel for independent analysis
- Limit concurrent agents based on resources

### 3. Knowledge Management

- Organize by area (main, fragments, solutions, instruments)
- Version important knowledge entries
- Include usage examples in documentation
- Regular review and cleanup

### 4. Error Handling

```python
try:
    result = await coordinator.coordinate(tasks)
except asyncio.TimeoutError:
    # Handle timeout
    print("Coordination timed out, retrying with fewer tasks...")
    result = await coordinator.coordinate(tasks[:2])
except Exception as e:
    # Handle other errors
    print(f"Error: {e}")
    # Fallback to single agent
    result = await single_agent_fallback(task_description)
```

## Next Steps

1. Review [full documentation](multi_agent_memory_system.md)
2. Try [quick start examples](../QUICK_START_MULTI_AGENT.md)
3. Explore [agent profiles](../agents/)
4. Join community discussions

## Support Resources

- **Documentation**: `/docs/` directory
- **Examples**: See usage examples above
- **Community**: Discord server
- **Issues**: GitHub issue tracker

---

For more information, see the [Multi-Agent Memory System documentation](multi_agent_memory_system.md).
