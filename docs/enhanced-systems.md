# Enhanced Memory & Rules Systems

Agent Zero now includes enhanced memory and rules systems with advanced features for better control and organization.

## Enhanced Memory System

### Features

- **Semantic Similarity Search**: Advanced retrieval with multiple weighting strategies
- **Temporal Weighting**: Recent memories score higher in search results
- **Importance Scoring**: Assign importance levels to memories
- **Memory Tagging**: Organize memories with tags
- **Access Tracking**: Track how often memories are accessed
- **Memory Consolidation**: Automatic deduplication of similar memories
- **Statistics & Analytics**: Detailed insights into memory usage

### Memory Importance Levels

```python
class MemoryImportance(Enum):
    CRITICAL = 5  # Must-remember information
    HIGH = 4      # Important information
    MEDIUM = 3    # Default importance
    LOW = 2       # Nice-to-have information
    TRIVIAL = 1   # Rarely useful information
```

### Usage Examples

#### Adding Memories with Metadata

```python
from python.helpers.enhanced_memory import EnhancedMemory, MemoryImportance

# Add important memory
doc_id = await enhanced_memory.add_memory(
    text="User prefers concise responses",
    importance=MemoryImportance.HIGH,
    tags=["preference", "communication"],
    context="During conversation about response style"
)
```

#### Enhanced Search

```python
# Search with temporal and importance weighting
results = await enhanced_memory.search_enhanced(
    query="user preferences",
    max_results=5,
    use_temporal_weighting=True,
    use_importance_weighting=True,
    filter_tags=["preference"]
)
```

#### Memory Statistics

```python
stats = enhanced_memory.get_memory_statistics()
# Returns:
# {
#     "total_memories": 150,
#     "importance_distribution": {
#         "CRITICAL": 5,
#         "HIGH": 20,
#         "MEDIUM": 100,
#         "LOW": 20,
#         "TRIVIAL": 5
#     },
#     "total_accesses": 500,
#     "average_accesses": 3.33,
#     "age_distribution": {
#         "today": 10,
#         "this_week": 30,
#         "this_month": 60,
#         "older": 50
#     }
# }
```

### API Endpoints

#### POST /api/memory_search

Search memories with enhanced filtering.

**Request:**
```json
{
  "query": "user preferences",
  "max_results": 5,
  "use_temporal_weighting": true,
  "filter_tags": ["preference"]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "content": "User prefers concise responses",
      "score": 0.95,
      "metadata": {
        "importance": 4,
        "tags": ["preference", "communication"],
        "created_at": "2024-01-15T10:30:00"
      }
    }
  ]
}
```

#### POST /api/memory_add

Add memory with metadata.

**Request:**
```json
{
  "text": "User is interested in machine learning",
  "importance": "HIGH",
  "tags": ["interest", "topic"],
  "context": "Conversation about career goals"
}
```

#### GET /api/memory_stats

Get memory usage statistics.

## Enhanced Rules System

### Features

- **Rule Versioning**: Track changes to rules over time
- **Rule Validation**: Ensure rules are valid before applying
- **Conditional Rules**: Rules that apply based on context
- **Rule Priority**: Control rule application order
- **Rule Templates**: Pre-built rule templates
- **Rule History**: View and revert to previous versions
- **Import/Export**: Share rulesets between agents

### Rule Types

```python
class RuleType(Enum):
    BEHAVIOR = "behavior"      # How agent should behave
    CONSTRAINT = "constraint"  # What agent cannot do
    PREFERENCE = "preference"  # Agent preferences
    SECURITY = "security"      # Security-related rules
    CUSTOM = "custom"         # User-defined rules
```

### Rule Priority

```python
class RulePriority(Enum):
    CRITICAL = 1  # Must be followed
    HIGH = 2      # Should be followed
    MEDIUM = 3    # Default priority
    LOW = 4       # Nice to follow
```

### Usage Examples

#### Creating a Rule

```python
from python.helpers.enhanced_rules import Rule, RuleType, RulePriority

rule = Rule(
    id="verify_sources",
    name="Verify Information Sources",
    content="Always cite sources when providing factual information",
    type=RuleType.BEHAVIOR,
    priority=RulePriority.HIGH,
    tags=["accuracy", "transparency"]
)
```

#### Conditional Rules

```python
# Rule that only applies during certain contexts
rule = Rule(
    id="coding_standards",
    name="Follow Python PEP 8",
    content="Use PEP 8 style guide for Python code",
    type=RuleType.BEHAVIOR,
    conditions=[
        RuleCondition(
            type="task",
            operator="contains",
            value="python"
        )
    ]
)
```

#### Managing Rules

```python
from python.helpers.enhanced_rules import RuleManager

rule_mgr = RuleManager(agent)

# Add rule
rule_mgr.add_rule(rule)

# Update rule (creates new version)
rule_mgr.update_rule(
    rule_id="verify_sources",
    content="Always cite sources with URLs when available"
)

# Get applicable rules for context
context = {"task": "write python code"}
applicable = rule_mgr.get_applicable_rules(context)

# Generate prompt from rules
prompt = rule_mgr.compile_rules_prompt(context)
```

