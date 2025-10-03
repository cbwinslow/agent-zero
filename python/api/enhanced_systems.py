"""
Enhanced Memory and Rules API Endpoints
"""

from flask import session
from python.helpers.api import ApiHandler
from python.helpers.enhanced_memory import EnhancedMemory, MemoryImportance
from python.helpers.enhanced_rules import RuleManager, Rule, RuleType, RulePriority, RuleCondition
from python.helpers.auth import get_session_manager
from python.helpers.memory import Memory


class MemorySearch(ApiHandler):
    """Enhanced memory search"""
    
    async def process(self, input: dict):
        """
        Handle an enhanced memory search request and return matching memory entries.
        
        Parameters:
            input (dict): Request parameters. Recognized keys:
                - query (str): Text query to search memories for. Defaults to "".
                - max_results (int): Maximum number of results to return. Defaults to 5.
                - use_temporal_weighting (bool): Whether to apply temporal weighting to scores. Defaults to True.
                - filter_tags (list[str] | None): Optional list of tags to filter results by.
        
        Returns:
            dict: Response object with keys:
                - "success" (bool): `True` for a successful search.
                - "results" (list[dict]): List of matching memory entries, each containing:
                    - "content" (str): The memory text.
                    - "score" (float): Relevance score for the memory.
                    - "metadata" (dict): Associated metadata for the memory.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        query = input.get("query", "")
        max_results = input.get("max_results", 5)
        use_temporal = input.get("use_temporal_weighting", True)
        filter_tags = input.get("filter_tags")
        
        # Get base memory
        base_memory = await Memory.get(user_session.context.agent0)
        enhanced_memory = EnhancedMemory(base_memory)
        
        # Search
        results = await enhanced_memory.search_enhanced(
            query=query,
            max_results=max_results,
            use_temporal_weighting=use_temporal,
            filter_tags=filter_tags
        )
        
        return {
            "success": True,
            "results": [
                {
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                }
                for doc, score in results
            ]
        }


class MemoryAdd(ApiHandler):
    """Add memory with metadata"""
    
    async def process(self, input: dict):
        """
        Add a memory entry for the authenticated user's `agent0` context.
        
        Parameters:
            input (dict): Request payload. Expected keys:
                - text (str): The memory text to store (required).
                - importance (str): Importance level name from `MemoryImportance` (default "MEDIUM").
                - tags (list): List of tag strings to attach to the memory (default empty list).
                - context (str): Optional context string for the memory (default empty string).
        
        Returns:
            dict: On success, a dictionary with keys:
                - "success" (bool): `True` on success.
                - "doc_id" (str): ID of the newly created memory document.
                - "message" (str): Confirmation message.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        text = input.get("text", "")
        importance = input.get("importance", "MEDIUM")
        tags = input.get("tags", [])
        context = input.get("context", "")
        
        if not text:
            return self.error("Text is required")
        
        # Get base memory
        base_memory = await Memory.get(user_session.context.agent0)
        enhanced_memory = EnhancedMemory(base_memory)
        
        # Add memory
        doc_id = await enhanced_memory.add_memory(
            text=text,
            importance=MemoryImportance[importance],
            tags=tags,
            context=context
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": "Memory added successfully"
        }


