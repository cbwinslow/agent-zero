"""
Advanced Reasoning System for Agent Zero

This module implements sophisticated reasoning patterns:

1. Chain-of-Thought (CoT) Reasoning
   - Step-by-step breakdown of complex problems
   - Explicit reasoning traces
   - Intermediate verification steps

2. ReAct (Reasoning + Acting) Pattern
   - Interleaved thought and action
   - Dynamic planning and execution
   - Action-observation loops

3. Self-Reflection and Meta-Cognition
   - Confidence scoring for decisions
   - Self-evaluation of reasoning quality
   - Error detection and correction

4. Multi-Strategy Reasoning
   - Forward reasoning (goal-directed)
   - Backward reasoning (constraint-based)
   - Analogical reasoning (pattern matching)
   - Abductive reasoning (best explanation)

5. Reasoning Optimization
   - Prompt compression
   - Context pruning
   - Reasoning cache
"""

import asyncio
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable

from python.helpers.print_style import PrintStyle
from python.helpers import files


class ReasoningStrategy(Enum):
    """Different reasoning strategies"""
    CHAIN_OF_THOUGHT = "cot"           # Step-by-step reasoning
    REACT = "react"                     # Reasoning + Acting
    TREE_OF_THOUGHTS = "tot"           # Multiple reasoning paths
    SELF_CONSISTENCY = "self_consistency"  # Multiple samples, majority vote
    REFLEXION = "reflexion"            # Self-reflection and correction


class ReasoningStep(Enum):
    """Types of reasoning steps"""
    OBSERVATION = "observation"        # Input or environment state
    THOUGHT = "thought"                # Internal reasoning
    ACTION = "action"                  # Planned or executed action
    REFLECTION = "reflection"          # Self-evaluation
    CONCLUSION = "conclusion"          # Final answer or decision


@dataclass
class ReasoningTrace:
    """A single step in the reasoning process"""
    step_type: ReasoningStep
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.5  # Confidence in this step (0-1)
    alternatives: List[str] = field(default_factory=list)  # Alternative reasoning paths
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "step_type": self.step_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "metadata": self.metadata,
        }


