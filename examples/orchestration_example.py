"""
Example script demonstrating how to use the orchestration system.
"""

import os
import asyncio
import sys
import uuid
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.orchestration.setup import initialize_orchestration_system
from framework.orchestration.model_orchestrator import ModelCapability
from framework.orchestration.agent_orchestrator import AgentRole
from framework.orchestration.task_router import Task, TaskType, TaskPriority
from agent import AgentConfig


async def run_single_model_example(components: Dict[str, Any]):
    """Example of using a single model directly."""
    model_orchestrator = components["model_orchestrator"]
    
    print("\n=== Running Single Model Example ===")
    
    # Get a model
    model_id = "gpt-3.5-turbo"  # Use a model that's registered in the orchestrator
    print(f"Using model: {model_id}")
    
    # Call the model
    system_prompt = "You are a helpful assistant."
    user_message = "Write a short poem about artificial intelligence."
    
    print(f"Sending message: {user_message}")
    response = await model_orchestrator.call_model(
        system=system_prompt,
        message=user_message,
        model_id=model_id,
    )
    
    print(f"Response:\n{response}")


async def run_single_agent_example(components: Dict[str, Any]):
    """Example of using a single agent."""
    agent_orchestrator = components["agent_orchestrator"]
    
    print("\n=== Running Single Agent Example ===")
    
    # Get an agent
    agent_id = "writer"  # Use an agent that's registered in the orchestrator
    print(f"Using agent: {agent_id}")
    
    # Initialize the agent with a config
    config = AgentConfig()
    agent = agent_orchestrator.initialize_agent(agent_id, config)
    
    # Send a message to the agent
    message = "Write a short story about a robot that becomes self-aware."
    
    print(f"Sending message: {message}")
    response = await agent_orchestrator.communicate(message, agent_id)
    
    print(f"Response:\n{response}")


async def run_task_routing_example(components: Dict[str, Any]):
    """Example of routing a task to an appropriate agent."""
    task_router = components["task_router"]
    
    print("\n=== Running Task Routing Example ===")
    
    # Create a task
    task = Task(
        task_id=str(uuid.uuid4()),
        task_type=TaskType.CODE_GENERATION,
        description="Write a Python function to calculate the Fibonacci sequence",
        input_data={
            "language": "python",
            "requirements": "The function should be efficient and handle large numbers",
        },
        priority=TaskPriority.HIGH,
        required_capabilities=[ModelCapability.CODE_GENERATION],
        preferred_agent_role=AgentRole.CODER,
    )
    
    print(f"Created task: {task.task_id}")
    print(f"Task type: {task.task_type.value}")
    print(f"Task description: {task.description}")
    
    # Submit the task
    task_id = task_router.submit_task(task)
    
    # Process the task
    print("Processing task...")
    result = await task_router.process_task(task_id)
    
    print(f"Task status: {result['status']}")
    if result['status'] == 'completed':
        print(f"Task result:\n{result['result']['response']}")
    else:
        print(f"Task error: {result.get('result', {}).get('error', 'Unknown error')}")


async def run_team_example(components: Dict[str, Any]):
    """Example of using a team of agents."""
    team_manager = components["team_manager"]
    
    print("\n=== Running Team Example ===")
    
    # Get the default team
    team_id = "default-team"  # Use a team that's registered in the team manager
    team = team_manager.get_team(team_id)
    
    if not team:
        print(f"Team {team_id} not found")
        return
    
    print(f"Using team: {team.name}")
    print(f"Team members: {', '.join([member.role_in_team for member in team.members.values()])}")
    
    # Assign a task to the team
    task_type = TaskType.PLANNING
    description = "Create a project plan for developing a new mobile app"
    input_data = {
        "app_type": "fitness tracking",
        "target_platform": "iOS and Android",
        "timeline": "3 months",
        "team_size": "5 developers",
    }
    
    print(f"Assigning task: {description}")
    result = await team_manager.assign_task_to_team(
        team_id=team_id,
        task_type=task_type,
        description=description,
        input_data=input_data,
        priority=TaskPriority.MEDIUM,
    )
    
    print(f"Task status: {result['status']}")
    if result['status'] == 'completed':
        print(f"Task result:\n{result['result']['response']}")
    else:
        print(f"Task error: {result.get('result', {}).get('error', 'Unknown error')}")


async def main():
    """Main function to run the examples."""
    # Initialize the orchestration system
    components = initialize_orchestration_system()
    
    # Run the examples
    await run_single_model_example(components)
    await run_single_agent_example(components)
    await run_task_routing_example(components)
    await run_team_example(components)


if __name__ == "__main__":
    asyncio.run(main())