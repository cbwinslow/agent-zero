# CrewAI Integration

Agent Zero now supports CrewAI for managing multi-agent crews to tackle complex tasks.

## Overview

CrewAI integration allows Agent Zero to:
- Create and configure multi-agent crews
- Define specialized agents with specific roles
- Assign tasks to agents
- Monitor crew execution
- Save and reuse crew configurations

## Quick Start

### 1. List Available Templates

```bash
curl -X POST http://localhost:50001/api/crew_templates
```

Available templates:
- **research**: Research and analysis crew
- **development**: Software development crew
- **content_creation**: Content writing and editing crew

### 2. Create a Crew from Template

```bash
curl -X POST http://localhost:50001/api/crew_create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_research_crew",
    "template": "research"
  }'
```

### 3. Run the Crew

```bash
curl -X POST http://localhost:50001/api/crew_run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_research_crew",
    "inputs": {
      "topic": "Latest developments in AI"
    }
  }'
```

## Using the CrewAI Tool

Agent Zero can use CrewAI through its tool interface:

```python
# List available crews
response = await agent.use_tool("crewai", action="list")

# Create a crew from template
response = await agent.use_tool(
    "crewai",
    action="create",
    template="research",
    name="my_research_crew"
)

# Run a crew
response = await agent.use_tool(
    "crewai",
    action="run",
    name="my_research_crew",
    inputs={"topic": "AI trends"}
)
```

## Creating Custom Crews

### Define Agents

Each agent has:
- **Role**: What the agent does
- **Goal**: What the agent aims to achieve
- **Backstory**: Context and expertise

```json
{
  "name": "custom_crew",
  "description": "My custom crew",
  "agents": [
    {
      "role": "Data Scientist",
      "goal": "Analyze data and create insights",
      "backstory": "You are an experienced data scientist with expertise in ML"
    }
  ]
}
```

### Define Tasks

Each task has:
- **Description**: What needs to be done
- **Agent**: Which agent performs it
- **Expected Output**: What the result should look like

```json
{
  "tasks": [
    {
      "description": "Analyze the dataset: {dataset}",
      "agent": "Data Scientist",
      "expected_output": "Statistical analysis report with visualizations"
    }
  ]
}
```

## Crew Templates

### Research Crew

**Agents:**
- Researcher: Gathers information
- Analyst: Analyzes findings

**Use Case:** Research topics, gather information, create reports

**Example:**
```json
{
  "name": "market_research",
  "template": "research",
  "inputs": {
    "topic": "Electric vehicle market trends"
  }
}
```

### Development Crew

**Agents:**
- Software Architect: Designs architecture
- Developer: Implements code
- QA Engineer: Tests quality

**Use Case:** Build software projects, create applications

**Example:**
```json
{
  "name": "web_app_dev",
  "template": "development",
  "inputs": {
    "project_description": "E-commerce website with React and Node.js"
  }
}
```

### Content Creation Crew

**Agents:**
- Content Writer: Creates content
- Editor: Reviews and improves

**Use Case:** Write articles, create documentation

**Example:**
```json
{
  "name": "blog_writing",
  "template": "content_creation",
  "inputs": {
    "topic": "Getting started with Agent Zero"
  }
}
```

## API Endpoints

### GET /api/crew_list
List all crew configurations.

### GET /api/crew_templates
List available crew templates.

### POST /api/crew_create
Create a new crew.

**Request:**
```json
{
  "name": "my_crew",
  "template": "research"
}
```

### POST /api/crew_get
Get crew configuration details.

**Request:**
```json
{
  "name": "my_crew"
}
```

### POST /api/crew_run
Run a crew.

**Request:**
```json
{
  "name": "my_crew",
  "inputs": {
    "topic": "AI trends"
  }
}
```

### POST /api/crew_delete
Delete a crew configuration.

**Request:**
```json
{
  "name": "my_crew"
}
```

### GET /api/crew_active_list
List currently running crews.

## Advanced Features

### Sequential vs Hierarchical Process

**Sequential**: Tasks execute one after another
```python
config.process = "sequential"
```

**Hierarchical**: Manager agent coordinates other agents
```python
config.process = "hierarchical"
```

### Agent Delegation

Allow agents to delegate tasks:
```python
agent_config.allow_delegation = True
```

### Async Task Execution

Run tasks asynchronously:
```python
task_config.async_execution = True
```

## Monitoring

### View Active Crews

```bash
curl -X GET http://localhost:50001/api/crew_active_list
```

### Check Logs

Crew execution is logged in Agent Zero's log system with detailed progress information.

## Best Practices

1. **Use Templates**: Start with templates and customize as needed
2. **Clear Goals**: Define clear agent goals and tasks
3. **Specific Tasks**: Make task descriptions specific and actionable
4. **Expected Outputs**: Define clear expected outputs
5. **Test First**: Test crews with simple inputs before complex tasks

## Integration with Agent Zero

CrewAI crews inherit Agent Zero's LLM configuration, ensuring consistent behavior and model usage.

### Memory Integration

Crews can access Agent Zero's memory system for context.

### Tool Integration

Crews can use Agent Zero's tools for enhanced capabilities.

## Troubleshooting

**Problem**: Crew fails to start
**Solution**: Check agent roles and task descriptions are properly defined

**Problem**: Tasks take too long
**Solution**: Break down complex tasks into smaller subtasks

**Problem**: Crew not found
**Solution**: Verify crew name and use `crew_list` to see available crews

## Examples

### Research Crew Example

```python
# Create research crew
crew_mgr.save_config(CrewConfig(
    name="ai_research",
    description="AI research and analysis",
    agents=[
        AgentConfig(
            role="AI Researcher",
            goal="Research latest AI developments",
            backstory="Expert in AI with 10+ years experience"
        ),
        AgentConfig(
            role="Report Writer",
            goal="Create comprehensive reports",
            backstory="Technical writer specializing in AI"
        )
    ],
    tasks=[
        TaskConfig(
            description="Research: {topic}",
            agent="AI Researcher",
            expected_output="Research findings with sources"
        ),
        TaskConfig(
            description="Write report from research",
            agent="Report Writer",
            expected_output="Publication-ready report"
        )
    ]
))

# Run the crew
result = await crew_mgr.run_crew(
    "ai_research",
    inputs={"topic": "Large Language Models 2024"}
)
```

## Future Enhancements

Planned features:
- Crew templates marketplace
- Visual crew builder
- Crew performance analytics
- Multi-crew orchestration
- Crew versioning
- Shared crew library

## Support

For issues or questions:
- GitHub Issues: https://github.com/agent0ai/agent-zero/issues
- Documentation: /docs/
- Discord: https://discord.gg/B8KZKNsPpj
