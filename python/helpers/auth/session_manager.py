"""
User Session Management for Agent Zero
Manages user-specific agent contexts and resources
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import secrets

from agent import AgentConfig, AgentContext, AgentContextType
from python.helpers.auth import get_user_manager, User


class UserSession:
    """Represents a user session with associated agent context"""
    
    def __init__(self, user: User, session_id: str, context: AgentContext):
        self.user = user
        self.session_id = session_id
        self.context = context
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.request_count = 0
        self.request_timestamps = []
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def check_rate_limit(self) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if ts > one_minute_ago
        ]
        
        # Check if under limit
        if len(self.request_timestamps) >= self.user.max_requests_per_minute:
            return False
        
        # Add current request
        self.request_timestamps.append(now)
        self.request_count += 1
        return True
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session has expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class UserSessionManager:
    """Manages user sessions and their agent contexts"""
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
        self._user_sessions: Dict[str, list[str]] = {}  # username -> session_ids
    
    def create_session(self, user: User) -> UserSession:
        """Create a new session for a user"""
        session_id = secrets.token_urlsafe(32)
        
        # Create user-specific agent config
        from initialize import initialize_agent
        base_config = initialize_agent()
        
        # Override with user-specific settings
        config = AgentConfig(
            chat_model=base_config.chat_model,
            utility_model=base_config.utility_model,
            embeddings_model=base_config.embeddings_model,
            browser_model=base_config.browser_model,
            mcp_servers=base_config.mcp_servers,
            prompts_subdir=base_config.prompts_subdir,
            memory_subdir=user.memory_subdir,
            knowledge_subdirs=["default", user.knowledge_subdir],
            code_exec_docker_enabled=base_config.code_exec_docker_enabled,
            code_exec_docker_name=base_config.code_exec_docker_name,
            code_exec_docker_image=base_config.code_exec_docker_image,
            code_exec_docker_ports=base_config.code_exec_docker_ports,
            code_exec_docker_volumes=base_config.code_exec_docker_volumes,
            code_exec_ssh_enabled=base_config.code_exec_ssh_enabled,
            code_exec_ssh_addr=base_config.code_exec_ssh_addr,
            code_exec_ssh_port=base_config.code_exec_ssh_port,
            code_exec_ssh_user=base_config.code_exec_ssh_user,
            code_exec_ssh_pass=base_config.code_exec_ssh_pass,
            additional=base_config.additional
        )
        
        # Create user-specific context
        context = AgentContext(
            config=config,
            name=f"{user.username}'s Agent",
            type=AgentContextType.USER
        )
        
        # Create session
        session = UserSession(user, session_id, context)
        
        # Store session
        self._sessions[session_id] = session
        if user.username not in self._user_sessions:
            self._user_sessions[user.username] = []
        self._user_sessions[user.username].append(session_id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    def get_user_sessions(self, username: str) -> list[UserSession]:
        """Get all sessions for a user"""
        session_ids = self._user_sessions.get(username, [])
        return [
            self._sessions[sid] for sid in session_ids 
            if sid in self._sessions
        ]
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        session = self._sessions.pop(session_id, None)
        if session:
            # Remove from user sessions
            username = session.user.username
            if username in self._user_sessions:
                self._user_sessions[username].remove(session_id)
            
            # Remove agent context
            AgentContext.remove(session.context.id)
            return True
        return False
    
    def remove_user_sessions(self, username: str) -> int:
        """Remove all sessions for a user"""
        session_ids = self._user_sessions.get(username, []).copy()
        count = 0
        for session_id in session_ids:
            if self.remove_session(session_id):
                count += 1
        return count
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 60):
        """Remove expired sessions"""
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired(timeout_minutes)
        ]
        for session_id in expired:
            self.remove_session(session_id)
        return len(expired)
    
    def get_session_by_context_id(self, context_id: str) -> Optional[UserSession]:
        """Get session by agent context ID"""
        for session in self._sessions.values():
            if session.context.id == context_id:
                return session
        return None


# Global session manager instance
_session_manager: Optional[UserSessionManager] = None


def get_session_manager() -> UserSessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = UserSessionManager()
    return _session_manager
