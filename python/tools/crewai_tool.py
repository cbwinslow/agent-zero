"""
CrewAI Tool for Agent Zero
Allows Agent Zero to create, configure, and run CrewAI crews
"""

from python.helpers.tool import Tool, Response
from python.helpers.crewai_integration import CrewManager, CrewConfig, AgentConfig, TaskConfig, CREW_TEMPLATES
import json


class CrewAI(Tool):
    """
    Tool for managing CrewAI crews.
    
    Allows creating, configuring, and running multi-agent crews for complex tasks.
    """
    
    async def execute(self, action="", **kwargs):
        """
        Execute CrewAI action.
        
        Actions:
        - list: List available crew configurations
        - templates: List available crew templates
        - create: Create a new crew configuration
        - run: Run a crew
        - get: Get crew configuration details
        - delete: Delete a crew configuration
        
        Examples:
        - List crews: action="list"
        - Use template: action="create", template="research", name="my_research_crew"
        - Run crew: action="run", name="my_research_crew", inputs={"topic": "AI trends"}
        """
        
        crew_mgr = CrewManager(self.agent)
        
        if action == "list":
            return await self._list_crews(crew_mgr)
        
        elif action == "templates":
            return await self._list_templates()
        
        elif action == "create":
            return await self._create_crew(crew_mgr, **kwargs)
        
        elif action == "run":
            return await self._run_crew(crew_mgr, **kwargs)
        
        elif action == "get":
            return await self._get_crew(crew_mgr, **kwargs)
        
        elif action == "delete":
            return await self._delete_crew(crew_mgr, **kwargs)
        
        else:
            return Response(
                message=f"Unknown action: {action}. "
                       f"Available actions: list, templates, create, run, get, delete",
                break_loop=False
            )
    
    async def _list_crews(self, crew_mgr: CrewManager):
        """List all crew configurations"""
        configs = crew_mgr.list_configs()
        
        if not configs:
            return Response(
                message="No crew configurations found. Use action='templates' to see available templates.",
                break_loop=False
            )
        
        message = "## Available Crew Configurations\n\n"
        for config in configs:
            message += f"### {config.name}\n"
            message += f"- Description: {config.description}\n"
            message += f"- Agents: {len(config.agents)}\n"
            message += f"- Tasks: {len(config.tasks)}\n"
            message += f"- Process: {config.process}\n\n"
        
        return Response(message=message, break_loop=False)
    
    async def _list_templates(self):
        """List available crew templates"""
        message = "## Available Crew Templates\n\n"
        
        for name, template in CREW_TEMPLATES.items():
            message += f"### {name}\n"
            message += f"- Description: {template.description}\n"
            message += f"- Agents: {', '.join(a.role for a in template.agents)}\n"
            message += f"- Tasks: {len(template.tasks)}\n\n"
            message += f"To use: action='create', template='{name}', name='my_{name}_crew'\n\n"
        
        return Response(message=message, break_loop=False)
    
    async def _create_crew(self, crew_mgr: CrewManager, **kwargs):
        """Create a new crew configuration"""
        name = kwargs.get("name")
        template = kwargs.get("template")
        
        if not name:
            return Response(
                message="Error: 'name' parameter is required",
                break_loop=False
            )
        
        # Check if crew already exists
        if crew_mgr.get_config(name):
            return Response(
                message=f"Error: Crew '{name}' already exists",
                break_loop=False
            )
        
        # Use template or create custom
        if template:
            if template not in CREW_TEMPLATES:
                return Response(
                    message=f"Error: Template '{template}' not found. "
                           f"Use action='templates' to see available templates.",
                    break_loop=False
                )
            
            config = CREW_TEMPLATES[template]
            config.name = name
            config.created_by = self.agent.agent_name
        
        else:
            # Create custom crew from parameters
            description = kwargs.get("description", "Custom crew")
            agents_data = kwargs.get("agents", [])
            tasks_data = kwargs.get("tasks", [])
            
            if not agents_data or not tasks_data:
                return Response(
                    message="Error: 'agents' and 'tasks' are required for custom crews",
                    break_loop=False
                )
            
            agents = [
                AgentConfig(
                    role=a.get("role"),
                    goal=a.get("goal"),
                    backstory=a.get("backstory")
                )
                for a in agents_data
            ]
            
            tasks = [
                TaskConfig(
                    description=t.get("description"),
                    agent=t.get("agent"),
                    expected_output=t.get("expected_output", "Task completed")
                )
                for t in tasks_data
            ]
            
            config = CrewConfig(
                name=name,
                description=description,
                agents=agents,
                tasks=tasks,
                created_by=self.agent.agent_name
            )
        
        # Save configuration
        crew_mgr.save_config(config)
        
        message = f"✅ Created crew '{name}'\n\n"
        message += f"Description: {config.description}\n"
        message += f"Agents: {len(config.agents)}\n"
        message += f"Tasks: {len(config.tasks)}\n"
        
        return Response(message=message, break_loop=False)
    
    async def _run_crew(self, crew_mgr: CrewManager, **kwargs):
        """Run a crew"""
        name = kwargs.get("name")
        inputs = kwargs.get("inputs", {})
        
        if not name:
            return Response(
                message="Error: 'name' parameter is required",
                break_loop=False
            )
        
        # Check if crew exists
        if not crew_mgr.get_config(name):
            return Response(
                message=f"Error: Crew '{name}' not found. "
                       f"Use action='list' to see available crews.",
                break_loop=False
            )
        
        # Run crew
        result = await crew_mgr.run_crew(name, inputs)
        
        if result["success"]:
            message = f"✅ Crew '{name}' completed successfully!\n\n"
            message += f"Duration: {result['duration']:.2f}s\n\n"
            message += f"## Results\n\n{result['result']}"
        else:
            message = f"❌ Crew '{name}' failed\n\n"
            message += f"Error: {result['error']}"
        
        return Response(message=message, break_loop=False)
    
    async def _get_crew(self, crew_mgr: CrewManager, **kwargs):
        """Get crew configuration details"""
        name = kwargs.get("name")
        
        if not name:
            return Response(
                message="Error: 'name' parameter is required",
                break_loop=False
            )
        
        config = crew_mgr.get_config(name)
        if not config:
            return Response(
                message=f"Error: Crew '{name}' not found",
                break_loop=False
            )
        
        message = f"## Crew Configuration: {config.name}\n\n"
        message += f"Description: {config.description}\n"
        message += f"Process: {config.process}\n"
        message += f"Created by: {config.created_by}\n\n"
        
        message += "### Agents\n\n"
        for agent in config.agents:
            message += f"**{agent.role}**\n"
            message += f"- Goal: {agent.goal}\n"
            message += f"- Backstory: {agent.backstory}\n\n"
        
        message += "### Tasks\n\n"
        for i, task in enumerate(config.tasks, 1):
            message += f"{i}. {task.description}\n"
            message += f"   - Agent: {task.agent}\n"
            message += f"   - Expected Output: {task.expected_output}\n\n"
        
        return Response(message=message, break_loop=False)
    
    async def _delete_crew(self, crew_mgr: CrewManager, **kwargs):
        """Delete a crew configuration"""
        name = kwargs.get("name")
        
        if not name:
            return Response(
                message="Error: 'name' parameter is required",
                break_loop=False
            )
        
        success = crew_mgr.delete_config(name)
        
        if success:
            return Response(
                message=f"✅ Deleted crew '{name}'",
                break_loop=False
            )
        else:
            return Response(
                message=f"Error: Crew '{name}' not found",
                break_loop=False
            )
