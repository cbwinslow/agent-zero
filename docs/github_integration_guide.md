# GitHub Integration Guide for Agent Zero

This guide shows you how to integrate GitHub operations into your Agent Zero workflows for automated issue and pull request management.

## Quick Start

### 1. Setup

Add your GitHub credentials to the `.env` file:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_personal_access_token_here
GITHUB_REPOSITORY=owner/repo  # e.g., "cbwinslow/agent-zero"
```

### 2. Test the Integration

Run a simple test to verify everything works:

```bash
python examples/github_issue_workflow.py --example review
```

This will list all open issues in your repository.

## Agent Integration Patterns

### Pattern 1: Automated Issue Creation from User Feedback

When users report issues via chat, automatically create GitHub issues:

```python
# In your agent workflow
async def handle_user_issue_report(agent, issue_description):
    # Create issue on GitHub
    result = await agent.use_tool(
        "github_operations",
        method="create_issue",
        title=f"User Report: {issue_description[:50]}",
        body=f"**Reported by user:**\n\n{issue_description}",
        labels=["user-report", "bug"]
    )
    
    return f"Created issue #{result['number']} to track this"
```

### Pattern 2: Automated Code Review and PR Creation

Have agents review code and automatically create PRs for improvements:

```python
async def automated_code_review_workflow(agent):
    # 1. Review issues
    issues = await agent.use_tool(
        "github_operations",
        method="review_issues"
    )
    
    # 2. For each bug, create a fix
    for issue in issues:
        if 'bug' in issue['labels']:
            # Create branch
            await agent.use_tool(
                "git_workflow",
                method="branch_create",
                branch_name=f"fix-issue-{issue['number']}"
            )
            
            # Use code execution to create fix
            await agent.use_tool(
                "code_execution_tool",
                language="python",
                code=f"# Fix for issue {issue['number']}\n# ..."
            )
            
            # Commit and push
            await agent.use_tool(
                "git_workflow",
                method="commit",
                message=f"Fix issue #{issue['number']}",
                add_all=True
            )
            
            await agent.use_tool(
                "git_workflow",
                method="push",
                set_upstream=True
            )
            
            # Create PR
            await agent.use_tool(
                "github_operations",
                method="create_pr",
                title=f"Fix: {issue['title']}",
                body=f"Fixes #{issue['number']}",
                head=f"fix-issue-{issue['number']}",
                base="main"
            )
```

### Pattern 3: Multi-Agent Code Improvement Pipeline

Use specialized agents for different tasks:

```python
async def multi_agent_improvement_pipeline(agent):
    # 1. Researcher agent finds issues
    research_result = await agent.use_tool(
        "multi_agent_delegation",
        task_description="Review all open GitHub issues and prioritize bugs",
        agent_profiles="researcher",
        coordination_strategy="sequential"
    )
    
    # 2. Developer agent creates fixes
    dev_result = await agent.use_tool(
        "multi_agent_delegation",
        task_description="Fix the top 3 priority bugs and create PRs",
        agent_profiles="developer",
        coordination_strategy="parallel"
    )
    
    # 3. Analyst agent reviews PRs
    review_result = await agent.use_tool(
        "multi_agent_delegation",
        task_description="Review created PRs and add comments",
        agent_profiles="analyst",
        coordination_strategy="sequential"
    )
```

### Pattern 4: Automated Project Board Management

Keep project boards updated automatically:

```python
async def update_project_boards(agent, issue_number, status):
    """Update issue status on project board"""
    
    # Update issue labels
    await agent.use_tool(
        "github_operations",
        method="update_issue",
        issue_number=issue_number,
        labels=[status, "tracked"]
    )
    
    # Add comment about status change
    await agent.use_tool(
        "github_operations",
        method="add_comment",
        issue_number=issue_number,
        comment=f"Status updated to: {status}"
    )
```

### Pattern 5: Scheduled Issue Triage

Run automated issue triage on a schedule:

```python
async def scheduled_triage(agent):
    """Run daily to triage new issues"""
    
    # Get all open, unlabeled issues
    issues = await agent.use_tool(
        "github_operations",
        method="list_issues",
        state="open",
        limit=50
    )
    
    for issue in issues:
        # Analyze issue content
        analysis = await agent.analyze_text(issue['body'])
        
        # Auto-label based on content
        labels = []
        if 'error' in issue['body'].lower():
            labels.append('bug')
        if 'feature' in issue['title'].lower():
            labels.append('enhancement')
        if 'documentation' in issue['body'].lower():
            labels.append('documentation')
        
        if labels:
            await agent.use_tool(
                "github_operations",
                method="update_issue",
                issue_number=issue['number'],
                labels=labels
            )
