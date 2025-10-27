"""
GitHub Integration Tool

This tool provides comprehensive GitHub operations including:
- Repository management
- Issues and PR operations
- Knowledge base backup and restore
- GitHub Actions integration
- Content management
"""

from python.helpers.tool import Tool, Response
from python.helpers.github_api import GitHubAPIHelper
from python.helpers.print_style import PrintStyle
from typing import Optional
import os


class GitHubIntegration(Tool):
    """
    Tool for GitHub API integration and operations.
    
    Supported methods:
    - repo_info: Get repository information
    - list_repos: List repositories for a user/org
    - create_repo: Create a new repository
    - list_issues: List issues in a repository
    - create_issue: Create a new issue
    - get_issue: Get issue details
    - list_prs: List pull requests
    - get_pr: Get pull request details
    - backup_knowledge: Backup knowledge base to GitHub
    - backup_memory: Backup memory to GitHub
    - restore_knowledge: Restore knowledge base from GitHub
    - search_code: Search for code on GitHub
    - list_workflows: List GitHub Actions workflows
    - trigger_workflow: Trigger a workflow
    """
    
    async def execute(self, **kwargs):
        """
        Execute the GitHub integration tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        method = self.args.get("method", "repo_info")
        token = self.args.get("token") or os.getenv("GITHUB_TOKEN")
        
        if not token:
            return Response(
                message="GitHub token not provided. Set GITHUB_TOKEN environment variable or pass 'token' parameter.",
                break_loop=False
            )
        
        # Initialize GitHub API helper
        try:
            github = GitHubAPIHelper(token=token)
        except Exception as e:
            return Response(
                message=f"Failed to initialize GitHub API: {e}",
                break_loop=False
            )
        
        # Route to appropriate method
        if method == "repo_info":
            return await self._repo_info(github, **kwargs)
        elif method == "list_repos":
            return await self._list_repos(github, **kwargs)
        elif method == "create_repo":
            return await self._create_repo(github, **kwargs)
        elif method == "list_issues":
            return await self._list_issues(github, **kwargs)
        elif method == "create_issue":
            return await self._create_issue(github, **kwargs)
        elif method == "get_issue":
            return await self._get_issue(github, **kwargs)
        elif method == "list_prs":
            return await self._list_prs(github, **kwargs)
        elif method == "get_pr":
            return await self._get_pr(github, **kwargs)
        elif method == "backup_knowledge":
            return await self._backup_knowledge(github, **kwargs)
        elif method == "backup_memory":
            return await self._backup_memory(github, **kwargs)
        elif method == "restore_knowledge":
            return await self._restore_knowledge(github, **kwargs)
        elif method == "search_code":
            return await self._search_code(github, **kwargs)
        elif method == "list_workflows":
            return await self._list_workflows(github, **kwargs)
        elif method == "trigger_workflow":
            return await self._trigger_workflow(github, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: repo_info, list_repos, create_repo, list_issues, create_issue, get_issue, list_prs, get_pr, backup_knowledge, backup_memory, restore_knowledge, search_code, list_workflows, trigger_workflow",
                break_loop=False
            )
    
    async def _repo_info(self, github: GitHubAPIHelper, **kwargs):
        """Get repository information"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            info = github.get_repo(owner, repo)
            
            message = f"# Repository: {info['full_name']}\n\n"
            message += f"**Description**: {info.get('description', 'N/A')}\n"
            message += f"**Stars**: {info['stargazers_count']} ⭐\n"
            message += f"**Forks**: {info['forks_count']} 🍴\n"
            message += f"**Open Issues**: {info['open_issues_count']} 📋\n"
            message += f"**Language**: {info.get('language', 'N/A')}\n"
            message += f"**Private**: {'Yes' if info['private'] else 'No'}\n"
            message += f"**Created**: {info['created_at']}\n"
            message += f"**Updated**: {info['updated_at']}\n"
            message += f"**URL**: {info['html_url']}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Repository Info",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get repository info: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_repos(self, github: GitHubAPIHelper, **kwargs):
        """List repositories"""
        owner = self.args.get("owner")
        repo_type = self.args.get("type", "all")
        
        if not owner:
            return Response(
                message="Please specify 'owner' parameter",
                break_loop=False
            )
        
        try:
            repos = github.list_repos(owner, repo_type)
            
            message = f"# Repositories for {owner}\n\n"
            for repo in repos[:20]:  # Limit to 20
                message += f"- **{repo['name']}** - {repo.get('description', 'No description')}\n"
                message += f"  ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']}\n"
            
            if len(repos) > 20:
                message += f"\n... and {len(repos) - 20} more repositories\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Repositories",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list repositories: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _create_repo(self, github: GitHubAPIHelper, **kwargs):
        """Create a new repository"""
        name = self.args.get("name")
        description = self.args.get("description", "")
        private = self.args.get("private", False)
        org = self.args.get("org")
        
        if not name:
            return Response(
                message="Please specify 'name' parameter",
                break_loop=False
            )
        
        try:
            repo = github.create_repo(name, description, private, auto_init=True, org=org)
            
            message = f"✅ Successfully created repository: {repo['full_name']}\n"
            message += f"URL: {repo['html_url']}\n"
            
            PrintStyle(font_color="green", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Repository Created",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to create repository: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_issues(self, github: GitHubAPIHelper, **kwargs):
        """List issues in a repository"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        state = self.args.get("state", "open")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            issues = github.list_issues(owner, repo, state)
            
            message = f"# Issues in {owner}/{repo} ({state})\n\n"
            for issue in issues[:15]:  # Limit to 15
                message += f"- **#{issue['number']}**: {issue['title']}\n"
                message += f"  State: {issue['state']} | Comments: {issue['comments']}\n"
            
            if len(issues) > 15:
                message += f"\n... and {len(issues) - 15} more issues\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Issues",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list issues: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _create_issue(self, github: GitHubAPIHelper, **kwargs):
        """Create a new issue"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        title = self.args.get("title")
        body = self.args.get("body", "")
        
        if not owner or not repo or not title:
            return Response(
                message="Please specify 'owner', 'repo', and 'title' parameters",
                break_loop=False
            )
        
        try:
            issue = github.create_issue(owner, repo, title, body)
            
            message = f"✅ Created issue #{issue['number']}: {issue['title']}\n"
            message += f"URL: {issue['html_url']}\n"
            
            PrintStyle(font_color="green", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Issue Created",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to create issue: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_issue(self, github: GitHubAPIHelper, **kwargs):
        """Get issue details"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        issue_number = self.args.get("issue_number")
        
        if not owner or not repo or not issue_number:
            return Response(
                message="Please specify 'owner', 'repo', and 'issue_number' parameters",
                break_loop=False
            )
        
        try:
            issue = github.get_issue(owner, repo, int(issue_number))
            
            message = f"# Issue #{issue['number']}: {issue['title']}\n\n"
            message += f"**State**: {issue['state']}\n"
            message += f"**Author**: {issue['user']['login']}\n"
            message += f"**Created**: {issue['created_at']}\n"
            message += f"**Comments**: {issue['comments']}\n\n"
            message += f"**Body**:\n{issue['body']}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Issue",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get issue: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_prs(self, github: GitHubAPIHelper, **kwargs):
        """List pull requests"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        state = self.args.get("state", "open")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            prs = github.list_pull_requests(owner, repo, state)
            
            message = f"# Pull Requests in {owner}/{repo} ({state})\n\n"
            for pr in prs[:15]:  # Limit to 15
                message += f"- **#{pr['number']}**: {pr['title']}\n"
                message += f"  {pr['head']['ref']} → {pr['base']['ref']}\n"
            
            if len(prs) > 15:
                message += f"\n... and {len(prs) - 15} more pull requests\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Pull Requests",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list pull requests: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_pr(self, github: GitHubAPIHelper, **kwargs):
        """Get pull request details"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        pr_number = self.args.get("pr_number")
        
        if not owner or not repo or not pr_number:
            return Response(
                message="Please specify 'owner', 'repo', and 'pr_number' parameters",
                break_loop=False
            )
        
        try:
            pr = github.get_pull_request(owner, repo, int(pr_number))
            
            message = f"# PR #{pr['number']}: {pr['title']}\n\n"
            message += f"**State**: {pr['state']}\n"
            message += f"**Author**: {pr['user']['login']}\n"
            message += f"**Branch**: {pr['head']['ref']} → {pr['base']['ref']}\n"
            message += f"**Mergeable**: {pr.get('mergeable', 'Unknown')}\n"
            message += f"**Commits**: {pr['commits']}\n"
            message += f"**Changed Files**: {pr['changed_files']}\n\n"
            message += f"**Body**:\n{pr['body']}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Pull Request",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get pull request: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _backup_knowledge(self, github: GitHubAPIHelper, **kwargs):
        """Backup knowledge base to GitHub"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        knowledge_dir = self.args.get("knowledge_dir", "/a0/knowledge")
        branch = self.args.get("branch", "main")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            result = github.backup_knowledge_base(owner, repo, knowledge_dir, branch)
            
            if result["success"]:
                message = f"✅ Successfully backed up knowledge base to {owner}/{repo}\n"
                message += f"Files backed up: {len(result['files_backed_up'])}\n"
            else:
                message = f"❌ Backup completed with errors:\n"
                message += f"Files backed up: {len(result['files_backed_up'])}\n"
                message += f"Errors: {len(result['errors'])}\n"
                for error in result['errors'][:5]:
                    message += f"- {error['file']}: {error['error']}\n"
            
            PrintStyle(font_color="green" if result["success"] else "yellow", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Knowledge Base Backup",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to backup knowledge base: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _backup_memory(self, github: GitHubAPIHelper, **kwargs):
        """Backup memory to GitHub"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        memory_dir = self.args.get("memory_dir", "/a0/memory")
        branch = self.args.get("branch", "main")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            result = github.backup_memory(owner, repo, memory_dir, branch)
            
            if result["success"]:
                message = f"✅ Successfully backed up memory to {owner}/{repo}\n"
                message += f"Files backed up: {len(result['files_backed_up'])}\n"
            else:
                message = f"❌ Backup completed with errors:\n"
                message += f"Files backed up: {len(result['files_backed_up'])}\n"
                message += f"Errors: {len(result['errors'])}\n"
            
            PrintStyle(font_color="green" if result["success"] else "yellow", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Memory Backup",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to backup memory: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _restore_knowledge(self, github: GitHubAPIHelper, **kwargs):
        """Restore knowledge base from GitHub"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        knowledge_dir = self.args.get("knowledge_dir", "/a0/knowledge")
        branch = self.args.get("branch", "main")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            result = github.restore_knowledge_base(owner, repo, knowledge_dir, branch)
            
            if result["success"]:
                message = f"✅ Successfully restored knowledge base from {owner}/{repo}\n"
                message += f"Files restored: {len(result['files_restored'])}\n"
            else:
                message = f"❌ Restore completed with errors:\n"
                message += f"Files restored: {len(result['files_restored'])}\n"
                if "error" in result:
                    message += f"Error: {result['error']}\n"
            
            PrintStyle(font_color="green" if result["success"] else "yellow", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Knowledge Base Restore",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to restore knowledge base: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _search_code(self, github: GitHubAPIHelper, **kwargs):
        """Search for code on GitHub"""
        query = self.args.get("query")
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        
        if not query:
            return Response(
                message="Please specify 'query' parameter",
                break_loop=False
            )
        
        try:
            results = github.search_code(query, owner, repo)
            
            message = f"# Code Search Results for: {query}\n\n"
            for item in results[:10]:  # Limit to 10
                message += f"- **{item['name']}** in {item['repository']['full_name']}\n"
                message += f"  Path: {item['path']}\n"
            
            if len(results) > 10:
                message += f"\n... and {len(results) - 10} more results\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Code Search",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to search code: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_workflows(self, github: GitHubAPIHelper, **kwargs):
        """List GitHub Actions workflows"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        
        if not owner or not repo:
            return Response(
                message="Please specify 'owner' and 'repo' parameters",
                break_loop=False
            )
        
        try:
            workflows = github.list_workflows(owner, repo)
            
            message = f"# Workflows in {owner}/{repo}\n\n"
            for workflow in workflows:
                message += f"- **{workflow['name']}** (ID: {workflow['id']})\n"
                message += f"  State: {workflow['state']} | Path: {workflow['path']}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub Workflows",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list workflows: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _trigger_workflow(self, github: GitHubAPIHelper, **kwargs):
        """Trigger a GitHub Actions workflow"""
        owner = self.args.get("owner")
        repo = self.args.get("repo")
        workflow_id = self.args.get("workflow_id")
        ref = self.args.get("ref", "main")
        
        if not owner or not repo or not workflow_id:
            return Response(
                message="Please specify 'owner', 'repo', and 'workflow_id' parameters",
                break_loop=False
            )
        
        try:
            github.trigger_workflow(owner, repo, workflow_id, ref)
            
            message = f"✅ Successfully triggered workflow {workflow_id} on {ref}\n"
            
            PrintStyle(font_color="green", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Workflow Triggered",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to trigger workflow: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
