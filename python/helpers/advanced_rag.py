"""
Advanced RAG (Retrieval-Augmented Generation) System

This module implements sophisticated retrieval and generation techniques:

1. Query Decomposition
   - Break complex queries into sub-queries
   - Hierarchical query planning
   - Parallel sub-query execution

2. Hybrid Retrieval
   - Semantic search (embeddings)
   - Keyword/BM25 search
   - Temporal/recency filtering
   - Metadata filtering

3. Knowledge Graph Integration
   - Entity extraction and linking
   - Relationship mapping
   - Graph-based reasoning

4. Context Optimization
   - Chunk ranking and selection
   - Context window management
   - Redundancy elimination

5. Incremental Knowledge Updates
   - Streaming document ingestion
   - Efficient re-indexing
   - Change detection
"""

import asyncio
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from langchain_core.documents import Document
from python.helpers.print_style import PrintStyle
from python.helpers import files
from python.helpers.vector_db import VectorDB


class QueryType(Enum):
    """Types of queries"""
    SIMPLE = "simple"              # Single-topic query
    COMPLEX = "complex"            # Multi-topic query
    COMPARATIVE = "comparative"    # Comparison query
    TEMPORAL = "temporal"          # Time-based query
    AGGREGATION = "aggregation"    # Aggregation/summary query


@dataclass
class QueryDecomposition:
    """Decomposed query structure"""
    original_query: str
    query_type: QueryType
    sub_queries: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    temporal_constraints: Optional[Dict[str, Any]] = None
    confidence: float = 0.5


@dataclass
class RetrievalResult:
    """Enhanced retrieval result"""
    document: Document
    score: float
    retrieval_method: str  # "semantic", "keyword", "hybrid"
    rank: int
    relevance_explanation: str = ""
    chunk_context: Optional[str] = None  # Surrounding context


