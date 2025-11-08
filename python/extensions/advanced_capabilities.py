"""
Enhanced Agent Extensions for Advanced Capabilities

This extension integrates the new advanced systems into Agent Zero:
- Hierarchical memory management
- Advanced reasoning
- Tool optimization
- Advanced RAG

Extension points:
- agent_init: Initialize advanced systems
- monologue_start: Setup for reasoning session
- message_loop_start: Prepare for message processing
- before_main_llm_call: Apply reasoning strategies
- tool_execute_before: Optimize tool execution
- tool_execute_after: Track tool metrics
- hist_add_before: Enhanced memory storage
"""

import asyncio
from typing import Any, Dict
from agent import Agent
from python.helpers.print_style import PrintStyle

# Import advanced systems
try:
    from python.helpers.memory_hierarchy import get_hierarchical_memory, MemoryTier, MemoryImportance
    from python.helpers.advanced_reasoning import get_advanced_reasoning, ReasoningStrategy
    from python.helpers.tool_optimizer import get_tool_optimizer
    from python.helpers.advanced_rag import get_advanced_rag
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    PrintStyle(font_color="yellow", padding=True).print(
        "Advanced features not available. Some extensions will be disabled."
    )


async def agent_init(agent: Agent):
    """Initialize advanced systems when agent is created"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    # Check if advanced features are enabled in config
    enable_advanced = agent.config.additional.get("enable_advanced_features", True)
    if not enable_advanced:
        return
    
    try:
        # Initialize hierarchical memory
        if agent.config.additional.get("enable_hierarchical_memory", True):
            hierarchical_memory = get_hierarchical_memory(agent)
            agent.set_data("hierarchical_memory", hierarchical_memory)
            PrintStyle(font_color="green").print(
                f"{agent.agent_name}: Hierarchical memory initialized"
            )
        
        # Initialize advanced reasoning
        if agent.config.additional.get("enable_advanced_reasoning", True):
            advanced_reasoning = get_advanced_reasoning(agent)
            agent.set_data("advanced_reasoning", advanced_reasoning)
            PrintStyle(font_color="green").print(
                f"{agent.agent_name}: Advanced reasoning initialized"
            )
        
        # Initialize tool optimizer
        if agent.config.additional.get("enable_tool_optimizer", True):
            tool_optimizer = get_tool_optimizer(agent)
            agent.set_data("tool_optimizer", tool_optimizer)
            PrintStyle(font_color="green").print(
                f"{agent.agent_name}: Tool optimizer initialized"
            )
        
        # Initialize advanced RAG
        if agent.config.additional.get("enable_advanced_rag", True):
            advanced_rag = get_advanced_rag(agent)
            agent.set_data("advanced_rag", advanced_rag)
            PrintStyle(font_color="green").print(
                f"{agent.agent_name}: Advanced RAG initialized"
            )
        
    except Exception as e:
        PrintStyle(font_color="red", padding=True).print(
            f"Failed to initialize advanced features: {e}"
        )


async def monologue_start(agent: Agent, loop_data):
    """Setup for reasoning session"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    advanced_reasoning = agent.get_data("advanced_reasoning")
    if not advanced_reasoning:
        return
    
    # Determine if we should use advanced reasoning for this task
    use_cot = agent.config.additional.get("use_chain_of_thought", False)
    
    if use_cot and loop_data.user_message:
        # Store flag to apply CoT reasoning
        loop_data.params_persistent["use_cot"] = True


