"""
Task Router for Agent Zero.
Routes tasks to appropriate agents based on task requirements and agent capabilities.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from enum import Enum
import json

from .model_orchestrator import ModelOrchestrator, ModelCapability
from .agent_orchestrator import AgentOrchestrator, AgentRole


class TaskType(Enum):
    """Types of tasks that can be routed to agents."""
    CONVERSATION = "conversation"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    FACTUAL = "factual"
    CUSTOM = "custom"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task:
    """Represents a task to be performed by an agent."""
    
    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        required_capabilities: List[ModelCapability] = None,
        preferred_agent_role: Optional[AgentRole] = None,
        preferred_agent_id: Optional[str] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.input_data = input_data
        self.priority = priority
        self.required_capabilities = required_capabilities or []
        self.preferred_agent_role = preferred_agent_role
        self.preferred_agent_id = preferred_agent_id
        self.callback = callback
        self.result: Optional[Dict[str, Any]] = None
        self.status = "pending"
        self.assigned_agent_id: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "input_data": self.input_data,
            "priority": self.priority.value,
            "required_capabilities": [cap.value for cap in self.required_capabilities],
            "preferred_agent_role": self.preferred_agent_role.value if self.preferred_agent_role else None,
            "preferred_agent_id": self.preferred_agent_id,
            "status": self.status,
            "assigned_agent_id": self.assigned_agent_id,
            "result": self.result,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a task from a dictionary."""
        task = cls(
            task_id=data["task_id"],
            task_type=TaskType(data["task_type"]),
            description=data["description"],
            input_data=data["input_data"],
            priority=TaskPriority(data["priority"]),
            required_capabilities=[ModelCapability(cap) for cap in data.get("required_capabilities", [])],
            preferred_agent_role=AgentRole(data["preferred_agent_role"]) if data.get("preferred_agent_role") else None,
            preferred_agent_id=data.get("preferred_agent_id"),
        )
        task.status = data.get("status", "pending")
        task.assigned_agent_id = data.get("assigned_agent_id")
        task.result = data.get("result")
        return task


class TaskRouter:
    """
    Routes tasks to appropriate agents based on task requirements and agent capabilities.
    """
    
    def __init__(
        self, 
        model_orchestrator: ModelOrchestrator,
        agent_orchestrator: AgentOrchestrator
    ):
        self.model_orchestrator = model_orchestrator
        self.agent_orchestrator = agent_orchestrator
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.running = False
        self.processing_task = None
        
    def submit_task(self, task: Task) -> str:
        """Submit a task for processing."""
        self.tasks[task.task_id] = task
        
        # Add to queue based on priority
        if task.priority == TaskPriority.CRITICAL:
            self.task_queue.insert(0, task.task_id)
        elif task.priority == TaskPriority.HIGH:
            # Insert after any CRITICAL tasks
            insert_pos = 0
            for i, task_id in enumerate(self.task_queue):
                if self.tasks[task_id].priority != TaskPriority.CRITICAL:
                    insert_pos = i
                    break
            self.task_queue.insert(insert_pos, task.task_id)
        else:
            # Add to the end for MEDIUM and LOW priority
            self.task_queue.append(task.task_id)
            
        return task.task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status."""
        tasks = self.tasks.values()
        if status:
            tasks = [task for task in tasks if task.status == status]
        return [task.to_dict() for task in tasks]
    
    def _find_best_agent_for_task(self, task: Task) -> Optional[str]:
        """Find the best agent for a task based on capabilities and role."""
        # If a preferred agent is specified and exists, use it
        if task.preferred_agent_id and task.preferred_agent_id in self.agent_orchestrator.agents:
            return task.preferred_agent_id
        
        # If a preferred role is specified, find agents with that role
        if task.preferred_agent_role:
            agents_with_role = self.agent_orchestrator.find_agents_by_role(task.preferred_agent_role)
            if agents_with_role:
                # For now, just return the first one
                return agents_with_role[0][0]
        
        # If required capabilities are specified, find models with those capabilities
        if task.required_capabilities:
            # For each agent, check if its model has all required capabilities
            for agent_id, profile in self.agent_orchestrator.agents.items():
                model_profile = self.model_orchestrator.get_model_profile(profile.model_id)
                if all(model_profile.has_capability(cap) for cap in task.required_capabilities):
                    return agent_id
        
        # If no suitable agent is found, return the default agent
        return self.agent_orchestrator.default_agent_id
    
    async def process_task(self, task_id: str) -> Dict[str, Any]:
        """Process a task by routing it to the appropriate agent."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        task.status = "processing"
        
        # Find the best agent for the task
        agent_id = self._find_best_agent_for_task(task)
        if not agent_id:
            task.status = "failed"
            task.result = {"error": "No suitable agent found for the task"}
            return task.to_dict()
        
        # Assign the agent to the task
        task.assigned_agent_id = agent_id
        
        try:
            # Prepare the message for the agent
            message = f"""
Task Type: {task.task_type.value}
Priority: {task.priority.value}
Description: {task.description}

Input Data:
{json.dumps(task.input_data, indent=2)}
"""
            
            # Send the message to the agent
            response = await self.agent_orchestrator.communicate(message, agent_id)
            
            # Update task status and result
            task.status = "completed"
            task.result = {"response": response}
            
            # Call the callback if provided
            if task.callback:
                task.callback(task.result)
                
            return task.to_dict()
            
        except Exception as e:
            # Update task status and result on error
            task.status = "failed"
            task.result = {"error": str(e)}
            return task.to_dict()
    
    async def start_processing(self):
        """Start processing tasks from the queue."""
        self.running = True
        while self.running and self.task_queue:
            # Get the next task from the queue
            task_id = self.task_queue.pop(0)
            
            # Process the task
            self.processing_task = asyncio.create_task(self.process_task(task_id))
            await self.processing_task
            self.processing_task = None
    
    def stop_processing(self):
        """Stop processing tasks."""
        self.running = False
        if self.processing_task:
            self.processing_task.cancel()
            
    def save_to_file(self, filepath: str) -> None:
        """Save the task registry to a file."""
        with open(filepath, "w") as f:
            json.dump({
                "tasks": {
                    task_id: task.to_dict()
                    for task_id, task in self.tasks.items()
                },
                "task_queue": self.task_queue,
            }, f, indent=2)
    
    @classmethod
    def load_from_file(
        cls, 
        filepath: str, 
        model_orchestrator: ModelOrchestrator,
        agent_orchestrator: AgentOrchestrator
    ) -> "TaskRouter":
        """Load a task registry from a file."""
        router = cls(model_orchestrator, agent_orchestrator)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                for task_id, task_data in data.get("tasks", {}).items():
                    router.tasks[task_id] = Task.from_dict(task_data)
                router.task_queue = data.get("task_queue", [])
        return router