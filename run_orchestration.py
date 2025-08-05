#!/usr/bin/env python3
"""
CLI script to demonstrate the orchestration capabilities of Agent Zero.
"""

import os
import sys
import asyncio
import argparse
import uuid
import json
from typing import Dict, Any, List, Optional

from framework.orchestrator import (
    model_orchestrator,
    agent_orchestrator,
    task_router,
    team_manager,
)
from framework.orchestration.model_orchestrator import ModelCapability
from framework.orchestration.agent_orchestrator import AgentRole
from framework.orchestration.task_router import Task, TaskType, TaskPriority
from agent import AgentConfig


async def list_models():
    """List all available models."""
    models = model_orchestrator.list_models()
    print(f"\nAvailable Models ({len(models)}):")
    print("-" * 80)
    for model in models:
        print(f"ID: {model['id']}")
        print(f"Provider: {model['provider']}")
        print(f"Name: {model['model_name']}")
        print(f"Type: {model['model_type']}")
        print(f"Capabilities: {', '.join(model['capabilities'])}")
        print(f"Cost per 1K tokens: ${model['cost_per_1k_tokens']:.4f}")
        print(f"Max tokens: {model['max_tokens']}")
        print(f"Typical latency: {model['typical_latency_ms']}ms")
        print(f"Description: {model['description']}")
        print("-" * 80)


async def list_agents():
    """List all available agents."""
    agents = agent_orchestrator.list_agents()
    print(f"\nAvailable Agents ({len(agents)}):")
    print("-" * 80)
    for agent in agents:
        print(f"ID: {agent['id']}")
        print(f"Name: {agent['name']}")
        print(f"Role: {agent['role']}")
        print(f"Model: {agent['model_id']}")
        print(f"Description: {agent['description']}")
        print("-" * 80)


async def list_teams():
    """List all available teams."""
    teams = team_manager.list_teams()
    print(f"\nAvailable Teams ({len(teams)}):")
    print("-" * 80)
    for team in teams:
        print(f"ID: {team['team_id']}")
        print(f"Name: {team['name']}")
        print(f"Description: {team['description']}")
        print(f"Coordinator: {team['coordinator_agent_id']}")
        print(f"Members: {len(team['members'])}")
        for member_id, member in team['members'].items():
            print(f"  - {member['role_in_team']} (Agent: {member_id})")
        print("-" * 80)


async def call_model(model_id: str, message: str):
    """Call a model directly."""
    print(f"\nCalling model: {model_id}")
    print(f"Message: {message}")
    print("-" * 80)
    
    response = await model_orchestrator.call_model(
        system="You are a helpful assistant.",
        message=message,
        model_id=model_id,
    )
    
    print(f"Response:\n{response}")


async def call_agent(agent_id: str, message: str):
    """Call an agent directly."""
    print(f"\nCalling agent: {agent_id}")
    print(f"Message: {message}")
    print("-" * 80)
    
    # Initialize the agent with a config if needed
    if agent_id not in agent_orchestrator.agents or not agent_orchestrator.agents[agent_id].agent_instance:
        config = AgentConfig()
        agent_orchestrator.initialize_agent(agent_id, config)
    
    response = await agent_orchestrator.communicate(message, agent_id)
    
    print(f"Response:\n{response}")


