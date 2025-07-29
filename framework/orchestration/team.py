"""
Team module for Agent Zero.
Provides functionality for creating and managing teams of agents.
"""

import os
import uuid
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import json

from .model_orchestrator import ModelOrchestrator
from .agent_orchestrator import AgentOrchestrator, AgentRole, AgentProfile
from .task_router import TaskRouter, Task, TaskType, TaskPriority


class TeamMember:
    """Represents a member of a team with a specific role."""
    
    def __init__(
        self,
        agent_id: str,
        role_in_team: str,
        description: str = ""
    ):
        self.agent_id = agent_id
        self.role_in_team = role_in_team
        self.description = description
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the team member to a dictionary."""
        return {
            "agent_id": self.agent_id,
            "role_in_team": self.role_in_team,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeamMember":
        """Create a team member from a dictionary."""
        return cls(
            agent_id=data["agent_id"],
            role_in_team=data["role_in_team"],
            description=data.get("description", ""),
        )


class Team:
    """
    Represents a team of agents that can collaborate on tasks.
    """
    
    def __init__(
        self,
        team_id: str,
        name: str,
        description: str = "",
        coordinator_agent_id: Optional[str] = None,
    ):
        self.team_id = team_id
        self.name = name
        self.description = description
        self.coordinator_agent_id = coordinator_agent_id
        self.members: Dict[str, TeamMember] = {}
        
    def add_member(self, member: TeamMember) -> None:
        """Add a member to the team."""
        self.members[member.agent_id] = member
        
    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the team."""
        if agent_id in self.members:
            del self.members[agent_id]
            
    def get_member(self, agent_id: str) -> Optional[TeamMember]:
        """Get a team member by agent ID."""
        return self.members.get(agent_id)
    
    def list_members(self) -> List[Dict[str, Any]]:
        """List all team members."""
        return [member.to_dict() for member in self.members.values()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the team to a dictionary."""
        return {
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "coordinator_agent_id": self.coordinator_agent_id,
            "members": {
                agent_id: member.to_dict()
                for agent_id, member in self.members.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Team":
        """Create a team from a dictionary."""
        team = cls(
            team_id=data["team_id"],
            name=data["name"],
            description=data.get("description", ""),
            coordinator_agent_id=data.get("coordinator_agent_id"),
        )
        for agent_id, member_data in data.get("members", {}).items():
            team.members[agent_id] = TeamMember.from_dict(member_data)
        return team


class TeamManager:
    """
    Manages teams of agents and coordinates their activities.
    """
    
    def __init__(
        self,
        model_orchestrator: ModelOrchestrator,
        agent_orchestrator: AgentOrchestrator,
        task_router: TaskRouter
    ):
        self.model_orchestrator = model_orchestrator
        self.agent_orchestrator = agent_orchestrator
        self.task_router = task_router
        self.teams: Dict[str, Team] = {}
        
    def create_team(
        self,
        name: str,
        description: str = "",
        coordinator_agent_id: Optional[str] = None,
    ) -> Team:
        """Create a new team."""
        team_id = str(uuid.uuid4())
        team = Team(team_id, name, description, coordinator_agent_id)
        self.teams[team_id] = team
        return team
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[Dict[str, Any]]:
        """List all teams."""
        return [team.to_dict() for team in self.teams.values()]
    
    def delete_team(self, team_id: str) -> None:
        """Delete a team."""
        if team_id in self.teams:
            del self.teams[team_id]
            
    async def assign_task_to_team(
        self,
        team_id: str,
        task_type: TaskType,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Dict[str, Any]:
        """Assign a task to a team and coordinate the work."""
        team = self.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        # If no coordinator is set, use the first member
        coordinator_id = team.coordinator_agent_id
        if not coordinator_id and team.members:
            coordinator_id = next(iter(team.members))
        
        if not coordinator_id:
            raise ValueError(f"Team {team_id} has no coordinator or members")
        
        # Create a task for the coordinator
        coordinator_task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            description=f"Coordinate team task: {description}",
            input_data={
                "original_task": input_data,
                "team_members": team.list_members(),
            },
            priority=priority,
            preferred_agent_id=coordinator_id,
        )
        
        # Submit the task to the router
        task_id = self.task_router.submit_task(coordinator_task)
        
        # Process the task
        result = await self.task_router.process_task(task_id)
        
        return result
    
    def save_to_file(self, filepath: str) -> None:
        """Save the team registry to a file."""
        with open(filepath, "w") as f:
            json.dump({
                "teams": {
                    team_id: team.to_dict()
                    for team_id, team in self.teams.items()
                }
            }, f, indent=2)
    
    @classmethod
    def load_from_file(
        cls, 
        filepath: str, 
        model_orchestrator: ModelOrchestrator,
        agent_orchestrator: AgentOrchestrator,
        task_router: TaskRouter
    ) -> "TeamManager":
        """Load a team registry from a file."""
        manager = cls(model_orchestrator, agent_orchestrator, task_router)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                for team_id, team_data in data.get("teams", {}).items():
                    manager.teams[team_id] = Team.from_dict(team_data)
        return manager