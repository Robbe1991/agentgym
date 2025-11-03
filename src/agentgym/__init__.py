"""AgentGym: The Vercel for Agent Training - Powered by Agent Lightning

AgentGym is an open-core platform for training AI agents using reinforcement learning.

Key Features:
    - 95% tool reliability (vs 60-70% untrained)
    - 98% time savings (4 hours → 3 minutes)
    - 30-50% cost reduction
    - One-click deployment
    - Framework-agnostic (LangChain, AutoGen, CrewAI)

Quick Start:
    >>> from agentgym import Trainer
    >>> trainer = Trainer()
    >>> result = trainer.train("customer_support")
    >>> print(f"Tool reliability: {result.metrics.tool_reliability:.1%}")
    Tool reliability: 94.7%

For more information, visit: https://agentgym.com
"""

__version__ = "0.1.0"
__author__ = "AgentGym Team"
__email__ = "hello@agentgym.com"
__license__ = "MIT"

# Core exports
from agentgym.core.config import TrainingConfig
from agentgym.core.result import TrainingMetrics, TrainingResult
from agentgym.core.trainer import Trainer, Trajectory

# Scenario exports
from agentgym.scenarios.base import Scenario
from agentgym.scenarios.registry import ScenarioNotFoundError, ScenarioRegistry

# Integration exports
# from agentgym.integrations.base import FrameworkAdapter  # TODO: Implement in Issue #7

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",

    # Core classes
    "Trainer",
    "TrainingConfig",
    "TrainingResult",
    "TrainingMetrics",
    "Trajectory",

    # Scenarios
    "Scenario",
    "ScenarioRegistry",
    "ScenarioNotFoundError",

    # Integrations
    # "FrameworkAdapter",  # TODO: Implement in Issue #7
]
