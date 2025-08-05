# Agent Zero Orchestration Framework

The Orchestration Framework provides a powerful system for managing and coordinating multiple LLM models and agents within Agent Zero. It enables dynamic model selection, agent collaboration, and task routing based on capabilities and requirements.

## Key Components

### 1. Model Orchestrator

The Model Orchestrator manages multiple LLM models and provides a unified interface for model selection and usage.

Features:
- Register and manage multiple models from different providers
- Define model capabilities and performance characteristics
- Select models based on specific capabilities
- Optimize model selection based on cost, latency, or other factors

### 2. Agent Orchestrator

The Agent Orchestrator manages multiple agents and provides a unified interface for agent coordination.

Features:
- Register and manage multiple agents with different roles
- Initialize agents with specific configurations
- Communicate with agents and get responses
- Find agents based on roles and capabilities

### 3. Task Router

The Task Router routes tasks to appropriate agents based on task requirements and agent capabilities.

Features:
- Define tasks with specific requirements and priorities
- Route tasks to the most suitable agents
- Process tasks asynchronously
- Track task status and results

### 4. Team Manager

The Team Manager creates and manages teams of agents that can collaborate on complex tasks.

Features:
- Create teams with specific roles and responsibilities
- Assign tasks to teams and coordinate their work
- Manage team membership and roles
- Facilitate communication between team members

## Getting Started

### Basic Usage

```python
from framework.orchestration.setup import initialize_orchestration_system

# Initialize the orchestration system
components = initialize_orchestration_system()

# Access the components
model_orchestrator = components["model_orchestrator"]
agent_orchestrator = components["agent_orchestrator"]
task_router = components["task_router"]
team_manager = components["team_manager"]

# Use a model directly
response = await model_orchestrator.call_model(
    system="You are a helpful assistant.",
    message="Write a short poem about AI.",
    model_id="gpt-3.5-turbo"
)

# Use an agent
response = await agent_orchestrator.communicate(
    message="Explain quantum computing in simple terms.",
    agent_id="writer"
)

# Create and process a task
task = Task(
    task_id=str(uuid.uuid4()),
    task_type=TaskType.CODE_GENERATION,
    description="Write a Python function to calculate prime numbers",
    input_data={"language": "python"},
    priority=TaskPriority.MEDIUM,
    required_capabilities=[ModelCapability.CODE_GENERATION],
    preferred_agent_role=AgentRole.CODER,
)
task_id = task_router.submit_task(task)
result = await task_router.process_task(task_id)

# Assign a task to a team
result = await team_manager.assign_task_to_team(
    team_id="default-team",
    task_type=TaskType.PLANNING,
    description="Create a project plan for a new website",
    input_data={"project_type": "e-commerce"},
    priority=TaskPriority.HIGH,
)
```

### Custom Configuration

You can customize the orchestration system by:

1. Creating custom model profiles:
```python
from models import ModelType, ModelProvider
from framework.orchestration.model_orchestrator import ModelProfile, ModelCapability

custom_model = ModelProfile(
    provider=ModelProvider.OPENAI,
    model_name="custom-model",
    model_type=ModelType.CHAT,
    capabilities=[ModelCapability.TEXT_GENERATION],
    cost_per_1k_tokens=0.01,
    max_tokens=4096,
    typical_latency_ms=1000,
    description="Custom model for specific tasks",
)
model_orchestrator.register_model("custom-model", custom_model)
```

2. Creating custom agent profiles:
```python
from framework.orchestration.agent_orchestrator import AgentProfile, AgentRole

custom_agent = AgentProfile(
    name="Custom Agent",
    role=AgentRole.CUSTOM,
    model_id="custom-model",
    system_prompt="You are a specialized agent for custom tasks.",
    description="Handles specialized tasks",
)
agent_orchestrator.register_agent("custom-agent", custom_agent)
```

3. Creating custom teams:
```python
from framework.orchestration.team import Team, TeamMember

custom_team = Team(
    team_id="custom-team",
    name="Custom Team",
    description="A specialized team for specific tasks",
    coordinator_agent_id="coordinator",
)
custom_team.add_member(TeamMember(
    agent_id="custom-agent",
    role_in_team="Specialist",
    description="Handles specialized tasks"
))
team_manager.teams[custom_team.team_id] = custom_team
```

## Advanced Features

### Dynamic Model Selection

The Model Orchestrator can dynamically select the best model for a specific capability:

```python
model_id, model_profile = model_orchestrator.find_best_model_for_capability(
    capability=ModelCapability.CODE_GENERATION,
    prefer_low_cost=True
)
```

### Task Prioritization

The Task Router prioritizes tasks based on their priority level:

```python
task = Task(
    task_id=str(uuid.uuid4()),
    task_type=TaskType.ANALYSIS,
    description="Analyze this dataset",
    input_data={"dataset": "..."},
    priority=TaskPriority.CRITICAL,  # Will be processed before other tasks
)
```

### Team Collaboration

Teams can collaborate on complex tasks, with each agent handling a specific aspect:

```python
result = await team_manager.assign_task_to_team(
    team_id="research-team",
    task_type=TaskType.RESEARCH,
    description="Research the latest advancements in quantum computing",
    input_data={"focus_areas": ["algorithms", "hardware"]},
)
```

## Configuration and Persistence

The orchestration system can save and load configurations from files:

```python
# Save configurations
model_orchestrator.save_to_file("config/models.json")
agent_orchestrator.save_to_file("config/agents.json")
team_manager.save_to_file("config/teams.json")

# Load configurations
model_orchestrator = ModelOrchestrator.load_from_file("config/models.json")
agent_orchestrator = AgentOrchestrator.load_from_file("config/agents.json", model_orchestrator)
team_manager = TeamManager.load_from_file("config/teams.json", model_orchestrator, agent_orchestrator, task_router)
```

## Example Scripts

See the `examples/orchestration_example.py` script for a complete example of using the orchestration system.