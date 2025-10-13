from agent import Agent
from python.helpers.tool import Tool, Response
from python.helpers.multi_agent_coordinator import (
    MultiAgentCoordinator,
    TaskDecomposer,
    AgentTask,
    CoordinationStrategy
)
from python.helpers import dotenv
import os


class MultiAgentDelegation(Tool):
    """
    Tool for delegating complex tasks to multiple specialized agents
    """
    
    async def execute(
        self,
        task_description: str = "",
        agent_profiles: str = "",
        coordination_strategy: str = "adaptive",
        **kwargs
    ):
        """
        Execute a task using multiple specialized agents
        
        Args:
            task_description: Description of the complex task to solve
            agent_profiles: Comma-separated list of agent profiles to use
                           (e.g., "researcher,developer,analyst")
            coordination_strategy: How to coordinate agents: sequential, parallel, or adaptive
        """
        
        # Check if multi-agent is enabled
        multi_agent_enabled = dotenv.get_dotenv_value("MULTI_AGENT_ENABLED", "true")
        if multi_agent_enabled.lower() != "true":
            return Response(
                message="Multi-agent mode is disabled. Enable it in .env to use this feature.",
                break_loop=False
            )
        
        # Get max agents from environment
        max_agents = int(dotenv.get_dotenv_value("MAX_SUB_AGENTS", "5"))
        
        # Parse agent profiles
        if agent_profiles:
            profiles = [p.strip() for p in agent_profiles.split(",")]
        else:
            # Use default profiles from environment
            default_profiles = dotenv.get_dotenv_value(
                "SUB_AGENT_PROFILES",
                "researcher,developer,analyst"
            )
            profiles = [p.strip() for p in default_profiles.split(",")]
        
        # Parse coordination strategy
        try:
            strategy = CoordinationStrategy[coordination_strategy.upper()]
        except KeyError:
            strategy = CoordinationStrategy.ADAPTIVE
        
        # Create coordinator
        coordinator = MultiAgentCoordinator(self.agent.context, max_agents=max_agents)
        
        # Decompose task into subtasks
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(task_description, profiles)
        
        # Log the coordination
        log_item = self.agent.context.log.log(
            type="tool",
            heading=f"icon://communication Multi-Agent Coordination: {len(tasks)} agents",
            content=f"Task: {task_description}\nProfiles: {', '.join(profiles)}\nStrategy: {strategy.value}",
            kvps={
                "task": task_description,
                "agents": len(tasks),
                "strategy": strategy.value
            }
        )
        
        try:
            # Execute coordination
            results = await coordinator.coordinate(tasks, strategy)
            
            # Synthesize results
            synthesis = coordinator.synthesize_results()
            
            # Update log
            if log_item:
                log_item.update(
                    content=f"Coordination completed with {len(results)} agents",
                )
            
            return Response(
                message=synthesis,
                break_loop=False
            )
            
        except Exception as e:
            if log_item:
                log_item.update(
                    content=f"Error during coordination: {str(e)}",
                )
            return Response(
                message=f"Error during multi-agent coordination: {str(e)}",
                break_loop=False
            )
    
    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://communication {self.agent.agent_name}: Multi-Agent Delegation",
            content="",
            kvps=self.args,
        )
