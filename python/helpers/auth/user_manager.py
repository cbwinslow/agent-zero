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
        """
        Normalize and initialize derived User fields after dataclass creation.
        
        Converts string representations of `role` into a `UserRole`, and ISO-format timestamp strings in `created_at` and `last_login` into `datetime` objects. Ensures `memory_subdir` and `knowledge_subdir` are set to a default value of "user_<username>" when they are empty.
        """
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
        """
        Serialize the User instance to a dictionary suitable for JSON storage.
        
        The returned dictionary has the user's fields as keys. The `role` field is converted to its string value, and `created_at` and `last_login` are formatted as ISO 8601 strings or `None` if not set.
        
        Returns:
            dict: Dictionary representation of the user with `role` as a string and timestamps as ISO 8601 strings or `None`.
        """
        data = asdict(self)
        data['role'] = self.role.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """
        Create a User instance from a dictionary representation.
        
        Parameters:
            data (Dict): Dictionary containing user fields as produced by User.to_dict(); expected keys include 'username', 'email', 'password_hash', 'role' (string or UserRole), 'created_at' and 'last_login' (ISO-formatted datetime strings or datetime objects), and optional keys such as 'api_key', 'settings', resource limits, 'memory_subdir', and 'knowledge_subdir'.
        
        Returns:
            User: A User instance populated from the provided dictionary.
        """
        return User(**data)
    
    def verify_password(self, password: str) -> bool:
        """
        Check whether the provided plaintext password matches the user's stored password hash.
        
        Returns:
            True if the provided password matches the stored password hash, False otherwise.
        """
        return hash_password(password) == self.password_hash
    
    def update_last_login(self):
        """
        Set the user's last login timestamp to the current time.
        
        Updates the user's `last_login` field to the current system datetime.
        """
        self.last_login = datetime.now()
    
    def generate_api_key(self) -> str:
        """
        Generate and assign a new URL-safe API key for this user.
        
        Returns:
            api_key (str): The newly generated API key stored on the user.
        """
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key


class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, users_file: str = "users/users.json"):
        """
        Initialize the UserManager and load users from persistent storage.
        
        Parameters:
            users_file (str): Path to the JSON file used to persist user records; defaults to "users/users.json". The path is resolved to an absolute location, the storage is created if missing, and existing users are loaded into the manager's internal cache.
        """
        self.users_file = files.get_abs_path(users_file)
        self._ensure_users_file()
        self._users: Dict[str, User] = {}
        self._load_users()
    
    def _ensure_users_file(self):
        """
        Ensure the users JSON file and its parent directory exist.
        
        If the directory or file is missing, create them; when creating a new users file, seed it with a default admin user (username "admin", email "admin@agent-zero.local") whose password is the hash of "admin", role is ADMIN, and an API key is generated and stored.
        """
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
        """
        Populate the manager's internal user cache from the configured users file if it exists.
        
        If the users file is present, read its JSON array of user records and replace self._users with a mapping from each username to a corresponding User instance created via User.from_dict.
        """
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
                self._users = {
                    user_data['username']: User.from_dict(user_data)
                    for user_data in users_data
                }
    
    def _save_users(self):
        """
        Persist the current in-memory users to the configured users file.
        
        Serializes all managed User objects to a list of dictionaries and writes that JSON to self.users_file, replacing its contents.
        """
        users_data = [user.to_dict() for user in self._users.values()]
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.USER) -> User:
        """
                   Create a new user account and persist it to the users store.
                   
                   Returns:
                       user (User): The newly created User instance with an assigned API key.
                   
                   Raises:
                       ValueError: If a user with the given username already exists.
                   """
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
        """
        Retrieve a user account by username.
        
        Returns:
            The `User` with the given username, or `None` if no such user exists.
        """
        return self._users.get(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Matches the email exactly.
        
        Returns:
            User if a user with the given email exists, `None` otherwise.
        """
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Retrieve the user associated with an API key.
        
        Returns:
            The User whose `api_key` matches the provided `api_key`, or `None` if no matching user is found.
        """
        for user in self._users.values():
            if user.api_key == api_key:
                return user
        return None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Verify credentials and return the corresponding active user.
        
        If the username and password match an active account, updates the user's last_login timestamp and persists users to storage.
        
        Returns:
            `User` if authentication succeeds and the account is active, `None` otherwise.
        """
        user = self.get_user(username)
        if user and user.active and user.verify_password(password):
            user.update_last_login()
            self._save_users()
            return user
        return None
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """
        Authenticate and return the active user associated with an API key.
        
        @returns User if the API key belongs to an active user, `None` otherwise.
        """
        user = self.get_user_by_api_key(api_key)
        if user and user.active:
            return user
        return None
    
    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """
        Update attributes of an existing user and persist the change.
        
        Only keys that match attributes on the User object are applied; unknown keys are ignored. The updated user list is saved to the backing users file.
        
        Parameters:
            username (str): The username of the user to update.
            **kwargs: Attribute names and values to set on the user.
        
        Returns:
            Optional[User]: The updated User if found, `None` if no user with `username` exists.
        """
        user = self.get_user(username)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._save_users()
        return user
    
    def delete_user(self, username: str) -> bool:
        """
        Remove the user account identified by `username` and persist the change.
        
        Parameters:
            username (str): The username of the account to delete.
        
        Returns:
            bool: `True` if the user existed and was deleted, `False` otherwise.
        """
        if username in self._users:
            del self._users[username]
            self._save_users()
            return True
        return False
    
    def list_users(self) -> List[User]:
        """
        Retrieve all users.
        
        Returns:
            users (List[User]): All User objects currently managed by this UserManager.
        """
        return list(self._users.values())
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password after verifying the current password.
        
        Parameters:
            username (str): Username of the account to update.
            old_password (str): Current password used for verification.
            new_password (str): New password to set for the account.
        
        Returns:
            bool: `True` if the password was successfully changed and persisted, `False` otherwise.
        """
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        self._save_users()
        return True
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """
        Reset a user's password and persist the change.
        
        Parameters:
            username (str): The username of the account whose password will be replaced.
            new_password (str): The new plaintext password to set for the user.
        
        Returns:
            bool: `true` if the user was found and the password was updated and saved, `false` if no such user exists.
        """
        user = self.get_user(username)
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        self._save_users()
        return True


def hash_password(password: str) -> str:
    """
    Produce the SHA-256 hexadecimal digest of a password.
    
    Returns:
        hex_hash (str): Hexadecimal SHA-256 hash of the provided password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)


# Global user manager instance
_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """
    Provide the module-level singleton UserManager instance; created on first access if necessary.
    
    Returns:
        The singleton UserManager instance.
    """
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
