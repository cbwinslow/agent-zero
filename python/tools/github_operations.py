"""
GitHub Operations Tool

This tool provides comprehensive GitHub operations for the agent including:
- Issue management (create, update, close)
- Pull request management (create, update, merge, link to issues)
- Project management (add cards, update status)
- Code review and issue resolution support
"""

from python.helpers.tool import Tool, Response
from python.helpers.github_api import GitHubHelper
from python.helpers.print_style import PrintStyle
from typing import Optional
import json


class GitHubOperations(Tool):
    """
    Tool for GitHub API operations.
    
    Supported methods:
    - create_issue: Create a new issue
    - update_issue: Update an existing issue
    - close_issue: Close an issue
    - list_issues: List repository issues
    - add_comment: Add comment to an issue
    - create_pr: Create a pull request
    - update_pr: Update a pull request
    - link_issue_to_pr: Link issues to a pull request
    - merge_pr: Merge a pull request
    - list_prs: List pull requests
    - add_to_project: Add issue to project board
    - review_issues: Get issues for code review
    """
    
    async def execute(self, **kwargs):
        """
        Execute the GitHub operations tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        # Get method from args
        method = self.args.get("method", "list_issues")
        token = self.args.get("token") or self.agent.context.get("GITHUB_TOKEN")
        repo = self.args.get("repository") or self.agent.context.get("GITHUB_REPOSITORY")
        
        # Initialize GitHub helper
        try:
            gh_helper = GitHubHelper(token=token, repo_name=repo)
            
            if not gh_helper.is_valid_repo():
                return Response(
                    message=f"Failed to access GitHub repository: {repo}. Make sure GITHUB_TOKEN and GITHUB_REPOSITORY are set.",
                    break_loop=False
                )
        except Exception as e:
            return Response(
                message=f"Failed to initialize GitHub API: {e}",
                break_loop=False
            )
        
        # Route to appropriate method
        if method == "create_issue":
            return await self._create_issue(gh_helper, **kwargs)
        elif method == "update_issue":
            return await self._update_issue(gh_helper, **kwargs)
        elif method == "close_issue":
            return await self._close_issue(gh_helper, **kwargs)
        elif method == "list_issues":
            return await self._list_issues(gh_helper, **kwargs)
        elif method == "add_comment":
            return await self._add_comment(gh_helper, **kwargs)
        elif method == "create_pr":
            return await self._create_pr(gh_helper, **kwargs)
        elif method == "update_pr":
            return await self._update_pr(gh_helper, **kwargs)
        elif method == "link_issue_to_pr":
            return await self._link_issue_to_pr(gh_helper, **kwargs)
        elif method == "merge_pr":
            return await self._merge_pr(gh_helper, **kwargs)
        elif method == "list_prs":
            return await self._list_prs(gh_helper, **kwargs)
        elif method == "add_to_project":
            return await self._add_to_project(gh_helper, **kwargs)
        elif method == "review_issues":
            return await self._review_issues(gh_helper, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: create_issue, update_issue, close_issue, list_issues, add_comment, create_pr, update_pr, link_issue_to_pr, merge_pr, list_prs, add_to_project, review_issues",
                break_loop=False
            )
    
    async def _create_issue(self, gh_helper: GitHubHelper, **kwargs):
        """Create a new issue"""
        title = self.args.get("title")
        body = self.args.get("body", "")
        labels = self.args.get("labels", [])
        assignees = self.args.get("assignees", [])
        
        if not title:
            return Response(
                message="Please specify 'title' for the issue",
                break_loop=False
            )
        
        try:
            result = gh_helper.create_issue(
                title=title,
                body=body,
                labels=labels if isinstance(labels, list) else [labels],
                assignees=assignees if isinstance(assignees, list) else [assignees]
            )
            
            if result:
                message = f"✅ Successfully created issue #{result['number']}\n\n"
                message += f"**Title**: {result['title']}\n"
                message += f"**URL**: {result['url']}\n"
                message += f"**State**: {result['state']}\n"
                message += f"**Created**: {result['created_at']}\n"
                
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = "❌ Failed to create issue"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Create Issue",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to create issue: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _update_issue(self, gh_helper: GitHubHelper, **kwargs):
        """Update an existing issue"""
        issue_number = self.args.get("issue_number")
        
        if not issue_number:
            return Response(
                message="Please specify 'issue_number' to update",
                break_loop=False
            )
        
        try:
            result = gh_helper.update_issue(
                issue_number=int(issue_number),
                title=self.args.get("title"),
                body=self.args.get("body"),
                state=self.args.get("state"),
                labels=self.args.get("labels"),
                assignees=self.args.get("assignees")
            )
            
            if result:
                message = f"✅ Successfully updated issue #{result['number']}\n\n"
                message += f"**Title**: {result['title']}\n"
                message += f"**URL**: {result['url']}\n"
                message += f"**State**: {result['state']}\n"
                message += f"**Updated**: {result['updated_at']}\n"
                
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to update issue #{issue_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Update Issue",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to update issue: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _close_issue(self, gh_helper: GitHubHelper, **kwargs):
        """Close an issue"""
        issue_number = self.args.get("issue_number")
        comment = self.args.get("comment")
        
        if not issue_number:
            return Response(
                message="Please specify 'issue_number' to close",
                break_loop=False
            )
        
        try:
            success = gh_helper.close_issue(
                issue_number=int(issue_number),
                comment=comment
            )
            
            if success:
                message = f"✅ Successfully closed issue #{issue_number}"
                if comment:
                    message += f"\nAdded comment: {comment[:100]}..."
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to close issue #{issue_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Close Issue",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to close issue: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_issues(self, gh_helper: GitHubHelper, **kwargs):
        """List repository issues"""
        state = self.args.get("state", "open")
        labels = self.args.get("labels")
        assignee = self.args.get("assignee")
        limit = int(self.args.get("limit", 30))
        
        try:
            issues = gh_helper.list_issues(
                state=state,
                labels=labels if isinstance(labels, list) else ([labels] if labels else None),
                assignee=assignee,
                limit=limit
            )
            
            if issues:
                message = f"# GitHub Issues ({len(issues)} found)\n\n"
                for issue in issues:
                    message += f"## #{issue['number']}: {issue['title']}\n"
                    message += f"- **State**: {issue['state']}\n"
                    message += f"- **Labels**: {', '.join(issue['labels']) if issue['labels'] else 'None'}\n"
                    message += f"- **Assignees**: {', '.join(issue['assignees']) if issue['assignees'] else 'Unassigned'}\n"
                    message += f"- **URL**: {issue['url']}\n"
                    message += f"- **Created**: {issue['created_at']}\n\n"
            else:
                message = f"No {state} issues found"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub: List Issues",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to list issues: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _add_comment(self, gh_helper: GitHubHelper, **kwargs):
        """Add comment to an issue"""
        issue_number = self.args.get("issue_number")
        comment = self.args.get("comment")
        
        if not issue_number or not comment:
            return Response(
                message="Please specify both 'issue_number' and 'comment'",
                break_loop=False
            )
        
        try:
            success = gh_helper.add_issue_comment(
                issue_number=int(issue_number),
                comment=comment
            )
            
            if success:
                message = f"✅ Successfully added comment to issue #{issue_number}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to add comment to issue #{issue_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Add Comment",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to add comment: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _create_pr(self, gh_helper: GitHubHelper, **kwargs):
        """Create a pull request"""
        title = self.args.get("title")
        body = self.args.get("body", "")
        head = self.args.get("head")
        base = self.args.get("base", "main")
        draft = self.args.get("draft", False)
        
        if not title or not head:
            return Response(
                message="Please specify both 'title' and 'head' branch for the pull request",
                break_loop=False
            )
        
        try:
            result = gh_helper.create_pull_request(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
            
            if result:
                message = f"✅ Successfully created pull request #{result['number']}\n\n"
                message += f"**Title**: {result['title']}\n"
                message += f"**URL**: {result['url']}\n"
                message += f"**State**: {result['state']}\n"
                message += f"**Created**: {result['created_at']}\n"
                
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = "❌ Failed to create pull request"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Create PR",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to create pull request: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _update_pr(self, gh_helper: GitHubHelper, **kwargs):
        """Update a pull request"""
        pr_number = self.args.get("pr_number")
        
        if not pr_number:
            return Response(
                message="Please specify 'pr_number' to update",
                break_loop=False
            )
        
        try:
            result = gh_helper.update_pull_request(
                pr_number=int(pr_number),
                title=self.args.get("title"),
                body=self.args.get("body"),
                state=self.args.get("state")
            )
            
            if result:
                message = f"✅ Successfully updated pull request #{result['number']}\n\n"
                message += f"**Title**: {result['title']}\n"
                message += f"**URL**: {result['url']}\n"
                message += f"**State**: {result['state']}\n"
                message += f"**Updated**: {result['updated_at']}\n"
                
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to update pull request #{pr_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Update PR",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to update pull request: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _link_issue_to_pr(self, gh_helper: GitHubHelper, **kwargs):
        """Link issues to a pull request"""
        pr_number = self.args.get("pr_number")
        issue_numbers = self.args.get("issue_numbers", [])
        
        if not pr_number or not issue_numbers:
            return Response(
                message="Please specify both 'pr_number' and 'issue_numbers' (as list)",
                break_loop=False
            )
        
        # Convert to list if single number provided
        if not isinstance(issue_numbers, list):
            issue_numbers = [issue_numbers]
        
        try:
            success = gh_helper.link_issue_to_pr(
                pr_number=int(pr_number),
                issue_numbers=[int(n) for n in issue_numbers]
            )
            
            if success:
                message = f"✅ Successfully linked issues {issue_numbers} to PR #{pr_number}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to link issues to PR #{pr_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Link Issues to PR",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to link issues: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _merge_pr(self, gh_helper: GitHubHelper, **kwargs):
        """Merge a pull request"""
        pr_number = self.args.get("pr_number")
        commit_message = self.args.get("commit_message")
        merge_method = self.args.get("merge_method", "merge")
        
        if not pr_number:
            return Response(
                message="Please specify 'pr_number' to merge",
                break_loop=False
            )
        
        try:
            success = gh_helper.merge_pull_request(
                pr_number=int(pr_number),
                commit_message=commit_message,
                merge_method=merge_method
            )
            
            if success:
                message = f"✅ Successfully merged pull request #{pr_number}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to merge pull request #{pr_number}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Merge PR",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to merge pull request: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _list_prs(self, gh_helper: GitHubHelper, **kwargs):
        """List pull requests"""
        state = self.args.get("state", "open")
        base = self.args.get("base")
        limit = int(self.args.get("limit", 30))
        
        try:
            prs = gh_helper.list_pull_requests(
                state=state,
                base=base,
                limit=limit
            )
            
            if prs:
                message = f"# GitHub Pull Requests ({len(prs)} found)\n\n"
                for pr in prs:
                    message += f"## #{pr['number']}: {pr['title']}\n"
                    message += f"- **State**: {pr['state']}\n"
                    message += f"- **Head**: {pr['head']} → **Base**: {pr['base']}\n"
                    message += f"- **URL**: {pr['url']}\n"
                    message += f"- **Created**: {pr['created_at']}\n\n"
            else:
                message = f"No {state} pull requests found"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub: List PRs",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to list pull requests: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _add_to_project(self, gh_helper: GitHubHelper, **kwargs):
        """Add issue to project board"""
        project_number = self.args.get("project_number")
        column_name = self.args.get("column_name")
        issue_number = self.args.get("issue_number")
        
        if not all([project_number, column_name, issue_number]):
            return Response(
                message="Please specify 'project_number', 'column_name', and 'issue_number'",
                break_loop=False
            )
        
        try:
            success = gh_helper.create_project_card_for_issue(
                project_number=int(project_number),
                column_name=column_name,
                issue_number=int(issue_number)
            )
            
            if success:
                message = f"✅ Successfully added issue #{issue_number} to project #{project_number} in column '{column_name}'"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"❌ Failed to add issue to project"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Add to Project",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to add to project: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _review_issues(self, gh_helper: GitHubHelper, **kwargs):
        """Get all open issues for review"""
        try:
            issues = gh_helper.get_repository_issues_for_review()
            
            if issues:
                message = f"# Open Issues for Review ({len(issues)} found)\n\n"
                for issue in issues:
                    message += f"## #{issue['number']}: {issue['title']}\n"
                    message += f"**Description**: {issue['body'][:200]}{'...' if len(issue['body']) > 200 else ''}\n\n"
                    message += f"- **State**: {issue['state']}\n"
                    message += f"- **Labels**: {', '.join(issue['labels']) if issue['labels'] else 'None'}\n"
                    message += f"- **Assignees**: {', '.join(issue['assignees']) if issue['assignees'] else 'Unassigned'}\n"
                    message += f"- **URL**: {issue['url']}\n"
                    message += f"- **Created**: {issue['created_at']}\n"
                    message += f"- **Updated**: {issue['updated_at']}\n\n"
                    message += "---\n\n"
            else:
                message = "No open issues found for review"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="GitHub: Review Issues",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"❌ Failed to review issues: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
