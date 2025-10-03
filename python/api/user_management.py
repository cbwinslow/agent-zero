"""
User Management API Endpoints
"""

import json
from flask import request, Response, session
from python.helpers.api import ApiHandler
from python.helpers.auth import get_user_manager, UserRole


class UserLogin(ApiHandler):
    """Handle user login"""
    
    async def process(self, input: dict):
        """
        Authenticate a user using provided credentials and, on success, store the user id and role in the session.
        
        Parameters:
            input (dict): Request payload containing "username" and "password".
        
        Returns:
            dict: On success, a payload with "success": True and a "user" object containing "username", "email", "role", and "api_key". On failure, an error response dict produced by self.error (e.g., missing credentials or invalid credentials).
        """
        username = input.get("username")
        password = input.get("password")
        
        if not username or not password:
            return self.error("Username and password are required")
        
        user_manager = get_user_manager()
        user = user_manager.authenticate(username, password)
        
        if not user:
            return self.error("Invalid credentials")
        
        # Set session
        session['user_id'] = user.username
        session['user_role'] = user.role.value
        
        return {
            "success": True,
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "api_key": user.api_key
            }
        }


class UserLogout(ApiHandler):
    """Handle user logout"""
    
    async def process(self, input: dict):
        """
        Clear the current user's session to log out the user.
        
        Returns:
            dict: Result payload with `success` set to `True` and a `message` confirming logout.
        """
        session.clear()
        return {"success": True, "message": "Logged out successfully"}


class UserRegister(ApiHandler):
    """Handle user registration"""
    
    async def process(self, input: dict):
        """
        Create a new user account from the provided credentials.
        
        Parameters:
            input (dict): Expected keys: "username" (str), "email" (str), and "password" (str). All three are required.
        
        Returns:
            dict: On success, a payload with "success": True, "message": success text, and "user" containing "username", "email", and "role". On failure, an error response dictionary describing the problem.
        """
        username = input.get("username")
        email = input.get("email")
        password = input.get("password")
        
        if not all([username, email, password]):
            return self.error("Username, email and password are required")
        
        user_manager = get_user_manager()
        
        try:
            user = user_manager.create_user(username, email, password)
            return {
                "success": True,
                "message": "User created successfully",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value
                }
            }
        except ValueError as e:
            return self.error(str(e))


