"""
Advanced Features Control Tool

This tool allows the agent to query and control advanced capabilities:
- Hierarchical memory management
- Advanced reasoning strategies
- Tool optimization
- Advanced RAG queries

The agent can use this tool to:
1. Query memory across different tiers
2. Apply advanced reasoning to complex problems
3. Get tool recommendations
4. Perform sophisticated knowledge retrieval
5. Get statistics about system performance
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import json
from typing import Dict, Any


class AdvancedFeatures(Tool):
    
    async def execute(self, action: str = "status", **kwargs) -> Response:
        """
        Control and query advanced features.
        
        Args:
            action: Action to perform
                - status: Get status of all advanced features
                - memory_query: Query hierarchical memory
                - memory_summary: Get memory statistics
                - apply_reasoning: Apply advanced reasoning to a problem
                - tool_stats: Get tool optimization statistics
                - tool_recommend: Get tool recommendations
                - rag_query: Perform advanced RAG query
                - enable_feature: Enable a specific feature
                - disable_feature: Disable a specific feature
            **kwargs: Additional arguments based on action
            
        Returns:
            Response with results
        """
        
        try:
            if action == "status":
                return await self._get_status()
            
            elif action == "memory_query":
                return await self._memory_query(**kwargs)
            
            elif action == "memory_summary":
                return await self._memory_summary()
            
            elif action == "apply_reasoning":
                return await self._apply_reasoning(**kwargs)
            
            elif action == "tool_stats":
                return await self._get_tool_stats()
            
            elif action == "tool_recommend":
                return await self._get_tool_recommendations(**kwargs)
            
            elif action == "rag_query":
                return await self._rag_query(**kwargs)
            
            elif action == "enable_feature":
                return await self._enable_feature(**kwargs)
            
            elif action == "disable_feature":
                return await self._disable_feature(**kwargs)
            
            else:
                return Response(
                    message=f"Unknown action: {action}",
                    break_loop=False
                )
        
        except Exception as e:
            return Response(
                message=f"Error executing advanced features tool: {e}",
                break_loop=False
            )
    
    async def _get_status(self) -> Response:
        """Get status of all advanced features"""
        try:
            from python.extensions.advanced_capabilities import get_advanced_features_status
            status = get_advanced_features_status(self.agent)
            
            # Get more detailed status
            detailed_status = {
                "features_enabled": status,
                "systems_initialized": {},
            }
            
            # Check which systems are initialized
            detailed_status["systems_initialized"]["hierarchical_memory"] = \
                self.agent.get_data("hierarchical_memory") is not None
            detailed_status["systems_initialized"]["advanced_reasoning"] = \
                self.agent.get_data("advanced_reasoning") is not None
            detailed_status["systems_initialized"]["tool_optimizer"] = \
                self.agent.get_data("tool_optimizer") is not None
            detailed_status["systems_initialized"]["advanced_rag"] = \
                self.agent.get_data("advanced_rag") is not None
            
            result = json.dumps(detailed_status, indent=2)
            
            return Response(
                message=f"Advanced Features Status:\n{result}",
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Failed to get status: {e}",
                break_loop=False
            )
    
    async def _memory_query(
        self,
        query: str = "",
        tier: str = "",
        limit: int = 5,
        importance_threshold: float = 0.3,
        **kwargs
    ) -> Response:
        """Query hierarchical memory"""
        hierarchical_memory = self.agent.get_data("hierarchical_memory")
        
        if not hierarchical_memory:
            return Response(
                message="Hierarchical memory not initialized. Enable it first.",
                break_loop=False
            )
        
        if not query:
            return Response(
                message="Please provide a query string",
                break_loop=False
            )
        
        try:
            from python.helpers.memory_hierarchy import MemoryTier
            
            # Parse tier if provided
            search_tier = None
            if tier:
                try:
                    search_tier = MemoryTier(tier.lower())
                except ValueError:
                    return Response(
                        message=f"Invalid tier: {tier}. Valid: working, episodic, semantic, procedural",
                        break_loop=False
                    )
            
            # Query memory
            results = await hierarchical_memory.retrieve_memory(
                query=query,
                tier=search_tier,
                limit=limit,
                importance_threshold=importance_threshold,
            )
            
            if not results:
                return Response(
                    message="No memories found matching the query",
                    break_loop=False
                )
            
            # Format results
            formatted_results = []
            for doc, score, metadata in results:
                formatted_results.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "score": round(score, 3),
                    "tier": metadata.tier.value,
                    "importance": round(metadata.importance, 2),
                    "created": metadata.created_at.isoformat(),
                    "access_count": metadata.access_count,
                })
            
            result_text = json.dumps(formatted_results, indent=2)
            
            return Response(
                message=f"Found {len(results)} memories:\n{result_text}",
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Memory query failed: {e}",
                break_loop=False
            )
    
    async def _memory_summary(self) -> Response:
        """Get memory system statistics"""
        hierarchical_memory = self.agent.get_data("hierarchical_memory")
        
        if not hierarchical_memory:
            return Response(
                message="Hierarchical memory not initialized",
                break_loop=False
            )
        
        try:
            summary = await hierarchical_memory.get_memory_summary()
            result = json.dumps(summary, indent=2)
            
            return Response(
                message=f"Memory Summary:\n{result}",
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Failed to get memory summary: {e}",
                break_loop=False
            )
    
    async def _apply_reasoning(
        self,
        problem: str = "",
        strategy: str = "cot",
        **kwargs
    ) -> Response:
        """Apply advanced reasoning to a problem"""
        advanced_reasoning = self.agent.get_data("advanced_reasoning")
        
        if not advanced_reasoning:
            return Response(
                message="Advanced reasoning not initialized",
                break_loop=False
            )
        
        if not problem:
            return Response(
                message="Please provide a problem to reason about",
                break_loop=False
            )
        
        try:
            from python.helpers.advanced_reasoning import ReasoningStrategy
            
            if strategy.lower() == "cot":
                chain = await advanced_reasoning.apply_chain_of_thought(problem)
            elif strategy.lower() == "react":
                chain = await advanced_reasoning.apply_react_pattern(problem)
            else:
                return Response(
                    message=f"Unknown reasoning strategy: {strategy}. Use 'cot' or 'react'",
                    break_loop=False
                )
            
            # Format reasoning chain
            reasoning_text = f"Strategy: {chain.strategy.value}\n"
            reasoning_text += f"Confidence: {chain.overall_confidence:.2f}\n\n"
            reasoning_text += "Reasoning Steps:\n"
            
            for i, trace in enumerate(chain.traces[:5]):  # Limit to 5 steps
                reasoning_text += f"{i+1}. {trace.step_type.value}: {trace.content[:150]}...\n"
            
            reasoning_text += f"\nFinal Answer: {chain.final_answer[:300]}"
            
            return Response(
                message=reasoning_text,
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Reasoning failed: {e}",
                break_loop=False
            )
    
    async def _get_tool_stats(self) -> Response:
        """Get tool optimization statistics"""
        tool_optimizer = self.agent.get_data("tool_optimizer")
        
        if not tool_optimizer:
            return Response(
                message="Tool optimizer not initialized",
                break_loop=False
            )
        
        try:
            stats = tool_optimizer.get_optimization_stats()
            result = json.dumps(stats, indent=2)
            
            return Response(
                message=f"Tool Optimization Statistics:\n{result}",
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Failed to get tool stats: {e}",
                break_loop=False
            )
    
    async def _get_tool_recommendations(
        self,
        query: str = "",
        top_k: int = 5,
        **kwargs
    ) -> Response:
        """Get tool recommendations"""
        tool_optimizer = self.agent.get_data("tool_optimizer")
        
        if not tool_optimizer:
            return Response(
                message="Tool optimizer not initialized",
                break_loop=False
            )
        
        if not query:
            return Response(
                message="Please provide a query for tool recommendations",
                break_loop=False
            )
        
        try:
            recommendations = tool_optimizer.get_tool_recommendations(query, top_k)
            
            result = "Tool Recommendations:\n"
            for i, (tool_name, score) in enumerate(recommendations, 1):
                result += f"{i}. {tool_name} (score: {score:.3f})\n"
            
            return Response(
                message=result,
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"Failed to get recommendations: {e}",
                break_loop=False
            )
    
    async def _rag_query(
        self,
        query: str = "",
        top_k: int = 5,
        use_kg: bool = True,
        **kwargs
    ) -> Response:
        """Perform advanced RAG query"""
        advanced_rag = self.agent.get_data("advanced_rag")
        
        if not advanced_rag:
            return Response(
                message="Advanced RAG not initialized",
                break_loop=False
            )
        
        if not query:
            return Response(
                message="Please provide a query",
                break_loop=False
            )
        
        try:
            results = await advanced_rag.query_with_decomposition(
                query=query,
                top_k=top_k,
                use_kg=use_kg,
            )
            
            if not results:
                return Response(
                    message="No results found",
                    break_loop=False
                )
            
            # Format results
            result_text = f"Found {len(results)} results:\n\n"
            
            for i, result in enumerate(results[:5], 1):
                result_text += f"{i}. Score: {result.score:.3f} ({result.retrieval_method})\n"
                result_text += f"   {result.document.page_content[:200]}...\n\n"
            
            return Response(
                message=result_text,
                break_loop=False
            )
        
        except Exception as e:
            return Response(
                message=f"RAG query failed: {e}",
                break_loop=False
            )
    
    async def _enable_feature(self, feature: str = "", **kwargs) -> Response:
        """Enable a specific feature"""
        if not feature:
            return Response(
                message="Please specify a feature to enable",
                break_loop=False
            )
        
        valid_features = [
            "hierarchical_memory",
            "advanced_reasoning",
            "tool_optimizer",
            "advanced_rag",
            "tool_cache",
            "chain_of_thought",
        ]
        
        if feature not in valid_features:
            return Response(
                message=f"Invalid feature: {feature}. Valid: {', '.join(valid_features)}",
                break_loop=False
            )
        
        self.agent.config.additional[f"enable_{feature}"] = True
        
        return Response(
            message=f"Enabled {feature}. Restart may be required for full effect.",
            break_loop=False
        )
    
    async def _disable_feature(self, feature: str = "", **kwargs) -> Response:
        """Disable a specific feature"""
        if not feature:
            return Response(
                message="Please specify a feature to disable",
                break_loop=False
            )
        
        self.agent.config.additional[f"enable_{feature}"] = False
        
        return Response(
            message=f"Disabled {feature}",
            break_loop=False
        )
