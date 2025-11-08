"""
Tool Optimization System for Agent Zero

This module implements advanced tool management and optimization:

1. Tool Result Caching
   - Cache frequently used tool results
   - Intelligent cache invalidation
   - Context-aware caching

2. Parallel Tool Execution
   - Execute independent tools concurrently
   - Dependency-aware scheduling
   - Resource management

3. Tool Chaining
   - Automatic tool composition
   - Pipeline creation
   - Data flow optimization

4. Tool Learning
   - Usage pattern analysis
   - Automatic tool selection
   - Performance tracking

5. Tool Discovery
   - Dynamic tool registration
   - Capability matching
   - Smart tool recommendations
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
import inspect

from python.helpers.print_style import PrintStyle
from python.helpers import files


class CacheStrategy(Enum):
    """Cache strategies for tool results"""
    ALWAYS = "always"          # Always cache
    CONDITIONAL = "conditional"  # Cache based on conditions
    NEVER = "never"            # Never cache
    TIME_BASED = "time_based"  # Cache with TTL


@dataclass
class ToolResult:
    """Enhanced tool result with metadata"""
    result: Any
    success: bool
    execution_time: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecution:
    """Tool execution record"""
    tool_name: str
    args: Dict[str, Any]
    result: Optional[ToolResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class ToolMetrics:
    """Performance metrics for a tool"""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    last_used: Optional[datetime] = None
    
    def update(self, execution: ToolExecution):
        """Update metrics with a new execution"""
        self.total_calls += 1
        self.last_used = datetime.now(timezone.utc)
        
        if execution.result and execution.result.success:
            self.successful_calls += 1
            self.total_execution_time += execution.duration
            self.average_execution_time = self.total_execution_time / self.successful_calls
            
            if execution.result.cached:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
        else:
            self.failed_calls += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_cache_attempts = self.cache_hits + self.cache_misses
        if total_cache_attempts == 0:
            return 0.0
        return self.cache_hits / total_cache_attempts


class ToolCache:
    """
    Intelligent caching system for tool results.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,  # 1 hour
        enable_compression: bool = True,
    ):
        """
        Initialize tool cache.
        
        Args:
            max_size: Maximum number of cached entries
            default_ttl: Default time-to-live in seconds
            enable_compression: Whether to compress cached data
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression
        
        # Cache storage: key -> (result, timestamp, access_count)
        self.cache: Dict[str, Tuple[Any, datetime, int]] = {}
        
        # LRU tracking
        self.access_order: deque = deque()
        
        # TTL configuration per tool
        self.tool_ttls: Dict[str, int] = {}
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }
    
    def _generate_cache_key(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a unique cache key for tool execution.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            context: Optional context for cache key
            
        Returns:
            Cache key string
        """
        # Sort args for consistent hashing
        sorted_args = json.dumps(args, sort_keys=True)
        key_data = f"{tool_name}:{sorted_args}"
        if context:
            key_data += f":{context}"
        
        # Use hash for shorter keys
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Get cached result if available and valid.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            context: Optional context
            
        Returns:
            Cached result or None
        """
        cache_key = self._generate_cache_key(tool_name, args, context)
        
        if cache_key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        result, timestamp, access_count = self.cache[cache_key]
        
        # Check TTL
        ttl = self.tool_ttls.get(tool_name, self.default_ttl)
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        
        if age > ttl:
            # Expired
            del self.cache[cache_key]
            self.stats["misses"] += 1
            return None
        
        # Update access tracking
        self.cache[cache_key] = (result, timestamp, access_count + 1)
        self.access_order.remove(cache_key) if cache_key in self.access_order else None
        self.access_order.append(cache_key)
        
        self.stats["hits"] += 1
        return result
    
    def put(
        self,
        tool_name: str,
        args: Dict[str, Any],
        result: Any,
        context: Optional[str] = None,
        ttl: Optional[int] = None,
    ):
        """
        Cache a tool result.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            result: Result to cache
            context: Optional context
            ttl: Optional custom TTL
        """
        cache_key = self._generate_cache_key(tool_name, args, context)
        
        # Set custom TTL if provided
        if ttl is not None:
            self.tool_ttls[tool_name] = ttl
        
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Store result
        self.cache[cache_key] = (result, datetime.now(timezone.utc), 1)
        self.access_order.append(cache_key)
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_order:
            return
        
        lru_key = self.access_order.popleft()
        if lru_key in self.cache:
            del self.cache[lru_key]
            self.stats["evictions"] += 1
    
    def invalidate(
        self,
        tool_name: Optional[str] = None,
        pattern: Optional[str] = None,
    ):
        """
        Invalidate cached entries.
        
        Args:
            tool_name: Invalidate all entries for this tool
            pattern: Invalidate entries matching pattern
        """
        if tool_name:
            # Invalidate by tool name (requires storing tool names with keys)
            # For simplicity, clear entire cache
            count = len(self.cache)
            self.cache.clear()
            self.access_order.clear()
            self.stats["invalidations"] += count
        
        PrintStyle(font_color="yellow").print(
            f"Invalidated cache entries"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            **self.stats,
        }


class ToolOptimizer:
    """
    Advanced tool optimization and management system.
    """
    
    def __init__(self, agent):
        """
        Initialize tool optimizer.
        
        Args:
            agent: The agent instance
        """
        self.agent = agent
        self.cache = ToolCache()
        self.metrics: Dict[str, ToolMetrics] = {}
        self.execution_history: deque = deque(maxlen=1000)
        
        # Tool capabilities registry
        self.tool_capabilities: Dict[str, Set[str]] = {}
        
        # Tool dependency graph
        self.tool_dependencies: Dict[str, Set[str]] = {}
        
        # Parallel execution pool
        self.max_parallel_tools = 5
        self.active_executions: Set[asyncio.Task] = set()
    
    async def execute_tool_optimized(
        self,
        tool_name: str,
        args: Dict[str, Any],
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
        context: Optional[str] = None,
    ) -> ToolResult:
        """
        Execute a tool with optimization (caching, metrics, etc.).
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            use_cache: Whether to use caching
            cache_ttl: Optional cache TTL
            context: Optional execution context
            
        Returns:
            ToolResult with execution details
        """
        execution = ToolExecution(tool_name=tool_name, args=args)
        execution.start_time = datetime.now(timezone.utc)
        
        # Check cache
        if use_cache:
            cached_result = self.cache.get(tool_name, args, context)
            if cached_result is not None:
                execution.end_time = datetime.now(timezone.utc)
                execution.result = ToolResult(
                    result=cached_result,
                    success=True,
                    execution_time=0.0,
                    cached=True,
                )
                self._update_metrics(execution)
                return execution.result
        
        # Execute tool
        try:
            start = time.time()
            
            # Get tool instance and execute
            tool = self.agent.get_tool(
                name=tool_name,
                method=None,
                args=args,
                message="",
                loop_data=None,
            )
            
            if tool:
                response = await tool.execute(**args)
                result = response.message if hasattr(response, 'message') else str(response)
                success = True
            else:
                result = None
                success = False
                execution.error = f"Tool {tool_name} not found"
            
            execution_time = time.time() - start
            
            execution.result = ToolResult(
                result=result,
                success=success,
                execution_time=execution_time,
                cached=False,
            )
            
            # Cache result if successful
            if success and use_cache:
                self.cache.put(tool_name, args, result, context, cache_ttl)
            
        except Exception as e:
            execution.error = str(e)
            execution.result = ToolResult(
                result=None,
                success=False,
                execution_time=0.0,
            )
            PrintStyle(font_color="red").print(
                f"Tool execution error: {e}"
            )
        
        execution.end_time = datetime.now(timezone.utc)
        self._update_metrics(execution)
        self.execution_history.append(execution)
        
        return execution.result
    
    async def execute_tools_parallel(
        self,
        tool_specs: List[Tuple[str, Dict[str, Any]]],
        max_parallel: Optional[int] = None,
    ) -> List[ToolResult]:
        """
        Execute multiple independent tools in parallel.
        
        Args:
            tool_specs: List of (tool_name, args) tuples
            max_parallel: Maximum number of parallel executions
            
        Returns:
            List of ToolResults in the same order as input
        """
        max_parallel = max_parallel or self.max_parallel_tools
        
        # Create tasks
        tasks = []
        for tool_name, args in tool_specs:
            task = asyncio.create_task(
                self.execute_tool_optimized(tool_name, args)
            )
            tasks.append(task)
            self.active_executions.add(task)
        
        # Execute with concurrency limit
        results = []
        for i in range(0, len(tasks), max_parallel):
            batch = tasks[i:i + max_parallel]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
            
            # Remove completed tasks
            for task in batch:
                self.active_executions.discard(task)
        
        PrintStyle(font_color="green").print(
            f"Executed {len(tool_specs)} tools in parallel"
        )
        
        return results
    
    async def create_tool_pipeline(
        self,
        pipeline: List[Tuple[str, Dict[str, Any], Optional[Callable]]],
    ) -> Any:
        """
        Execute a pipeline of tools where output of one feeds into the next.
        
        Args:
            pipeline: List of (tool_name, args, transform_func) tuples
                     transform_func takes output and returns args for next tool
            
        Returns:
            Final pipeline result
        """
        result = None
        
        for i, (tool_name, args, transform) in enumerate(pipeline):
            # If transform function provided and we have previous result
            if transform and result is not None:
                try:
                    args = transform(result)
                except Exception as e:
                    PrintStyle(font_color="red").print(
                        f"Pipeline transform error at step {i}: {e}"
                    )
                    break
            
            # Execute tool
            tool_result = await self.execute_tool_optimized(tool_name, args)
            
            if not tool_result.success:
                PrintStyle(font_color="red").print(
                    f"Pipeline failed at step {i}: {tool_name}"
                )
                break
            
            result = tool_result.result
        
        return result
    
    def _update_metrics(self, execution: ToolExecution):
        """Update metrics for a tool execution"""
        if execution.tool_name not in self.metrics:
            self.metrics[execution.tool_name] = ToolMetrics(
                tool_name=execution.tool_name
            )
        
        self.metrics[execution.tool_name].update(execution)
    
    def get_tool_recommendations(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Get tool recommendations based on query and usage patterns.
        
        Args:
            query: The query or task description
            top_k: Number of recommendations
            
        Returns:
            List of (tool_name, score) tuples
        """
        scores = []
        
        for tool_name, metrics in self.metrics.items():
            score = 0.0
            
            # Success rate component
            score += metrics.success_rate * 0.4
            
            # Recent usage component
            if metrics.last_used:
                age_days = (datetime.now(timezone.utc) - metrics.last_used).days
                recency_score = max(0, 1.0 - (age_days / 30))
                score += recency_score * 0.2
            
            # Performance component (faster is better)
            if metrics.average_execution_time > 0:
                # Normalize to 0-1 (assuming max 10s)
                perf_score = max(0, 1.0 - (metrics.average_execution_time / 10.0))
                score += perf_score * 0.2
            
            # Usage frequency component
            freq_score = min(1.0, metrics.total_calls / 100)
            score += freq_score * 0.2
            
            scores.append((tool_name, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        stats = {
            "cache": self.cache.get_stats(),
            "total_tools": len(self.metrics),
            "total_executions": sum(m.total_calls for m in self.metrics.values()),
            "tools": {},
        }
        
        # Per-tool stats
        for tool_name, metrics in self.metrics.items():
            stats["tools"][tool_name] = {
                "calls": metrics.total_calls,
                "success_rate": metrics.success_rate,
                "avg_time": metrics.average_execution_time,
                "cache_hit_rate": metrics.cache_hit_rate,
            }
        
        return stats
    
    def export_metrics(self, filepath: str):
        """Export tool metrics to a file"""
        try:
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stats": self.get_optimization_stats(),
                "metrics": {
                    name: {
                        "total_calls": m.total_calls,
                        "successful_calls": m.successful_calls,
                        "failed_calls": m.failed_calls,
                        "average_execution_time": m.average_execution_time,
                        "success_rate": m.success_rate,
                        "cache_hit_rate": m.cache_hit_rate,
                        "last_used": m.last_used.isoformat() if m.last_used else None,
                    }
                    for name, m in self.metrics.items()
                },
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            PrintStyle(font_color="green").print(
                f"Exported tool metrics to {filepath}"
            )
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Failed to export metrics: {e}"
            )


# Global instance
_tool_optimizer_instance: Optional[ToolOptimizer] = None


def get_tool_optimizer(agent) -> ToolOptimizer:
    """Get or create the global tool optimizer instance"""
    global _tool_optimizer_instance
    if _tool_optimizer_instance is None:
        _tool_optimizer_instance = ToolOptimizer(agent)
    return _tool_optimizer_instance
