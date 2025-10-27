"""
Hierarchical Memory System for Agent Zero

This module implements a multi-tier memory architecture inspired by human cognition:

1. Working Memory (Short-term, immediate context)
   - Current conversation state
   - Active tool results
   - Recent observations
   - Fast access, limited capacity

2. Episodic Memory (Event-based, chronological)
   - Conversation episodes
   - Task execution sequences
   - User interactions
   - Time-stamped events

3. Semantic Memory (Factual knowledge)
   - General facts and knowledge
   - Concepts and definitions
   - Relationships and patterns
   - Context-independent information

4. Procedural Memory (How-to knowledge)
   - Solution patterns
   - Code templates
   - Tool usage patterns
   - Workflows and strategies

Features:
- Automatic memory consolidation and promotion between tiers
- Importance-based memory retention
- Memory clustering and categorization
- Hybrid retrieval (semantic + temporal + keyword)
- Memory pruning and archival
- Cross-tier memory linking
"""

import asyncio
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import numpy as np

from langchain_core.documents import Document
from python.helpers import files
from python.helpers.print_style import PrintStyle
from python.helpers.vector_db import VectorDB


class MemoryTier(Enum):
    """Memory hierarchy tiers"""
    WORKING = "working"          # Immediate, volatile
    EPISODIC = "episodic"        # Event-based, time-bound
    SEMANTIC = "semantic"        # Factual, timeless
    PROCEDURAL = "procedural"    # Skill-based, solution patterns


class MemoryImportance(Enum):
    """Memory importance levels"""
    CRITICAL = 1.0    # Must retain
    HIGH = 0.8        # Very important
    MEDIUM = 0.5      # Moderately important
    LOW = 0.3         # Nice to have
    TRIVIAL = 0.1     # Can be discarded


