"""
Setup script for the orchestration system.
Provides utility functions to initialize and configure the orchestration components.
"""

import os
import json
from typing import Dict, List, Any, Optional

from models import ModelType, ModelProvider
from .model_orchestrator import ModelOrchestrator, ModelProfile, ModelCapability
from .agent_orchestrator import AgentOrchestrator, AgentProfile, AgentRole
from .task_router import TaskRouter
from .team import TeamManager, Team, TeamMember


def setup_default_model_profiles() -> Dict[str, ModelProfile]:
    """Set up default model profiles for common LLMs."""
    profiles = {}
    
    # OpenAI models
    profiles["gpt-4"] = ModelProfile(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4",
        model_type=ModelType.CHAT,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.CLASSIFICATION,
            ModelCapability.EXTRACTION,
            ModelCapability.TRANSLATION,
            ModelCapability.CREATIVE,
            ModelCapability.FACTUAL,
        ],
        cost_per_1k_tokens=0.03,
        max_tokens=8192,
        typical_latency_ms=2000,
        description="Advanced model with strong reasoning and general capabilities",
    )
    
    profiles["gpt-3.5-turbo"] = ModelProfile(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        model_type=ModelType.CHAT,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.SUMMARIZATION,
            ModelCapability.CLASSIFICATION,
            ModelCapability.TRANSLATION,
            ModelCapability.CREATIVE,
        ],
        cost_per_1k_tokens=0.002,
        max_tokens=4096,
        typical_latency_ms=500,
        description="Fast and cost-effective model for general tasks",
    )
    
    # Anthropic models
    profiles["claude-3-opus"] = ModelProfile(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-opus",
        model_type=ModelType.CHAT,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.CLASSIFICATION,
            ModelCapability.EXTRACTION,
            ModelCapability.TRANSLATION,
            ModelCapability.CREATIVE,
            ModelCapability.FACTUAL,
        ],
        cost_per_1k_tokens=0.015,
        max_tokens=100000,
        typical_latency_ms=2500,
        description="Advanced model with strong reasoning and long context",
    )
    
    # Mistral models
    profiles["mistral-large"] = ModelProfile(
        provider=ModelProvider.MISTRALAI,
        model_name="mistral-large-latest",
        model_type=ModelType.CHAT,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.CLASSIFICATION,
        ],
        cost_per_1k_tokens=0.008,
        max_tokens=32768,
        typical_latency_ms=1000,
        description="Balanced model with good reasoning and long context",
    )
    
    # Ollama models
    profiles["llama3"] = ModelProfile(
        provider=ModelProvider.OLLAMA,
        model_name="llama3",
        model_type=ModelType.CHAT,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.SUMMARIZATION,
        ],
        cost_per_1k_tokens=0.0,
        max_tokens=4096,
        typical_latency_ms=1500,
        description="Local open-source model for general tasks",
    )
    
    return profiles


def setup_default_agent_profiles() -> Dict[str, AgentProfile]:
    """Set up default agent profiles for common roles."""
    profiles = {}
    
    # Coordinator agent
    profiles["coordinator"] = AgentProfile(
        name="Coordinator",
        role=AgentRole.COORDINATOR,
        model_id="gpt-4",
        system_prompt="""You are a Coordinator agent responsible for managing a team of specialized AI agents.
Your job is to:
1. Analyze incoming tasks and break them down into subtasks
2. Assign subtasks to the most appropriate specialized agents
3. Integrate the results from different agents
4. Ensure the final output meets the requirements

When you receive a task, carefully analyze it and create a plan for how to solve it using the available team members.
""",
        description="Coordinates the work of other agents and manages complex tasks",
    )
    
    # Coder agent
    profiles["coder"] = AgentProfile(
        name="Coder",
        role=AgentRole.CODER,
        model_id="gpt-4",
        system_prompt="""You are a Coder agent specialized in writing high-quality code.
Your job is to:
1. Write clean, efficient, and well-documented code
2. Debug and fix issues in existing code
3. Optimize code for performance and readability
4. Follow best practices and coding standards

When given a coding task, first understand the requirements thoroughly, then plan your approach before writing code.
""",
        description="Specializes in writing and debugging code",
    )
    
    # Researcher agent
    profiles["researcher"] = AgentProfile(
        name="Researcher",
        role=AgentRole.RESEARCHER,
        model_id="claude-3-opus",
        system_prompt="""You are a Researcher agent specialized in gathering and analyzing information.
Your job is to:
1. Find relevant information on a given topic
2. Analyze and synthesize information from multiple sources
3. Evaluate the credibility and reliability of sources
4. Present findings in a clear and organized manner

When given a research task, be thorough and comprehensive in your search, and critically evaluate all information.
""",
        description="Specializes in gathering and analyzing information",
    )
    
    # Writer agent
    profiles["writer"] = AgentProfile(
        name="Writer",
        role=AgentRole.WRITER,
        model_id="claude-3-opus",
        system_prompt="""You are a Writer agent specialized in creating high-quality written content.
Your job is to:
1. Create clear, engaging, and well-structured content
2. Adapt your writing style to different audiences and purposes
3. Edit and improve existing content
4. Ensure content is grammatically correct and free of errors

When given a writing task, consider the target audience, purpose, and context before crafting your response.
""",
        description="Specializes in creating high-quality written content",
    )
    
    # Critic agent
    profiles["critic"] = AgentProfile(
        name="Critic",
        role=AgentRole.CRITIC,
        model_id="gpt-4",
        system_prompt="""You are a Critic agent specialized in evaluating and improving work.
Your job is to:
1. Identify strengths and weaknesses in content or code
2. Provide constructive feedback for improvement
3. Check for errors, inconsistencies, or logical flaws
4. Suggest specific improvements

When reviewing work, be thorough, fair, and constructive in your feedback.
""",
        description="Specializes in evaluating and improving work",
    )
    
    return profiles


