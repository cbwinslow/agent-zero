"""
Error Tracking and Logging System for Agent Zero

This module provides comprehensive error tracking, logging, and solution lookup
capabilities. It maintains a persistent database of errors encountered during
agent execution, along with their solutions and context.

Features:
- Persistent error logging to JSON database
- Error pattern matching and similarity detection
- Solution lookup based on previous error resolutions
- Error statistics and frequency tracking
- Automatic error categorization
- Error prevention recommendations
"""

import json
import os
import re
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
from dataclasses import dataclass, asdict
from python.helpers import files
from python.helpers.print_style import PrintStyle


@dataclass
class ErrorEntry:
    """Represents a single error entry in the tracking system"""
    error_id: str  # Unique identifier based on error signature
    error_type: str  # Type of exception (e.g., ValueError, RuntimeError)
    error_message: str  # The error message
    error_signature: str  # Normalized error pattern for matching
    traceback: str  # Full traceback
    timestamp: str  # When the error occurred
    context: Dict[str, Any]  # Additional context (agent info, tool being used, etc.)
    occurrence_count: int = 1  # How many times this error occurred
    solutions: List[Dict[str, str]] = None  # List of attempted solutions
    resolved: bool = False  # Whether this error has been resolved
    category: str = "unknown"  # Error category (network, file_io, llm, tool, etc.)
    
    def __post_init__(self):
        """Initialize solutions list if None"""
        if self.solutions is None:
            self.solutions = []


