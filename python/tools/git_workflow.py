"""
Git Workflow Tool

This tool provides comprehensive Git operations for the agent including:
- Repository status and information
- Branch management (create, checkout, list, delete)
- Commit operations
- Push/pull operations
- Diff viewing
- Conflict detection and resolution support
"""

from python.helpers.tool import Tool, Response
from python.helpers.git import GitHelper
from python.helpers.print_style import PrintStyle
from typing import Optional


class GitWorkflow(Tool):
    """
    Tool for Git workflow operations.
    
    Supported methods:
    - status: Get repository status
    - info: Get repository information
    - branch_create: Create a new branch
    - branch_checkout: Checkout a branch
    - branch_list: List all branches
    - commit: Create a commit
    - push: Push changes to remote
    - pull: Pull changes from remote
    - diff: View changes
    - conflicts: Check for merge conflicts
    """
    
    async def execute(self, **kwargs):
        """
        Execute the Git workflow tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        # Get method from args
        method = self.args.get("method", "status")
        repo_path = self.args.get("repo_path")
        
        # Initialize Git helper
        try:
            git_helper = GitHelper(repo_path)
            
            if not git_helper.is_valid_repo():
                return Response(
                    message=f"Not a valid Git repository: {git_helper.repo_path}",
                    break_loop=False
                )
        except Exception as e:
            return Response(
                message=f"Failed to initialize Git repository: {e}",
                break_loop=False
            )
        
        # Route to appropriate method
        if method == "status":
            return await self._get_status(git_helper, **kwargs)
        elif method == "info":
            return await self._get_info(git_helper, **kwargs)
        elif method == "branch_create":
            return await self._branch_create(git_helper, **kwargs)
        elif method == "branch_checkout":
            return await self._branch_checkout(git_helper, **kwargs)
        elif method == "branch_list":
            return await self._branch_list(git_helper, **kwargs)
        elif method == "commit":
            return await self._commit(git_helper, **kwargs)
        elif method == "push":
            return await self._push(git_helper, **kwargs)
        elif method == "pull":
            return await self._pull(git_helper, **kwargs)
        elif method == "diff":
            return await self._diff(git_helper, **kwargs)
        elif method == "conflicts":
            return await self._conflicts(git_helper, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: status, info, branch_create, branch_checkout, branch_list, commit, push, pull, diff, conflicts",
                break_loop=False
            )
    
    async def _get_status(self, git_helper: GitHelper, **kwargs):
        """Get repository status"""
        try:
            status = git_helper.get_status()
            
            message = "# Git Repository Status\n\n"
            
            if status['modified']:
                message += "## Modified Files\n"
                for file in status['modified']:
                    message += f"- {file}\n"
                message += "\n"
            
            if status['staged']:
                message += "## Staged Files\n"
                for file in status['staged']:
                    message += f"- {file}\n"
                message += "\n"
            
            if status['untracked']:
                message += "## Untracked Files\n"
                for file in status['untracked']:
                    message += f"- {file}\n"
                message += "\n"
            
            if status['deleted']:
                message += "## Deleted Files\n"
                for file in status['deleted']:
                    message += f"- {file}\n"
                message += "\n"
            
            if status['renamed']:
                message += "## Renamed Files\n"
                for old_path, new_path in status['renamed']:
                    message += f"- {old_path} → {new_path}\n"
                message += "\n"
            
            if not any(status.values()):
                message += "Working tree is clean.\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Git Status",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get status: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_info(self, git_helper: GitHelper, **kwargs):
        """Get repository information"""
        try:
            info = git_helper.get_info()
            
            message = "# Git Repository Information\n\n"
            message += f"**Repository**: {info['repo_path']}\n"
            message += f"**Branch**: {info['branch']}\n"
            message += f"**Commit**: {info['commit_hash'][:12]}\n"
            message += f"**Commit Time**: {info['commit_time']}\n"
            message += f"**Tag**: {info.get('tag', 'N/A')}\n"
            message += f"**Version**: {info['version']}\n"
            message += f"**Has Changes**: {'Yes' if info['is_dirty'] else 'No'}\n"
            
            if info['untracked_files']:
                message += f"\n**Untracked Files**: {len(info['untracked_files'])}\n"
            
            if info['remotes']:
                message += f"\n**Remotes**: {', '.join(info['remotes'])}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Git Info",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get info: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _branch_create(self, git_helper: GitHelper, **kwargs):
        """Create a new branch"""
        branch_name = self.args.get("branch_name")
        checkout = self.args.get("checkout", True)
        
        if not branch_name:
            return Response(
                message="Please specify 'branch_name' to create",
                break_loop=False
            )
        
        try:
            success = git_helper.create_branch(branch_name, checkout=checkout)
            
            if success:
                message = f"Successfully created branch '{branch_name}'"
                if checkout:
                    message += " and checked it out"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Failed to create branch '{branch_name}'"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Branch Create",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to create branch: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _branch_checkout(self, git_helper: GitHelper, **kwargs):
        """Checkout a branch"""
        branch_name = self.args.get("branch_name")
        
        if not branch_name:
            return Response(
                message="Please specify 'branch_name' to checkout",
                break_loop=False
            )
        
        try:
            success = git_helper.checkout_branch(branch_name)
            
            if success:
                message = f"Successfully checked out branch '{branch_name}'"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Failed to checkout branch '{branch_name}'"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Branch Checkout",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to checkout branch: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _branch_list(self, git_helper: GitHelper, **kwargs):
        """List branches"""
        remote = self.args.get("remote", False)
        
        try:
            branches = git_helper.list_branches(remote=remote)
            
            message = f"# {'Remote' if remote else 'Local'} Branches\n\n"
            for branch in branches:
                message += f"- {branch}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Branches",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list branches: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _commit(self, git_helper: GitHelper, **kwargs):
        """Create a commit"""
        message_text = self.args.get("message")
        add_all = self.args.get("add_all", False)
        
        if not message_text:
            return Response(
                message="Please specify 'message' for the commit",
                break_loop=False
            )
        
        try:
            commit_hash = git_helper.commit(message_text, add_all=add_all)
            
            if commit_hash:
                message = f"Successfully created commit: {commit_hash[:12]}\n"
                message += f"Message: {message_text}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = "Failed to create commit"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Commit",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to commit: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _push(self, git_helper: GitHelper, **kwargs):
        """Push changes to remote"""
        remote = self.args.get("remote", "origin")
        branch = self.args.get("branch")
        set_upstream = self.args.get("set_upstream", False)
        
        try:
            success = git_helper.push(remote=remote, branch=branch, set_upstream=set_upstream)
            
            if success:
                message = f"Successfully pushed to {remote}"
                if branch:
                    message += f"/{branch}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Failed to push to {remote}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Push",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to push: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _pull(self, git_helper: GitHelper, **kwargs):
        """Pull changes from remote"""
        remote = self.args.get("remote", "origin")
        branch = self.args.get("branch")
        
        try:
            success = git_helper.pull(remote=remote, branch=branch)
            
            if success:
                message = f"Successfully pulled from {remote}"
                if branch:
                    message += f"/{branch}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Failed to pull from {remote}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Pull",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to pull: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _diff(self, git_helper: GitHelper, **kwargs):
        """View changes"""
        staged = self.args.get("staged", False)
        file_path = self.args.get("file_path")
        
        try:
            diff = git_helper.get_diff(staged=staged, file_path=file_path)
            
            if diff:
                message = f"# {'Staged' if staged else 'Unstaged'} Changes\n\n"
                if file_path:
                    message += f"File: {file_path}\n\n"
                message += f"```diff\n{diff}\n```"
            else:
                message = "No changes to show"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Diff",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get diff: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _conflicts(self, git_helper: GitHelper, **kwargs):
        """Check for merge conflicts"""
        try:
            has_conflicts = git_helper.has_conflicts()
            
            if has_conflicts:
                conflict_files = git_helper.get_conflict_files()
                message = f"# Merge Conflicts Detected\n\n"
                message += f"The following files have conflicts:\n\n"
                for file in conflict_files:
                    message += f"- {file}\n"
                message += f"\nResolve these conflicts before continuing."
            else:
                message = "No merge conflicts detected"
            
            PrintStyle(font_color="cyan" if not has_conflicts else "yellow", padding=True).print(message)
            self.agent.context.log.log(
                type="warning" if has_conflicts else "info",
                heading="Conflicts Check",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to check for conflicts: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
