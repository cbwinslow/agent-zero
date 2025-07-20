"""
Orchestrator for the Agent Zero Multi-Agent Framework.
Provides a simplified interface to the orchestration system.
"""

import json
import logging

from pathlib import Path

from framework.orchestration.setup import initialize_orchestration_system
from framework.orchestration.model_orchestrator import ModelOrchestrator, ModelCapability
from framework.orchestration.agent_orchestrator import AgentOrchestrator, AgentRole
from framework.orchestration.task_router import TaskRouter, Task, TaskType, TaskPriority
from framework.orchestration.team import TeamManager, Team, TeamMember

# Configuration directories
CONFIG_DIR = Path(__file__).resolve().parent / "configs"
PROJECTS_DIR = Path(__file__).resolve().parent / "projects"
ORCHESTRATION_DIR = CONFIG_DIR / "orchestration"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
ORCHESTRATION_DIR.mkdir(parents=True, exist_ok=True)


def load_workflow(path: Path) -> list[dict]:
    if path.exists():
        return json.loads(path.read_text()).get("agents", [])
    return []


def spawn_agents(workflow_path: Path) -> None:
    agents = load_workflow(workflow_path)
    for spec in agents:
        mod = importlib.import_module(spec["module"])
        cls = getattr(mod, spec["class"])
        agent = cls(spec.get("name", "agent"))
        logging.info("Spawning %s", agent.name)
        agent.run()


def load_config(name: str = "default.json") -> dict:
    """Load a configuration file."""
    path = CONFIG_DIR / name
    if path.exists():
        return json.loads(path.read_text())
    return {}


def create_project(name: str) -> Path:
    """Create a project directory."""
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def get_orchestration_system():
    """Get or initialize the orchestration system."""
    return initialize_orchestration_system(
        config_dir=str(ORCHESTRATION_DIR),
        load_from_files=True,
        save_to_files=True,
    )


# Initialize the orchestration system when the module is imported
orchestration = get_orchestration_system()

# Export the components for easy access
model_orchestrator = orchestration["model_orchestrator"]
agent_orchestrator = orchestration["agent_orchestrator"]
task_router = orchestration["task_router"]
team_manager = orchestration["team_manager"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    cfg = load_config()
    project_name = cfg.get("project", "demo")
    project_dir = create_project(project_name)

