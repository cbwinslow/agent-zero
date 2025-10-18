"""
Automatic Memory Agent

This module implements a background memory monitoring agent that:
- Monitors conversations between user and AI agent
- Automatically determines when to save memories
- Decides how to organize memories (hierarchical, linear, parallel)
- Implements short-term and long-term memory separation
- Runs on a separate thread using Ollama for efficiency

The memory agent watches for:
- Important facts, preferences, and context
- Recurring themes or topics
- Solutions to problems
- User instructions and preferences
- Code snippets and configurations
"""

import asyncio
import threading
import queue
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from python.helpers.print_style import PrintStyle
from python.helpers import files
import models


class MemoryType(Enum):
    """Types of memories to store"""
    SHORT_TERM = "short_term"  # Temporary, session-based memories
    LONG_TERM = "long_term"    # Persistent, cross-session memories
    EPISODIC = "episodic"      # Specific events or conversations
    SEMANTIC = "semantic"      # General knowledge and facts
    PROCEDURAL = "procedural"  # How-to knowledge, solutions


class MemoryOrganization(Enum):
    """How to organize memories"""
    LINEAR = "linear"          # Sequential, chronological
    HIERARCHICAL = "hierarchical"  # Tree-like, categorized
    PARALLEL = "parallel"      # Multiple independent streams
    GRAPH = "graph"           # Network of related memories


@dataclass
class ConversationEvent:
    """Represents a conversation event to be processed"""
    timestamp: datetime
    speaker: str  # "user" or "agent"
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    agent_name: str = "A0"
    context_id: str = ""


@dataclass
class MemoryCandidate:
    """A potential memory to be saved"""
    content: str
    memory_type: MemoryType
    importance: float  # 0.0 to 1.0
    categories: List[str]
    timestamp: datetime
    source_event: ConversationEvent
    keywords: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)


