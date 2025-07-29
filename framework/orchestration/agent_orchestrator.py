"""
Agent Orchestrator for Agent Zero.
Manages multiple agents and provides a unified interface for agent coordination.
"""

import os
import uuid
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from enum import Enum
import json

from agent import Agent, AgentConfig, AgentContext, AgentContextType
from .model_orchestrator import ModelOrchestrator, ModelCapability


class AgentRole(Enum):
    """Roles that agents can have in a multi-agent system."""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    CRITIC = "critic"
    RESEARCHER = "researcher"
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    WRITER = "writer"
    CUSTOM = "custom"


class AgentProfile:
    """Profile for an agent with its role and capabilities."""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        model_id: str,
        system_prompt: str,
        description: str = "",
        custom_tools: List[str] = None,
    ):
        self.name = name
        self.role = role
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.description = description
        self.custom_tools = custom_tools or []
        self.agent_instance: Optional[Agent] = None
        self.context_id: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent profile to a dictionary."""
        return {
            "name": self.name,
            "role": self.role.value,
            "model_id": self.model_id,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "custom_tools": self.custom_tools,
            "context_id": self.context_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProfile":
        """Create an agent profile from a dictionary."""
        profile = cls(
            name=data["name"],
            role=AgentRole(data["role"]),
            model_id=data["model_id"],
            system_prompt=data["system_prompt"],
            description=data.get("description", ""),
            custom_tools=data.get("custom_tools", []),
        )
        profile.context_id = data.get("context_id")
        return profile


class AgentOrchestrator:
    """
    Orchestrates multiple agents, providing a unified interface for agent coordination.
    """
    
    def __init__(self, model_orchestrator: ModelOrchestrator):
        self.model_orchestrator = model_orchestrator
        self.agents: Dict[str, AgentProfile] = {}
        self.default_agent_id: Optional[str] = None
        
    def register_agent(self, agent_id: str, agent_profile: AgentProfile) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent_id] = agent_profile
        if not self.default_agent_id:
            self.default_agent_id = agent_id
            
    def set_default_agent(self, agent_id: str) -> None:
        """Set the default agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        self.default_agent_id = agent_id
        
    def get_agent_profile(self, agent_id: Optional[str] = None) -> AgentProfile:
        """Get an agent profile by ID or the default agent profile."""
        agent_id = agent_id or self.default_agent_id
        if not agent_id or agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        return self.agents[agent_id]
    
    def initialize_agent(self, agent_id: str, config: AgentConfig) -> Agent:
        """Initialize an agent with the given configuration."""
        profile = self.get_agent_profile(agent_id)
        
        # Create a new context for this agent if it doesn't exist
        if not profile.context_id:
            context = AgentContext(
                config=config,
                name=profile.name,
                type=AgentContextType.TASK
            )
            profile.context_id = context.id
        else:
            context = AgentContext.get(profile.context_id)
            if not context:
                context = AgentContext(
                    config=config,
                    id=profile.context_id,
                    name=profile.name,
                    type=AgentContextType.TASK
                )
        
        # Create the agent
        agent = Agent(0, config, context)
        
        # Set the agent's model
        model = self.model_orchestrator.get_model(profile.model_id)
        agent.model = model
        
        # Set the agent's system prompt
        agent.system_prompt = profile.system_prompt
        
        # Store the agent instance
        profile.agent_instance = agent
        
        return agent
    
    def get_agent(self, agent_id: Optional[str] = None, config: Optional[AgentConfig] = None) -> Agent:
        """Get an agent by ID or the default agent."""
        agent_id = agent_id or self.default_agent_id
        if not agent_id or agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        profile = self.agents[agent_id]
        
        # If the agent is already initialized, return it
        if profile.agent_instance:
            return profile.agent_instance
        
        # Otherwise, initialize it with the provided config
        if not config:
            raise ValueError("Agent not initialized and no config provided")
        
        return self.initialize_agent(agent_id, config)
    
    def find_agents_by_role(self, role: AgentRole) -> List[Tuple[str, AgentProfile]]:
        """Find all agents with a specific role."""
        return [(agent_id, profile) for agent_id, profile in self.agents.items() 
                if profile.role == role]
    
    async def communicate(self, message: str, agent_id: Optional[str] = None) -> str:
        """Send a message to an agent and get the response."""
        agent_id = agent_id or self.default_agent_id
        if not agent_id or agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        profile = self.agents[agent_id]
        if not profile.agent_instance:
            raise ValueError(f"Agent {agent_id} not initialized")
        
        context = AgentContext.get(profile.context_id)
        if not context:
            raise ValueError(f"Context for agent {agent_id} not found")
        
        # Create a task to process the message
        task = context.communicate(message)
        
        # Wait for the task to complete
        result = await task.wait()
        return result
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [
            {"id": agent_id, **profile.to_dict()}
            for agent_id, profile in self.agents.items()
        ]
    
    def save_to_file(self, filepath: str) -> None:
        """Save the agent registry to a file."""
        with open(filepath, "w") as f:
            json.dump({
                "default_agent_id": self.default_agent_id,
                "agents": {
                    agent_id: profile.to_dict()
                    for agent_id, profile in self.agents.items()
                }
            }, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str, model_orchestrator: ModelOrchestrator) -> "AgentOrchestrator":
        """Load an agent registry from a file."""
        orchestrator = cls(model_orchestrator)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                for agent_id, agent_data in data.get("agents", {}).items():
                    orchestrator.register_agent(
                        agent_id, AgentProfile.from_dict(agent_data)
                    )
                default_agent_id = data.get("default_agent_id")
                if default_agent_id and default_agent_id in orchestrator.agents:
                    orchestrator.default_agent_id = default_agent_id
        return orchestrator