class ErrorTracker:
    """
    Tracks and manages errors encountered during agent execution.
    
    Provides methods to:
    - Log new errors with context
    - Find similar errors from history
    - Store and retrieve solutions
    - Generate error statistics
    - Provide error prevention recommendations
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the error tracker.
        
        Args:
            db_path: Path to the error database JSON file. 
                     Defaults to 'logs/error_tracker.json'
        """
        if db_path is None:
            db_path = files.get_abs_path("logs", "error_tracker.json")
        
        self.db_path = db_path
        self.errors: Dict[str, ErrorEntry] = {}
        self._ensure_db_exists()
        self._load_errors()
    
    def _ensure_db_exists(self):
        """Ensure the error database directory and file exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({}, f)
    
    def _load_errors(self):
        """Load errors from the database file"""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                for error_id, error_data in data.items():
                    # Convert dict back to ErrorEntry
                    self.errors[error_id] = ErrorEntry(**error_data)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, start fresh
            self.errors = {}
            PrintStyle(font_color="yellow", padding=True).print(
                f"Error tracker database at {self.db_path} was reset due to read error"
            )
    
    def _save_errors(self):
        """Save errors to the database file"""
        try:
            # Convert ErrorEntry objects to dicts for JSON serialization
            data = {
                error_id: asdict(error_entry) 
                for error_id, error_entry in self.errors.items()
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            PrintStyle(font_color="red", padding=True).print(
                f"Failed to save error tracker database: {e}"
            )
    
    def _generate_error_signature(self, error_type: str, error_message: str) -> str:
        """
        Generate a normalized signature for error pattern matching.
        
        This removes specific values like file paths, numbers, variable names
        to create a pattern that can match similar errors.
        
        Args:
            error_type: The type of exception
            error_message: The error message
            
        Returns:
            Normalized error signature
        """
        # Normalize the error message
        signature = error_message
        
        # Remove file paths (both Unix and Windows style)
        signature = re.sub(r'[/\\][\w/\\.-]+\.\w+', '[FILE_PATH]', signature)
        
        # Remove line numbers
        signature = re.sub(r'line \d+', 'line [NUM]', signature)
        
        # Remove numeric values
        signature = re.sub(r'\b\d+\b', '[NUM]', signature)
        
        # Remove quoted strings
        signature = re.sub(r'"[^"]*"', '[STRING]', signature)
        signature = re.sub(r"'[^']*'", '[STRING]', signature)
        
        # Remove memory addresses
        signature = re.sub(r'0x[0-9a-fA-F]+', '[ADDR]', signature)
        
        # Combine with error type
        full_signature = f"{error_type}: {signature}"
        
        return full_signature
    
    def _generate_error_id(self, signature: str) -> str:
        """Generate a unique ID for an error based on its signature"""
        return hashlib.md5(signature.encode()).hexdigest()[:12]
    
    def _categorize_error(self, error_type: str, error_message: str, traceback_text: str) -> str:
        """
        Automatically categorize an error based on its characteristics.
        
        Args:
            error_type: The type of exception
            error_message: The error message
            traceback_text: The full traceback
            
        Returns:
            Error category string
        """
        error_lower = error_message.lower()
        tb_lower = traceback_text.lower()
        
        # Network-related errors
        if any(kw in error_lower for kw in ['connection', 'timeout', 'network', 'socket', 'url', 'http', 'ssl']):
            return "network"
        
        # File I/O errors
        if any(kw in error_lower for kw in ['file', 'directory', 'path', 'permission', 'not found']):
            return "file_io"
        
        # LLM/API errors
        if any(kw in error_lower for kw in ['api', 'rate limit', 'quota', 'token', 'model', 'openai', 'anthropic']):
            return "llm_api"
        
        # Memory errors
        if any(kw in error_lower for kw in ['memory', 'allocation', 'out of']):
            return "memory"
        
        # Tool execution errors
        if 'python/tools/' in tb_lower or 'tool' in error_lower:
            return "tool_execution"
        
        # Import/dependency errors
        if error_type in ['ImportError', 'ModuleNotFoundError']:
            return "import"
        
        # Value/type errors (data validation)
        if error_type in ['ValueError', 'TypeError', 'KeyError']:
            return "data_validation"
        
        # Default category
        return "unknown"
    
    def log_error(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        solution: Optional[str] = None
    ) -> str:
        """
        Log an error to the tracking system.
        
        Args:
            exception: The exception that occurred
            context: Additional context information (agent name, tool being used, etc.)
            solution: Optional solution if one was found
            
        Returns:
            The error ID for this error
        """
        if context is None:
            context = {}
        
        # Extract error information
        error_type = type(exception).__name__
        error_message = str(exception)
        traceback_text = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        # Generate signature and ID
        signature = self._generate_error_signature(error_type, error_message)
        error_id = self._generate_error_id(signature)
        
        # Categorize the error
        category = self._categorize_error(error_type, error_message, traceback_text)
        
        # Check if this error already exists
        if error_id in self.errors:
            # Update existing error
            self.errors[error_id].occurrence_count += 1
            self.errors[error_id].timestamp = datetime.now(timezone.utc).isoformat()
            
            # Add solution if provided
            if solution:
                self.errors[error_id].solutions.append({
                    "solution": solution,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                self.errors[error_id].resolved = True
        else:
            # Create new error entry
            solutions = []
            if solution:
                solutions.append({
                    "solution": solution,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            self.errors[error_id] = ErrorEntry(
                error_id=error_id,
                error_type=error_type,
                error_message=error_message,
                error_signature=signature,
                traceback=traceback_text,
                timestamp=datetime.now(timezone.utc).isoformat(),
                context=context,
                occurrence_count=1,
                solutions=solutions,
                resolved=bool(solution),
                category=category
            )
        
        # Save to database
        self._save_errors()
        
        return error_id
    
    def find_similar_errors(
        self, 
        exception: Exception, 
        limit: int = 5
    ) -> List[Tuple[ErrorEntry, float]]:
        """
        Find similar errors from the database.
        
        Args:
            exception: The exception to find similar errors for
            limit: Maximum number of similar errors to return
            
        Returns:
            List of tuples (ErrorEntry, similarity_score) sorted by similarity
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        signature = self._generate_error_signature(error_type, error_message)
        
        similar = []
        
        for error_entry in self.errors.values():
            # Calculate similarity score
            # 1. Exact type match: +0.4
            # 2. Signature similarity: +0.6
            score = 0.0
            
            if error_entry.error_type == error_type:
                score += 0.4
            
            # Simple string similarity based on common words
            sig_words = set(signature.lower().split())
            entry_words = set(error_entry.error_signature.lower().split())
            
            if sig_words and entry_words:
                common_words = sig_words & entry_words
                similarity = len(common_words) / max(len(sig_words), len(entry_words))
                score += 0.6 * similarity
            
            if score > 0.3:  # Minimum threshold for similarity
                similar.append((error_entry, score))
        
        # Sort by similarity score (descending) and return top results
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:limit]
    
    def get_solutions(self, exception: Exception) -> List[Dict[str, str]]:
        """
        Get known solutions for an error.
        
        Args:
            exception: The exception to find solutions for
            
        Returns:
            List of solution dictionaries with 'solution' and 'timestamp' keys
        """
        similar_errors = self.find_similar_errors(exception, limit=3)
        
        all_solutions = []
        for error_entry, score in similar_errors:
            if error_entry.solutions:
                for solution in error_entry.solutions:
                    all_solutions.append({
                        **solution,
                        "similarity_score": score,
                        "error_id": error_entry.error_id
                    })
        
        # Sort by similarity score
        all_solutions.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return all_solutions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            Dictionary containing error statistics
        """
        if not self.errors:
            return {
                "total_errors": 0,
                "unique_errors": 0,
                "resolved_count": 0,
                "by_category": {},
                "by_type": {},
                "most_frequent": []
            }
        
        # Calculate statistics
        total_occurrences = sum(e.occurrence_count for e in self.errors.values())
        resolved_count = sum(1 for e in self.errors.values() if e.resolved)
        
        # Group by category
        by_category = {}
        for error in self.errors.values():
            category = error.category
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += error.occurrence_count
        
        # Group by type
        by_type = {}
        for error in self.errors.values():
            error_type = error.error_type
            if error_type not in by_type:
                by_type[error_type] = 0
            by_type[error_type] += error.occurrence_count
        
        # Most frequent errors
        most_frequent = sorted(
            self.errors.values(), 
            key=lambda x: x.occurrence_count, 
            reverse=True
        )[:10]
        
        return {
            "total_errors": total_occurrences,
            "unique_errors": len(self.errors),
            "resolved_count": resolved_count,
            "resolution_rate": resolved_count / len(self.errors) if self.errors else 0,
            "by_category": by_category,
            "by_type": by_type,
            "most_frequent": [
                {
                    "error_id": e.error_id,
                    "error_type": e.error_type,
                    "error_message": e.error_message[:100],
                    "count": e.occurrence_count,
                    "resolved": e.resolved
                }
                for e in most_frequent
            ]
        }
    
    def get_prevention_recommendations(self, category: Optional[str] = None) -> List[str]:
        """
        Get error prevention recommendations based on tracked errors.
        
        Args:
            category: Optional category to get recommendations for
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Get errors for the specified category or all errors
        if category:
            errors = [e for e in self.errors.values() if e.category == category]
        else:
            errors = list(self.errors.values())
        
        if not errors:
            return ["No errors tracked yet for recommendations"]
        
        # Category-specific recommendations
        category_counts = {}
        for error in errors:
            cat = error.category
            category_counts[cat] = category_counts.get(cat, 0) + error.occurrence_count
        
        # Recommend based on most common categories
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            if cat == "network":
                recommendations.append(
                    "Add retry logic with exponential backoff for network operations"
                )
                recommendations.append(
                    "Implement timeout handling for API calls"
                )
            elif cat == "file_io":
                recommendations.append(
                    "Add file existence checks before operations"
                )
                recommendations.append(
                    "Implement proper path handling with pathlib"
                )
            elif cat == "llm_api":
                recommendations.append(
                    "Implement rate limiting and quota tracking"
                )
                recommendations.append(
                    "Add fallback models for API failures"
                )
            elif cat == "tool_execution":
                recommendations.append(
                    "Add input validation before tool execution"
                )
                recommendations.append(
                    "Implement tool timeout mechanisms"
                )
            elif cat == "import":
                recommendations.append(
                    "Add dependency checks at startup"
                )
                recommendations.append(
                    "Implement graceful fallbacks for optional dependencies"
                )
        
        # General recommendations based on error patterns
        unresolved = [e for e in errors if not e.resolved]
        if len(unresolved) > len(errors) * 0.5:
            recommendations.append(
                f"{len(unresolved)} unresolved errors - consider implementing better error recovery"
            )
        
        return recommendations if recommendations else ["No specific recommendations at this time"]


# Global error tracker instance
_global_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """
    Get the global error tracker instance.
    
    Returns:
        The global ErrorTracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ErrorTracker()
    return _global_tracker


def log_error(
    exception: Exception, 
    context: Optional[Dict[str, Any]] = None,
    solution: Optional[str] = None
) -> str:
    """
    Convenience function to log an error to the global tracker.
    
    Args:
        exception: The exception that occurred
        context: Additional context information
        solution: Optional solution if one was found
        
    Returns:
        The error ID
    """
    return get_error_tracker().log_error(exception, context, solution)


def find_similar_errors(exception: Exception, limit: int = 5) -> List[Tuple[ErrorEntry, float]]:
    """
    Convenience function to find similar errors from the global tracker.
    
    Args:
        exception: The exception to find similar errors for
        limit: Maximum number of similar errors to return
        
    Returns:
        List of tuples (ErrorEntry, similarity_score)
    """
    return get_error_tracker().find_similar_errors(exception, limit)


def get_solutions(exception: Exception) -> List[Dict[str, str]]:
    """
    Convenience function to get solutions from the global tracker.
    
    Args:
        exception: The exception to find solutions for
        
    Returns:
        List of solution dictionaries
    """
    return get_error_tracker().get_solutions(exception)
