from .base import BaseAgent
import logging

class DummyAgent(BaseAgent):
    """A simple agent that logs a message."""

    def run(self) -> None:
        logging.info("%s is running", self.name)
        print(f"Agent {self.name} started")
