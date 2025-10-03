"""
Enhanced Memory System for Agent Zero
Provides improved indexing, retrieval, and memory management

Features:
- Semantic similarity search with advanced filtering
- Temporal weighting (recent memories score higher)
- Contextual memory grouping
- Memory importance scoring
- Automatic memory consolidation
- Memory statistics and analytics
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from langchain_core.documents import Document

from python.helpers.memory import Memory as BaseMemory


class MemoryImportance(Enum):
    """Memory importance levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


@dataclass
class EnhancedMemoryMetadata:
    """Enhanced metadata for memory entries"""
    importance: MemoryImportance = MemoryImportance.MEDIUM
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    context: str = ""
    related_memory_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """
        Serialize the metadata into a JSON-serializable dictionary.
        
        Returns:
            dict: Mapping with keys:
                - "importance": integer value of the MemoryImportance enum.
                - "access_count": integer access counter.
                - "last_accessed": ISO 8601 timestamp string or `None`.
                - "created_at": ISO 8601 timestamp string or `None`.
                - "tags": list of tag strings.
                - "context": context string.
                - "related_memory_ids": list of related memory ID strings.
        """
        return {
            "importance": self.importance.value,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": self.tags,
            "context": self.context,
            "related_memory_ids": self.related_memory_ids
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EnhancedMemoryMetadata':
        """
        Create an EnhancedMemoryMetadata instance from a dictionary produced by `to_dict`.
        
        Parameters:
            data (Dict): Dictionary with keys matching EnhancedMemoryMetadata fields. Expected keys include
                "importance" (int or enum value), "access_count" (int), "last_accessed" (ISO 8601 string or None),
                "created_at" (ISO 8601 string), "tags" (list of str), "context" (str), and "related_memory_ids" (list of str).
        
        Returns:
            EnhancedMemoryMetadata: The reconstructed metadata object with enums and datetimes parsed from the input.
        """
        return EnhancedMemoryMetadata(
            importance=MemoryImportance(data.get("importance", 3)),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            tags=data.get("tags", []),
            context=data.get("context", ""),
            related_memory_ids=data.get("related_memory_ids", [])
        )


class EnhancedMemory:
    """Enhanced memory system with improved retrieval and management"""
    
    def __init__(self, base_memory: BaseMemory):
        """
        Initialize the EnhancedMemory wrapper using a BaseMemory backend and load persisted enhanced metadata.
        
        Parameters:
            base_memory (BaseMemory): The underlying memory backend whose agent, database, and memory_subdir will be used by this enhanced memory instance.
        
        Description:
            Stores a reference to the provided base_memory, exposes its agent, db, and memory_subdir on the instance, initializes the internal enhanced metadata store, and loads any existing metadata from persistent storage.
        """
        self.base_memory = base_memory
        self.agent = base_memory.agent
        self.db = base_memory.db
        self.memory_subdir = base_memory.memory_subdir
        
        # Enhanced features
        self._memory_metadata: Dict[str, EnhancedMemoryMetadata] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """
        Load enhanced memory metadata from memory/{memory_subdir}/enhanced_metadata.json into the instance metadata store.
        
        If the metadata file exists, parse its JSON contents and populate self._memory_metadata with EnhancedMemoryMetadata instances keyed by document ID.
        """
        # Load from storage if exists
        from python.helpers import files
        metadata_file = files.get_abs_path(f"memory/{self.memory_subdir}/enhanced_metadata.json")
        
        if files.exists(metadata_file):
            import json
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                self._memory_metadata = {
                    k: EnhancedMemoryMetadata.from_dict(v)
                    for k, v in data.items()
                }
    
    def _save_metadata(self):
        """
        Persist enhanced memory metadata to disk as JSON.
        
        Writes the instance's internal `_memory_metadata` mapping to
        memory/{memory_subdir}/enhanced_metadata.json, serializing each
        EnhancedMemoryMetadata via its `to_dict()` representation.
        """
        from python.helpers import files
        import json
        
        metadata_file = files.get_abs_path(f"memory/{self.memory_subdir}/enhanced_metadata.json")
        data = {
            k: v.to_dict()
            for k, v in self._memory_metadata.items()
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_temporal_weight(self, created_at: datetime, decay_days: int = 30) -> float:
        """
        Compute a temporal relevance weight so more recent memories score higher.
        
        Parameters:
            created_at (datetime): Timestamp when the memory was created.
            decay_days (int): Characteristic decay period in days; larger values slow the decay (default 30).
        
        Returns:
            float: A weight between 0.1 and 1.0 representing temporal relevance (`1.0` for very recent, approaching `0.1` for old entries).
        """
        now = datetime.now()
        age_days = (now - created_at).days
        
        # Exponential decay
        weight = np.exp(-age_days / decay_days)
        return max(0.1, weight)  # Minimum weight 0.1
    
    def calculate_importance_weight(self, importance: MemoryImportance) -> float:
        """
        Map a MemoryImportance level to a normalized weight between 0.2 and 1.0.
        
        The importance's numeric value is divided by 5.0 so that MemoryImportance.CRITICAL maps to 1.0 and MemoryImportance.TRIVIAL maps to 0.2.
        
        Returns:
            float: Weight in the range [0.2, 1.0] corresponding to the provided importance.
        """
        return importance.value / 5.0
    
    def calculate_access_weight(self, access_count: int, max_access: int = 100) -> float:
        """
        Compute a normalized weight that reflects how frequently a memory has been accessed.
        
        Parameters:
            access_count (int): Number of times the memory has been accessed.
            max_access (int): Access count at which the weight saturates to its maximum.
        
        Returns:
            float: A weight greater than 0 and at most 1.0 that increases with access_count and is capped at 1.0.
        """
        return min(1.0, (access_count + 1) / max_access)
    
    async def search_enhanced(
        self,
        query: str,
        area: BaseMemory.Area = BaseMemory.Area.MAIN,
        threshold: float = 0.1,
        max_results: int = 5,
        use_temporal_weighting: bool = True,
        use_importance_weighting: bool = True,
        use_access_weighting: bool = False,
        filter_tags: Optional[List[str]] = None,
        min_importance: Optional[MemoryImportance] = None
    ) -> List[Tuple[Document, float]]:
        """
        Enhanced semantic search with multiple weighting strategies
        
        Args:
            query: Search query
            area: Memory area to search
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
            use_temporal_weighting: Weight by recency
            use_importance_weighting: Weight by importance
            use_access_weighting: Weight by access frequency
            filter_tags: Only return memories with these tags
            min_importance: Minimum importance level
        
        Returns:
            List of (Document, weighted_score) tuples
        """
        # Get base search results
        results = await self.base_memory.search_similarity_threshold(
            area=area,
            query=query,
            threshold=threshold,
            limit=max_results * 2  # Get more to filter
        )
        
        enhanced_results = []
        
        for doc, base_score in results:
            doc_id = doc.metadata.get("id", "")
            metadata = self._memory_metadata.get(doc_id)
            
            if not metadata:
                # Create default metadata
                metadata = EnhancedMemoryMetadata()
                self._memory_metadata[doc_id] = metadata
            
            # Apply filters
            if filter_tags and not any(tag in metadata.tags for tag in filter_tags):
                continue
            
            if min_importance and metadata.importance.value < min_importance.value:
                continue
            
            # Calculate composite score
            score = base_score
            
            if use_temporal_weighting:
                temporal_weight = self.calculate_temporal_weight(metadata.created_at)
                score *= temporal_weight
            
            if use_importance_weighting:
                importance_weight = self.calculate_importance_weight(metadata.importance)
                score *= importance_weight
            
            if use_access_weighting:
                access_weight = self.calculate_access_weight(metadata.access_count)
                score *= access_weight
            
            # Update access metadata
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()
            
            enhanced_results.append((doc, score))
        
        # Sort by weighted score
        enhanced_results.sort(key=lambda x: x[1], reverse=True)
        
        # Save updated metadata
        self._save_metadata()
        
        return enhanced_results[:max_results]
    
    async def add_memory(
        self,
        text: str,
        area: BaseMemory.Area = BaseMemory.Area.MAIN,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: Optional[List[str]] = None,
        context: str = "",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a new memory entry to the base memory and record enhanced metadata for it.
        
        Parameters:
            text (str): The content to store as the memory.
            area (BaseMemory.Area): The memory area/namespace to store the document in.
            importance (MemoryImportance): The significance level assigned to the memory.
            tags (Optional[List[str]]): Tags to attach to the memory for later filtering.
            context (str): Optional contextual note or short description for the memory.
            metadata (Optional[Dict]): Additional document metadata to persist with the stored document; a timestamp and area will be added automatically.
        
        Returns:
            str: The ID of the created document if successful, or an empty string on failure.
        """
        # Create document
        doc_metadata = metadata or {}
        doc_metadata["timestamp"] = datetime.now().isoformat()
        doc_metadata["area"] = area.value
        
        # Add to base memory
        doc_ids = await self.base_memory.add_documents(
            area=area,
            documents=[Document(page_content=text, metadata=doc_metadata)]
        )
        
        if doc_ids:
            doc_id = doc_ids[0]
            
            # Create enhanced metadata
            enhanced_meta = EnhancedMemoryMetadata(
                importance=importance,
                tags=tags or [],
                context=context,
                created_at=datetime.now()
            )
            
            self._memory_metadata[doc_id] = enhanced_meta
            self._save_metadata()
            
            return doc_id
        
        return ""
    
    async def consolidate_memories(
        self,
        area: BaseMemory.Area = BaseMemory.Area.MAIN,
        min_similarity: float = 0.85,
        max_age_days: int = 7
    ) -> int:
        """
        Attempt to consolidate similar memories created within the past `max_age_days` to reduce redundancy.
        
        Compares recent memories in the specified `area` using a pairwise similarity check governed by `min_similarity` and merges or marks redundant items when detected. The current implementation is a scaffold: it iterates recent memory pairs but does not perform actual similarity comparison or merging, and therefore will always return 0 until consolidation logic is implemented.
        
        Parameters:
            area (BaseMemory.Area): Memory area to consider for consolidation.
            min_similarity (float): Similarity threshold in [0, 1] used to decide whether two memories are similar enough to consolidate.
            max_age_days (int): Only memories created within this many days from now are considered.
        
        Returns:
            int: Number of memories consolidated (currently always 0 until consolidation is implemented).
        """
        # Get recent memories
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        recent_memories = [
            (doc_id, meta) for doc_id, meta in self._memory_metadata.items()
            if meta.created_at >= cutoff_date
        ]
        
        if len(recent_memories) < 2:
            return 0
        
        consolidated = 0
        
        # Compare each pair (this is O(n²), could be optimized)
        for i, (id1, meta1) in enumerate(recent_memories):
            for id2, meta2 in recent_memories[i+1:]:
                # Get documents
                docs1 = self.db.get_by_ids([id1])
                docs2 = self.db.get_by_ids([id2])
                
                if not docs1 or not docs2:
                    continue
                
                # Check similarity (simplified - in production use embeddings)
                # For now, mark for potential consolidation
                # TODO: Implement actual consolidation logic
                pass
        
        self._save_metadata()
        return consolidated
    
    def get_memory_statistics(self) -> Dict:
        """
        Return aggregated statistics about the stored enhanced memories.
        
        Provides counts and summaries useful for analytics and monitoring:
        - total_memories: total number of tracked memories.
        - importance_distribution: mapping of importance level name to count.
        - total_accesses: sum of all memory access counts.
        - average_accesses: mean access count per memory (0 if none).
        - age_distribution: counts of memories created "today", "this_week" (<=7 days), "this_month" (<=30 days), and "older" (>30 days).
        - memory_subdir: the subdirectory name where memory data is stored.
        
        Returns:
            Dict: A dictionary containing the statistics described above.
        """
        total_memories = len(self._memory_metadata)
        
        importance_counts = {
            imp: sum(1 for m in self._memory_metadata.values() if m.importance == imp)
            for imp in MemoryImportance
        }
        
        total_accesses = sum(m.access_count for m in self._memory_metadata.values())
        avg_accesses = total_accesses / total_memories if total_memories > 0 else 0
        
        # Calculate age distribution
        now = datetime.now()
        age_ranges = {
            "today": 0,
            "this_week": 0,
            "this_month": 0,
            "older": 0
        }
        
        for meta in self._memory_metadata.values():
            age = (now - meta.created_at).days
            if age == 0:
                age_ranges["today"] += 1
            elif age <= 7:
                age_ranges["this_week"] += 1
            elif age <= 30:
                age_ranges["this_month"] += 1
            else:
                age_ranges["older"] += 1
        
        return {
            "total_memories": total_memories,
            "importance_distribution": {k.name: v for k, v in importance_counts.items()},
            "total_accesses": total_accesses,
            "average_accesses": avg_accesses,
            "age_distribution": age_ranges,
            "memory_subdir": self.memory_subdir
        }
    
    def tag_memory(self, doc_id: str, tags: List[str]):
        """
        Append tags to an existing memory's tag list.
        
        If the given memory ID does not exist, the function does nothing.
        
        Parameters:
            doc_id (str): The identifier of the memory to tag.
            tags (List[str]): Tags to append to the memory's existing tags.
        """
        if doc_id in self._memory_metadata:
            self._memory_metadata[doc_id].tags.extend(tags)
            self._save_metadata()
    
    def set_importance(self, doc_id: str, importance: MemoryImportance):
        """
        Set the importance level for a stored memory.
        
        Parameters:
            doc_id (str): ID of the memory to update.
            importance (MemoryImportance): New importance level to assign to the memory.
        """
        if doc_id in self._memory_metadata:
            self._memory_metadata[doc_id].importance = importance
            self._save_metadata()
    
    def get_memories_by_tag(self, tags: List[str]) -> List[str]:
        """
        Retrieve IDs of memories that have any of the specified tags.
        
        Parameters:
        	tags (List[str]): Tags to match against each memory's tag list. A memory is selected if it contains at least one of these tags.
        
        Returns:
        	List[str]: List of memory IDs whose tags intersect with the provided tags (empty if no matches).
        """
        return [
            doc_id for doc_id, meta in self._memory_metadata.items()
            if any(tag in meta.tags for tag in tags)
        ]
    
    def get_related_memories(self, doc_id: str, max_depth: int = 2) -> List[str]:
        """
        Retrieve memory IDs related to a given memory by traversing related links up to a specified depth.
        
        Parameters:
            doc_id (str): The starting memory ID to find related memories for.
            max_depth (int): Maximum number of hops to follow through related_memory_ids (default 2).
        
        Returns:
            List of related memory IDs reachable within max_depth hops; returns an empty list if the starting ID is not tracked.
        """
        if doc_id not in self._memory_metadata:
            return []
        
        related = set()
        to_check = [doc_id]
        depth = 0
        
        while to_check and depth < max_depth:
            current = to_check.pop(0)
            if current in self._memory_metadata:
                new_related = self._memory_metadata[current].related_memory_ids
                related.update(new_related)
                to_check.extend([r for r in new_related if r not in related])
            depth += 1
        
        return list(related)
