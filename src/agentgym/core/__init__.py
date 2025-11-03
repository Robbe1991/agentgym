"""Core training logic and configuration for AgentGym."""

# from agentgym.core.trainer import Trainer  # TODO: Implement in Issue #3
from agentgym.core.config import TrainingConfig
from agentgym.core.result import TrainingMetrics, TrainingResult

__all__ = [
    # "Trainer",  # TODO: Implement in Issue #3
    "TrainingConfig",
    "TrainingResult",
    "TrainingMetrics",
]
