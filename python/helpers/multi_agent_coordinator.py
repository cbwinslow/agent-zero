"""
Multi-Agent Coordinator for Agent Zero
Manages multiple specialized agents working together on complex tasks
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

from agent import Agent, AgentContext, UserMessage, AgentConfig
from initialize import initialize_agent
from python.helpers.print_style import PrintStyle

_PRINTER = PrintStyle(italic=True, font_color="magenta", padding=False)


class CoordinationStrategy(Enum):
    """Strategies for coordinating multiple agents"""
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"      # Agents work simultaneously
    ADAPTIVE = "adaptive"      # Choose strategy based on task


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    agent_profile: str
    message: str
    priority: int = 0
    depends_on: List[str] = None  # Task IDs this depends on
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class MultiAgentCoordinator:
    """Coordinates multiple specialized agents working on a problem"""
    
    def __init__(self, context: AgentContext, max_agents: int = 5):
        self.context = context
        self.max_agents = max_agents
        self.agents: Dict[str, Agent] = {}
        self.results: Dict[str, str] = {}
        
    def create_agent(self, profile: str, agent_id: str) -> Agent:
        """Create a specialized agent with the given profile"""
        _PRINTER.print(f"Creating {profile} agent with ID: {agent_id}")
        
        # Initialize agent config with the specified profile
        config = initialize_agent()
        config.profile = profile
        
        # Create agent as a subordinate of the main agent
        agent = Agent(len(self.agents) + 1, config, self.context)
        
        # Store agent
        self.agents[agent_id] = agent
        
        return agent
    
    async def execute_task(self, agent_id: str, task: AgentTask) -> str:
        """Execute a task with a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            agent = self.create_agent(task.agent_profile, agent_id)
        
        _PRINTER.print(f"Agent {agent_id} ({task.agent_profile}) executing task")
        
        # Add user message to agent
        agent.hist_add_user_message(UserMessage(message=task.message, attachments=[]))
        
        # Run agent monologue
        result = await agent.monologue()
        
        # Store result
        self.results[agent_id] = result
        
        return result
    
    async def execute_sequential(self, tasks: List[AgentTask]) -> Dict[str, str]:
        """Execute tasks sequentially"""
        _PRINTER.print(f"Executing {len(tasks)} tasks sequentially")
        
        results = {}
        for i, task in enumerate(tasks):
            agent_id = f"{task.agent_profile}_{i}"
            result = await self.execute_task(agent_id, task)
            results[agent_id] = result
            
        return results
    
    async def execute_parallel(self, tasks: List[AgentTask]) -> Dict[str, str]:
        """Execute tasks in parallel"""
        _PRINTER.print(f"Executing {len(tasks)} tasks in parallel")
        
        # Create tasks for asyncio
        async_tasks = []
        agent_ids = []
        
        for i, task in enumerate(tasks):
            agent_id = f"{task.agent_profile}_{i}"
            agent_ids.append(agent_id)
            async_tasks.append(self.execute_task(agent_id, task))
        
        # Execute all tasks concurrently
        results_list = await asyncio.gather(*async_tasks)
        
        # Combine results
        results = dict(zip(agent_ids, results_list))
        
        return results
    
    async def execute_adaptive(self, tasks: List[AgentTask]) -> Dict[str, str]:
        """Execute tasks with adaptive strategy based on dependencies"""
        _PRINTER.print(f"Executing {len(tasks)} tasks with adaptive strategy")
        
        # Separate tasks into groups based on dependencies
        independent_tasks = [t for t in tasks if not t.depends_on]
        dependent_tasks = [t for t in tasks if t.depends_on]
        
        results = {}
        
        # Execute independent tasks in parallel
        if independent_tasks:
            parallel_results = await self.execute_parallel(independent_tasks)
            results.update(parallel_results)
        
        # Execute dependent tasks sequentially or in waves
        if dependent_tasks:
            sequential_results = await self.execute_sequential(dependent_tasks)
            results.update(sequential_results)
        
        return results
    
    async def coordinate(
        self,
        tasks: List[AgentTask],
        strategy: CoordinationStrategy = CoordinationStrategy.ADAPTIVE
    ) -> Dict[str, str]:
        """Coordinate execution of multiple agent tasks"""
        
        if not tasks:
            return {}
        
        # Validate max agents constraint
        if len(tasks) > self.max_agents:
            _PRINTER.print(
                f"Warning: {len(tasks)} tasks exceed max agents limit of {self.max_agents}. "
                f"Tasks will be batched."
            )
        
        # Execute based on strategy
        if strategy == CoordinationStrategy.SEQUENTIAL:
            return await self.execute_sequential(tasks)
        elif strategy == CoordinationStrategy.PARALLEL:
            return await self.execute_parallel(tasks)
        else:  # ADAPTIVE
            return await self.execute_adaptive(tasks)
    
    def synthesize_results(self) -> str:
        """Combine results from all agents into a coherent response"""
        if not self.results:
            return "No results to synthesize"
        
        synthesis = "# Multi-Agent Results\n\n"
        
        for agent_id, result in self.results.items():
            synthesis += f"## {agent_id}\n\n{result}\n\n"
        
        return synthesis


class TaskDecomposer:
    """Decomposes complex tasks into subtasks for specialized agents"""
    
    @staticmethod
    def decompose(task_description: str, available_profiles: List[str]) -> List[AgentTask]:
        """
        Decompose a complex task into subtasks for different agent profiles.
        This is a simple implementation - in production, this would use an LLM.
        """
        tasks = []
        
        # Simple keyword-based decomposition (placeholder)
        task_lower = task_description.lower()
        
        if "research" in task_lower or "find" in task_lower or "search" in task_lower:
            if "researcher" in available_profiles:
                tasks.append(AgentTask(
                    agent_profile="researcher",
                    message=f"Research: {task_description}",
                    priority=1
                ))
        
        if "code" in task_lower or "implement" in task_lower or "develop" in task_lower:
            if "developer" in available_profiles:
                tasks.append(AgentTask(
                    agent_profile="developer",
                    message=f"Develop: {task_description}",
                    priority=2
                ))
        
        if "analyze" in task_lower or "evaluate" in task_lower or "assess" in task_lower:
            if "analyst" in available_profiles:
                tasks.append(AgentTask(
                    agent_profile="analyst",
                    message=f"Analyze: {task_description}",
                    priority=1
                ))
        
        if "plan" in task_lower or "organize" in task_lower or "coordinate" in task_lower:
            if "planner" in available_profiles:
                tasks.append(AgentTask(
                    agent_profile="planner",
                    message=f"Plan: {task_description}",
                    priority=0
                ))
        
        # If no specific tasks identified, create a general task
        if not tasks:
            # Use first available profile or default
            profile = available_profiles[0] if available_profiles else "default"
            tasks.append(AgentTask(
                agent_profile=profile,
                message=task_description,
                priority=0
            ))
        
        return tasks


# Export main classes
__all__ = ["MultiAgentCoordinator", "TaskDecomposer", "AgentTask", "CoordinationStrategy"]
