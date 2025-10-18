# GitHub Operations Examples

This directory contains example scripts demonstrating how to use the GitHub operations tools in Agent Zero.

## Prerequisites

1. **GitHub Token**: You need a GitHub personal access token with appropriate permissions
2. **Repository Access**: The token must have access to the repository you want to manage

### Setting up Environment Variables

```bash
export GITHUB_TOKEN=your_github_token_here
export GITHUB_REPOSITORY=owner/repo  # e.g., "cbwinslow/agent-zero"
```

## Examples

### 1. GitHub Issue Workflow (`github_issue_workflow.py`)

Demonstrates issue management operations:

#### Create and Manage Issues

```bash
python examples/github_issue_workflow.py --example create
```

This example:
- Creates a new issue with labels and description
- Adds comments to the issue
- Updates issue labels
- Lists all open issues
- Closes the issue (cleanup)

#### Review and Prioritize Issues

```bash
python examples/github_issue_workflow.py --example review
```

This example:
- Fetches all open issues from the repository
- Categorizes them by type (bugs, enhancements, questions)
- Displays a prioritized summary
- Shows high-priority items first

### 2. GitHub Pull Request Workflow (`github_pr_workflow.py`)

Demonstrates PR management operations:

#### Create PR with Issue Linking

```bash
python examples/github_pr_workflow.py --example create
```

This example:
- Creates an issue to fix
- Creates a pull request
- Links the PR to the issue using "Fixes #123" syntax
- Updates PR details
- Lists all open PRs

**Note**: This requires a branch named `example-fix-branch` to exist in the repository.

#### Review Pull Requests

```bash
python examples/github_pr_workflow.py --example review
```

This example:
- Fetches all open pull requests
- Displays PR details including branch information
- Shows creation dates and URLs

#### Automated Merge Workflow

```bash
python examples/github_pr_workflow.py --example merge
```

This example demonstrates the steps for an automated merge workflow:
- Check PR approvals
- Verify CI/CD checks
- Confirm no merge conflicts
- Merge using appropriate method
- Close linked issues

**⚠️ Warning**: This is a demonstration only. Do not use automated merging in production without proper review processes!

## Common Use Cases

### Use Case 1: Automated Issue Triage

Create a script that:
1. Reviews all new issues
2. Automatically labels them based on content
3. Assigns them to appropriate team members
4. Adds them to project boards

### Use Case 2: PR Status Updates

Create a script that:
1. Monitors all open PRs
2. Adds labels based on review status
3. Comments when CI checks fail
4. Notifies relevant parties

### Use Case 3: Codebase Maintenance

Create a script that:
1. Reviews all open bugs
2. Creates fix branches automatically
3. Submits PRs with fixes
4. Links PRs to original issues

## Integration with Agent Zero

These tools can be used within Agent Zero's agent system:

```python
# Example: Use within an agent
result = await agent.use_tool(
    "github_operations",
    method="create_issue",
    title="New feature request",
    body="Description of the feature",
    labels=["enhancement"]
)
```

## Troubleshooting

### "Authentication Error"
- Check that `GITHUB_TOKEN` is set correctly
- Verify the token has not expired
- Ensure the token has the required scopes (`repo`, `workflow`)

### "Repository Not Found"
- Verify `GITHUB_REPOSITORY` is in the correct format: `owner/repo`
- Check that the token has access to the repository
- Ensure the repository exists

### "Permission Denied"
- The token may not have the required permissions
- For private repositories, ensure the token has `repo` scope
- For organization repositories, check organization settings

## Further Reading

- [GitHub Operations Documentation](../docs/github_operations.md)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)

## Contributing

Feel free to add more examples! Please:
1. Follow the existing code style
2. Add clear comments and documentation
3. Include error handling
4. Test your examples before submitting
