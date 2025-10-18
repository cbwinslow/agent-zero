"""
Git Helper Module for Agent Zero

This module provides comprehensive Git operations including:
- Repository information and status
- Branch management
- Commit operations
- Remote operations (GitHub and GitLab)
- Diff and change tracking
- Conflict resolution support
"""

from git import Repo, GitCommandError, InvalidGitRepositoryError
from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple, Any
from python.helpers import files
from python.helpers.print_style import PrintStyle


class GitHelper:
    """
    Helper class for Git operations.
    
    Provides methods for:
    - Repository initialization and validation
    - Branch operations (create, checkout, delete, list)
    - Commit operations (create, amend, revert)
    - Remote operations (fetch, pull, push)
    - Status and diff operations
    - Conflict detection and resolution support
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize the Git helper.
        
        Args:
            repo_path: Path to the Git repository. Defaults to the base directory.
        """
        self.repo_path = repo_path or files.get_base_dir()
        self.repo: Optional[Repo] = None
        self._init_repo()
    
    def _init_repo(self):
        """Initialize the Git repository object"""
        try:
            self.repo = Repo(self.repo_path)
            if self.repo.bare:
                raise ValueError(f"Repository at {self.repo_path} is bare and cannot be used.")
        except InvalidGitRepositoryError:
            self.repo = None
    
    def is_valid_repo(self) -> bool:
        """Check if the current path is a valid Git repository"""
        return self.repo is not None
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive repository information.
        
        Returns:
            Dictionary containing repository information including:
            - branch: Current branch name
            - commit_hash: Current commit hash
            - commit_time: Current commit timestamp
            - tag: Latest tag description
            - short_tag: Shortened tag name
            - version: Version string
            - is_dirty: Whether there are uncommitted changes
            - untracked_files: List of untracked files
            - remotes: List of configured remotes
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        # Get the current branch name
        try:
            branch = self.repo.active_branch.name if not self.repo.head.is_detached else "detached HEAD"
        except:
            branch = ""

        # Get the latest commit hash
        commit_hash = self.repo.head.commit.hexsha if self.repo.head.is_valid() else ""

        # Get the commit date (ISO 8601 format)
        if self.repo.head.is_valid():
            commit_time = datetime.fromtimestamp(self.repo.head.commit.committed_date).strftime('%y-%m-%d %H:%M')
        else:
            commit_time = ""

        # Get the latest tag description (if available)
        short_tag = ""
        tag = ""
        try:
            tag = self.repo.git.describe(tags=True)
            tag_split = tag.split('-')
            if len(tag_split) >= 3:
                short_tag = "-".join(tag_split[:-1])
            else:
                short_tag = tag
        except:
            pass

        version = (branch[0].upper() if branch else "") + " " + (short_tag or commit_hash[:7])
        
        # Check for uncommitted changes
        is_dirty = self.repo.is_dirty()
        
        # Get untracked files
        untracked_files = self.repo.untracked_files
        
        # Get remotes
        remotes = [remote.name for remote in self.repo.remotes]

        # Create the dictionary with collected information
        git_info = {
            "branch": branch,
            "commit_hash": commit_hash,
            "commit_time": commit_time,
            "tag": tag,
            "short_tag": short_tag,
            "version": version,
            "is_dirty": is_dirty,
            "untracked_files": untracked_files,
            "remotes": remotes,
            "repo_path": self.repo_path,
        }

        return git_info
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed repository status.
        
        Returns:
            Dictionary containing:
            - modified: List of modified files
            - staged: List of staged files
            - untracked: List of untracked files
            - deleted: List of deleted files
            - renamed: List of renamed files
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        # Get changed files
        changed_files = [item.a_path for item in self.repo.index.diff(None)]
        
        # Get staged files
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        
        # Get untracked files
        untracked_files = self.repo.untracked_files
        
        # Get deleted files
        deleted_files = [item.a_path for item in self.repo.index.diff(None) if item.deleted_file]
        
        # Get renamed files
        renamed_files = [(item.a_path, item.b_path) for item in self.repo.index.diff("HEAD") if item.renamed_file]
        
        return {
            "modified": changed_files,
            "staged": staged_files,
            "untracked": untracked_files,
            "deleted": deleted_files,
            "renamed": renamed_files,
        }
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the branch to create
            checkout: Whether to checkout the new branch immediately
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return True
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to create branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            self.repo.git.checkout(branch_name)
            return True
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to checkout branch: {e}")
            return False
    
    def list_branches(self, remote: bool = False) -> List[str]:
        """
        List all branches.
        
        Args:
            remote: Whether to list remote branches
            
        Returns:
            List of branch names
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        if remote:
            return [ref.name for ref in self.repo.remote().refs]
        else:
            return [head.name for head in self.repo.heads]
    
    def commit(self, message: str, add_all: bool = False) -> Optional[str]:
        """
        Create a commit.
        
        Args:
            message: Commit message
            add_all: Whether to add all changes before committing
            
        Returns:
            Commit hash if successful, None otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            if add_all:
                self.repo.git.add(A=True)
            
            commit = self.repo.index.commit(message)
            return commit.hexsha
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to commit: {e}")
            return None
    
    def push(self, remote: str = "origin", branch: Optional[str] = None, set_upstream: bool = False) -> bool:
        """
        Push commits to remote.
        
        Args:
            remote: Remote name (default: "origin")
            branch: Branch name (default: current branch)
            set_upstream: Whether to set upstream tracking
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            if branch is None:
                branch = self.repo.active_branch.name
            
            if set_upstream:
                self.repo.git.push("--set-upstream", remote, branch)
            else:
                self.repo.git.push(remote, branch)
            return True
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to push: {e}")
            return False
    
    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """
        Pull changes from remote.
        
        Args:
            remote: Remote name (default: "origin")
            branch: Branch name (default: current branch)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            if branch is None:
                branch = self.repo.active_branch.name
            
            self.repo.git.pull(remote, branch)
            return True
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to pull: {e}")
            return False
    
    def get_diff(self, staged: bool = False, file_path: Optional[str] = None) -> str:
        """
        Get diff of changes.
        
        Args:
            staged: Whether to get diff of staged changes
            file_path: Optional specific file to get diff for
            
        Returns:
            Diff string
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            if staged:
                if file_path:
                    return self.repo.git.diff("--staged", file_path)
                return self.repo.git.diff("--staged")
            else:
                if file_path:
                    return self.repo.git.diff(file_path)
                return self.repo.git.diff()
        except GitCommandError as e:
            PrintStyle(font_color="red", padding=True).print(f"Failed to get diff: {e}")
            return ""
    
    def has_conflicts(self) -> bool:
        """
        Check if there are merge conflicts.
        
        Returns:
            True if there are conflicts, False otherwise
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            # Check for unmerged paths
            unmerged = self.repo.git.diff("--name-only", "--diff-filter=U")
            return len(unmerged.strip()) > 0
        except GitCommandError:
            return False
    
    def get_conflict_files(self) -> List[str]:
        """
        Get list of files with merge conflicts.
        
        Returns:
            List of file paths with conflicts
        """
        if not self.is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        try:
            unmerged = self.repo.git.diff("--name-only", "--diff-filter=U")
            return unmerged.strip().split("\n") if unmerged.strip() else []
        except GitCommandError:
            return []


# Backwards compatible function
def get_git_info():
    """
    Get Git repository information (backwards compatible).
    
    Returns:
        Dictionary containing repository information
    """
    helper = GitHelper()
    return helper.get_info()