"""
Authentication module for Agent Zero
"""

from .user_manager import (
    User,
    UserRole,
    UserManager,
    get_user_manager,
    hash_password,
    generate_session_token
)

from .session_manager import (
    UserSession,
    UserSessionManager,
    get_session_manager
)

__all__ = [
    'User',
    'UserRole', 
    'UserManager',
    'get_user_manager',
    'hash_password',
    'generate_session_token',
    'UserSession',
    'UserSessionManager',
    'get_session_manager'
]
