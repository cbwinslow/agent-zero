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
        """
        List all crew configurations available to the current user session.
        
        Parameters:
            input (dict): Request payload (not used by this handler).
        
        Returns:
            dict: On success, a dictionary with "success": True and "crews": a list of crew configuration dictionaries (each produced by `to_dict()`).
            On failure, returns an error response dict when the session is missing or not found (status 401).
        """
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
        """
        Provide available crew templates as a mapping from template names to their dictionary representations.
        
        Returns:
            dict: Response with "success": True and "templates" mapping each template name to its dict form.
        """
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
        """
        Create a new crew configuration from a template or custom definition.
        
        Creates and persists a CrewConfig with the provided `name`. If `template` is provided, uses the named template from CREW_TEMPLATES (assigning the requested name and the current user as creator); otherwise builds a custom CrewConfig from `input` and assigns the current user as creator. Fails with an error response when the caller is not logged in, the session is missing, `name` is not provided, a crew with the same name already exists, or the specified template does not exist.
        
        Parameters:
            input (dict): Request payload. Expected keys:
                - name (str): The new crew's name (required).
                - template (str, optional): Template name to copy from.
                - ... (other keys): When creating a custom crew, additional crew fields accepted by CrewConfig.from_dict.
        
        Returns:
            dict: On success, a dict with keys:
                - "success" (bool): True.
                - "message" (str): Success message including the crew name.
                - "crew" (dict): The created crew represented as a dict.
        """
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
        """
        Retrieve a crew configuration by name and return its dictionary representation.
        
        Parameters:
            input (dict): Request payload; must include the "name" key with the crew name to fetch.
        
        Returns:
            dict: On success, a mapping with "success": True and "crew": the crew configuration as a dict.
        """
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
        """
        Run a named crew configuration with provided inputs.
        
        Parameters:
            input (dict): Request data with keys:
                - name (str): Name of the crew to run (required).
                - inputs (dict): Optional inputs supplied to the crew (defaults to an empty dict).
        
        Returns:
            dict: The execution result returned by CrewManager.run_crew.
        """
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
        """
        Delete a crew configuration by name for the current session's agent.
        
        Parameters:
            input (dict): Request payload; must include the key `"name"` specifying the crew to delete.
        
        Returns:
            dict: On success, `{'success': True, 'message': "Crew '<name>' deleted successfully"}`. On failure, returns an error response produced by `self.error` for missing session, missing `"name"`, or if the crew is not found.
        """
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
        """
        List currently running crew instances for the authenticated user session.
        
        If the request is not associated with a valid session, responds with a 401 error.
        Returns a dictionary containing a success flag and the list of active crews.
        
        Returns:
            dict: {
                "success": True,
                "active_crews": list  # list of active crew descriptors
            }
        """
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
