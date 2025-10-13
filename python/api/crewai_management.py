"""
CrewAI API Endpoints
"""

from flask import session
from python.helpers.api import ApiHandler
from python.helpers.crewai_integration import CrewManager, CrewConfig, AgentConfig, TaskConfig, CREW_TEMPLATES
from python.helpers.auth import get_session_manager


class CrewList(ApiHandler):
    """List all crew configurations"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        crew_mgr = CrewManager(user_session.context.agent0)
        configs = crew_mgr.list_configs()
        
        return {
            "success": True,
            "crews": [c.to_dict() for c in configs]
        }


class CrewTemplates(ApiHandler):
    """List available crew templates"""
    
    async def process(self, input: dict):
        return {
            "success": True,
            "templates": {
                name: template.to_dict()
                for name, template in CREW_TEMPLATES.items()
            }
        }


class CrewCreate(ApiHandler):
    """Create a new crew configuration"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        crew_mgr = CrewManager(user_session.context.agent0)
        
        name = input.get("name")
        template = input.get("template")
        
        if not name:
            return self.error("'name' is required")
        
        if crew_mgr.get_config(name):
            return self.error(f"Crew '{name}' already exists")
        
        # Use template or create custom
        if template:
            if template not in CREW_TEMPLATES:
                return self.error(f"Template '{template}' not found")
            
            config = CREW_TEMPLATES[template]
            config.name = name
            config.created_by = user_session.user.username
        else:
            # Create custom crew
            config = CrewConfig.from_dict(input)
            config.created_by = user_session.user.username
        
        crew_mgr.save_config(config)
        
        return {
            "success": True,
            "message": f"Crew '{name}' created successfully",
            "crew": config.to_dict()
        }


class CrewGet(ApiHandler):
    """Get crew configuration"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        name = input.get("name")
        if not name:
            return self.error("'name' is required")
        
        crew_mgr = CrewManager(user_session.context.agent0)
        config = crew_mgr.get_config(name)
        
        if not config:
            return self.error(f"Crew '{name}' not found")
        
        return {
            "success": True,
            "crew": config.to_dict()
        }


class CrewRun(ApiHandler):
    """Run a crew"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        name = input.get("name")
        inputs = input.get("inputs", {})
        
        if not name:
            return self.error("'name' is required")
        
        crew_mgr = CrewManager(user_session.context.agent0)
        
        if not crew_mgr.get_config(name):
            return self.error(f"Crew '{name}' not found")
        
        result = await crew_mgr.run_crew(name, inputs)
        
        return result


class CrewDelete(ApiHandler):
    """Delete a crew configuration"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        name = input.get("name")
        if not name:
            return self.error("'name' is required")
        
        crew_mgr = CrewManager(user_session.context.agent0)
        success = crew_mgr.delete_config(name)
        
        if success:
            return {
                "success": True,
                "message": f"Crew '{name}' deleted successfully"
            }
        else:
            return self.error(f"Crew '{name}' not found")


class CrewActiveList(ApiHandler):
    """List currently running crews"""
    
    async def process(self, input: dict):
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        crew_mgr = CrewManager(user_session.context.agent0)
        active = crew_mgr.get_active_crews()
        
        return {
            "success": True,
            "active_crews": active
        }
