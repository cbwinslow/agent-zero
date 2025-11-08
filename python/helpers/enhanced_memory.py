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
        self.base_memory = base_memory
        self.agent = base_memory.agent
        self.db = base_memory.db
        self.memory_subdir = base_memory.memory_subdir
        
        # Enhanced features
        self._memory_metadata: Dict[str, EnhancedMemoryMetadata] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load enhanced metadata for existing memories"""
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
        """Save enhanced metadata"""
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
        """Calculate temporal weight for memory (recent memories score higher)"""
        now = datetime.now()
        age_days = (now - created_at).days
        
        # Exponential decay
        weight = np.exp(-age_days / decay_days)
        return max(0.1, weight)  # Minimum weight 0.1
    
    def calculate_importance_weight(self, importance: MemoryImportance) -> float:
        """Calculate importance weight"""
        return importance.value / 5.0
    
    def calculate_access_weight(self, access_count: int, max_access: int = 100) -> float:
        """Calculate access frequency weight"""
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
        """Add memory with enhanced metadata"""
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
        Consolidate similar recent memories to reduce redundancy
        
        Returns number of memories consolidated
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
        """Get statistics about memory usage"""
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
        """Add tags to a memory"""
        if doc_id in self._memory_metadata:
            self._memory_metadata[doc_id].tags.extend(tags)
            self._save_metadata()
    
    def set_importance(self, doc_id: str, importance: MemoryImportance):
        """Set importance level for a memory"""
        if doc_id in self._memory_metadata:
            self._memory_metadata[doc_id].importance = importance
            self._save_metadata()
    
    def get_memories_by_tag(self, tags: List[str]) -> List[str]:
        """Get memory IDs by tags"""
        return [
            doc_id for doc_id, meta in self._memory_metadata.items()
            if any(tag in meta.tags for tag in tags)
        ]
    
    def get_related_memories(self, doc_id: str, max_depth: int = 2) -> List[str]:
        """Get related memories recursively"""
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
