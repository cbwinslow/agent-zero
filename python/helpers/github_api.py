"""
GitHub API Helper Module for Agent Zero

This module provides comprehensive GitHub API operations including:
- Repository management (create, read, update, delete)
- Issues and PR management
- GitHub Actions integration
- Commits and content management
- Backup and restore functionality for knowledge base
- Organization and team management
"""

import os
import json
import base64
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from python.helpers.print_style import PrintStyle


class GitHubAPIHelper:
    """
    Helper class for GitHub API operations.
    
    Provides comprehensive GitHub integration including:
    - Repository operations
    - Issues and pull requests
    - Actions and workflows
    - Content management
    - Backup and restore
    """
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.github.com"):
        """
        Initialize the GitHub API helper.
        
        Args:
            token: GitHub personal access token. If not provided, tries to get from env.
            base_url: GitHub API base URL (defaults to public GitHub)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a request to the GitHub API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {"success": True}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"GitHub API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - {error_data.get('message', '')}"
                except:
                    pass
            raise Exception(error_msg)
    
    # ==================== Repository Operations ====================
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        return self._request("GET", f"/repos/{owner}/{repo}")
    
    def list_repos(self, owner: str, repo_type: str = "all") -> List[Dict[str, Any]]:
        """
        List repositories for a user or organization.
        
        Args:
            owner: Username or organization name
            repo_type: Type of repos (all, public, private, forks, sources, member)
        """
        return self._request("GET", f"/users/{owner}/repos", params={"type": repo_type})
    
    def create_repo(self, name: str, description: str = "", private: bool = False, 
                    auto_init: bool = False, org: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether to make the repository private
            auto_init: Initialize with README
            org: Organization name (if creating org repo)
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        
        endpoint = f"/orgs/{org}/repos" if org else "/user/repos"
        return self._request("POST", endpoint, json=data)
    
    def delete_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Delete a repository."""
        return self._request("DELETE", f"/repos/{owner}/{repo}")
    
    # ==================== Content Operations ====================
    
    def get_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Get contents of a file or directory.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to file or directory
            ref: Git reference (branch, tag, commit)
        """
        params = {"ref": ref} if ref else {}
        return self._request("GET", f"/repos/{owner}/{repo}/contents/{path}", params=params)
    
    def create_or_update_file(self, owner: str, repo: str, path: str, content: str,
                              message: str, branch: str = "main", 
                              sha: Optional[str] = None) -> Dict[str, Any]:
        """
        Create or update a file in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content (will be base64 encoded)
            message: Commit message
            branch: Branch name
            sha: File SHA (required for updates)
        """
        content_b64 = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": message,
            "content": content_b64,
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=data)
    
    def delete_file(self, owner: str, repo: str, path: str, message: str,
                   sha: str, branch: str = "main") -> Dict[str, Any]:
        """Delete a file from a repository."""
        data = {
            "message": message,
            "sha": sha,
            "branch": branch
        }
        return self._request("DELETE", f"/repos/{owner}/{repo}/contents/{path}", json=data)
    
    # ==================== Issue Operations ====================
    
    def list_issues(self, owner: str, repo: str, state: str = "open", 
                    labels: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List issues in a repository."""
        params = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)
        return self._request("GET", f"/repos/{owner}/{repo}/issues", params=params)
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get a specific issue."""
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                    labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue."""
        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
        return self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)
    
    def update_issue(self, owner: str, repo: str, issue_number: int,
                    title: Optional[str] = None, body: Optional[str] = None,
                    state: Optional[str] = None) -> Dict[str, Any]:
        """Update an issue."""
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        return self._request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=data)
    
    # ==================== Pull Request Operations ====================
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """List pull requests in a repository."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls", params={"state": state})
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get a specific pull request."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    
    def create_pull_request(self, owner: str, repo: str, title: str, head: str,
                           base: str, body: str = "") -> Dict[str, Any]:
        """Create a new pull request."""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", json=data)
    
    # ==================== Actions/Workflows ====================
    
    def list_workflows(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List workflows in a repository."""
        result = self._request("GET", f"/repos/{owner}/{repo}/actions/workflows")
        return result.get("workflows", [])
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: Union[int, str],
                        ref: str = "main", inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger a workflow dispatch event."""
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        return self._request("POST", f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches", 
                           json=data)
    
    def list_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[Union[int, str]] = None,
                          status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflow runs."""
        params = {}
        if workflow_id:
            endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            endpoint = f"/repos/{owner}/{repo}/actions/runs"
        
        if status:
            params["status"] = status
            
        result = self._request("GET", endpoint, params=params)
        return result.get("workflow_runs", [])
    
    # ==================== Backup Operations ====================
    
    def backup_knowledge_base(self, owner: str, repo: str, knowledge_dir: str, 
                             branch: str = "main") -> Dict[str, Any]:
        """
        Backup knowledge base directory to GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            knowledge_dir: Local knowledge base directory path
            branch: Target branch
            
        Returns:
            Dictionary with backup results
        """
        import os
        from pathlib import Path
        
        results = {
            "success": True,
            "files_backed_up": [],
            "errors": []
        }
        
        knowledge_path = Path(knowledge_dir)
        if not knowledge_path.exists():
            return {"success": False, "error": f"Knowledge directory not found: {knowledge_dir}"}
        
        # Walk through knowledge directory
        for file_path in knowledge_path.rglob("*"):
            if file_path.is_file():
                try:
                    # Get relative path for GitHub
                    rel_path = file_path.relative_to(knowledge_path)
                    github_path = f"knowledge/{rel_path}"
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Try to get existing file SHA for update
                    sha = None
                    try:
                        existing = self.get_content(owner, repo, github_path, ref=branch)
                        sha = existing.get("sha")
                    except:
                        pass  # File doesn't exist, will create new
                    
                    # Upload file
                    message = f"Backup: {github_path} - {datetime.now().isoformat()}"
                    self.create_or_update_file(owner, repo, github_path, content, message, branch, sha)
                    
                    results["files_backed_up"].append(str(rel_path))
                    
                except Exception as e:
                    results["errors"].append({
                        "file": str(rel_path),
                        "error": str(e)
                    })
        
        if results["errors"]:
            results["success"] = False
        
        return results
    
    def backup_memory(self, owner: str, repo: str, memory_dir: str,
                     branch: str = "main") -> Dict[str, Any]:
        """Backup memory directory to GitHub."""
        # Similar to backup_knowledge_base but for memory directory
        return self.backup_knowledge_base(owner, repo, memory_dir, branch)
    
    def restore_knowledge_base(self, owner: str, repo: str, knowledge_dir: str,
                              branch: str = "main") -> Dict[str, Any]:
        """
        Restore knowledge base from GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            knowledge_dir: Local knowledge base directory path
            branch: Source branch
            
        Returns:
            Dictionary with restore results
        """
        import os
        from pathlib import Path
        
        results = {
            "success": True,
            "files_restored": [],
            "errors": []
        }
        
        knowledge_path = Path(knowledge_dir)
        knowledge_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get knowledge directory contents from GitHub
            contents = self.get_content(owner, repo, "knowledge", ref=branch)
            
            # If it's a single file, wrap it in a list
            if isinstance(contents, dict):
                contents = [contents]
            
            # Process each file
            for item in contents:
                if item["type"] == "file":
                    try:
                        # Get file content
                        file_data = self.get_content(owner, repo, item["path"], ref=branch)
                        content = base64.b64decode(file_data["content"]).decode('utf-8')
                        
                        # Create local file
                        local_path = knowledge_path / item["path"].replace("knowledge/", "")
                        local_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        results["files_restored"].append(item["path"])
                        
                    except Exception as e:
                        results["errors"].append({
                            "file": item["path"],
                            "error": str(e)
                        })
                
                elif item["type"] == "dir":
                    # Recursively process subdirectories
                    # This is a simplified version - full implementation would recursively walk
                    pass
                    
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
        
        if results["errors"]:
            results["success"] = False
        
        return results
    
    # ==================== Search Operations ====================
    
    def search_code(self, query: str, owner: Optional[str] = None, 
                   repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for code across GitHub.
        
        Args:
            query: Search query
            owner: Optional owner filter
            repo: Optional repo filter
        """
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        result = self._request("GET", "/search/code", params={"q": search_query})
        return result.get("items", [])
    
    def search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """Search for repositories."""
        result = self._request("GET", "/search/repositories", params={"q": query})
        return result.get("items", [])
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search for users."""
        result = self._request("GET", "/search/users", params={"q": query})
        return result.get("items", [])
    
    # ==================== User Operations ====================
    
    def get_user(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user information. If no username, gets authenticated user."""
        endpoint = f"/users/{username}" if username else "/user"
        return self._request("GET", endpoint)
    
    def get_authenticated_user(self) -> Dict[str, Any]:
        """Get the authenticated user's information."""
        return self._request("GET", "/user")
    
    # ==================== Gist Operations ====================
    
    def create_gist(self, files: Dict[str, str], description: str = "",
                   public: bool = False) -> Dict[str, Any]:
        """
        Create a gist.
        
        Args:
            files: Dictionary of filename -> content
            description: Gist description
            public: Whether gist is public
        """
        data = {
            "description": description,
            "public": public,
            "files": {name: {"content": content} for name, content in files.items()}
        }
        return self._request("POST", "/gists", json=data)
    
    def list_gists(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """List gists for a user or authenticated user."""
        endpoint = f"/users/{username}/gists" if username else "/gists"
        return self._request("GET", endpoint)
