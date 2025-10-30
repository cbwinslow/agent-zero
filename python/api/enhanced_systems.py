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