```

## GitHub Actions Integration

The GitHub Actions workflows in `.github/workflows/` automatically:

1. **Auto-label issues and PRs** based on content
2. **Link PRs to issues** using "Fixes #123" syntax
3. **Close issues automatically** when linked PRs are merged
4. **Add items to project boards** when issues are opened
5. **Run weekly codebase reviews** and create tracking issues

These workflows work alongside the Python tools to provide complete automation.

## Advanced Workflows

### Workflow 1: Automated Dependency Updates

```python
async def check_and_update_dependencies(agent):
    # Check for outdated dependencies
    outdated = await agent.use_tool(
        "code_execution_tool",
        language="bash",
        code="pip list --outdated"
    )
    
    if outdated:
        # Create issue
        issue = await agent.use_tool(
            "github_operations",
            method="create_issue",
            title="Update outdated dependencies",
            body=f"The following dependencies need updating:\n\n```\n{outdated}\n```",
            labels=["dependencies", "maintenance"]
        )
        
        # Create PR with updates
        # ... update requirements.txt ...
        
        pr = await agent.use_tool(
            "github_operations",
            method="create_pr",
            title="chore: Update dependencies",
            body=f"Fixes #{issue['number']}",
            head="update-deps",
            base="main"
        )
```

### Workflow 2: Documentation Sync

```python
async def sync_documentation(agent):
    """Ensure documentation is up to date with code"""
    
    # Check for undocumented functions
    undocumented = await agent.use_tool(
        "code_execution_tool",
        language="python",
        code="""
# Script to find undocumented functions
import ast
import os

# Parse Python files and find undocumented functions
# ...
"""
    )
    
    if undocumented:
        # Create issue
        await agent.use_tool(
            "github_operations",
            method="create_issue",
            title="Add documentation for undocumented functions",
            body=f"Found undocumented functions:\n{undocumented}",
            labels=["documentation", "good-first-issue"]
        )
```

### Workflow 3: Security Audit

```python
async def security_audit(agent):
    """Check for security issues and create reports"""
    
    # Run security checks
    security_results = await agent.use_tool(
        "code_execution_tool",
        language="bash",
        code="safety check -r requirements.txt"
    )
    
    if "vulnerabilities" in security_results.lower():
        # Create high-priority issue
        issue = await agent.use_tool(
            "github_operations",
            method="create_issue",
            title="🔒 Security: Vulnerabilities found in dependencies",
            body=f"Security scan results:\n\n```\n{security_results}\n```",
            labels=["security", "high-priority", "bug"]
        )
        
        # Notify team
        await agent.use_tool(
            "notify_user",
            message=f"Security issue created: #{issue['number']}"
        )
```

## Best Practices

### 1. Error Handling

Always wrap GitHub operations in try-catch blocks:

```python
try:
    result = await agent.use_tool("github_operations", ...)
    if not result:
        # Handle failure
        await agent.log_error("GitHub operation failed")
except Exception as e:
    await agent.handle_error(e)
```

### 2. Rate Limiting

Be mindful of GitHub API rate limits:

```python
# Add delays between bulk operations
import asyncio

for issue in issues:
    await process_issue(issue)
    await asyncio.sleep(1)  # Rate limiting
```

### 3. Authentication

Never hardcode tokens:

```python
# ❌ Bad
token = "ghp_hardcoded_token"

# ✅ Good
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("GITHUB_TOKEN not set")
```

### 4. Testing

Test GitHub operations in a test repository first:

```bash
export GITHUB_REPOSITORY=your-username/test-repo
python examples/github_issue_workflow.py --example create
```

### 5. Logging

Log all GitHub operations for audit trails:

```python
result = await agent.use_tool("github_operations", ...)
agent.context.log.log(
    type="info",
    heading="GitHub Operation",
    content=f"Created issue #{result['number']}"
)
```

## Troubleshooting

### Issue: "No module named 'github'"

**Solution**: Install PyGithub:
```bash
pip install PyGithub
```

### Issue: "Authentication failed"

**Solutions**:
1. Check token is valid: Visit github.com/settings/tokens
2. Verify token permissions include `repo` scope
3. Ensure token hasn't expired

### Issue: "Rate limit exceeded"

**Solutions**:
1. Add delays between operations
2. Check current rate limit: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`
3. Wait for rate limit to reset (shown in API response)

### Issue: "Repository not found"

**Solutions**:
1. Check `GITHUB_REPOSITORY` format: must be "owner/repo"
2. Verify token has access to the repository
3. Ensure repository name is spelled correctly

## Examples

See the `examples/` directory for complete working examples:

- `examples/github_issue_workflow.py` - Issue management examples
- `examples/github_pr_workflow.py` - Pull request examples
- `examples/README.md` - Detailed usage instructions

## Further Reading

- [GitHub Operations Documentation](./github_operations.md)
- [Agent Zero Multi-Agent System](./multi_agent_memory_system.md)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)

## Support

For help with GitHub integration:
- Check the [troubleshooting guide](./troubleshooting.md)
- Open an issue on GitHub
- Join the Discord community