async def before_main_llm_call(agent: Agent, loop_data):
    """Apply reasoning strategies before main LLM call"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    advanced_reasoning = agent.get_data("advanced_reasoning")
    if not advanced_reasoning:
        return
    
    # Check if we should apply advanced reasoning
    use_cot = loop_data.params_persistent.get("use_cot", False)
    
    if use_cot and loop_data.iteration == 0:
        # Only apply on first iteration to avoid recursion
        try:
            # Get the user message
            if loop_data.user_message and hasattr(loop_data.user_message, 'content'):
                user_text = str(loop_data.user_message.content)
                
                # Apply Chain-of-Thought reasoning
                reasoning_chain = await advanced_reasoning.apply_chain_of_thought(
                    problem=user_text,
                    max_steps=5,
                )
                
                # Add reasoning to extras for context
                if reasoning_chain.traces:
                    reasoning_summary = "\n".join([
                        f"Step {i+1}: {trace.content[:100]}..."
                        for i, trace in enumerate(reasoning_chain.traces[:3])
                    ])
                    
                    loop_data.extras_persistent["reasoning_chain"] = {
                        "summary": reasoning_summary,
                        "confidence": reasoning_chain.overall_confidence,
                    }
                    
                    PrintStyle(font_color="cyan").print(
                        f"Applied CoT reasoning (confidence: {reasoning_chain.overall_confidence:.2f})"
                    )
        
        except Exception as e:
            PrintStyle(font_color="yellow").print(
                f"CoT reasoning failed: {e}"
            )


async def tool_execute_before(agent: Agent, tool_args: Dict, tool_name: str):
    """Optimize tool execution"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    tool_optimizer = agent.get_data("tool_optimizer")
    if not tool_optimizer:
        return
    
    # Check if tool should use caching
    cache_enabled = agent.config.additional.get("enable_tool_cache", True)
    
    if cache_enabled:
        # Store flag to use optimized execution
        agent.set_data("_use_tool_optimizer", True)


async def tool_execute_after(agent: Agent, response, tool_name: str):
    """Track tool metrics after execution"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    tool_optimizer = agent.get_data("tool_optimizer")
    if not tool_optimizer:
        return
    
    # Tool metrics are tracked automatically by optimizer
    # This hook can be used for additional processing
    pass


async def hist_add_before(agent: Agent, content_data: Dict, ai: bool):
    """Enhanced memory storage with hierarchical memory"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return
    
    hierarchical_memory = agent.get_data("hierarchical_memory")
    if not hierarchical_memory:
        return
    
    # Check if hierarchical memory is enabled
    enable_auto_memory = agent.config.additional.get("enable_auto_hierarchical_memory", False)
    
    if not enable_auto_memory:
        return
    
    try:
        content = content_data.get("content", "")
        if not content or not isinstance(content, str):
            return
        
        # Determine memory tier and importance
        if ai:
            # AI responses go to working memory by default
            tier = MemoryTier.WORKING
            importance = 0.5
        else:
            # User messages have higher importance
            tier = MemoryTier.WORKING
            importance = 0.7
        
        # Extract keywords from content
        words = content.lower().split()
        keywords = [w for w in words if len(w) > 4][:5]
        
        # Store in hierarchical memory asynchronously
        asyncio.create_task(
            hierarchical_memory.store_memory(
                content=content[:500],  # Limit size
                tier=tier,
                importance=importance,
                keywords=keywords,
                source_type="agent" if ai else "user",
            )
        )
        
    except Exception as e:
        # Don't let memory storage break the main flow
        PrintStyle(font_color="yellow").print(
            f"Hierarchical memory storage failed: {e}"
        )


# Configuration helper functions

def enable_all_advanced_features(agent: Agent):
    """Enable all advanced features"""
    agent.config.additional["enable_advanced_features"] = True
    agent.config.additional["enable_hierarchical_memory"] = True
    agent.config.additional["enable_advanced_reasoning"] = True
    agent.config.additional["enable_tool_optimizer"] = True
    agent.config.additional["enable_advanced_rag"] = True
    agent.config.additional["enable_tool_cache"] = True
    agent.config.additional["use_chain_of_thought"] = True


def disable_all_advanced_features(agent: Agent):
    """Disable all advanced features"""
    agent.config.additional["enable_advanced_features"] = False


def get_advanced_features_status(agent: Agent) -> Dict[str, bool]:
    """Get status of all advanced features"""
    return {
        "advanced_features": agent.config.additional.get("enable_advanced_features", False),
        "hierarchical_memory": agent.config.additional.get("enable_hierarchical_memory", False),
        "advanced_reasoning": agent.config.additional.get("enable_advanced_reasoning", False),
        "tool_optimizer": agent.config.additional.get("enable_tool_optimizer", False),
        "advanced_rag": agent.config.additional.get("enable_advanced_rag", False),
        "tool_cache": agent.config.additional.get("enable_tool_cache", False),
        "chain_of_thought": agent.config.additional.get("use_chain_of_thought", False),
    }
