"""Simple orchestrator skeleton for the Multi-Agent Development Framework."""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent / "configs"
PROJECTS_DIR = Path(__file__).resolve().parent / "projects"


def load_config(name: str = "default.json") -> dict:
    path = CONFIG_DIR / name
    if path.exists():
        return json.loads(path.read_text())
    return {}


def create_project(name: str) -> Path:
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    cfg = load_config()
    project_name = cfg.get("project", "demo")
    project_dir = create_project(project_name)
    logging.info(f"Initialized project at {project_dir}")
