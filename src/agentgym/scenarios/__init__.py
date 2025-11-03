"""Pre-built training scenarios for common agent tasks."""

from agentgym.scenarios.base import Scenario
from agentgym.scenarios.registry import ScenarioNotFoundError, ScenarioRegistry

__all__ = [
    "Scenario",
    "ScenarioRegistry",
    "ScenarioNotFoundError",
]
