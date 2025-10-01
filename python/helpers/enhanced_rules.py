"""
Enhanced Rules System for Agent Zero
Provides configurable, versioned, and validated rules management

Features:
- Rule versioning and history
- Rule validation and testing
- Conditional rules based on context
- Rule templates and presets
- Rule conflict detection
- Rule analytics and impact tracking
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
from python.helpers import files
from agent import Agent


class RuleType(Enum):
    """Types of rules"""
    BEHAVIOR = "behavior"
    CONSTRAINT = "constraint"
    PREFERENCE = "preference"
    SECURITY = "security"
    CUSTOM = "custom"


class RulePriority(Enum):
    """Rule priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class RuleCondition:
    """Condition for conditional rules"""
    type: str  # e.g., "context", "time", "user", "task"
    operator: str  # e.g., "equals", "contains", "greater_than"
    value: Any
    
    def evaluate(self, context: Dict) -> bool:
        """Evaluate condition against context"""
        if self.type not in context:
            return False
        
        ctx_value = context[self.type]
        
        if self.operator == "equals":
            return ctx_value == self.value
        elif self.operator == "contains":
            return self.value in str(ctx_value)
        elif self.operator == "greater_than":
            return ctx_value > self.value
        elif self.operator == "less_than":
            return ctx_value < self.value
        elif self.operator == "in":
            return ctx_value in self.value
        
        return False


@dataclass
class Rule:
    """Individual rule with metadata"""
    id: str
    name: str
    content: str
    type: RuleType
    priority: RulePriority = RulePriority.MEDIUM
    enabled: bool = True
    conditions: List[RuleCondition] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: int = 1
    parent_version_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "type": self.type.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "conditions": [
                {"type": c.type, "operator": c.operator, "value": c.value}
                for c in self.conditions
            ],
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version,
            "parent_version_id": self.parent_version_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Rule':
        conditions = [
            RuleCondition(c["type"], c["operator"], c["value"])
            for c in data.get("conditions", [])
        ]
        
        return Rule(
            id=data["id"],
            name=data["name"],
            content=data["content"],
            type=RuleType(data["type"]),
            priority=RulePriority(data.get("priority", 3)),
            enabled=data.get("enabled", True),
            conditions=conditions,
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            created_by=data.get("created_by", "system"),
            version=data.get("version", 1),
            parent_version_id=data.get("parent_version_id")
        )
    
    def applies_to_context(self, context: Dict) -> bool:
        """Check if rule applies to given context"""
        if not self.enabled:
            return False
        
        if not self.conditions:
            return True
        
        # All conditions must be met
        return all(cond.evaluate(context) for cond in self.conditions)
    
    def get_hash(self) -> str:
        """Get hash of rule content for change detection"""
        return hashlib.sha256(self.content.encode()).hexdigest()


@dataclass
class RuleSet:
    """Collection of rules with metadata"""
    name: str
    description: str
    rules: List[Rule] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RuleSet':
        return RuleSet(
            name=data["name"],
            description=data["description"],
            rules=[Rule.from_dict(r) for r in data.get("rules", [])],
            version=data.get("version", "1.0.0"),
            created_at=datetime.fromisoformat(data["created_at"])
        )