class UserList(ApiHandler):
    """List all users (admin only)"""
    
    async def process(self, input: dict):
        # Check if user is admin
        """
        Provide a list of all registered users; access is restricted to administrators.
        
        If the requester is not an administrator, the handler returns an unauthorized error with HTTP status 403.
        
        Returns:
            dict: A response object with keys:
                - "success": True
                - "users": A list of user summaries where each summary contains:
                    - "username" (str): The user's username.
                    - "email" (str): The user's email address.
                    - "role" (str): The user's role value.
                    - "active" (bool): Whether the user's account is active.
                    - "created_at" (str|None): ISO 8601 timestamp of user creation, or None if not set.
                    - "last_login" (str|None): ISO 8601 timestamp of last login, or None if not set.
        """
        user_role = session.get('user_role')
        if user_role != UserRole.ADMIN.value:
            return self.error("Unauthorized", status=403)
        
        user_manager = get_user_manager()
        users = user_manager.list_users()
        
        return {
            "success": True,
            "users": [
                {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "active": user.active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
        }


class UserUpdate(ApiHandler):
    """Update user settings"""
    
    async def process(self, input: dict):
        """
        Update a user's allowed fields, enforcing that only the current user or an admin may perform the update.
        
        Parameters:
            input (dict): Input payload containing:
                - username (str): Username of the user to update.
                - email (str, optional): New email address.
                - settings (dict, optional): New settings to apply to the user.
                - max_requests_per_minute (int, optional): New per-minute request limit.
        
        Returns:
            dict: On success, a payload with keys:
                - "success" (bool): True when the update succeeded.
                - "message" (str): Human-readable success message.
                - "user" (dict): Updated user summary containing "username", "email", and "role".
            Otherwise returns an error response via self.error (e.g., unauthorized or user not found).
        """
        username = input.get("username")
        current_user = session.get('user_id')
        user_role = session.get('user_role')
        
        # Users can only update themselves unless they're admin
        if username != current_user and user_role != UserRole.ADMIN.value:
            return self.error("Unauthorized", status=403)
        
        user_manager = get_user_manager()
        
        # Only allow certain fields to be updated
        allowed_fields = ['email', 'settings', 'max_requests_per_minute']
        update_data = {k: v for k, v in input.items() if k in allowed_fields}
        
        user = user_manager.update_user(username, **update_data)
        
        if not user:
            return self.error("User not found")
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        }


class UserDelete(ApiHandler):
    """Delete user (admin only)"""
    
    async def process(self, input: dict):
        """
        Delete a user account identified by `username`. This action requires the requester to have the Admin role and will refuse attempts to delete the built-in "admin" account.
        
        Parameters:
            input (dict): Expected to contain the key `"username"` with the username to delete.
        
        Returns:
            dict: On success, `{"success": True, "message": "User deleted successfully"}`.
            On failure, returns the result of `self.error(...)`:
              - Unauthorized request when the caller is not an admin (`"Unauthorized"`, status 403).
              - Error message `"Cannot delete admin user"` when attempting to delete `"admin"`.
              - Error message `"User not found"` when the specified user does not exist.
        """
        username = input.get("username")
        user_role = session.get('user_role')
        
        if user_role != UserRole.ADMIN.value:
            return self.error("Unauthorized", status=403)
        
        if username == "admin":
            return self.error("Cannot delete admin user")
        
        user_manager = get_user_manager()
        success = user_manager.delete_user(username)
        
        if success:
            return {"success": True, "message": "User deleted successfully"}
        else:
            return self.error("User not found")


class UserChangePassword(ApiHandler):
    """Change user password"""
    
    async def process(self, input: dict):
        """
        Change the current logged-in user's password using the provided old and new passwords.
        
        Parameters:
            input (dict): Expected to contain:
                - "old_password" (str): The user's current password.
                - "new_password" (str): The desired new password.
        
        Returns:
            dict: On success, {'success': True, 'message': 'Password changed successfully'}; otherwise an error payload describing the failure (e.g., missing fields or invalid old password).
        """
        username = session.get('user_id')
        old_password = input.get("old_password")
        new_password = input.get("new_password")
        
        if not all([old_password, new_password]):
            return self.error("Old and new passwords are required")
        
        user_manager = get_user_manager()
        success = user_manager.change_password(username, old_password, new_password)
        
        if success:
            return {"success": True, "message": "Password changed successfully"}
        else:
            return self.error("Invalid old password")


class UserInfo(ApiHandler):
    """Get current user info"""
    
    async def process(self, input: dict):
        """
        Return information about the currently logged-in user.
        
        Returns:
            A dict with "success": True and a "user" payload containing:
                - username: the user's username
                - email: the user's email address
                - role: the user's role value
                - active: whether the user is active
                - api_key: the user's API key
                - memory_subdir: path for the user's memory storage
                - knowledge_subdir: path for the user's knowledge storage
                - max_requests_per_minute: request limit per minute for the user
                - settings: user-specific settings
            If no user is logged in or the user record cannot be found, returns the handler's error response.
        """
        username = session.get('user_id')
        
        if not username:
            return self.error("Not logged in", status=401)
        
        user_manager = get_user_manager()
        user = user_manager.get_user(username)
        
        if not user:
            return self.error("User not found")
        
        return {
            "success": True,
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "active": user.active,
                "api_key": user.api_key,
                "memory_subdir": user.memory_subdir,
                "knowledge_subdir": user.knowledge_subdir,
                "max_requests_per_minute": user.max_requests_per_minute,
                "settings": user.settings
            }
        }
