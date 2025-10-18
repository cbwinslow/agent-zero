# Error Logs Tool

Use this tool to manage and view error history and solutions.

## Methods

### statistics
Get overall error statistics including total errors, resolution rate, and breakdowns by category and type.

**Example:**
```json
{
    "thoughts": [
        "I should check what errors have been occurring",
        "This will help me understand common issues"
    ],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "statistics"
    }
}
```

### search
Search for errors by type or category.

**Arguments:**
- `error_type` (optional): Search by exception type (e.g., "ValueError", "ConnectionError")
- `category` (optional): Search by category (e.g., "network", "file_io", "llm_api", "tool_execution")

**Example:**
```json
{
    "thoughts": [
        "I need to find all network-related errors",
        "This will help identify connection issues"
    ],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "search",
        "category": "network"
    }
}
```

### solutions
Get solutions for a specific error by its ID.

**Arguments:**
- `error_id` (required): The error ID to get solutions for

**Example:**
```json
{
    "thoughts": [
        "I want to see if there are solutions for this error",
        "The error ID is abc123def456"
    ],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "solutions",
        "error_id": "abc123def456"
    }
}
```

### recommendations
Get error prevention recommendations based on error history.

**Arguments:**
- `category` (optional): Get recommendations for a specific category

**Example:**
```json
{
    "thoughts": [
        "I should get recommendations to prevent future errors",
        "Let's focus on file I/O errors"
    ],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "recommendations",
        "category": "file_io"
    }
}
```

### resolve
Mark an error as resolved with a solution.

**Arguments:**
- `error_id` (required): The error ID to mark as resolved
- `solution` (required): Description of the solution applied

**Example:**
```json
{
    "thoughts": [
        "I found a solution for this error",
        "I should record it for future reference"
    ],
    "tool_name": "error_logs",
    "tool_args": {
        "method": "resolve",
        "error_id": "abc123def456",
        "solution": "Added retry logic with exponential backoff"
    }
}
```

## Error Categories

The system automatically categorizes errors into:
- **network**: Connection, timeout, HTTP, SSL errors
- **file_io**: File not found, permission, path errors
- **llm_api**: API rate limits, quota, model errors
- **memory**: Memory allocation errors
- **tool_execution**: Tool-specific errors
- **import**: Missing dependencies, import errors
- **data_validation**: ValueError, TypeError, KeyError
- **unknown**: Uncategorized errors

## When to Use

Use this tool to:
1. Debug recurring issues by checking error history
2. Find known solutions to similar errors
3. Get recommendations for preventing errors
4. Record solutions when you fix errors
5. Monitor overall system health and error patterns

The error tracking system automatically logs all errors with context, so you can always refer back to them.
