"""
User Management Module for Agent Zero
Provides multi-user support with authentication and authorization
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from python.helpers import files


class UserRole(Enum):
    """User roles for access control"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """User model with authentication and authorization data"""
    username: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    active: bool = True
    api_key: Optional[str] = None
    settings: Dict = field(default_factory=dict)
    
    # User-specific resource limits
    max_requests_per_minute: int = 60
    max_memory_mb: int = 1000
    max_knowledge_items: int = 10000
    
    # User-specific subdirectories
    memory_subdir: str = ""
    knowledge_subdir: str = ""
    
    def __post_init__(self):
        if isinstance(self.role, str):
            self.role = UserRole(self.role)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_login, str):
            self.last_login = datetime.fromisoformat(self.last_login)
        
        # Set user-specific subdirectories if not already set
        if not self.memory_subdir:
            self.memory_subdir = f"user_{self.username}"
        if not self.knowledge_subdir:
            self.knowledge_subdir = f"user_{self.username}"
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for serialization"""
        data = asdict(self)
        data['role'] = self.role.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create user from dictionary"""
        return User(**data)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return hash_password(password) == self.password_hash
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
    
    def generate_api_key(self) -> str:
        """Generate a new API key for this user"""
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key


class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, users_file: str = "users/users.json"):
        self.users_file = files.get_abs_path(users_file)
        self._ensure_users_file()
        self._users: Dict[str, User] = {}
        self._load_users()
    
    def _ensure_users_file(self):
        """Ensure users file and directory exist"""
        users_dir = os.path.dirname(self.users_file)
        if not os.path.exists(users_dir):
            os.makedirs(users_dir, exist_ok=True)
        
        if not os.path.exists(self.users_file):
            # Create default admin user
            default_admin = User(
                username="admin",
                email="admin@agent-zero.local",
                password_hash=hash_password("admin"),
                role=UserRole.ADMIN,
                memory_subdir="admin",
                knowledge_subdir="admin"
            )
            default_admin.api_key = secrets.token_urlsafe(32)
            
            with open(self.users_file, 'w') as f:
                json.dump([default_admin.to_dict()], f, indent=2)
    
    def _load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
                self._users = {
                    user_data['username']: User.from_dict(user_data)
                    for user_data in users_data
                }
    
    def _save_users(self):
        """Save users to file"""
        users_data = [user.to_dict() for user in self._users.values()]
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.USER) -> User:
        """Create a new user"""
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role
        )
        user.generate_api_key()
        
        self._users[username] = user
        self._save_users()
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self._users.get(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key"""
        for user in self._users.values():
            if user.api_key == api_key:
                return user
        return None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user(username)
        if user and user.active and user.verify_password(password):
            user.update_last_login()
            self._save_users()
            return user
        return None
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user with API key"""
        user = self.get_user_by_api_key(api_key)
        if user and user.active:
            return user
        return None
    
    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """Update user attributes"""
        user = self.get_user(username)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._save_users()
        return user
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username in self._users:
            del self._users[username]
            self._save_users()
            return True
        return False
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self._users.values())
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        self._save_users()
        return True
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset user password (admin function)"""
        user = self.get_user(username)
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        self._save_users()
        return True


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)


# Global user manager instance
_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """Get global user manager instance"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