class MemoryStats(ApiHandler):
    """Get memory statistics"""
    
    async def process(self, input: dict):
        """
        Retrieve memory statistics for the authenticated user's agent0 context.
        
        Requires an active session; if no session_id is present or the session cannot be found, the handler returns an error response (401) via self.error.
        
        Returns:
            dict: A mapping with "success": True and "statistics": the memory statistics produced by EnhancedMemory.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        # Get base memory
        base_memory = await Memory.get(user_session.context.agent0)
        enhanced_memory = EnhancedMemory(base_memory)
        
        stats = enhanced_memory.get_memory_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }


class RuleList(ApiHandler):
    """List all rules"""
    
    async def process(self, input: dict):
        """
        List rules for the current user's agent, optionally filtered by rule type or tag.
        
        Parameters:
            input (dict): Optional filter keys:
                - type (str): Rule type name to filter by.
                - tag (str): Tag to filter rules by.
        
        Returns:
            result (dict): A dictionary with "success": True and "rules": a list of rule dictionaries.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_mgr = RuleManager(user_session.context.agent0)
        
        rule_type = input.get("type")
        tag = input.get("tag")
        
        if rule_type:
            rules = rule_mgr.get_rules_by_type(RuleType(rule_type))
        elif tag:
            rules = rule_mgr.get_rules_by_tag(tag)
        else:
            rules = list(rule_mgr.rules.values())
        
        return {
            "success": True,
            "rules": [r.to_dict() for r in rules]
        }


class RuleAdd(ApiHandler):
    """Add a new rule"""
    
    async def process(self, input: dict):
        """
        Add a new rule to the current user's RuleManager.
        
        Parameters:
            input (dict): Rule fields and options. Supported keys:
                - id (str, optional): Rule ID; generated if omitted.
                - name (str, optional): Rule name.
                - content (str, optional): Rule content.
                - type (str, optional): Rule type (defaults to "custom").
                - priority (int, optional): Rule priority (defaults to 3).
                - enabled (bool, optional): Whether the rule is enabled (defaults to True).
                - tags (list[str], optional): Tags for the rule.
        
        Returns:
            dict: On success, a dictionary with keys:
                - "success" (True),
                - "rule" (dict): the added rule as a dict,
                - "message" (str): confirmation message.
            On failure, an error response dictionary produced by self.error (e.g., validation failure, authentication issues, or rule already exists).
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_mgr = RuleManager(user_session.context.agent0)
        
        # Create rule
        import uuid
        rule = Rule(
            id=input.get("id", str(uuid.uuid4())),
            name=input.get("name", ""),
            content=input.get("content", ""),
            type=RuleType(input.get("type", "custom")),
            priority=RulePriority(input.get("priority", 3)),
            enabled=input.get("enabled", True),
            tags=input.get("tags", []),
            created_by=user_session.user.username
        )
        
        # Validate
        issues = rule_mgr.validate_rule(rule)
        if issues:
            return self.error(f"Validation failed: {', '.join(issues)}")
        
        # Add
        success = rule_mgr.add_rule(rule)
        
        if success:
            return {
                "success": True,
                "rule": rule.to_dict(),
                "message": "Rule added successfully"
            }
        else:
            return self.error("Rule already exists")


class RuleUpdate(ApiHandler):
    """Update an existing rule"""
    
    async def process(self, input: dict):
        """
        Update an existing rule's content and enabled status.
        
        Requires an authenticated user session. The input dictionary must include "rule_id"; optional keys "content" and "enabled" are applied as updates to the rule in the current user's agent0 context.
        
        Parameters:
            input (dict): Request payload containing:
                - rule_id (str): Identifier of the rule to update (required).
                - content (str, optional): New rule content to set.
                - enabled (bool, optional): New enabled state to set.
        
        Returns:
            dict: On success, a dictionary with `success: True`, a confirmation `message`, and `rule` containing the updated rule as a dictionary. On failure, an error response describing the problem.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_id = input.get("rule_id")
        if not rule_id:
            return self.error("rule_id is required")
        
        rule_mgr = RuleManager(user_session.context.agent0)
        
        success = rule_mgr.update_rule(
            rule_id=rule_id,
            content=input.get("content"),
            enabled=input.get("enabled")
        )
        
        if success:
            return {
                "success": True,
                "message": "Rule updated successfully",
                "rule": rule_mgr.get_rule(rule_id).to_dict()
            }
        else:
            return self.error("Rule not found")


