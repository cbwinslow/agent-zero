# GitHub Operations Documentation

This guide explains how to use Agent Zero's GitHub operations tools to manage issues, pull requests, and project boards automatically.

## Overview

Agent Zero now includes comprehensive GitHub integration capabilities through:

1. **GitHub API Helper** (`python/helpers/github_api.py`) - Low-level GitHub API operations
2. **GitHub Operations Tool** (`python/tools/github_operations.py`) - High-level tool for agents
3. **GitHub Actions Workflows** (`.github/workflows/`) - Automated workflows for CI/CD

## Features

### Issue Management

- **Create Issues**: Automatically create GitHub issues with title, body, labels, and assignees
- **Update Issues**: Modify existing issues (title, body, state, labels, assignees)
- **Close Issues**: Close issues with optional closing comments
- **List Issues**: Query issues by state, labels, or assignee
- **Add Comments**: Post comments on existing issues

### Pull Request Management

- **Create PRs**: Create pull requests with title, body, and draft mode
- **Update PRs**: Modify PR details
- **Link Issues to PRs**: Automatically link related issues using "Fixes #123" syntax
- **Merge PRs**: Merge pull requests with different merge strategies (merge, squash, rebase)
- **List PRs**: Query pull requests by state or base branch

### Project Board Management

- **Add to Projects**: Add issues to GitHub project boards
- **Move Cards**: Update card positions based on issue status
- **Auto-organize**: Automatically organize items based on labels

### Code Review

- **Review Issues**: Get all open issues for review and planning
- **Auto-label**: Automatically apply labels based on issue content
- **Track Progress**: Monitor issue resolution and PR completion

## Setup

### 1. Environment Variables

Set the following environment variables in your `.env` file:

```bash
# GitHub Personal Access Token
GITHUB_TOKEN=ghp_your_token_here

# Repository in format "owner/repo"
GITHUB_REPOSITORY=your-username/your-repo
```

### 2. GitHub Token Permissions

Your GitHub token needs the following permissions:
- `repo` - Full repository access
- `workflow` - Manage GitHub Actions workflows
- `project` - Manage GitHub Projects (if using project boards)

To create a token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select the required scopes
4. Copy the generated token to your `.env` file

### 3. Install Dependencies

The GitHub integration requires PyGithub:

```bash
pip install PyGithub
```

This is already included in `requirements.txt`.

## Usage

### Using the GitHub Operations Tool

The `github_operations` tool provides multiple methods for interacting with GitHub:

#### Create an Issue

```python
result = await agent.use_tool(
    "github_operations",
    method="create_issue",
    title="Add new feature",
    body="Detailed description of the feature",
    labels=["enhancement", "feature"],
    assignees=["username"]
)
```

#### Update an Issue

```python
result = await agent.use_tool(
    "github_operations",
    method="update_issue",
    issue_number=123,
    title="Updated title",
    state="closed",
    labels=["done"]
)
```

#### Close an Issue

```python
result = await agent.use_tool(
    "github_operations",
    method="close_issue",
    issue_number=123,
    comment="Issue resolved in PR #456"
)
```

#### List Issues

```python
result = await agent.use_tool(
    "github_operations",
    method="list_issues",
    state="open",
    labels=["bug"],
    limit=10
)
```

#### Create a Pull Request

```python
result = await agent.use_tool(
    "github_operations",
    method="create_pr",
    title="Fix bug in authentication",
    body="This PR fixes the authentication issue by...\n\nFixes #123",
    head="feature-branch",
    base="main",
    draft=False
)
```

#### Link Issues to PR

```python
result = await agent.use_tool(
    "github_operations",
    method="link_issue_to_pr",
    pr_number=456,
    issue_numbers=[123, 124, 125]
)
```

#### Merge a Pull Request

```python
result = await agent.use_tool(
    "github_operations",
    method="merge_pr",
    pr_number=456,
    commit_message="Merge feature branch",
    merge_method="squash"  # Options: merge, squash, rebase
)
```

#### Add Issue to Project Board

```python
result = await agent.use_tool(
    "github_operations",
    method="add_to_project",
    project_number=1,
    column_name="To Do",
    issue_number=123
)
```

#### Review Open Issues

```python
result = await agent.use_tool(
    "github_operations",
    method="review_issues"
)
```

### Using the GitHub API Helper Directly

You can also use the `GitHubHelper` class directly in Python code:

```python
from python.helpers.github_api import GitHubHelper

# Initialize helper
gh = GitHubHelper(token="your_token", repo_name="owner/repo")

# Create an issue
issue = gh.create_issue(
    title="New issue",
    body="Description",
    labels=["bug"],
    assignees=["username"]
)

# List issues
issues = gh.list_issues(state="open", limit=10)

# Create a pull request
pr = gh.create_pull_request(
    title="New feature",
    body="Description\n\nFixes #123",
    head="feature-branch",
    base="main"
)

# Link issues to PR
gh.link_issue_to_pr(pr_number=456, issue_numbers=[123, 124])
```

## GitHub Actions Workflows

The repository includes several automated GitHub Actions workflows:

### 1. Auto Issue Management (`.github/workflows/auto-issue-management.yml`)

**Triggers**: When issues are opened, edited, closed, or commented on

**Features**:
- Automatically labels issues based on keywords in title/body
- Adds issues to project boards
- Supports `/close` comment command to close issues

### 2. Auto PR Management (`.github/workflows/auto-pr-management.yml`)

**Triggers**: When PRs are opened, edited, synchronized, or closed

