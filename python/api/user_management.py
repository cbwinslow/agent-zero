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
        session.clear()
        return {"success": True, "message": "Logged out successfully"}


class UserRegister(ApiHandler):
    """Handle user registration"""
    
    async def process(self, input: dict):
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
