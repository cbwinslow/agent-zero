import re
from typing import List, Dict
from fastmcp import FastMCP
from pydantic import BaseModel, Field

app = FastMCP(
    name="Objective Planner",
    instructions="""Break down an objective into tasks and micro-goals""",
)

class MicroGoal(BaseModel):
    description: str = Field(description="Micro goal description")
    criteria: str = Field(description="Completion criteria")

class TaskPlan(BaseModel):
    task: str = Field(description="Task description")
    micro_goals: List[MicroGoal] = Field(default_factory=list)

class PlanResponse(BaseModel):
    objective: str
    tasks: List[TaskPlan]

@app.tool(name="plan_objective", description="Create task plan from objective")
async def plan_objective(objective: str) -> PlanResponse:
    # Split objective into potential tasks using punctuation heuristics
    raw_parts = re.split(r"[\.\n]+|\band\b", objective)
    tasks: List[str] = [p.strip() for p in raw_parts if p.strip()]
    plans: List[TaskPlan] = []
    for t in tasks:
        micro_goals = [
            MicroGoal(description=f"Define requirements for {t}", criteria="Requirements documented"),
            MicroGoal(description=f"Implement {t}", criteria="Implementation completed"),
            MicroGoal(description=f"Validate {t}", criteria="All acceptance tests pass"),
        ]
        plans.append(TaskPlan(task=t, micro_goals=micro_goals))
    return PlanResponse(objective=objective, tasks=plans)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