**Features**:
- Automatically labels PRs based on title and content
- Links issues mentioned in PR body
- Auto-closes linked issues when PR is merged
- Alerts for large PRs (>20 files or >500 additions)

### 3. Codebase Review (`.github/workflows/codebase-review.yml`)

**Triggers**: 
- Weekly schedule (Mondays at 9 AM UTC)
- Manual workflow dispatch

**Features**:
- Reviews open issues weekly
- Creates tracking issues for reviews
- Checks code quality
- Can be extended to create automatic fix PRs

### 4. Project Board Management (`.github/workflows/project-management.yml`)

**Triggers**: When issues or PRs change state

**Features**:
- Adds new issues to project boards
- Moves cards based on label changes
- Updates project status when issues are closed
- Links PRs to issues and updates their status

## Advanced Usage

### Integrating with Multi-Agent System

Combine GitHub operations with the multi-agent system for complex workflows:

```python
result = await agent.use_tool(
    "multi_agent_delegation",
    task_description="Review all open issues, create fixes, and submit PRs",
    agent_profiles="researcher,developer",
    coordination_strategy="sequential"
)
```

### Automated Issue Resolution Workflow

1. **Review Issues**: Use `review_issues` to get all open issues
2. **Analyze Code**: Use code execution tools to analyze the codebase
3. **Create Fixes**: Make necessary code changes
4. **Create PR**: Use `create_pr` to submit fixes
5. **Link Issues**: Use `link_issue_to_pr` to link the PR to issues
6. **Update Status**: Issues are automatically closed when PR merges

### Example: Complete Workflow

```python
# 1. Get all open bugs
bugs = await agent.use_tool(
    "github_operations",
    method="list_issues",
    state="open",
    labels=["bug"]
)

# 2. For each bug, create a fix
for bug in bugs:
    # Analyze the issue
    issue_details = await agent.use_tool(
        "github_operations",
        method="review_issues"
    )
    
    # Create a branch
    await agent.use_tool(
        "git_workflow",
        method="branch_create",
        branch_name=f"fix-issue-{bug['number']}"
    )
    
    # Make fixes using code execution
    await agent.use_tool(
        "code_execution_tool",
        language="python",
        code="# Fix code here"
    )
    
    # Commit changes
    await agent.use_tool(
        "git_workflow",
        method="commit",
        message=f"Fix issue #{bug['number']}",
        add_all=True
    )
    
    # Push to remote
    await agent.use_tool(
        "git_workflow",
        method="push",
        set_upstream=True
    )
    
    # Create PR
    pr = await agent.use_tool(
        "github_operations",
        method="create_pr",
        title=f"Fix: {bug['title']}",
        body=f"This PR fixes #{bug['number']}\n\nFixes #{bug['number']}",
        head=f"fix-issue-{bug['number']}",
        base="main"
    )
    
    # The workflow will automatically link and close issues when merged
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure `GITHUB_TOKEN` is set correctly
   - Check token permissions include `repo` scope
   - Verify token hasn't expired

2. **Repository Not Found**
   - Verify `GITHUB_REPOSITORY` format is "owner/repo"
   - Check token has access to the repository
   - Ensure repository exists and is accessible

3. **Permission Denied**
   - Token needs appropriate scopes for the operation
   - For Projects V2, additional GraphQL permissions may be needed
   - Check if repository has required features enabled

4. **Rate Limiting**
   - GitHub API has rate limits (5,000 requests/hour for authenticated users)
   - Add delays between operations if hitting limits
   - Use conditional requests when possible

### Testing

Run the test suite to verify your setup:

```bash
python tests/test_github_operations.py
```

For live API testing (requires valid token and repository):

```bash
export GITHUB_TOKEN=your_token
export GITHUB_REPOSITORY=owner/repo
python tests/test_github_operations.py
```

## Best Practices

1. **Use Descriptive Titles**: Make issue and PR titles clear and actionable
2. **Link Related Items**: Always link PRs to issues using "Fixes #123" syntax
3. **Add Labels**: Use labels consistently for organization and automation
4. **Review Before Merging**: Don't auto-merge PRs without review
5. **Monitor Actions**: Check GitHub Actions logs for workflow issues
6. **Rate Limit Awareness**: Be mindful of API rate limits when automating
7. **Security**: Never commit tokens to the repository
8. **Atomic Operations**: Keep each issue/PR focused on a single change

## Examples

See the `examples/` directory for complete examples:
- `examples/github_issue_workflow.py` - Complete issue management workflow
- `examples/github_pr_workflow.py` - Pull request creation and management
- `examples/automated_code_review.py` - Automated codebase review

## API Reference

### GitHubHelper Methods

- `create_issue(title, body, labels, assignees, milestone)` - Create new issue
- `update_issue(issue_number, title, body, state, labels, assignees)` - Update issue
- `close_issue(issue_number, comment)` - Close issue with comment
- `add_issue_comment(issue_number, comment)` - Add comment to issue
- `list_issues(state, labels, assignee, limit)` - List issues
- `create_pull_request(title, body, head, base, draft)` - Create PR
- `update_pull_request(pr_number, title, body, state)` - Update PR
- `link_issue_to_pr(pr_number, issue_numbers)` - Link issues to PR
- `merge_pull_request(pr_number, commit_message, merge_method)` - Merge PR
- `list_pull_requests(state, base, limit)` - List PRs
- `create_project_card_for_issue(project_number, column_name, issue_number)` - Add to project
- `get_repository_issues_for_review()` - Get all open issues for review

## Support

For issues or questions:
- Create an issue on GitHub
- Check the documentation at [docs/README.md](./README.md)
- Join the Discord community

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Same as Agent Zero main project license.
