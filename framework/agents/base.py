class BaseAgent:
    """Minimal base class for agents."""

    def __init__(self, name: str):
        self.name = name

    def run(self) -> None:
        raise NotImplementedError