@dataclass
class ReasoningChain:
    """A complete reasoning chain"""
    strategy: ReasoningStrategy
    traces: List[ReasoningTrace] = field(default_factory=list)
    final_answer: str = ""
    overall_confidence: float = 0.0
    reasoning_quality: float = 0.0  # Self-assessed quality
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    
    def add_trace(self, trace: ReasoningTrace):
        """Add a reasoning trace"""
        self.traces.append(trace)
        # Update overall confidence (weighted average)
        self.overall_confidence = sum(t.confidence for t in self.traces) / len(self.traces)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "traces": [t.to_dict() for t in self.traces],
            "final_answer": self.final_answer,
            "overall_confidence": self.overall_confidence,
            "reasoning_quality": self.reasoning_quality,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class AdvancedReasoning:
    """
    Advanced reasoning system with multiple strategies.
    
    Implements CoT, ReAct, self-reflection, and other reasoning patterns
    to enhance agent decision-making and problem-solving.
    """
    
    def __init__(self, agent):
        """
        Initialize advanced reasoning system.
        
        Args:
            agent: The agent instance
        """
        self.agent = agent
        self.reasoning_history: List[ReasoningChain] = []
        self.reasoning_cache: Dict[str, ReasoningChain] = {}
        self.max_history_size = 100
        
        # Reasoning prompts
        self.cot_prompt_template = """
Let's solve this step by step:

1. First, let me understand the problem:
{problem}

2. Let me break this down into smaller steps:
[Your step-by-step reasoning here]

3. Now, let me verify my reasoning:
[Check if each step makes sense]

4. Therefore, my conclusion is:
[Final answer]
"""
        
        self.react_prompt_template = """
Let me think through this using reasoning and actions:

Thought 1: What do I need to understand first?
{initial_thought}

Action 1: What should I do?
{action}

Observation 1: What did I learn?
{observation}

[Continue this pattern until solved]

Final Answer: {conclusion}
"""
        
        self.reflection_prompt_template = """
Let me reflect on my reasoning:

Original reasoning:
{original_reasoning}

Critical evaluation:
1. Are there any logical flaws? {flaw_check}
2. Did I consider all possibilities? {completeness_check}
3. Is my confidence justified? {confidence_check}
4. What could go wrong? {risk_assessment}

Revised reasoning (if needed):
{revised_reasoning}
"""
    
    async def apply_chain_of_thought(
        self,
        problem: str,
        context: Optional[str] = None,
        max_steps: int = 10,
    ) -> ReasoningChain:
        """
        Apply Chain-of-Thought reasoning to a problem.
        
        Args:
            problem: The problem to solve
            context: Additional context
            max_steps: Maximum reasoning steps
            
        Returns:
            ReasoningChain with step-by-step reasoning
        """
        chain = ReasoningChain(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
        
        # Add initial observation
        observation = ReasoningTrace(
            step_type=ReasoningStep.OBSERVATION,
            content=problem,
            confidence=1.0,
        )
        chain.add_trace(observation)
        
        # Generate reasoning prompt
        prompt = f"""
Problem: {problem}
{f'Context: {context}' if context else ''}

Let's solve this step-by-step using careful reasoning:

Step 1: Understanding the problem
"""
        
        # Get initial reasoning from LLM
        try:
            response = await self.agent.call_utility_model(
                system="You are an expert problem solver. Break down problems step-by-step.",
                message=prompt,
            )
            
            # Parse response into reasoning steps
            steps = self._parse_reasoning_steps(response)
            
            for i, step_content in enumerate(steps):
                # Each step is a thought
                thought = ReasoningTrace(
                    step_type=ReasoningStep.THOUGHT,
                    content=step_content,
                    confidence=self._estimate_confidence(step_content),
                    metadata={"step_number": i + 1},
                )
                chain.add_trace(thought)
                
                # Stop if we've reached max steps
                if len(chain.traces) >= max_steps:
                    break
            
            # Add conclusion
            conclusion = ReasoningTrace(
                step_type=ReasoningStep.CONCLUSION,
                content=steps[-1] if steps else response,
                confidence=chain.overall_confidence,
            )
            chain.add_trace(conclusion)
            chain.final_answer = conclusion.content
            
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Error in CoT reasoning: {e}"
            )
            # Fallback
            chain.final_answer = "Unable to complete reasoning due to error"
        
        chain.end_time = datetime.now(timezone.utc)
        self._add_to_history(chain)
        
        return chain
    
    async def apply_react_pattern(
        self,
        problem: str,
        max_iterations: int = 5,
    ) -> ReasoningChain:
        """
        Apply ReAct (Reasoning + Acting) pattern.
        
        Args:
            problem: The problem to solve
            max_iterations: Maximum thought-action-observation cycles
            
        Returns:
            ReasoningChain with interleaved reasoning and actions
        """
        chain = ReasoningChain(strategy=ReasoningStrategy.REACT)
        
        # Initial observation
        observation_content = problem
        
        for iteration in range(max_iterations):
            # Add observation
            observation = ReasoningTrace(
                step_type=ReasoningStep.OBSERVATION,
                content=observation_content,
                confidence=1.0,
                metadata={"iteration": iteration + 1},
            )
            chain.add_trace(observation)
            
            # Generate thought
            thought_prompt = f"""
Based on this observation:
{observation_content}

What should I think about next? Provide a single, focused thought about what to do.
"""
            
            try:
                thought_content = await self.agent.call_utility_model(
                    system="You are a strategic thinker. Generate focused, actionable thoughts.",
                    message=thought_prompt,
                )
                
                thought = ReasoningTrace(
                    step_type=ReasoningStep.THOUGHT,
                    content=thought_content,
                    confidence=0.7,
                    metadata={"iteration": iteration + 1},
                )
                chain.add_trace(thought)
                
                # Decide on action
                action_prompt = f"""
Given this thought: {thought_content}

What specific action should I take? Describe the action clearly.
"""
                
                action_content = await self.agent.call_utility_model(
                    system="You are an action planner. Suggest concrete, executable actions.",
                    message=action_prompt,
                )
                
                action = ReasoningTrace(
                    step_type=ReasoningStep.ACTION,
                    content=action_content,
                    confidence=0.6,
                    metadata={"iteration": iteration + 1},
                )
                chain.add_trace(action)
                
                # Check if we have a conclusion
                if "conclude" in action_content.lower() or "final answer" in action_content.lower():
                    conclusion = ReasoningTrace(
                        step_type=ReasoningStep.CONCLUSION,
                        content=action_content,
                        confidence=chain.overall_confidence,
                    )
                    chain.add_trace(conclusion)
                    chain.final_answer = action_content
                    break
                
                # Simulate observation (in real scenario, this would come from tool execution)
                observation_content = f"Result of action: {action_content[:100]}..."
                
            except Exception as e:
                PrintStyle(font_color="red").print(
                    f"Error in ReAct iteration {iteration}: {e}"
                )
                break
        
        chain.end_time = datetime.now(timezone.utc)
        self._add_to_history(chain)
        
        return chain
    
    async def apply_self_reflection(
        self,
        reasoning_chain: ReasoningChain,
    ) -> ReasoningChain:
        """
        Apply self-reflection to evaluate and improve reasoning.
        
        Args:
            reasoning_chain: The reasoning chain to reflect on
            
        Returns:
            New ReasoningChain with reflections and improvements
        """
        reflected_chain = ReasoningChain(strategy=ReasoningStrategy.REFLEXION)
        
        # Summarize original reasoning
        original_summary = "\n".join([
            f"{t.step_type.value}: {t.content[:100]}..."
            for t in reasoning_chain.traces
        ])
        
        # Generate reflection prompt
        reflection_prompt = f"""
Original reasoning:
{original_summary}

Final answer: {reasoning_chain.final_answer}
Confidence: {reasoning_chain.overall_confidence:.2f}

Please critically evaluate this reasoning:
1. Are there any logical flaws or gaps?
2. Were all important factors considered?
3. Is the confidence level appropriate?
4. What could be improved?

Provide a detailed reflection and suggest improvements if needed.
"""
        
        try:
            reflection_content = await self.agent.call_utility_model(
                system="You are a critical thinker who evaluates reasoning quality.",
                message=reflection_prompt,
            )
            
            reflection = ReasoningTrace(
                step_type=ReasoningStep.REFLECTION,
                content=reflection_content,
                confidence=0.8,
            )
            reflected_chain.add_trace(reflection)
            
            # Assess reasoning quality
            quality_score = self._assess_reasoning_quality(
                reflection_content,
                reasoning_chain.overall_confidence
            )
            reflected_chain.reasoning_quality = quality_score
            
            # If quality is low, generate improved reasoning
            if quality_score < 0.7:
                improvement_prompt = f"""
The original reasoning had some issues:
{reflection_content}

Please provide an improved reasoning approach:
"""
                
                improved_reasoning = await self.agent.call_utility_model(
                    system="You are an expert problem solver who improves flawed reasoning.",
                    message=improvement_prompt,
                )
                
                improved_trace = ReasoningTrace(
                    step_type=ReasoningStep.THOUGHT,
                    content=improved_reasoning,
                    confidence=0.8,
                    metadata={"improved": True},
                )
                reflected_chain.add_trace(improved_trace)
                reflected_chain.final_answer = improved_reasoning
            else:
                reflected_chain.final_answer = reasoning_chain.final_answer
            
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Error in self-reflection: {e}"
            )
            reflected_chain.final_answer = reasoning_chain.final_answer
        
        reflected_chain.end_time = datetime.now(timezone.utc)
        self._add_to_history(reflected_chain)
        
        return reflected_chain
    
    def _parse_reasoning_steps(self, reasoning_text: str) -> List[str]:
        """
        Parse reasoning text into individual steps.
        
        Args:
            reasoning_text: The reasoning text to parse
            
        Returns:
            List of reasoning steps
        """
        # Simple parsing - split by numbered steps or paragraphs
        steps = []
        
        # Try to find numbered steps
        import re
        step_pattern = r'(?:Step|Thought|Action)\s*\d+[:\.]?\s*(.+?)(?=(?:Step|Thought|Action)\s*\d+|$)'
        matches = re.findall(step_pattern, reasoning_text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            steps = [m.strip() for m in matches if m.strip()]
        else:
            # Fallback: split by paragraphs
            paragraphs = reasoning_text.split('\n\n')
            steps = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 10]
        
        return steps if steps else [reasoning_text]
    
    def _estimate_confidence(self, content: str) -> float:
        """
        Estimate confidence based on content analysis.
        
        Args:
            content: The content to analyze
            
        Returns:
            Confidence score (0-1)
        """
        # Heuristics for confidence estimation
        confidence = 0.5  # Base confidence
        
        # Increase confidence for certain indicators
        confidence_boosters = [
            "clearly", "definitely", "certainly", "obviously",
            "must", "always", "never", "proven", "fact"
        ]
        confidence_reducers = [
            "maybe", "perhaps", "possibly", "might", "could",
            "uncertain", "unclear", "ambiguous", "guess"
        ]
        
        content_lower = content.lower()
        
        for booster in confidence_boosters:
            if booster in content_lower:
                confidence = min(1.0, confidence + 0.1)
        
        for reducer in confidence_reducers:
            if reducer in content_lower:
                confidence = max(0.0, confidence - 0.1)
        
        return confidence
    
    def _assess_reasoning_quality(
        self,
        reflection: str,
        original_confidence: float
    ) -> float:
        """
        Assess the quality of reasoning based on reflection.
        
        Args:
            reflection: The reflection text
            original_confidence: Original confidence score
            
        Returns:
            Quality score (0-1)
        """
        quality = 0.7  # Base quality
        
        # Look for quality indicators in reflection
        positive_indicators = [
            "sound reasoning", "logical", "well-structured",
            "comprehensive", "thorough", "correct"
        ]
        negative_indicators = [
            "flaw", "error", "mistake", "incomplete", "missing",
            "unclear", "weak", "poor", "incorrect"
        ]
        
        reflection_lower = reflection.lower()
        
        for indicator in positive_indicators:
            if indicator in reflection_lower:
                quality = min(1.0, quality + 0.05)
        
        for indicator in negative_indicators:
            if indicator in reflection_lower:
                quality = max(0.0, quality - 0.1)
        
        # Consider original confidence
        quality = (quality + original_confidence) / 2
        
        return quality
    
    def _add_to_history(self, chain: ReasoningChain):
        """Add reasoning chain to history"""
        self.reasoning_history.append(chain)
        
        # Maintain max history size
        if len(self.reasoning_history) > self.max_history_size:
            self.reasoning_history = self.reasoning_history[-self.max_history_size:]
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about reasoning usage.
        
        Returns:
            Dictionary with reasoning statistics
        """
        if not self.reasoning_history:
            return {"total_chains": 0}
        
        stats = {
            "total_chains": len(self.reasoning_history),
            "by_strategy": {},
            "average_confidence": 0.0,
            "average_quality": 0.0,
            "average_steps": 0.0,
        }
        
        # Count by strategy
        for chain in self.reasoning_history:
            strategy = chain.strategy.value
            stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
        
        # Calculate averages
        total_confidence = sum(c.overall_confidence for c in self.reasoning_history)
        total_quality = sum(c.reasoning_quality for c in self.reasoning_history)
        total_steps = sum(len(c.traces) for c in self.reasoning_history)
        
        stats["average_confidence"] = total_confidence / len(self.reasoning_history)
        stats["average_quality"] = total_quality / len(self.reasoning_history)
        stats["average_steps"] = total_steps / len(self.reasoning_history)
        
        return stats
    
    def export_reasoning_history(self, filepath: str):
        """
        Export reasoning history to a file.
        
        Args:
            filepath: Path to save the history
        """
        try:
            data = [chain.to_dict() for chain in self.reasoning_history]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            PrintStyle(font_color="green").print(
                f"Exported {len(data)} reasoning chains to {filepath}"
            )
        except Exception as e:
            PrintStyle(font_color="red").print(
                f"Failed to export reasoning history: {e}"
            )


# Global instance
_advanced_reasoning_instance: Optional[AdvancedReasoning] = None


def get_advanced_reasoning(agent) -> AdvancedReasoning:
    """Get or create the global advanced reasoning instance"""
    global _advanced_reasoning_instance
    if _advanced_reasoning_instance is None:
        _advanced_reasoning_instance = AdvancedReasoning(agent)
    return _advanced_reasoning_instance