async def submit_task(
    task_type: str,
    description: str,
    input_data: Dict[str, Any],
    priority: str = "medium",
    agent_role: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Submit a task to the task router."""
    print(f"\nSubmitting task:")
    print(f"Type: {task_type}")
    print(f"Description: {description}")
    print(f"Priority: {priority}")
    if agent_role:
        print(f"Preferred agent role: {agent_role}")
    if agent_id:
        print(f"Preferred agent ID: {agent_id}")
    print(f"Input data: {json.dumps(input_data, indent=2)}")
    print("-" * 80)
    
    # Create the task
    task = Task(
        task_id=str(uuid.uuid4()),
        task_type=TaskType(task_type),
        description=description,
        input_data=input_data,
        priority=TaskPriority(priority),
        preferred_agent_role=AgentRole(agent_role) if agent_role else None,
        preferred_agent_id=agent_id,
    )
    
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


async def assign_team_task(
    team_id: str,
    task_type: str,
    description: str,
    input_data: Dict[str, Any],
    priority: str = "medium",
):
    """Assign a task to a team."""
    print(f"\nAssigning task to team: {team_id}")
    print(f"Type: {task_type}")
    print(f"Description: {description}")
    print(f"Priority: {priority}")
    print(f"Input data: {json.dumps(input_data, indent=2)}")
    print("-" * 80)
    
    # Assign the task to the team
    result = await team_manager.assign_task_to_team(
        team_id=team_id,
        task_type=TaskType(task_type),
        description=description,
        input_data=input_data,
        priority=TaskPriority(priority),
    )
    
    print(f"Task status: {result['status']}")
    if result['status'] == 'completed':
        print(f"Task result:\n{result['result']['response']}")
    else:
        print(f"Task error: {result.get('result', {}).get('error', 'Unknown error')}")


async def interactive_mode():
    """Run in interactive mode."""
    print("\nAgent Zero Orchestration System - Interactive Mode")
    print("=" * 80)
    print("Type 'help' for a list of commands, 'exit' to quit.")
    
    while True:
        try:
            command = input("\nCommand: ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                break
                
            elif command.lower() in ['help', '?', 'h']:
                print("\nAvailable commands:")
                print("  list models - List all available models")
                print("  list agents - List all available agents")
                print("  list teams - List all available teams")
                print("  call model <model_id> <message> - Call a model directly")
                print("  call agent <agent_id> <message> - Call an agent directly")
                print("  submit task - Submit a task (interactive)")
                print("  team task - Assign a task to a team (interactive)")
                print("  exit - Exit the program")
                
            elif command.lower() == 'list models':
                await list_models()
                
            elif command.lower() == 'list agents':
                await list_agents()
                
            elif command.lower() == 'list teams':
                await list_teams()
                
            elif command.lower().startswith('call model '):
                parts = command.split(' ', 3)
                if len(parts) < 4:
                    print("Usage: call model <model_id> <message>")
                else:
                    await call_model(parts[2], parts[3])
                    
            elif command.lower().startswith('call agent '):
                parts = command.split(' ', 3)
                if len(parts) < 4:
                    print("Usage: call agent <agent_id> <message>")
                else:
                    await call_agent(parts[2], parts[3])
                    
            elif command.lower() == 'submit task':
                # Interactive task submission
                task_type = input("Task type (e.g., conversation, code_generation): ").strip()
                description = input("Task description: ").strip()
                priority = input("Priority (low, medium, high, critical) [medium]: ").strip() or "medium"
                agent_role = input("Preferred agent role (optional): ").strip() or None
                agent_id = input("Preferred agent ID (optional): ").strip() or None
                
                print("Enter input data as JSON (empty line to finish):")
                input_data_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    input_data_lines.append(line)
                
                input_data_str = "\n".join(input_data_lines)
                input_data = json.loads(input_data_str) if input_data_str else {}
                
                await submit_task(
                    task_type=task_type,
                    description=description,
                    input_data=input_data,
                    priority=priority,
                    agent_role=agent_role,
                    agent_id=agent_id,
                )
                
            elif command.lower() == 'team task':
                # Interactive team task assignment
                team_id = input("Team ID: ").strip()
                task_type = input("Task type (e.g., conversation, planning): ").strip()
                description = input("Task description: ").strip()
                priority = input("Priority (low, medium, high, critical) [medium]: ").strip() or "medium"
                
                print("Enter input data as JSON (empty line to finish):")
                input_data_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    input_data_lines.append(line)
                
                input_data_str = "\n".join(input_data_lines)
                input_data = json.loads(input_data_str) if input_data_str else {}
                
                await assign_team_task(
                    team_id=team_id,
                    task_type=task_type,
                    description=description,
                    input_data=input_data,
                    priority=priority,
                )
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for a list of commands.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Agent Zero Orchestration System")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List models command
    subparsers.add_parser("list-models", help="List all available models")
    
    # List agents command
    subparsers.add_parser("list-agents", help="List all available agents")
    
    # List teams command
    subparsers.add_parser("list-teams", help="List all available teams")
    
    # Call model command
    call_model_parser = subparsers.add_parser("call-model", help="Call a model directly")
    call_model_parser.add_argument("model_id", help="ID of the model to call")
    call_model_parser.add_argument("message", help="Message to send to the model")
    
    # Call agent command
    call_agent_parser = subparsers.add_parser("call-agent", help="Call an agent directly")
    call_agent_parser.add_argument("agent_id", help="ID of the agent to call")
    call_agent_parser.add_argument("message", help="Message to send to the agent")
    
    # Submit task command
    submit_task_parser = subparsers.add_parser("submit-task", help="Submit a task")
    submit_task_parser.add_argument("task_type", help="Type of task (e.g., conversation, code_generation)")
    submit_task_parser.add_argument("description", help="Description of the task")
    submit_task_parser.add_argument("--input-data", help="Input data for the task (JSON string)", default="{}")
    submit_task_parser.add_argument("--priority", help="Priority of the task", choices=["low", "medium", "high", "critical"], default="medium")
    submit_task_parser.add_argument("--agent-role", help="Preferred agent role", default=None)
    submit_task_parser.add_argument("--agent-id", help="Preferred agent ID", default=None)
    
    # Assign team task command
    team_task_parser = subparsers.add_parser("team-task", help="Assign a task to a team")
    team_task_parser.add_argument("team_id", help="ID of the team")
    team_task_parser.add_argument("task_type", help="Type of task (e.g., conversation, planning)")
    team_task_parser.add_argument("description", help="Description of the task")
    team_task_parser.add_argument("--input-data", help="Input data for the task (JSON string)", default="{}")
    team_task_parser.add_argument("--priority", help="Priority of the task", choices=["low", "medium", "high", "critical"], default="medium")
    
    # Interactive mode command
    subparsers.add_parser("interactive", help="Run in interactive mode")
    
    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_args()
    
    if args.command == "list-models":
        await list_models()
    elif args.command == "list-agents":
        await list_agents()
    elif args.command == "list-teams":
        await list_teams()
    elif args.command == "call-model":
        await call_model(args.model_id, args.message)
    elif args.command == "call-agent":
        await call_agent(args.agent_id, args.message)
    elif args.command == "submit-task":
        await submit_task(
            task_type=args.task_type,
            description=args.description,
            input_data=json.loads(args.input_data),
            priority=args.priority,
            agent_role=args.agent_role,
            agent_id=args.agent_id,
        )
    elif args.command == "team-task":
        await assign_team_task(
            team_id=args.team_id,
            task_type=args.task_type,
            description=args.description,
            input_data=json.loads(args.input_data),
            priority=args.priority,
        )
    elif args.command == "interactive" or not args.command:
        await interactive_mode()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())