class RuleDelete(ApiHandler):
    """Delete a rule"""
    
    async def process(self, input: dict):
        """
        Delete a rule identified by `rule_id` for the current user's agent context.
        
        Requires a valid user session (session_id in Flask session) and expects `input` to contain a `rule_id` key.
        
        Parameters:
            input (dict): Request payload; must include `rule_id` (str) specifying the rule to delete.
        
        Returns:
            dict: On success, a dictionary with `success: True` and `message` confirming deletion.
            On failure, an error response indicating missing authentication, missing `rule_id`, or that the rule was not found.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_id = input.get("rule_id")
        if not rule_id:
            return self.error("rule_id is required")
        
        rule_mgr = RuleManager(user_session.context.agent0)
        success = rule_mgr.delete_rule(rule_id)
        
        if success:
            return {
                "success": True,
                "message": "Rule deleted successfully"
            }
        else:
            return self.error("Rule not found")


class RuleHistory(ApiHandler):
    """Get rule version history"""
    
    async def process(self, input: dict):
        """
        Retrieve version history for a rule identified by `rule_id`.
        
        Parameters:
            input (dict): Expected to contain the key `"rule_id"` with the ID of the rule whose history will be retrieved.
        
        Returns:
            dict: A response dictionary with `"success": True` and `"history"` set to a list of rule version dictionaries.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_id = input.get("rule_id")
        if not rule_id:
            return self.error("rule_id is required")
        
        rule_mgr = RuleManager(user_session.context.agent0)
        history = rule_mgr.get_rule_history(rule_id)
        
        return {
            "success": True,
            "history": [r.to_dict() for r in history]
        }


class RuleExport(ApiHandler):
    """Export rules as a ruleset"""
    
    async def process(self, input: dict):
        """
        Export a ruleset for the current user's agent and return it as a serializable dictionary.
        
        Parameters:
            input (dict): Optional export options:
                - name (str): Human-readable name for the exported ruleset. Defaults to "My Ruleset".
                - description (str): Optional description for the ruleset.
                - rule_ids (list[str] | None): Optional list of rule IDs to include; if omitted, the manager decides which rules to export.
        
        Returns:
            dict: A response dictionary containing:
                - "success" (bool): `True` when the export succeeded.
                - "ruleset" (dict): The exported ruleset represented as a dictionary.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        rule_mgr = RuleManager(user_session.context.agent0)
        
        ruleset = rule_mgr.export_ruleset(
            name=input.get("name", "My Ruleset"),
            description=input.get("description", ""),
            rule_ids=input.get("rule_ids")
        )
        
        return {
            "success": True,
            "ruleset": ruleset.to_dict()
        }


class RuleImport(ApiHandler):
    """Import a ruleset"""
    
    async def process(self, input: dict):
        """
        Import a ruleset into the current user's rule manager.
        
        Parameters:
            input (dict): Request data containing:
                - "ruleset" (dict): Serialized RuleSet to import (required).
                - "overwrite" (bool): Whether to overwrite existing rules (optional, defaults to False).
        
        Returns:
            dict: Response with keys:
                - "success" (bool): True on successful import.
                - "imported" (int): Number of rules imported.
                - "message" (str): Human-readable summary of the result.
        """
        session_id = session.get('session_id')
        if not session_id:
            return self.error("Not logged in", status=401)
        
        session_mgr = get_session_manager()
        user_session = session_mgr.get_session(session_id)
        
        if not user_session:
            return self.error("Session not found", status=401)
        
        from python.helpers.enhanced_rules import RuleSet
        
        ruleset_data = input.get("ruleset")
        if not ruleset_data:
            return self.error("ruleset data is required")
        
        rule_mgr = RuleManager(user_session.context.agent0)
        ruleset = RuleSet.from_dict(ruleset_data)
        
        imported = rule_mgr.import_ruleset(
            ruleset=ruleset,
            overwrite=input.get("overwrite", False)
        )
        
        return {
            "success": True,
            "imported": imported,
            "message": f"Imported {imported} rules"
        }
