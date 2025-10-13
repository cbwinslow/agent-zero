# Multi-Agent Delegation Tool

Use this tool to delegate complex tasks to multiple specialized agents working together.

**When to use:**
- Complex tasks requiring different expertise
- Tasks that can be broken down into parallel subtasks
- Problems requiring research, planning, development, and analysis
- When you need specialized agents for optimal results

**Available Agent Profiles:**
- **researcher**: Information gathering, research, fact-finding
- **developer**: Software development, coding, technical implementation
- **analyst**: Data analysis, pattern recognition, insights
- **planner**: Project planning, task coordination, strategy
- **executor**: Task execution, implementation, automation

**Coordination Strategies:**
- **sequential**: Agents work one after another (use for dependent tasks)
- **parallel**: Agents work simultaneously (use for independent tasks)
- **adaptive**: Automatically choose based on task structure (recommended)

**Parameters:**
- `task_description` (required): Description of the complex task
- `agent_profiles` (optional): Comma-separated list of profiles to use
- `coordination_strategy` (optional): sequential, parallel, or adaptive (default: adaptive)

**Example:**
```json
{
  "thoughts": [
    "This task requires both research and implementation",
    "I should use researcher and developer agents",
    "Sequential strategy is best since development depends on research"
  ],
  "tool_name": "multi_agent_delegation",
  "tool_args": {
    "task_description": "Research REST API best practices and implement a basic API",
    "agent_profiles": "researcher,developer",
    "coordination_strategy": "sequential"
  }
}
```

**Tips:**
- Use researcher first for information-gathering tasks
- Use planner for complex multi-step projects
- Use parallel strategy when tasks are independent
- Use adaptive strategy when unsure about dependencies
