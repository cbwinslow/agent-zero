"""
GitHub API Helper Module for Agent Zero

This module provides comprehensive GitHub API operations including:
- Issue management (create, update, close, reopen)
- Pull request management (create, update, merge)
- Project management (create items, update status)
- Linking issues to pull requests
- Codebase review and issue resolution
"""

from github import Github, GithubException
from typing import Dict, List, Optional, Any
import os
from python.helpers.print_style import PrintStyle


class GitHubHelper:
    """
    Helper class for GitHub API operations.
    
    Provides methods for:
    - Issue operations (create, update, close, add labels, assign)
    - Pull request operations (create, update, merge, link to issues)
    - Project operations (create items, update status, move cards)
    - Repository operations (list issues, PRs, code review)
    """
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize the GitHub helper.
        
        Args:
            token: GitHub personal access token. Defaults to GITHUB_TOKEN env var.
            repo_name: Repository name in format "owner/repo". Defaults to GITHUB_REPOSITORY env var.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_name = repo_name or os.getenv("GITHUB_REPOSITORY")
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.github = Github(self.token)
        self.repo = None
        
        if self.repo_name:
            self._init_repo()
    
    def _init_repo(self):
        """Initialize the repository object"""
        try:
            self.repo = self.github.get_repo(self.repo_name)
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to access repository {self.repo_name}: {e}")
            self.repo = None
    
    def set_repository(self, repo_name: str):
        """
        Set the repository to work with.
        
        Args:
            repo_name: Repository name in format "owner/repo"
        """
        self.repo_name = repo_name
        self._init_repo()
    
    def is_valid_repo(self) -> bool:
        """Check if the repository is accessible"""
        return self.repo is not None
    
    # Issue Operations
    
    def create_issue(
        self,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new issue in the repository.
        
        Args:
            title: Issue title
            body: Issue description/body
            labels: List of label names to apply
            assignees: List of usernames to assign
            milestone: Milestone number
            
        Returns:
            Dictionary containing issue information or None on failure
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body or "",
                labels=labels or [],
                assignees=assignees or [],
                milestone=self.repo.get_milestone(milestone) if milestone else None
            )
            
            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "created_at": issue.created_at.isoformat()
            }
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to create issue: {e}")
            return None
    
    def update_issue(
        self,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing issue.
        
        Args:
            issue_number: Issue number to update
            title: New title
            body: New body
            state: New state ("open" or "closed")
            labels: New list of labels
            assignees: New list of assignees
            
        Returns:
            Dictionary containing updated issue information or None on failure
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            # Update fields if provided
            if title is not None:
                issue.edit(title=title)
            if body is not None:
                issue.edit(body=body)
            if state is not None:
                issue.edit(state=state)
            if labels is not None:
                issue.set_labels(*labels)
            if assignees is not None:
                issue.edit(assignees=assignees)
            
            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "updated_at": issue.updated_at.isoformat()
            }
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to update issue #{issue_number}: {e}")
            return None
    
    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> bool:
        """
        Close an issue.
        
        Args:
            issue_number: Issue number to close
            comment: Optional comment to add when closing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            if comment:
                issue.create_comment(comment)
            
            issue.edit(state="closed")
            return True
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to close issue #{issue_number}: {e}")
            return False
    
    def add_issue_comment(self, issue_number: int, comment: str) -> bool:
        """
        Add a comment to an issue.
        
        Args:
            issue_number: Issue number
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            return True
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to add comment to issue #{issue_number}: {e}")
            return False
    
    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        List issues in the repository.
        
        Args:
            state: Issue state ("open", "closed", or "all")
            labels: Filter by labels
            assignee: Filter by assignee
            limit: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issues = self.repo.get_issues(
                state=state,
                labels=labels or [],
                assignee=assignee or Github.GithubObject.NotSet
            )
            
            result = []
            for i, issue in enumerate(issues):
                if i >= limit:
                    break
                
                # Skip pull requests (they appear in issues list)
                if issue.pull_request:
                    continue
                
                result.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "url": issue.html_url,
                    "created_at": issue.created_at.isoformat()
                })
            
            return result
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to list issues: {e}")
            return []
    
    # Pull Request Operations
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new pull request.
        
        Args:
            title: PR title
            body: PR description
            head: Branch name containing changes
            base: Base branch to merge into (default: "main")
            draft: Whether to create as draft PR
            
        Returns:
            Dictionary containing PR information or None on failure
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
            
            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
                "created_at": pr.created_at.isoformat()
            }
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to create pull request: {e}")
            return None
    
    def update_pull_request(
        self,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing pull request.
        
        Args:
            pr_number: PR number to update
            title: New title
            body: New body
            state: New state ("open" or "closed")
            
        Returns:
            Dictionary containing updated PR information or None on failure
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            pr = self.repo.get_pull(pr_number)
            
            if title is not None:
                pr.edit(title=title)
            if body is not None:
                pr.edit(body=body)
            if state is not None:
                pr.edit(state=state)
            
            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
                "updated_at": pr.updated_at.isoformat()
            }
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to update pull request #{pr_number}: {e}")
            return None
    
    def link_issue_to_pr(self, pr_number: int, issue_numbers: List[int]) -> bool:
        """
        Link issues to a pull request by adding references in the PR body.
        
        Args:
            pr_number: PR number
            issue_numbers: List of issue numbers to link
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            pr = self.repo.get_pull(pr_number)
            current_body = pr.body or ""
            
            # Add "Fixes #123" references
            issue_refs = "\n\n---\n**Related Issues:**\n"
            for issue_num in issue_numbers:
                issue_refs += f"- Fixes #{issue_num}\n"
            
            # Check if references already exist
            if "Related Issues:" not in current_body:
                new_body = current_body + issue_refs
                pr.edit(body=new_body)
            
            return True
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to link issues to PR #{pr_number}: {e}")
            return False
    
    def merge_pull_request(
        self,
        pr_number: int,
        commit_message: Optional[str] = None,
        merge_method: str = "merge"
    ) -> bool:
        """
        Merge a pull request.
        
        Args:
            pr_number: PR number to merge
            commit_message: Optional commit message
            merge_method: Merge method ("merge", "squash", or "rebase")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            pr = self.repo.get_pull(pr_number)
            pr.merge(
                commit_message=commit_message,
                merge_method=merge_method
            )
            return True
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to merge pull request #{pr_number}: {e}")
            return False
    
    def list_pull_requests(
        self,
        state: str = "open",
        base: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        List pull requests in the repository.
        
        Args:
            state: PR state ("open", "closed", or "all")
            base: Filter by base branch
            limit: Maximum number of PRs to return
            
        Returns:
            List of PR dictionaries
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            prs = self.repo.get_pulls(
                state=state,
                base=base or Github.GithubObject.NotSet
            )
            
            result = []
            for i, pr in enumerate(prs):
                if i >= limit:
                    break
                
                result.append({
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "url": pr.html_url,
                    "created_at": pr.created_at.isoformat()
                })
            
            return result
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to list pull requests: {e}")
            return []
    
    # Project Operations
    
    def get_project(self, project_number: int):
        """
        Get a project by number.
        
        Args:
            project_number: Project number (not ID)
            
        Returns:
            Project object or None
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            # Note: PyGithub doesn't have full support for Projects V2
            # This is a basic implementation for classic projects
            projects = list(self.repo.get_projects())
            for project in projects:
                # Match by position/number (approximation)
                if projects.index(project) + 1 == project_number:
                    return project
            return None
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to get project #{project_number}: {e}")
            return None
    
    def create_project_card_for_issue(
        self,
        project_number: int,
        column_name: str,
        issue_number: int
    ) -> bool:
        """
        Create a project card for an issue.
        
        Args:
            project_number: Project number
            column_name: Column name to add card to
            issue_number: Issue number to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            project = self.get_project(project_number)
            if not project:
                raise ValueError(f"Project #{project_number} not found")
            
            # Find column by name
            columns = list(project.get_columns())
            column = None
            for col in columns:
                if col.name.lower() == column_name.lower():
                    column = col
                    break
            
            if not column:
                raise ValueError(f"Column '{column_name}' not found in project")
            
            # Get issue and create card
            issue = self.repo.get_issue(issue_number)
            column.create_card(content_id=issue.id, content_type="Issue")
            
            return True
        except (GithubException, ValueError) as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to create project card: {e}")
            return False
    
    # Code Review Operations
    
    def get_repository_issues_for_review(self) -> List[Dict[str, Any]]:
        """
        Get all open issues for code review and planning.
        
        Returns:
            List of issue dictionaries with full details
        """
        if not self.is_valid_repo():
            raise ValueError(f"Repository not initialized: {self.repo_name}")
        
        try:
            issues = self.repo.get_issues(state="open")
            
            result = []
            for issue in issues:
                # Skip pull requests
                if issue.pull_request:
                    continue
                
                result.append({
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "url": issue.html_url,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat()
                })
            
            return result
        except GithubException as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to get issues for review: {e}")
            return []