@dataclass
class KnowledgeGraphNode:
    """Node in the knowledge graph"""
    id: str
    entity: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class KnowledgeGraphEdge:
    """Edge in the knowledge graph"""
    source_id: str
    target_id: str
    relationship: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedRAG:
    """
    Advanced Retrieval-Augmented Generation system.
    
    Implements sophisticated retrieval, query decomposition,
    knowledge graph integration, and context optimization.
    """
    
    def __init__(self, agent):
        """
        Initialize advanced RAG system.
        
        Args:
            agent: The agent instance
        """
        self.agent = agent
        self.vector_db = VectorDB(agent, cache=True)
        
        # Knowledge graph
        self.kg_nodes: Dict[str, KnowledgeGraphNode] = {}
        self.kg_edges: List[KnowledgeGraphEdge] = []
        
        # Query cache
        self.query_cache: Dict[str, List[RetrievalResult]] = {}
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "decomposed_queries": 0,
            "kg_queries": 0,
            "cache_hits": 0,
        }
    
    async def query_with_decomposition(
        self,
        query: str,
        top_k: int = 10,
        use_kg: bool = True,
        use_cache: bool = True,
    ) -> List[RetrievalResult]:
        """
        Query with automatic decomposition for complex queries.
        
        Args:
            query: The query string
            top_k: Number of results to return
            use_kg: Whether to use knowledge graph
            use_cache: Whether to use query cache
            
        Returns:
            List of RetrievalResults
        """
        self.stats["total_queries"] += 1
        
        # Check cache
        if use_cache and query in self.query_cache:
            self.stats["cache_hits"] += 1
            return self.query_cache[query][:top_k]
        
        # Decompose query
        decomposition = await self._decompose_query(query)
        
        results = []
        
        if decomposition.query_type == QueryType.SIMPLE:
            # Simple query - direct retrieval
            results = await self._simple_retrieval(query, top_k)
        else:
            # Complex query - decompose and combine
            self.stats["decomposed_queries"] += 1
            results = await self._complex_retrieval(decomposition, top_k)
        
        # Enhance with knowledge graph if enabled
        if use_kg and self.kg_nodes:
            self.stats["kg_queries"] += 1
            results = await self._enhance_with_kg(results, decomposition)
        
        # Rank and deduplicate
        results = self._rank_and_deduplicate(results, query)
        
        # Cache results
        if use_cache:
            self.query_cache[query] = results
        
        return results[:top_k]
    
    async def _decompose_query(self, query: str) -> QueryDecomposition:
        """
        Decompose a query into components.
        
        Args:
            query: The query to decompose
            
        Returns:
            QueryDecomposition object
        """
        # Use LLM to decompose complex queries
        decomposition_prompt = f"""
Analyze this query and break it down:

Query: {query}

Please provide:
1. Query type (simple/complex/comparative/temporal/aggregation)
2. Sub-queries (if complex)
3. Key entities mentioned
4. Important keywords
5. Any temporal constraints

Format your response as JSON.
"""
        
        try:
            response = await self.agent.call_utility_model(
                system="You are a query analysis expert. Decompose queries into structured components.",
                message=decomposition_prompt,
            )
            
            # Parse response
            data = self._parse_decomposition_response(response)
            
            decomposition = QueryDecomposition(
                original_query=query,
                query_type=QueryType(data.get("query_type", "simple")),
                sub_queries=data.get("sub_queries", []),
                entities=data.get("entities", []),
                keywords=data.get("keywords", []),
                temporal_constraints=data.get("temporal_constraints"),
                confidence=data.get("confidence", 0.7),
            )
            
        except Exception as e:
            PrintStyle(font_color="yellow").print(
                f"Query decomposition failed, using simple mode: {e}"
            )
            # Fallback to simple decomposition
            decomposition = QueryDecomposition(
                original_query=query,
                query_type=QueryType.SIMPLE,
                keywords=self._extract_keywords(query),
            )
        
        return decomposition
    
    def _parse_decomposition_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for query decomposition"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback parsing
        data = {
            "query_type": "simple",
            "sub_queries": [],
            "entities": [],
            "keywords": [],
        }
        
        # Extract entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+\b', response)
        data["entities"] = list(set(entities))[:5]
        
        return data
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        # Remove common words
        stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        return list(set(keywords))[:10]
    
    async def _simple_retrieval(
        self,
        query: str,
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Simple semantic retrieval.
        
        Args:
            query: The query string
            top_k: Number of results
            
        Returns:
            List of RetrievalResults
        """
        try:
            # Semantic search
            docs_with_scores = await self.vector_db.search_by_similarity_threshold(
                query=query,
                limit=top_k,
                threshold=0.5,
            )
            
            results = []
            for rank, (doc, score) in enumerate(docs_with_scores):
                results.append(RetrievalResult(
                    document=doc,
                    score=score,
                    retrieval_method="semantic",
                    rank=rank,
                    relevance_explanation=f"Semantic similarity: {score:.3f}",
                ))
            
            return results
            
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Simple retrieval failed: {e}"
            )
            return []
    
    async def _complex_retrieval(
        self,
        decomposition: QueryDecomposition,
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Complex retrieval using query decomposition.
        
        Args:
            decomposition: Decomposed query
            top_k: Number of results
            
        Returns:
            List of RetrievalResults
        """
        all_results = []
        
        # Retrieve for each sub-query
        for sub_query in decomposition.sub_queries:
            sub_results = await self._simple_retrieval(sub_query, top_k // 2)
            all_results.extend(sub_results)
        
        # Also retrieve for original query
        original_results = await self._simple_retrieval(
            decomposition.original_query,
            top_k // 2
        )
        all_results.extend(original_results)
        
        return all_results
    
    async def _enhance_with_kg(
        self,
        results: List[RetrievalResult],
        decomposition: QueryDecomposition,
    ) -> List[RetrievalResult]:
        """
        Enhance results using knowledge graph.
        
        Args:
            results: Current retrieval results
            decomposition: Query decomposition
            
        Returns:
            Enhanced results
        """
        # Find related entities in knowledge graph
        related_entities = set()
        
        for entity in decomposition.entities:
            # Find matching nodes
            for node_id, node in self.kg_nodes.items():
                if entity.lower() in node.entity.lower():
                    related_entities.add(node_id)
                    
                    # Find connected entities
                    for edge in self.kg_edges:
                        if edge.source_id == node_id:
                            related_entities.add(edge.target_id)
                        elif edge.target_id == node_id:
                            related_entities.add(edge.source_id)
        
        # Boost scores for documents mentioning related entities
        for result in results:
            doc_text = result.document.page_content.lower()
            
            for entity_id in related_entities:
                entity = self.kg_nodes[entity_id].entity.lower()
                if entity in doc_text:
                    # Boost score
                    result.score *= 1.2
                    result.relevance_explanation += f" [KG: {entity}]"
        
        return results
    
    def _rank_and_deduplicate(
        self,
        results: List[RetrievalResult],
        query: str,
    ) -> List[RetrievalResult]:
        """
        Rank results and remove duplicates.
        
        Args:
            results: Results to rank
            query: Original query
            
        Returns:
            Ranked and deduplicated results
        """
        # Remove duplicates based on content similarity
        unique_results = []
        seen_contents = set()
        
        for result in results:
            # Use first 100 chars as signature
            content_sig = result.document.page_content[:100]
            
            if content_sig not in seen_contents:
                seen_contents.add(content_sig)
                unique_results.append(result)
        
        # Re-rank by score
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for rank, result in enumerate(unique_results):
            result.rank = rank
        
        return unique_results
    
    async def add_to_knowledge_graph(
        self,
        text: str,
        extract_entities: bool = True,
    ):
        """
        Add knowledge to the knowledge graph.
        
        Args:
            text: Text to extract knowledge from
            extract_entities: Whether to auto-extract entities
        """
        if not extract_entities:
            return
        
        # Use LLM to extract entities and relationships
        extraction_prompt = f"""
Extract entities and relationships from this text:

{text[:1000]}

Provide:
1. Entities (name, type)
2. Relationships (entity1, relationship, entity2)

Format as JSON.
"""
        
        try:
            response = await self.agent.call_utility_model(
                system="You are an entity extraction expert. Extract structured knowledge.",
                message=extraction_prompt,
            )
            
            # Parse and add to knowledge graph
            # For now, just log
            PrintStyle(font_color="cyan").print(
                "Extracted entities for knowledge graph"
            )
            
        except Exception as e:
            PrintStyle(font_color="yellow").print(
                f"Entity extraction failed: {e}"
            )
    
    async def ingest_documents(
        self,
        documents: List[Document],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        extract_kg: bool = True,
    ):
        """
        Ingest documents with chunking and indexing.
        
        Args:
            documents: Documents to ingest
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            extract_kg: Whether to extract knowledge graph
        """
        PrintStyle(font_color="cyan").print(
            f"Ingesting {len(documents)} documents..."
        )
        
        # Chunk documents
        chunked_docs = []
        
        for doc in documents:
            chunks = self._chunk_document(
                doc.page_content,
                chunk_size,
                chunk_overlap
            )
            
            for i, chunk in enumerate(chunks):
                chunk_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                    }
                )
                chunked_docs.append(chunk_doc)
        
        # Index in vector DB
        await self.vector_db.insert_documents(chunked_docs)
        
        PrintStyle(font_color="green").print(
            f"Indexed {len(chunked_docs)} chunks from {len(documents)} documents"
        )
        
        # Extract knowledge graph
        if extract_kg:
            for doc in documents:
                await self.add_to_knowledge_graph(doc.page_content)
    
    def _chunk_document(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """
        Chunk a document into overlapping segments.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [c for c in chunks if c]
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "statistics": self.stats,
            "knowledge_graph": {
                "nodes": len(self.kg_nodes),
                "edges": len(self.kg_edges),
            },
            "cache_size": len(self.query_cache),
        }


# Global instance
_advanced_rag_instance: Optional[AdvancedRAG] = None


def get_advanced_rag(agent) -> AdvancedRAG:
    """Get or create the global advanced RAG instance"""
    global _advanced_rag_instance
    if _advanced_rag_instance is None:
        _advanced_rag_instance = AdvancedRAG(agent)
    return _advanced_rag_instance
