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
        """
        Determine whether this condition matches the provided context.
        
        Parameters:
        	context (Dict): Mapping of context keys to their values; the condition's `type` is used as the lookup key.
        
        Returns:
        	True if the context contains the condition's `type` and the comparison defined by `operator` holds against `value`, `False` otherwise.
        
        Notes:
        	Supported `operator` values: "equals", "contains", "greater_than", "less_than", "in". If the context lacks the condition's `type` or the operator is unrecognized, the condition evaluates to `False`.
        """
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
        """
        Serialize the Rule into a dictionary suitable for JSON storage or transmission.
        
        Returns:
            dict: A mapping containing rule metadata and state with keys:
                - `id` (str)
                - `name` (str)
                - `content` (str)
                - `type` (str): enum value of the rule type
                - `priority` (int): numeric value of the rule priority
                - `enabled` (bool)
                - `conditions` (List[dict]): each with `type`, `operator`, and `value`
                - `tags` (List[str])
                - `created_at` (str): ISO 8601 timestamp
                - `updated_at` (str): ISO 8601 timestamp
                - `created_by` (Optional[str])
                - `version` (int)
                - `parent_version_id` (Optional[str])
        """
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
        """
        Create a Rule instance from a dictionary representation.
        
        Reconstructs rule fields from a mapping produced by Rule.to_dict(), converting enum values and ISO datetime strings back to their native types, rebuilding RuleCondition objects from condition dictionaries, and applying sensible defaults when keys are missing.
        
        Parameters:
            data (Dict): Dictionary containing rule data (keys include "id", "name", "content", "type", "created_at", "updated_at", and optional keys like "priority", "enabled", "conditions", "tags", "created_by", "version", "parent_version_id").
        
        Returns:
            Rule: A Rule object populated from the provided dictionary.
        """
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
        """
        Determines whether this rule applies to the provided context.
        
        Parameters:
            context (Dict): Mapping of contextual values used by the rule's conditions.
        
        Returns:
            `true` if the rule is enabled and all conditions evaluate to true (or there are no conditions), `false` otherwise.
        """
        if not self.enabled:
            return False
        
        if not self.conditions:
            return True
        
        # All conditions must be met
        return all(cond.evaluate(context) for cond in self.conditions)
    
    def get_hash(self) -> str:
        """
        Compute a SHA-256 hash of the rule's content.
        
        Returns:
            hash (str): Hexadecimal SHA-256 digest of the rule's content.
        """
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
        """
        Serialize the RuleSet into a JSON-serializable dictionary.
        
        Returns:
            dict: A dictionary containing the RuleSet fields:
                - `name` (str): RuleSet name.
                - `description` (str): RuleSet description.
                - `rules` (List[dict]): List of serialized rules produced by each rule's `to_dict()`.
                - `version` (str): RuleSet version string.
                - `created_at` (str): ISO 8601 string of the creation timestamp.
        """
        return {
            "name": self.name,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RuleSet':
        """
        Create a RuleSet from a dictionary produced by RuleSet.to_dict().
        
        Parameters:
            data (Dict): Serialized ruleset dictionary. Expected keys: "name", "description", "rules" (list of rule dicts, optional), "version" (optional), and "created_at" (ISO 8601 string).
        
        Returns:
            RuleSet: Deserialized RuleSet with Rule objects reconstructed from the "rules" list, "version" defaulting to "1.0.0" if absent, and "created_at" parsed from ISO 8601.
        """
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
        """
        Initialize the RuleManager for a specific Agent and load persisted rules and history.
        
        Parameters:
            agent (Agent): The agent instance whose memory directory and default prompts are used for rule persistence and prompt compilation.
        """
        self.agent = agent
        self.rules: Dict[str, Rule] = {}
        self.rule_history: Dict[str, List[Rule]] = {}
        self._load_rules()
    
    def _get_rules_file(self) -> str:
        """
        Provide the filesystem path to the rules.json file in the agent's memory subdirectory.
        
        Returns:
            rules_path (str): Absolute path to the rules.json file for the agent.
        """
        from python.helpers import memory
        memory_dir = memory.get_memory_subdir_abs(self.agent)
        return f"{memory_dir}/rules.json"
    
    def _get_history_file(self) -> str:
        """
        Return the absolute filesystem path to the agent's rules history JSON file.
        
        Returns:
            history_file_path (str): Absolute path to `rules_history.json` in the agent's memory subdirectory.
        """
        from python.helpers import memory
        memory_dir = memory.get_memory_subdir_abs(self.agent)
        return f"{memory_dir}/rules_history.json"
    
    def _load_rules(self):
        """
        Load persisted rules and rule history from the agent's memory files into the manager.
        
        Reads the rules file returned by _get_rules_file(), expecting a JSON object with a "rules" list of rule dictionaries, and populates self.rules mapping rule id -> Rule via Rule.from_dict. Reads the history file returned by _get_history_file(), expecting a JSON object mapping rule ids to lists of rule dictionaries, and populates self.rule_history with lists of Rule instances. If either file is missing, the corresponding in-memory mapping is left unchanged.
        """
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
        """
        Persist the current in-memory rules to the agent's rules storage file on disk.
        
        Serializes each Rule to a dictionary and writes the collection as JSON to the configured rules file.
        """
        rules_file = self._get_rules_file()
        data = {
            "rules": [r.to_dict() for r in self.rules.values()]
        }
        
        with open(rules_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_history(self):
        """
        Persist the in-memory rule history to the agent's rules_history.json file.
        
        Serializes the manager's `rule_history` mapping (rule ID -> list of Rule versions) to a JSON file in the agent's memory directory, writing each Rule as its dictionary representation.
        """
        history_file = self._get_history_file()
        data = {
            rule_id: [r.to_dict() for r in versions]
            for rule_id, versions in self.rule_history.items()
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_rule(self, rule: Rule) -> bool:
        """
        Add a new Rule to the manager and persist the updated rules.
        
        Parameters:
            rule (Rule): The rule to add.
        
        Returns:
            bool: `True` if the rule was added and persisted, `False` if a rule with the same `id` already exists.
        """
        if rule.id in self.rules:
            return False
        
        self.rules[rule.id] = rule
        self._save_rules()
        return True
    
    def update_rule(self, rule_id: str, content: Optional[str] = None,
                   enabled: Optional[bool] = None, **kwargs) -> bool:
        """
                   Create a new version of an existing rule by applying provided changes and persist the update.
                   
                   Parameters:
                       rule_id (str): Identifier of the rule to update.
                       content (Optional[str]): If provided, replaces the rule's content in the new version.
                       enabled (Optional[bool]): If provided, sets the enabled flag in the new version.
                       **kwargs: Additional Rule attributes to update on the new version; only attributes that exist on the Rule object will be applied.
                   
                   Returns:
                       bool: `True` if the rule was found, versioned, and saved; `False` if no rule with `rule_id` exists.
                   """
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
        """
        Delete a rule from the manager by its identifier.
        
        Parameters:
            rule_id (str): The identifier of the rule to remove.
        
        Returns:
            bool: `True` if a rule with the given id existed and was deleted, `False` otherwise.
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_rules()
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        Retrieve a rule by its identifier.
        
        Returns:
            The `Rule` with the matching id, or `None` if no rule with that id exists.
        """
        return self.rules.get(rule_id)
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[Rule]:
        """Get all rules of a specific type"""
        return [r for r in self.rules.values() if r.type == rule_type]
    
    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """
        Return all rules that include the given tag.
        
        Parameters:
        	tag (str): Tag to filter rules by.
        
        Returns:
        	List[Rule]: Rules that contain the specified tag.
        """
        return [r for r in self.rules.values() if tag in r.tags]
    
    def get_applicable_rules(self, context: Dict) -> List[Rule]:
        """
        List rules applicable to the provided context, ordered by priority (lowest value first).
        
        Parameters:
            context (Dict): Mapping of contextual keys and values evaluated against each rule's conditions.
        
        Returns:
            A list of Rule objects that apply to the context, sorted by ascending RulePriority value.
        """
        applicable = [
            r for r in self.rules.values()
            if r.applies_to_context(context)
        ]
        
        # Sort by priority
        applicable.sort(key=lambda r: r.priority.value)
        return applicable
    
    def compile_rules_prompt(self, context: Dict) -> str:
        """
        Compile applicable rules for the given context into a structured prompt grouped by rule type.
        
        When one or more rules apply to the provided context, returns a formatted prompt containing sections per rule type with each rule's name and content. If no rules apply, returns the agent's default behavior prompt read from the system prompt file.
        
        Parameters:
            context (Dict): Contextual data used to evaluate rule conditions (keys referenced by RuleCondition.evaluate).
        
        Returns:
            str: The assembled prompt string (grouped by rule type) or the agent's default behavior prompt if no rules apply.
        """
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
        """
        Identify validation issues for a given Rule.
        
        Performs checks for empty content, name conflicts with other stored rules, and missing condition fields.
        
        Parameters:
            rule (Rule): The rule to validate.
        
        Returns:
            List[str]: A list of human-readable validation issue messages; empty if the rule has no problems.
        """
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
        """
        Retrieve the version history for a rule identified by its ID.
        
        Parameters:
            rule_id (str): The unique identifier of the rule to lookup.
        
        Returns:
            List[Rule]: A list of historical Rule versions for the given rule ID, or an empty list if no history exists.
        """
        return self.rule_history.get(rule_id, [])
    
    def revert_rule(self, rule_id: str, version: int) -> bool:
        """
        Revert a rule to a specified historical version.
        
        If the requested version exists in the rule's history, create a new current rule derived from that historical version (incrementing the current rule's version number and linking the parent_version_id), persist the updated rules, and return `true`. If the requested version is not found, perform no changes and return `false`.
        
        Parameters:
            rule_id (str): Identifier of the rule to revert.
            version (int): Version number in the rule's history to revert to.
        
        Returns:
            `true` if the rule was reverted and persisted successfully, `false` otherwise.
        """
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
        """
                      Create a RuleSet containing a selection of managed rules with provided metadata.
                      
                      Parameters:
                          name (str): The name to assign to the exported RuleSet.
                          description (str): A short description for the exported RuleSet.
                          rule_ids (Optional[List[str]]): If provided, only rules whose IDs are present in this list and managed by this manager are included; if omitted, all managed rules are included.
                      
                      Returns:
                          RuleSet: A RuleSet instance populated with the selected Rule objects and the given name and description.
                      """
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
        """
        Import rules from a RuleSet into the manager, optionally replacing existing rules.
        
        Parameters:
            ruleset (RuleSet): The ruleset whose rules will be imported.
            overwrite (bool): If True, existing rules with the same id are replaced; if False, existing rules are skipped.
        
        Returns:
            int: The number of rules actually imported. If at least one rule was imported, the manager's persisted rule storage is updated.
        """
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
