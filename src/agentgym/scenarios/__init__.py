"""Pre-built training scenarios for common agent tasks."""

from agentgym.scenarios.base import Scenario
from agentgym.scenarios.code_review import CodeReviewScenario
from agentgym.scenarios.customer_support import CustomerSupportScenario
from agentgym.scenarios.data_analysis import DataAnalysisScenario
from agentgym.scenarios.registry import ScenarioNotFoundError, ScenarioRegistry

__all__ = [
    "Scenario",
    "ScenarioRegistry",
    "ScenarioNotFoundError",
    "CustomerSupportScenario",
    "CodeReviewScenario",
    "DataAnalysisScenario",
]