@dataclass
class MemoryMetadata:
    """Enhanced metadata for hierarchical memory entries"""
    tier: MemoryTier
    importance: float
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    parent_ids: List[str] = field(default_factory=list)  # Hierarchical links
    child_ids: List[str] = field(default_factory=list)   # Sub-memories
    related_ids: List[str] = field(default_factory=list)  # Cross-references
    context_id: str = ""
    agent_name: str = ""
    source_type: str = ""  # "user", "agent", "tool", "system"
    consolidation_score: float = 0.0  # Score for memory consolidation
    embedding_vector: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryMetadata':
        """Create from dictionary"""
        data['tier'] = MemoryTier(data['tier'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


@dataclass
class ConsolidationRule:
    """Rules for memory consolidation"""
    min_importance: float = 0.5
    min_access_count: int = 3
    age_threshold_days: int = 7
    similarity_threshold: float = 0.85
    consolidation_strategy: str = "merge"  # merge, summarize, archive


class HierarchicalMemory:
    """
    Advanced hierarchical memory management system.
    
    Manages multiple tiers of memory with automatic consolidation,
    importance-based retention, and intelligent retrieval.
    """
    
    # Capacity limits for each tier (number of items)
    TIER_CAPACITIES = {
        MemoryTier.WORKING: 50,      # Small, immediate context
        MemoryTier.EPISODIC: 500,    # Recent events
        MemoryTier.SEMANTIC: 5000,   # Long-term knowledge
        MemoryTier.PROCEDURAL: 1000, # Solutions and patterns
    }
    
    # Time-to-live for each tier (in days, 0 = infinite)
    TIER_TTL = {
        MemoryTier.WORKING: 1,       # 1 day
        MemoryTier.EPISODIC: 30,     # 30 days
        MemoryTier.SEMANTIC: 0,      # Permanent
        MemoryTier.PROCEDURAL: 0,    # Permanent
    }
    
    def __init__(self, agent, memory_dir: Optional[str] = None):
        """
        Initialize hierarchical memory system.
        
        Args:
            agent: The agent instance
            memory_dir: Directory for memory storage
        """
        self.agent = agent
        self.memory_dir = memory_dir or files.get_abs_path("memory", "hierarchy")
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Separate vector databases for each tier
        self.tier_dbs: Dict[MemoryTier, VectorDB] = {}
        self._initialize_tier_dbs()
        
        # Memory metadata index
        self.metadata_index: Dict[str, MemoryMetadata] = {}
        self._load_metadata_index()
        
        # Consolidation rules
        self.consolidation_rules = ConsolidationRule()
        
        # Statistics
        self.stats = {
            "total_memories": 0,
            "consolidations": 0,
            "promotions": 0,
            "prunings": 0,
        }
        self._load_stats()
    
    def _initialize_tier_dbs(self):
        """Initialize vector database for each memory tier"""
        for tier in MemoryTier:
            self.tier_dbs[tier] = VectorDB(self.agent, cache=True)
            PrintStyle(font_color="cyan").print(f"Initialized {tier.value} memory tier")
    
    def _load_metadata_index(self):
        """Load memory metadata from disk"""
        index_path = os.path.join(self.memory_dir, "metadata_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    data = json.load(f)
                    for mem_id, meta_dict in data.items():
                        self.metadata_index[mem_id] = MemoryMetadata.from_dict(meta_dict)
                PrintStyle(font_color="green").print(
                    f"Loaded {len(self.metadata_index)} memory entries"
                )
            except Exception as e:
                PrintStyle(font_color="yellow").print(
                    f"Failed to load metadata index: {e}"
                )
    
    def _save_metadata_index(self):
        """Save memory metadata to disk"""
        index_path = os.path.join(self.memory_dir, "metadata_index.json")
        try:
            data = {
                mem_id: meta.to_dict() 
                for mem_id, meta in self.metadata_index.items()
            }
            with open(index_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Failed to save metadata index: {e}"
            )
    
    def _load_stats(self):
        """Load memory statistics"""
        stats_path = os.path.join(self.memory_dir, "stats.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    self.stats = json.load(f)
            except Exception:
                pass
    
    def _save_stats(self):
        """Save memory statistics"""
        stats_path = os.path.join(self.memory_dir, "stats.json")
        try:
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            PrintStyle(font_color="yellow").print(
                f"Failed to save stats: {e}"
            )
    
    async def store_memory(
        self,
        content: str,
        tier: MemoryTier,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        source_type: str = "agent",
        parent_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a memory in the specified tier.
        
        Args:
            content: Memory content
            tier: Memory tier to store in
            importance: Importance score (0.0-1.0)
            tags: Category tags
            keywords: Search keywords
            source_type: Source of the memory
            parent_ids: Parent memory IDs for hierarchy
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        import uuid
        
        # Generate unique ID
        memory_id = str(uuid.uuid4())[:8]
        
        # Create metadata
        now = datetime.now(timezone.utc)
        mem_metadata = MemoryMetadata(
            tier=tier,
            importance=importance,
            created_at=now,
            last_accessed=now,
            tags=tags or [],
            keywords=keywords or [],
            parent_ids=parent_ids or [],
            context_id=self.agent.context.id if hasattr(self.agent, 'context') else "",
            agent_name=self.agent.agent_name if hasattr(self.agent, 'agent_name') else "",
            source_type=source_type,
        )
        
        # Create document with enhanced metadata
        doc_metadata = {
            "id": memory_id,
            "tier": tier.value,
            "importance": importance,
            "created_at": now.isoformat(),
            "tags": ",".join(tags or []),
            "keywords": ",".join(keywords or []),
            "source_type": source_type,
        }
        if metadata:
            doc_metadata.update(metadata)
        
        doc = Document(
            page_content=content,
            metadata=doc_metadata
        )
        
        # Store in vector DB
        await self.tier_dbs[tier].insert_documents([doc])
        
        # Update metadata index
        self.metadata_index[memory_id] = mem_metadata
        self._save_metadata_index()
        
        # Update statistics
        self.stats["total_memories"] += 1
        self._save_stats()
        
        # Check capacity and trigger consolidation if needed
        await self._check_tier_capacity(tier)
        
        PrintStyle(font_color="green").print(
            f"Stored memory {memory_id} in {tier.value} tier"
        )
        
        return memory_id
    
    async def retrieve_memory(
        self,
        query: str,
        tier: Optional[MemoryTier] = None,
        limit: int = 5,
        importance_threshold: float = 0.3,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Tuple[Document, float, MemoryMetadata]]:
        """
        Retrieve memories using hybrid search.
        
        Args:
            query: Search query
            tier: Specific tier to search (None = all tiers)
            limit: Maximum number of results
            importance_threshold: Minimum importance score
            time_range: Optional time range filter
            tags: Optional tag filter
            
        Returns:
            List of (Document, similarity_score, metadata) tuples
        """
        results = []
        
        # Determine which tiers to search
        search_tiers = [tier] if tier else list(MemoryTier)
        
        for search_tier in search_tiers:
            # Semantic search in vector DB
            tier_results = await self.tier_dbs[search_tier].search_by_similarity_threshold(
                query=query,
                limit=limit * 2,  # Get more candidates
                threshold=0.6,  # Lower threshold, we'll filter by importance
            )
            
            # Enhance with metadata and apply filters
            for doc, score in tier_results:
                memory_id = doc.metadata.get("id", "")
                if memory_id not in self.metadata_index:
                    continue
                
                mem_metadata = self.metadata_index[memory_id]
                
                # Apply importance filter
                if mem_metadata.importance < importance_threshold:
                    continue
                
                # Apply time range filter
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= mem_metadata.created_at <= end_time):
                        continue
                
                # Apply tag filter
                if tags and not any(tag in mem_metadata.tags for tag in tags):
                    continue
                
                # Update access statistics
                mem_metadata.access_count += 1
                mem_metadata.last_accessed = datetime.now(timezone.utc)
                
                # Calculate combined score
                recency_weight = 0.2
                importance_weight = 0.3
                similarity_weight = 0.5
                
                age_days = (datetime.now(timezone.utc) - mem_metadata.created_at).days
                recency_score = max(0, 1.0 - (age_days / 30))  # Decay over 30 days
                
                combined_score = (
                    similarity_weight * score +
                    importance_weight * mem_metadata.importance +
                    recency_weight * recency_score
                )
                
                results.append((doc, combined_score, mem_metadata))
        
        # Sort by combined score and limit
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:limit]
        
        # Save updated metadata
        self._save_metadata_index()
        
        return results
    
    async def consolidate_memories(self, tier: MemoryTier):
        """
        Consolidate memories in a tier by merging similar ones.
        
        Args:
            tier: Tier to consolidate
        """
        PrintStyle(font_color="cyan").print(
            f"Starting memory consolidation for {tier.value} tier"
        )
        
        # Get all memories in this tier
        tier_memories = [
            (mem_id, meta) 
            for mem_id, meta in self.metadata_index.items()
            if meta.tier == tier
        ]
        
        # Filter by consolidation criteria
        consolidation_candidates = [
            (mem_id, meta)
            for mem_id, meta in tier_memories
            if (
                meta.importance >= self.consolidation_rules.min_importance and
                meta.access_count >= self.consolidation_rules.min_access_count
            )
        ]
        
        PrintStyle(font_color="yellow").print(
            f"Found {len(consolidation_candidates)} consolidation candidates"
        )
        
        # Cluster similar memories
        # TODO: Implement actual clustering algorithm
        # For now, we'll just mark high-value memories for promotion
        
        for mem_id, meta in consolidation_candidates:
            # Calculate consolidation score
            age_days = (datetime.now(timezone.utc) - meta.created_at).days
            if age_days >= self.consolidation_rules.age_threshold_days:
                # Promote to higher tier if appropriate
                if tier == MemoryTier.WORKING and meta.importance >= 0.7:
                    await self._promote_memory(mem_id, MemoryTier.EPISODIC)
                elif tier == MemoryTier.EPISODIC and meta.access_count >= 10:
                    # High-access episodic memories become semantic
                    await self._promote_memory(mem_id, MemoryTier.SEMANTIC)
        
        self.stats["consolidations"] += 1
        self._save_stats()
    
    async def _promote_memory(self, memory_id: str, target_tier: MemoryTier):
        """
        Promote a memory to a higher tier.
        
        Args:
            memory_id: Memory to promote
            target_tier: Target tier
        """
        if memory_id not in self.metadata_index:
            return
        
        meta = self.metadata_index[memory_id]
        old_tier = meta.tier
        
        # Update tier
        meta.tier = target_tier
        
        # TODO: Move document between vector DBs
        # For now, just update metadata
        
        PrintStyle(font_color="green").print(
            f"Promoted memory {memory_id} from {old_tier.value} to {target_tier.value}"
        )
        
        self.stats["promotions"] += 1
        self._save_metadata_index()
        self._save_stats()
    
    async def _check_tier_capacity(self, tier: MemoryTier):
        """
        Check if tier capacity is exceeded and prune if necessary.
        
        Args:
            tier: Tier to check
        """
        tier_memories = [
            (mem_id, meta)
            for mem_id, meta in self.metadata_index.items()
            if meta.tier == tier
        ]
        
        capacity = self.TIER_CAPACITIES[tier]
        if len(tier_memories) > capacity:
            await self._prune_tier(tier, capacity)
    
    async def _prune_tier(self, tier: MemoryTier, target_size: int):
        """
        Prune low-value memories from a tier.
        
        Args:
            tier: Tier to prune
            target_size: Target number of memories
        """
        tier_memories = [
            (mem_id, meta)
            for mem_id, meta in self.metadata_index.items()
            if meta.tier == tier
        ]
        
        # Calculate retention score
        now = datetime.now(timezone.utc)
        scored_memories = []
        
        for mem_id, meta in tier_memories:
            age_days = (now - meta.created_at).days
            recency_score = max(0, 1.0 - (age_days / 30))
            
            retention_score = (
                0.4 * meta.importance +
                0.3 * min(meta.access_count / 10, 1.0) +
                0.3 * recency_score
            )
            
            scored_memories.append((mem_id, retention_score))
        
        # Sort by retention score
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top N, archive or delete the rest
        to_prune = scored_memories[target_size:]
        
        for mem_id, score in to_prune:
            # Archive low-value memories
            # TODO: Implement actual archival
            del self.metadata_index[mem_id]
            self.stats["prunings"] += 1
        
        PrintStyle(font_color="yellow").print(
            f"Pruned {len(to_prune)} memories from {tier.value} tier"
        )
        
        self._save_metadata_index()
        self._save_stats()
    
    async def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        summary = {
            "total_memories": len(self.metadata_index),
            "by_tier": {},
            "by_importance": {},
            "statistics": self.stats,
        }
        
        # Count by tier
        for tier in MemoryTier:
            count = sum(
                1 for meta in self.metadata_index.values()
                if meta.tier == tier
            )
            summary["by_tier"][tier.value] = count
        
        # Count by importance
        importance_ranges = [
            ("critical", 0.9, 1.0),
            ("high", 0.7, 0.9),
            ("medium", 0.4, 0.7),
            ("low", 0.0, 0.4),
        ]
        
        for label, min_imp, max_imp in importance_ranges:
            count = sum(
                1 for meta in self.metadata_index.values()
                if min_imp <= meta.importance < max_imp
            )
            summary["by_importance"][label] = count
        
        return summary


# Global instance for easy access
_hierarchical_memory_instance: Optional[HierarchicalMemory] = None


def get_hierarchical_memory(agent) -> HierarchicalMemory:
    """Get or create the global hierarchical memory instance"""
    global _hierarchical_memory_instance
    if _hierarchical_memory_instance is None:
        _hierarchical_memory_instance = HierarchicalMemory(agent)
    return _hierarchical_memory_instance
