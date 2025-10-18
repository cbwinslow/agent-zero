# Agent Zero Tools Guide

This guide provides comprehensive documentation for all tools available in Agent Zero.

## Table of Contents

1. [Core Tools](#core-tools)
2. [Memory Tools](#memory-tools)
3. [Code Execution Tools](#code-execution-tools)
4. [Search and Information](#search-and-information)
5. [Communication Tools](#communication-tools)
6. [Workflow and Automation](#workflow-and-automation)
7. [Error Management](#error-management)
8. [Git Integration](#git-integration)
9. [Custom Tools](#custom-tools)

---

## Core Tools

### response
**Purpose**: Return a final response to the user or superior agent.

**When to use**: When the task is complete and you have a final answer.

**Parameters**:
- `message` (required): The response message to return

**Example**:
```json
{
    "thoughts": ["I have completed the task", "Time to respond"],
    "tool_name": "response",
    "tool_args": {
        "message": "Task completed successfully. Here are the results..."
    }
}
```

### input
**Purpose**: Request additional input from the user.

**When to use**: When you need clarification or more information to proceed.

**Parameters**:
- `message` (required): The question or prompt for the user

**Example**:
```json
{
    "thoughts": ["I need to know the file path", "Let me ask the user"],
    "tool_name": "input",
    "tool_args": {
        "message": "Please provide the path to the configuration file you want me to update."
    }
}
```

---

## Memory Tools

### memory_save
**Purpose**: Save important information to long-term memory.

**When to use**: When you encounter information that should be remembered for future use.

**Parameters**:
- `memory` (required): The content to remember
- `area` (optional): Memory area ("main", "fragments", "solutions", "instruments")

**Example**:
```json
{
    "thoughts": ["User mentioned their preference", "I should remember this"],
    "tool_name": "memory_save",
    "tool_args": {
        "memory": "User prefers Python for scripting tasks",
        "area": "main"
    }
}
```

### memory_load
**Purpose**: Retrieve relevant memories based on a query.

**When to use**: When you need to recall previously saved information.

**Parameters**:
- `query` (required): What to search for in memories
- `limit` (optional): Maximum number of memories to retrieve (default: 10)
- `area` (optional): Specific memory area to search

**Example**:
```json
{
    "thoughts": ["I need to recall user preferences", "Let me search memory"],
    "tool_name": "memory_load",
    "tool_args": {
        "query": "user preferences programming languages",
        "limit": 5
    }
}
```

### memory_delete
**Purpose**: Remove specific memories from storage.

**When to use**: When information is outdated or incorrect.

**Parameters**:
- `ids` (required): List of memory IDs to delete

### memory_forget
**Purpose**: Remove all memories from a specific area.

**When to use**: For bulk cleanup of memories.

**Parameters**:
- `area` (optional): Area to clear (defaults to all)

---

## Code Execution Tools

### code_execution_tool
**Purpose**: Execute code in various languages (Python, Bash, JavaScript, etc.).

**When to use**: When you need to run code to accomplish a task.

**Parameters**:
- `language` (required): Programming language ("python", "bash", "javascript", etc.)
- `code` (required): The code to execute
- `timeout` (optional): Maximum execution time in seconds

**Example**:
```json
{
    "thoughts": ["I need to analyze this data", "Let me write Python code"],
    "tool_name": "code_execution_tool",
    "tool_args": {
        "language": "python",
        "code": "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.describe())"
    }
}
```

**Supported Languages**:
- `python` - Python 3
- `bash` - Bash shell
- `javascript` - Node.js
- `nodejs` - Node.js (alias)

---

## Search and Information

### search_engine
**Purpose**: Search the web for information.

**When to use**: When you need current information or facts from the internet.

**Parameters**:
- `query` (required): Search query

**Example**:
```json
{
    "thoughts": ["I need current information about this topic", "Let me search"],
    "tool_name": "search_engine",
    "tool_args": {
        "query": "latest Python 3.12 features"
    }
}
```

### document_query
**Purpose**: Query and analyze documents (PDF, text, etc.).

**When to use**: When you need to extract information from documents.

**Parameters**:
- `query` (required): What to search for in the document
- `file_path` (required): Path to the document

---

## Communication Tools

### notify_user
**Purpose**: Send a notification to the user.

**When to use**: For important alerts or updates during long-running tasks.

**Parameters**:
- `message` (required): Notification message
- `title` (optional): Notification title

**Example**:
```json
{
    "thoughts": ["This task will take a while", "Let me notify the user"],
    "tool_name": "notify_user",
    "tool_args": {
        "title": "Task Update",
        "message": "Data processing is 50% complete"
    }
}
```

### call_subordinate
**Purpose**: Delegate a subtask to a subordinate agent.

**When to use**: When a subtask requires focused attention or specialized expertise.

**Parameters**:
- `message` (required): Instructions for the subordinate
- `reset_message` (optional): Whether to reset subordinate's context

**Example**:
```json
{
    "thoughts": ["This requires detailed research", "Let me delegate to a subordinate"],
    "tool_name": "call_subordinate",
    "tool_args": {
        "message": "Research the top 5 Python web frameworks and compare their features"
    }
}
```

---

## Workflow and Automation

### scheduler
**Purpose**: Schedule tasks to run at specific times or intervals.

**When to use**: For recurring tasks or delayed execution.

**Methods**:
- `add` - Schedule a new task
- `list` - List scheduled tasks
- `remove` - Remove a scheduled task
- `pause` - Pause a scheduled task
- `resume` - Resume a paused task

**Example (Add Task)**:
```json
{
    "thoughts": ["User wants daily backups", "Let me schedule this"],
    "tool_name": "scheduler",
    "tool_args": {
        "method": "add",
        "schedule": "0 2 * * *",
        "task_description": "Run daily backup",
        "message": "Execute the backup script in /scripts/backup.sh"
    }
}
```

### multi_agent_delegation
**Purpose**: Coordinate multiple agents working on related subtasks.

**When to use**: For complex tasks requiring parallel or coordinated effort.

**Parameters**:
- `strategy` (required): "sequential", "parallel", or "adaptive"
- `subtasks` (required): List of subtasks to delegate
- `context` (optional): Shared context for all agents

---

## Error Management

### error_logs
**Purpose**: View and manage error history and solutions.

**When to use**: For debugging recurring issues or finding known solutions.

**Methods**:
- `statistics` - View error statistics
- `search` - Search for errors by type or category
- `solutions` - Get solutions for an error
- `recommendations` - Get error prevention recommendations
- `resolve` - Mark an error as resolved

**Example (View Statistics)**:
```json
{
    "thoughts": ["I should check what errors have been occurring", "Let me view stats"],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "statistics"
    }
}
```

**Example (Search Errors)**:
```json
{
    "thoughts": ["Looking for network-related errors", "Let me search"],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "search",
        "category": "network"
    }
}
```

---

## Git Integration

### git_workflow
**Purpose**: Perform Git operations on repositories.

**When to use**: For version control tasks, repository management, or code collaboration.

**Methods**:
- `status` - Get repository status
- `info` - Get repository information
- `branch_create` - Create a new branch
- `branch_checkout` - Checkout a branch
- `branch_list` - List branches
- `commit` - Create a commit
- `push` - Push changes to remote
- `pull` - Pull changes from remote
- `diff` - View changes
- `conflicts` - Check for merge conflicts

**Example (Create Branch)**:
```json
{
    "thoughts": ["User wants a new feature branch", "Let me create it"],
    "tool_name": "git_workflow",
    "tool_args": {
        "method": "branch_create",
        "branch_name": "feature/new-login-system",
        "checkout": true
    }
}
```

**Example (Commit Changes)**:
```json
{
    "thoughts": ["Changes are ready to commit", "Let me commit them"],
    "tool_name": "git_workflow",
    "tool_args": {
        "method": "commit",
        "message": "Add user authentication system",
        "add_all": true
    }
}
```

---

## Browser Tools

### browser_agent
**Purpose**: Automate browser interactions and web scraping.

**When to use**: For web automation, form filling, or data extraction.

**Parameters**:
- `task` (required): Description of what to do
- `url` (optional): Starting URL

**Example**:
```json
{
    "thoughts": ["Need to extract data from this website", "Let me use browser automation"],
    "tool_name": "browser_agent",
    "tool_args": {
        "task": "Navigate to example.com, fill in the search form with 'Python', and extract the first 5 results",
        "url": "https://example.com"
    }
}
```

---

## Memory Monitor

### memory_monitor
**Purpose**: Control and interact with the automatic memory monitoring system.

**When to use**: To manage automatic memory saving and retrieval.

**Methods**:
- `start` - Start the memory monitor
- `stop` - Stop the memory monitor
- `status` - Get current status and statistics
- `short_term` - View short-term memories
- `pending` - View pending long-term memories
- `configure` - Update monitor configuration

**Example (Check Status)**:
```json
{
    "thoughts": ["I should check the memory monitor status", "Let me see what it's doing"],
    "tool_name": "memory_monitor",
    "tool_args": {
        "method": "status"
    }
}
```

**Example (Configure)**:
```json
{
    "thoughts": ["Need to adjust memory importance threshold", "Let me configure it"],
    "tool_name": "memory_monitor",
    "tool_args": {
        "method": "configure",
        "importance_threshold": 0.6,
        "auto_save": true
    }
}
```

---

## Custom Tools

### Creating Custom Tools

You can create custom tools for Agent Zero by:

1. **Create a tool file** in `python/tools/your_tool.py`
2. **Inherit from Tool class**:
   ```python
   from python.helpers.tool import Tool, Response
   
   class YourTool(Tool):
       async def execute(self, **kwargs):
           # Your tool logic here
           return Response(message="Result", break_loop=False)
   ```

3. **Create a prompt file** in `prompts/agent.system.tool.your_tool.md`
4. **Document the tool** with examples and parameters

### Tool Response

All tools return a `Response` object:
- `message`: The result message
- `break_loop`: Whether to end the agent's message loop (True for final responses)

---

## Best Practices

### When to Use Each Tool

1. **Use `response`** when you have a final answer
2. **Use `input`** when you need more information
3. **Use `memory_save`** for important facts to remember
4. **Use `memory_load`** before starting complex tasks
5. **Use `code_execution_tool`** for data processing and automation
6. **Use `search_engine`** for current information
7. **Use `call_subordinate`** for complex subtasks
8. **Use `error_logs`** when debugging or seeking solutions
9. **Use `git_workflow`** for version control operations

### Error Handling

Tools may fail. Always:
- Check tool results for errors
- Have a fallback plan
- Log errors to error tracker when appropriate
- Consider using `error_logs` to find solutions

### Memory Management

- Save memories for important facts, preferences, and solutions
- Use appropriate memory areas (main, fragments, solutions, instruments)
- Load memories at the start of related tasks
- Clean up outdated memories periodically

### Code Execution

- Set appropriate timeouts
- Handle errors in your code
- Use safe practices (validate inputs, handle exceptions)
- Test code with small inputs first

---

## Tool Chaining

You can use multiple tools in sequence to accomplish complex tasks:

1. **Search** for information
2. **Process** with code
3. **Save** results to memory
4. **Respond** to user

Example workflow:
```
search_engine → code_execution_tool → memory_save → response
```

---

## Troubleshooting

### Tool Not Found
- Check tool name spelling
- Verify tool file exists in `python/tools/`
- Check for import errors in tool file

### Tool Execution Fails
- Check tool arguments are correct
- Verify required parameters are provided
- Check error logs for similar failures
- Review tool documentation

### Memory Issues
- Check memory database is accessible
- Verify embeddings model is configured
- Check available disk space

---

## Additional Resources

- [Agent Zero Documentation](../README.md)
- [Extensibility Guide](./extensibility.md)
- [MCP Servers Guide](./mcp_servers_guide.md)
- [Development Guide](./development.md)