class RuleManager:
    """Manages rules for an agent"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.rules: Dict[str, Rule] = {}
        self.rule_history: Dict[str, List[Rule]] = {}
        self._load_rules()
    
    def _get_rules_file(self) -> str:
        """Get path to rules file"""
        from python.helpers import memory
        memory_dir = memory.get_memory_subdir_abs(self.agent)
        return f"{memory_dir}/rules.json"
    
    def _get_history_file(self) -> str:
        """Get path to rules history file"""
        from python.helpers import memory
        memory_dir = memory.get_memory_subdir_abs(self.agent)
        return f"{memory_dir}/rules_history.json"
    
    def _load_rules(self):
        """Load rules from file"""
        rules_file = self._get_rules_file()
        
        if files.exists(rules_file):
            with open(rules_file, 'r') as f:
                data = json.load(f)
                self.rules = {
                    r["id"]: Rule.from_dict(r)
                    for r in data.get("rules", [])
                }
        
        # Load history
        history_file = self._get_history_file()
        if files.exists(history_file):
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.rule_history = {
                    rule_id: [Rule.from_dict(r) for r in versions]
                    for rule_id, versions in data.items()
                }
    
    def _save_rules(self):
        """Save rules to file"""
        rules_file = self._get_rules_file()
        data = {
            "rules": [r.to_dict() for r in self.rules.values()]
        }
        
        with open(rules_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_history(self):
        """Save rule history"""
        history_file = self._get_history_file()
        data = {
            rule_id: [r.to_dict() for r in versions]
            for rule_id, versions in self.rule_history.items()
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_rule(self, rule: Rule) -> bool:
        """Add a new rule"""
        if rule.id in self.rules:
            return False
        
        self.rules[rule.id] = rule
        self._save_rules()
        return True
    
    def update_rule(self, rule_id: str, content: Optional[str] = None,
                   enabled: Optional[bool] = None, **kwargs) -> bool:
        """Update an existing rule (creates new version)"""
        if rule_id not in self.rules:
            return False
        
        old_rule = self.rules[rule_id]
        
        # Save old version to history
        if rule_id not in self.rule_history:
            self.rule_history[rule_id] = []
        self.rule_history[rule_id].append(old_rule)
        
        # Create new version
        new_rule = Rule(
            id=rule_id,
            name=old_rule.name,
            content=content if content is not None else old_rule.content,
            type=old_rule.type,
            priority=old_rule.priority,
            enabled=enabled if enabled is not None else old_rule.enabled,
            conditions=old_rule.conditions.copy(),
            tags=old_rule.tags.copy(),
            created_at=old_rule.created_at,
            updated_at=datetime.now(),
            created_by=old_rule.created_by,
            version=old_rule.version + 1,
            parent_version_id=old_rule.id
        )
        
        # Apply additional updates
        for key, value in kwargs.items():
            if hasattr(new_rule, key):
                setattr(new_rule, key, value)
        
        self.rules[rule_id] = new_rule
        self._save_rules()
        self._save_history()
        return True
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_rules()
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID"""
        return self.rules.get(rule_id)
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[Rule]:
        """Get all rules of a specific type"""
        return [r for r in self.rules.values() if r.type == rule_type]
    
    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """Get all rules with a specific tag"""
        return [r for r in self.rules.values() if tag in r.tags]
    
    def get_applicable_rules(self, context: Dict) -> List[Rule]:
        """Get all rules that apply to the given context"""
        applicable = [
            r for r in self.rules.values()
            if r.applies_to_context(context)
        ]
        
        # Sort by priority
        applicable.sort(key=lambda r: r.priority.value)
        return applicable
    
    def compile_rules_prompt(self, context: Dict) -> str:
        """Compile applicable rules into a prompt"""
        applicable_rules = self.get_applicable_rules(context)
        
        if not applicable_rules:
            # Return default behavior
            return self.agent.read_prompt("agent.system.behaviour_default.md")
        
        # Group by type
        rules_by_type = {}
        for rule in applicable_rules:
            if rule.type not in rules_by_type:
                rules_by_type[rule.type] = []
            rules_by_type[rule.type].append(rule)
        
        # Build prompt
        sections = []
        for rule_type, rules in rules_by_type.items():
            section = f"\n## {rule_type.value.title()} Rules\n\n"
            for rule in rules:
                section += f"### {rule.name}\n{rule.content}\n\n"
            sections.append(section)
        
        return "\n".join(sections)
    
    def validate_rule(self, rule: Rule) -> List[str]:
        """Validate a rule and return list of issues"""
        issues = []
        
        # Check for empty content
        if not rule.content.strip():
            issues.append("Rule content is empty")
        
        # Check for conflicts with existing rules
        for existing in self.rules.values():
            if existing.id != rule.id and existing.name == rule.name:
                issues.append(f"Rule name conflicts with existing rule: {existing.id}")
        
        # Validate conditions
        for cond in rule.conditions:
            if not cond.type:
                issues.append("Condition missing type")
            if not cond.operator:
                issues.append("Condition missing operator")
        
        return issues
    
    def get_rule_history(self, rule_id: str) -> List[Rule]:
        """Get version history for a rule"""
        return self.rule_history.get(rule_id, [])
    
    def revert_rule(self, rule_id: str, version: int) -> bool:
        """Revert a rule to a previous version"""
        history = self.get_rule_history(rule_id)
        
        for old_rule in history:
            if old_rule.version == version:
                # Create new rule based on old version
                new_rule = Rule(
                    id=rule_id,
                    name=old_rule.name,
                    content=old_rule.content,
                    type=old_rule.type,
                    priority=old_rule.priority,
                    enabled=old_rule.enabled,
                    conditions=old_rule.conditions.copy(),
                    tags=old_rule.tags.copy(),
                    created_at=old_rule.created_at,
                    updated_at=datetime.now(),
                    created_by=old_rule.created_by,
                    version=self.rules[rule_id].version + 1 if rule_id in self.rules else 1,
                    parent_version_id=rule_id
                )
                
                self.rules[rule_id] = new_rule
                self._save_rules()
                return True
        
        return False
    
    def export_ruleset(self, name: str, description: str, 
                      rule_ids: Optional[List[str]] = None) -> RuleSet:
        """Export rules as a ruleset"""
        if rule_ids:
            rules = [self.rules[rid] for rid in rule_ids if rid in self.rules]
        else:
            rules = list(self.rules.values())
        
        return RuleSet(
            name=name,
            description=description,
            rules=rules
        )
    
    def import_ruleset(self, ruleset: RuleSet, overwrite: bool = False) -> int:
        """Import a ruleset"""
        imported = 0
        
        for rule in ruleset.rules:
            if rule.id in self.rules and not overwrite:
                continue
            
            self.rules[rule.id] = rule
            imported += 1
        
        if imported > 0:
            self._save_rules()
        
        return imported


# Rule templates
RULE_TEMPLATES = {
    "always_verify": Rule(
        id="template_always_verify",
        name="Always Verify Information",
        content="Always verify information from external sources before presenting it as fact.",
        type=RuleType.BEHAVIOR,
        priority=RulePriority.HIGH,
        tags=["accuracy", "verification"]
    ),
    "security_first": Rule(
        id="template_security_first",
        name="Security First",
        content="Never execute commands that could compromise system security without explicit user confirmation.",
        type=RuleType.SECURITY,
        priority=RulePriority.CRITICAL,
        tags=["security", "safety"]
    ),
    "explain_reasoning": Rule(
        id="template_explain_reasoning",
        name="Explain Reasoning",
        content="Always explain your reasoning and thought process when making decisions.",
        type=RuleType.BEHAVIOR,
        priority=RulePriority.MEDIUM,
        tags=["transparency", "communication"]
    )
}
