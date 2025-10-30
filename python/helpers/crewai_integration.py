"""
CrewAI Integration for Agent Zero
Allows Agent Zero to create, configure, and manage CrewAI crews

Features:
- Create and configure crews
- Define agents and tasks
- Execute crews and monitor progress
- Save and load crew configurations
- Integration with Agent Zero's LLM configuration
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

try:
    from crewai import Agent as CrewAgent, Task, Crew, Process
    from crewai_tools import Tool as CrewTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Define dummy classes for type hints
    class CrewAgent:
        pass
    class Task:
        pass
    class Crew:
        pass
    class Process:
        pass
    class CrewTool:
        pass

from python.helpers import files
from agent import Agent as A0Agent


@dataclass
class AgentConfig:
    """Configuration for a CrewAI agent"""
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = True
    tools: List[str] = field(default_factory=list)
    llm_config: Dict = field(default_factory=dict)


@dataclass
class TaskConfig:
    """Configuration for a CrewAI task"""
    description: str
    agent: str  # Agent role name
    expected_output: str
    context: List[str] = field(default_factory=list)  # Other task descriptions
    async_execution: bool = False
    tools: List[str] = field(default_factory=list)


@dataclass
class CrewConfig:
    """Configuration for a CrewAI crew"""
    name: str
    description: str
    agents: List[AgentConfig] = field(default_factory=list)
    tasks: List[TaskConfig] = field(default_factory=list)
    process: str = "sequential"  # sequential or hierarchical
    verbose: int = 2
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "agent-zero"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "agents": [
                {
                    "role": a.role,
                    "goal": a.goal,
                    "backstory": a.backstory,
                    "verbose": a.verbose,
                    "allow_delegation": a.allow_delegation,
                    "tools": a.tools,
                    "llm_config": a.llm_config
                }
                for a in self.agents
            ],
            "tasks": [
                {
                    "description": t.description,
                    "agent": t.agent,
                    "expected_output": t.expected_output,
                    "context": t.context,
                    "async_execution": t.async_execution,
                    "tools": t.tools
                }
                for t in self.tasks
            ],
            "process": self.process,
            "verbose": self.verbose,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CrewConfig':
        return CrewConfig(
            name=data["name"],
            description=data["description"],
            agents=[
                AgentConfig(
                    role=a["role"],
                    goal=a["goal"],
                    backstory=a["backstory"],
                    verbose=a.get("verbose", True),
                    allow_delegation=a.get("allow_delegation", True),
                    tools=a.get("tools", []),
                    llm_config=a.get("llm_config", {})
                )
                for a in data.get("agents", [])
            ],
            tasks=[
                TaskConfig(
                    description=t["description"],
                    agent=t["agent"],
                    expected_output=t["expected_output"],
                    context=t.get("context", []),
                    async_execution=t.get("async_execution", False),
                    tools=t.get("tools", [])
                )
                for t in data.get("tasks", [])
            ],
            process=data.get("process", "sequential"),
            verbose=data.get("verbose", 2),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            created_by=data.get("created_by", "agent-zero")
        )


class CrewManager:
    """Manages CrewAI crews for Agent Zero"""
    
    def __init__(self, agent: A0Agent):
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI is not installed. Install with: pip install crewai crewai-tools")
        
        self.agent = agent
        self.configs: Dict[str, CrewConfig] = {}
        self.active_crews: Dict[str, Crew] = {}
        self._load_configs()
    
    def _get_configs_dir(self) -> str:
        """Get directory for crew configurations"""
        from python.helpers import memory
        memory_dir = memory.get_memory_subdir_abs(self.agent)
        crews_dir = f"{memory_dir}/crews"
        os.makedirs(crews_dir, exist_ok=True)
        return crews_dir
    
    def _load_configs(self):
        """Load crew configurations from disk"""
        configs_dir = self._get_configs_dir()
        
        for filename in os.listdir(configs_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(configs_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    config = CrewConfig.from_dict(data)
                    self.configs[config.name] = config
    
    def _save_config(self, config: CrewConfig):
        """Save crew configuration to disk"""
        configs_dir = self._get_configs_dir()
        filepath = os.path.join(configs_dir, f"{config.name}.json")
        
        with open(filepath, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
    
    def _get_llm(self):
        """Get LLM configuration from Agent Zero"""
        from python.helpers import call_llm
        
        # Use Agent Zero's LLM configuration
        # This ensures consistency with the main agent
        model_config = self.agent.config.chat_model
        
        # Create LiteLLM-compatible LLM instance
        # CrewAI uses LiteLLM internally, so we can pass model name directly
        return model_config.name
    
    def create_crew(self, config: CrewConfig) -> Crew:
        """Create a Crew from configuration"""
        llm_name = self._get_llm()
        
        # Create agents
        agents_map = {}
        for agent_config in config.agents:
            crew_agent = CrewAgent(
                role=agent_config.role,
                goal=agent_config.goal,
                backstory=agent_config.backstory,
                verbose=agent_config.verbose,
                allow_delegation=agent_config.allow_delegation,
                llm=llm_name
            )
            agents_map[agent_config.role] = crew_agent
        
        # Create tasks
        tasks = []
        for task_config in config.tasks:
            agent = agents_map.get(task_config.agent)
            if not agent:
                raise ValueError(f"Agent '{task_config.agent}' not found for task")
            
            task = Task(
                description=task_config.description,
                agent=agent,
                expected_output=task_config.expected_output,
                async_execution=task_config.async_execution
            )
            tasks.append(task)
        
        # Create crew
        process = Process.sequential if config.process == "sequential" else Process.hierarchical
        
        crew = Crew(
            agents=list(agents_map.values()),
            tasks=tasks,
            process=process,
            verbose=config.verbose
        )
        
        return crew
    
    def save_config(self, config: CrewConfig):
        """Save crew configuration"""
        self.configs[config.name] = config
        self._save_config(config)
    
    def get_config(self, name: str) -> Optional[CrewConfig]:
        """Get crew configuration by name"""
        return self.configs.get(name)
    
    def list_configs(self) -> List[CrewConfig]:
        """List all crew configurations"""
        return list(self.configs.values())
    
    def delete_config(self, name: str) -> bool:
        """Delete crew configuration"""
        if name in self.configs:
            del self.configs[name]
            
            # Delete file
            configs_dir = self._get_configs_dir()
            filepath = os.path.join(configs_dir, f"{name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return True
        return False
    
    async def run_crew(self, name: str, inputs: Optional[Dict] = None) -> Dict:
        """
        Run a crew by name
        
        Args:
            name: Name of the crew configuration
            inputs: Optional inputs for the crew
        
        Returns:
            Dictionary with results and execution info
        """
        config = self.get_config(name)
        if not config:
            raise ValueError(f"Crew '{name}' not found")
        
        # Create crew
        crew = self.create_crew(config)
        
        # Store active crew
        self.active_crews[name] = crew
        
        # Log start
        log_item = self.agent.context.log.log(
            type="tool",
            heading=f"🤖 Running CrewAI Crew: {name}",
            content=f"Description: {config.description}\n"
                   f"Agents: {len(config.agents)}\n"
                   f"Tasks: {len(config.tasks)}"
        )
        
        try:
            # Run crew
            start_time = datetime.now()
            result = crew.kickoff(inputs=inputs or {})
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log completion
            log_item.update(
                content=f"✅ Crew completed successfully\n"
                       f"Duration: {duration:.2f}s\n"
                       f"Result: {result}"
            )
            
            return {
                "success": True,
                "result": str(result),
                "duration": duration,
                "crew_name": name
            }
        
        except Exception as e:
            # Log error
            log_item.update(
                content=f"❌ Crew failed: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "crew_name": name
            }
        
        finally:
            # Remove from active crews
            if name in self.active_crews:
                del self.active_crews[name]
    
    def get_active_crews(self) -> List[str]:
        """Get list of currently running crews"""
        return list(self.active_crews.keys())


# Predefined crew templates
CREW_TEMPLATES = {
    "research": CrewConfig(
        name="research_crew",
        description="Research crew for gathering and analyzing information",
        agents=[
            AgentConfig(
                role="Researcher",
                goal="Gather comprehensive information on the given topic",
                backstory="You are an experienced researcher with expertise in finding and validating information from multiple sources."
            ),
            AgentConfig(
                role="Analyst",
                goal="Analyze and synthesize research findings",
                backstory="You are a skilled analyst who can identify patterns, draw insights, and create comprehensive reports."
            )
        ],
        tasks=[
            TaskConfig(
                description="Research the topic: {topic}",
                agent="Researcher",
                expected_output="A comprehensive research report with sources"
            ),
            TaskConfig(
                description="Analyze the research findings and create a summary",
                agent="Analyst",
                expected_output="A detailed analysis with key insights and recommendations"
            )
        ]
    ),
    
    "development": CrewConfig(
        name="development_crew",
        description="Software development crew for building applications",
        agents=[
            AgentConfig(
                role="Software Architect",
                goal="Design software architecture and technical specifications",
                backstory="You are a senior software architect with experience in designing scalable systems."
            ),
            AgentConfig(
                role="Developer",
                goal="Implement the software according to specifications",
                backstory="You are an experienced developer proficient in multiple programming languages.",
                allow_delegation=False
            ),
            AgentConfig(
                role="QA Engineer",
                goal="Test the software and ensure quality",
                backstory="You are a meticulous QA engineer who finds and reports bugs.",
                allow_delegation=False
            )
        ],
        tasks=[
            TaskConfig(
                description="Design architecture for: {project_description}",
                agent="Software Architect",
                expected_output="Technical architecture document with specifications"
            ),
            TaskConfig(
                description="Implement the software based on the architecture",
                agent="Developer",
                expected_output="Working code with documentation"
            ),
            TaskConfig(
                description="Test the implementation and report issues",
                agent="QA Engineer",
                expected_output="Test report with findings and recommendations"
            )
        ]
    ),
    
    "content_creation": CrewConfig(
        name="content_crew",
        description="Content creation crew for writing and editing",
        agents=[
            AgentConfig(
                role="Content Writer",
                goal="Create engaging and informative content",
                backstory="You are a talented writer who creates compelling content for various audiences."
            ),
            AgentConfig(
                role="Editor",
                goal="Edit and improve content quality",
                backstory="You are an experienced editor with an eye for detail and clarity."
            )
        ],
        tasks=[
            TaskConfig(
                description="Write content about: {topic}",
                agent="Content Writer",
                expected_output="Well-written content draft"
            ),
            TaskConfig(
                description="Edit and improve the content",
                agent="Editor",
                expected_output="Polished, publication-ready content"
            )
        ]
    )
}