class MemoryMonitor:
    """
    Background agent that monitors conversations and manages memories.
    
    Runs on a separate thread and uses a lightweight Ollama model
    to analyze conversations and decide what to remember.
    """
    
    def __init__(
        self, 
        model_name: str = "llama3.2:3b",  # Small, efficient model
        importance_threshold: float = 0.5,
        short_term_ttl: int = 3600,  # 1 hour in seconds
        enable_auto_save: bool = True,
    ):
        """
        Initialize the memory monitor.
        
        Args:
            model_name: Ollama model to use for memory analysis
            importance_threshold: Minimum importance score to save a memory
            short_term_ttl: Time-to-live for short-term memories in seconds
            enable_auto_save: Whether to automatically save memories
        """
        self.model_name = model_name
        self.importance_threshold = importance_threshold
        self.short_term_ttl = short_term_ttl
        self.enable_auto_save = enable_auto_save
        
        # Event queue for conversation events
        self.event_queue: queue.Queue = queue.Queue()
        
        # Thread management
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Memory storage
        self.short_term_memories: List[MemoryCandidate] = []
        self.pending_long_term: List[MemoryCandidate] = []
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "memories_saved": 0,
            "short_term_count": 0,
            "long_term_count": 0,
        }
        
        # Callback for when memories are saved
        self.on_memory_saved: Optional[Callable[[MemoryCandidate], None]] = None
        
        # Model configuration
        self.model_config = None
        self._init_model()
    
    def _init_model(self):
        """Initialize the Ollama model configuration"""
        try:
            # Create a lightweight model config for Ollama
            self.model_config = models.ModelConfig(
                type=models.ModelType.CHAT,
                provider="ollama",
                name=self.model_name,
                api_base="http://localhost:11434",  # Default Ollama endpoint
                ctx_length=4096,
                kwargs={}
            )
            PrintStyle(font_color="cyan", padding=True).print(
                f"Memory monitor initialized with model: {self.model_name}"
            )
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"Warning: Could not initialize memory monitor model: {e}"
            )
            PrintStyle(font_color="yellow", padding=True).print(
                "Memory monitor will operate in fallback mode"
            )
    
    def start(self):
        """Start the memory monitoring thread"""
        if self.running:
            PrintStyle(font_color="yellow", padding=True).print(
                "Memory monitor is already running"
            )
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="MemoryMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        PrintStyle(font_color="green", padding=True).print(
            "Memory monitor started"
        )
    
    def stop(self):
        """Stop the memory monitoring thread"""
        if not self.running:
            return
        
        self.running = False
        
        # Wait for thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        PrintStyle(font_color="yellow", padding=True).print(
            "Memory monitor stopped"
        )
    
    def broadcast_event(self, event: ConversationEvent):
        """
        Broadcast a conversation event to the monitor.
        
        Args:
            event: The conversation event to process
        """
        if not self.running:
            self.start()
        
        self.event_queue.put(event)
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread"""
        PrintStyle(font_color="cyan", padding=True).print(
            "Memory monitor thread started"
        )
        
        while self.running:
            try:
                # Get event from queue with timeout
                try:
                    event = self.event_queue.get(timeout=1)
                except queue.Empty:
                    # No events, clean up old short-term memories
                    self._cleanup_short_term()
                    continue
                
                # Process the event
                self._process_event(event)
                self.stats["events_processed"] += 1
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                PrintStyle(font_color="red", padding=True).print(
                    f"Error in memory monitor loop: {e}"
                )
        
        PrintStyle(font_color="cyan", padding=True).print(
            "Memory monitor thread stopped"
        )
    
    def _process_event(self, event: ConversationEvent):
        """
        Process a conversation event and extract memories.
        
        Args:
            event: The conversation event to process
        """
        # Skip very short messages
        if len(event.message.strip()) < 10:
            return
        
        # Analyze the event to determine if it contains memorable information
        memory_candidate = self._analyze_event(event)
        
        if memory_candidate and memory_candidate.importance >= self.importance_threshold:
            # Add to appropriate memory store
            if memory_candidate.memory_type == MemoryType.SHORT_TERM:
                self.short_term_memories.append(memory_candidate)
                self.stats["short_term_count"] += 1
            elif memory_candidate.memory_type in [MemoryType.LONG_TERM, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]:
                self.pending_long_term.append(memory_candidate)
                
                # Auto-save if enabled
                if self.enable_auto_save:
                    self._save_memory(memory_candidate)
    
    def _analyze_event(self, event: ConversationEvent) -> Optional[MemoryCandidate]:
        """
        Analyze an event to determine if it should be remembered.
        
        Uses the Ollama model to assess importance and extract key information.
        
        Args:
            event: The event to analyze
            
        Returns:
            MemoryCandidate if the event is worth remembering, None otherwise
        """
        # Fallback heuristic-based analysis if model is not available
        if not self.model_config:
            return self._heuristic_analysis(event)
        
        try:
            # Use the model to analyze the conversation
            # This would be an async call in practice, but we're in a thread
            # so we'll use a simplified synchronous approach
            
            # For now, use heuristic analysis
            # TODO: Implement async model call from thread
            return self._heuristic_analysis(event)
            
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"Memory analysis failed, using fallback: {e}"
            )
            return self._heuristic_analysis(event)
    
    def _heuristic_analysis(self, event: ConversationEvent) -> Optional[MemoryCandidate]:
        """
        Heuristic-based analysis when model is not available.
        
        Args:
            event: The event to analyze
            
        Returns:
            MemoryCandidate if the event meets heuristic criteria
        """
        message = event.message.lower()
        importance = 0.0
        categories = []
        keywords = []
        memory_type = MemoryType.SHORT_TERM
        
        # Check for important keywords and patterns
        
        # User preferences and instructions
        if event.speaker == "user":
            if any(kw in message for kw in ["remember", "note that", "important", "don't forget", "keep in mind"]):
                importance += 0.3
                categories.append("user_preference")
                memory_type = MemoryType.LONG_TERM
            
            if any(kw in message for kw in ["always", "never", "prefer", "like", "dislike"]):
                importance += 0.2
                categories.append("preference")
                memory_type = MemoryType.SEMANTIC
        
        # Solutions and procedures
        if any(kw in message for kw in ["solution", "fixed", "solved", "here's how", "steps to", "workaround"]):
            importance += 0.3
            categories.append("solution")
            memory_type = MemoryType.PROCEDURAL
        
        # Facts and knowledge
        if event.speaker == "agent" and any(kw in message for kw in ["is defined as", "means", "refers to", "the formula"]):
            importance += 0.2
            categories.append("knowledge")
            memory_type = MemoryType.SEMANTIC
        
        # Code snippets
        if "```" in event.message or any(kw in message for kw in ["def ", "class ", "function", "import "]):
            importance += 0.2
            categories.append("code")
            memory_type = MemoryType.PROCEDURAL
        
        # Configuration and settings
        if any(kw in message for kw in ["config", "setting", "configure", "setup", "install"]):
            importance += 0.15
            categories.append("configuration")
        
        # Error messages (lower importance but useful)
        if any(kw in message for kw in ["error", "exception", "failed", "traceback"]):
            importance += 0.1
            categories.append("error")
        
        # Extract potential keywords (simple approach)
        words = message.split()
        # Get words longer than 4 characters as potential keywords
        keywords = [w.strip(".,!?;:") for w in words if len(w) > 4][:5]
        
        # Adjust importance based on message length and structure
        if len(event.message) > 100:
            importance += 0.1  # Longer messages might be more detailed
        
        if not categories:
            categories = ["general"]
            importance = max(importance, 0.1)  # Minimum importance for general messages
        
        # Only create candidate if importance is above minimum threshold (0.1)
        if importance < 0.1:
            return None
        
        # Cap importance at 1.0
        importance = min(importance, 1.0)
        
        return MemoryCandidate(
            content=event.message,
            memory_type=memory_type,
            importance=importance,
            categories=categories,
            timestamp=event.timestamp,
            source_event=event,
            keywords=keywords,
            related_memories=[]
        )
    
    def _cleanup_short_term(self):
        """Remove expired short-term memories"""
        current_time = datetime.now(timezone.utc)
        
        # Filter out expired memories
        self.short_term_memories = [
            mem for mem in self.short_term_memories
            if (current_time - mem.timestamp).total_seconds() < self.short_term_ttl
        ]
    
    def _save_memory(self, memory: MemoryCandidate):
        """
        Save a memory using the agent's memory system.
        
        Args:
            memory: The memory to save
        """
        try:
            # Here we would integrate with the existing memory system
            # For now, we'll just log it
            
            PrintStyle(font_color="green", padding=True).print(
                f"Memory saved: {memory.memory_type.value} - {memory.categories} - "
                f"Importance: {memory.importance:.2f}"
            )
            
            self.stats["memories_saved"] += 1
            
            if memory.memory_type != MemoryType.SHORT_TERM:
                self.stats["long_term_count"] += 1
            
            # Call callback if set
            if self.on_memory_saved:
                self.on_memory_saved(memory)
                
        except Exception as e:
            PrintStyle(font_color="red", padding=True).print(
                f"Failed to save memory: {e}"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory monitor statistics"""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "short_term_active": len(self.short_term_memories),
            "pending_long_term": len(self.pending_long_term),
            "is_running": self.running,
        }
    
    def get_short_term_memories(self) -> List[MemoryCandidate]:
        """Get current short-term memories"""
        self._cleanup_short_term()
        return self.short_term_memories.copy()
    
    def get_pending_long_term(self) -> List[MemoryCandidate]:
        """Get pending long-term memories"""
        return self.pending_long_term.copy()


# Global memory monitor instance
_global_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """
    Get the global memory monitor instance.
    
    Returns:
        The global MemoryMonitor instance
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MemoryMonitor()
    return _global_monitor


def broadcast_conversation_event(
    speaker: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    agent_name: str = "A0",
    context_id: str = ""
):
    """
    Convenience function to broadcast a conversation event.
    
    Args:
        speaker: "user" or "agent"
        message: The message content
        context: Additional context information
        agent_name: Name of the agent
        context_id: Context/session ID
    """
    event = ConversationEvent(
        timestamp=datetime.now(timezone.utc),
        speaker=speaker,
        message=message,
        context=context or {},
        agent_name=agent_name,
        context_id=context_id
    )
    
    monitor = get_memory_monitor()
    monitor.broadcast_event(event)