def setup_default_team() -> Team:
    """Set up a default team with common roles."""
    team = Team(
        team_id="default-team",
        name="Default Team",
        description="A general-purpose team with agents for common tasks",
        coordinator_agent_id="coordinator",
    )
    
    # Add team members
    team.add_member(TeamMember(
        agent_id="coordinator",
        role_in_team="Team Lead",
        description="Manages the team and coordinates work"
    ))
    
    team.add_member(TeamMember(
        agent_id="coder",
        role_in_team="Developer",
        description="Handles coding tasks"
    ))
    
    team.add_member(TeamMember(
        agent_id="researcher",
        role_in_team="Information Specialist",
        description="Gathers and analyzes information"
    ))
    
    team.add_member(TeamMember(
        agent_id="writer",
        role_in_team="Content Creator",
        description="Creates written content"
    ))
    
    team.add_member(TeamMember(
        agent_id="critic",
        role_in_team="Quality Assurance",
        description="Reviews and improves work"
    ))
    
    return team


def initialize_orchestration_system(
    config_dir: str = "config/orchestration",
    load_from_files: bool = True,
    save_to_files: bool = True,
) -> Dict[str, Any]:
    """Initialize the complete orchestration system."""
    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Paths for configuration files
    models_file = os.path.join(config_dir, "models.json")
    agents_file = os.path.join(config_dir, "agents.json")
    teams_file = os.path.join(config_dir, "teams.json")
    
    # Initialize model orchestrator
    model_orchestrator = (
        ModelOrchestrator.load_from_file(models_file)
        if load_from_files and os.path.exists(models_file)
        else ModelOrchestrator()
    )
    
    # If no models are registered, set up default models
    if not model_orchestrator.models:
        default_models = setup_default_model_profiles()
        for model_id, profile in default_models.items():
            model_orchestrator.register_model(model_id, profile)
        model_orchestrator.set_default_model("gpt-3.5-turbo")
    
    # Initialize agent orchestrator
    agent_orchestrator = (
        AgentOrchestrator.load_from_file(agents_file, model_orchestrator)
        if load_from_files and os.path.exists(agents_file)
        else AgentOrchestrator(model_orchestrator)
    )
    
    # If no agents are registered, set up default agents
    if not agent_orchestrator.agents:
        default_agents = setup_default_agent_profiles()
        for agent_id, profile in default_agents.items():
            agent_orchestrator.register_agent(agent_id, profile)
        agent_orchestrator.set_default_agent("coordinator")
    
    # Initialize task router
    task_router = TaskRouter(model_orchestrator, agent_orchestrator)
    
    # Initialize team manager
    team_manager = (
        TeamManager.load_from_file(teams_file, model_orchestrator, agent_orchestrator, task_router)
        if load_from_files and os.path.exists(teams_file)
        else TeamManager(model_orchestrator, agent_orchestrator, task_router)
    )
    
    # If no teams are registered, set up default team
    if not team_manager.teams:
        default_team = setup_default_team()
        team_manager.teams[default_team.team_id] = default_team
    
    # Save configurations if requested
    if save_to_files:
        model_orchestrator.save_to_file(models_file)
        agent_orchestrator.save_to_file(agents_file)
        team_manager.save_to_file(teams_file)
    
    # Return all components
    return {
        "model_orchestrator": model_orchestrator,
        "agent_orchestrator": agent_orchestrator,
        "task_router": task_router,
        "team_manager": team_manager,
    }