#### Rule History

```python
# View version history
history = rule_mgr.get_rule_history("verify_sources")
for version in history:
    print(f"Version {version.version}: {version.updated_at}")

# Revert to previous version
rule_mgr.revert_rule("verify_sources", version=2)
```

#### Import/Export Rulesets

```python
# Export ruleset
ruleset = rule_mgr.export_ruleset(
    name="My Custom Rules",
    description="Personal agent rules",
    rule_ids=["rule1", "rule2"]
)

# Save to file
with open("my_rules.json", "w") as f:
    json.dump(ruleset.to_dict(), f)

# Import ruleset
with open("my_rules.json", "r") as f:
    data = json.load(f)
    ruleset = RuleSet.from_dict(data)
    rule_mgr.import_ruleset(ruleset)
```

### API Endpoints

#### GET /api/rule_list

List all rules.

**Query Parameters:**
- `type`: Filter by rule type
- `tag`: Filter by tag

**Response:**
```json
{
  "success": true,
  "rules": [
    {
      "id": "verify_sources",
      "name": "Verify Information Sources",
      "content": "Always cite sources...",
      "type": "behavior",
      "priority": 2,
      "enabled": true,
      "tags": ["accuracy"],
      "version": 1
    }
  ]
}
```

#### POST /api/rule_add

Add a new rule.

**Request:**
```json
{
  "name": "Security First",
  "content": "Never execute dangerous commands without confirmation",
  "type": "security",
  "priority": 1,
  "tags": ["security", "safety"]
}
```

#### POST /api/rule_update

Update an existing rule.

**Request:**
```json
{
  "rule_id": "verify_sources",
  "content": "Updated content...",
  "enabled": true
}
```

#### POST /api/rule_delete

Delete a rule.

**Request:**
```json
{
  "rule_id": "verify_sources"
}
```

#### GET /api/rule_history

Get version history for a rule.

**Request:**
```json
{
  "rule_id": "verify_sources"
}
```

#### POST /api/rule_export

Export rules as a ruleset.

**Request:**
```json
{
  "name": "My Ruleset",
  "description": "Custom rules",
  "rule_ids": ["rule1", "rule2"]
}
```

#### POST /api/rule_import

Import a ruleset.

**Request:**
```json
{
  "ruleset": {
    "name": "Imported Rules",
    "rules": [...]
  },
  "overwrite": false
}
```

## Rule Templates

Pre-built rule templates are available:

### Always Verify
Ensures information is verified before presenting as fact.

### Security First
Prevents execution of potentially dangerous commands.

### Explain Reasoning
Requires the agent to explain its decision-making process.

### Usage

```python
from python.helpers.enhanced_rules import RULE_TEMPLATES

# Use a template
rule = RULE_TEMPLATES["always_verify"]
rule_mgr.add_rule(rule)
```

## Integration with Existing Systems

### Memory Integration

The enhanced memory system works seamlessly with the existing memory system:

```python
# Get base memory
base_memory = await Memory.get(agent)

# Wrap with enhanced features
enhanced_memory = EnhancedMemory(base_memory)

# Use enhanced features
results = await enhanced_memory.search_enhanced(...)
```

### Rules Integration

Rules are automatically applied to agent prompts:

```python
# In agent system prompt extension
rule_mgr = RuleManager(agent)
context = {"task": "current task"}
rules_prompt = rule_mgr.compile_rules_prompt(context)

# Rules are compiled and added to system prompt
system_prompt.insert(0, rules_prompt)
```

## Best Practices

### Memory Management

1. **Use appropriate importance levels**: Reserve CRITICAL for must-remember information
2. **Tag consistently**: Use consistent tag names for better organization
3. **Add context**: Include context to make memories more useful
4. **Review statistics**: Regularly check memory stats to optimize

### Rule Management

1. **Keep rules specific**: Specific rules are easier to understand and debug
2. **Use priorities wisely**: Reserve CRITICAL priority for essential rules
3. **Test rules**: Validate rules before enabling
4. **Version control**: Use history to track rule changes
5. **Export regularly**: Backup your rulesets

### Performance

1. **Limit search results**: Use reasonable max_results values
2. **Use filters**: Filter by tags to reduce search scope
3. **Consolidate memories**: Run periodic consolidation
4. **Disable unused rules**: Keep only active rules enabled

## Troubleshooting

### Memory Issues

**Problem**: Search returns irrelevant results
**Solution**: Adjust threshold, use more specific queries, add filters

**Problem**: Too many memories
**Solution**: Run consolidation, increase importance thresholds

### Rule Issues

**Problem**: Rules not applying
**Solution**: Check conditions, verify rule is enabled, check priority

**Problem**: Conflicting rules
**Solution**: Review validation errors, adjust priorities

## Future Enhancements

Planned features:
- Machine learning-based memory importance scoring
- Automatic rule conflict resolution
- Rule performance analytics
- Memory clustering and categorization
- Cross-user shared rule libraries
- Rule testing framework

## Support

For issues or questions:
- GitHub Issues: https://github.com/agent0ai/agent-zero/issues
- Documentation: /docs/
- Discord: https://discord.gg/B8KZKNsPpj
