"""Training results and metrics for AgentGym.

This module provides dataclasses for storing and managing training results,
including metrics, model paths, and artifacts.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agentgym.core.config import TrainingConfig


@dataclass
class TrainingMetrics:
    """Metrics collected during agent training.

    This class stores all key performance indicators from a training session,
    focusing on tool reliability (primary metric), efficiency, and cost.

    Attributes:
        tool_reliability: Tool call success rate (0.0-1.0). Target: 0.95 (95%).
        avg_tokens_used: Average tokens consumed per episode.
        avg_response_time: Average response time in seconds per episode.
        cost_reduction: Cost reduction percentage compared to baseline (0.0-1.0).
        episodes_completed: Total number of training episodes completed.
        total_training_time: Total training time in seconds.
        final_reward: Final cumulative reward achieved.
        convergence_episode: Episode number where model converged (or None).

    Example:
        >>> metrics = TrainingMetrics(
        ...     tool_reliability=0.947,
        ...     avg_tokens_used=250.5,
        ...     avg_response_time=1.2,
        ...     cost_reduction=0.35,
        ...     episodes_completed=10000
        ... )
        >>> print(f"Tool reliability: {metrics.tool_reliability:.1%}")
        Tool reliability: 94.7%
    """

    tool_reliability: float
    avg_tokens_used: float
    avg_response_time: float
    cost_reduction: float
    episodes_completed: int
    total_training_time: float = 0.0
    final_reward: float = 0.0
    convergence_episode: int | None = None

    def __post_init__(self) -> None:
        """Validate metric values after initialization."""
        if not 0.0 <= self.tool_reliability <= 1.0:
            raise ValueError(
                f"tool_reliability must be between 0.0 and 1.0, got {self.tool_reliability}"
            )
        if not 0.0 <= self.cost_reduction <= 1.0:
            raise ValueError(
                f"cost_reduction must be between 0.0 and 1.0, got {self.cost_reduction}"
            )
        if self.avg_tokens_used < 0:
            raise ValueError(
                f"avg_tokens_used must be non-negative, got {self.avg_tokens_used}"
            )
        if self.avg_response_time < 0:
            raise ValueError(
                f"avg_response_time must be non-negative, got {self.avg_response_time}"
            )
        if self.episodes_completed < 0:
            raise ValueError(
                f"episodes_completed must be non-negative, got {self.episodes_completed}"
            )

    def meets_target(self, target_reliability: float = 0.95) -> bool:
        """Check if tool reliability meets target threshold.

        Args:
            target_reliability: Target reliability threshold (default: 0.95).

        Returns:
            True if tool_reliability >= target_reliability.

        Example:
            >>> metrics = TrainingMetrics(
            ...     tool_reliability=0.96,
            ...     avg_tokens_used=200,
            ...     avg_response_time=1.0,
            ...     cost_reduction=0.3,
            ...     episodes_completed=5000
            ... )
            >>> metrics.meets_target()
            True
            >>> metrics.meets_target(target_reliability=0.97)
            False
        """
        return self.tool_reliability >= target_reliability

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary.

        Returns:
            Dictionary representation of metrics.

        Example:
            >>> metrics = TrainingMetrics(
            ...     tool_reliability=0.95,
            ...     avg_tokens_used=200,
            ...     avg_response_time=1.0,
            ...     cost_reduction=0.3,
            ...     episodes_completed=5000
            ... )
            >>> result = metrics.to_dict()
            >>> result["tool_reliability"]
            0.95
        """
        return asdict(self)


@dataclass
class TrainingResult:
    """Complete training result including config, metrics, and artifacts.

    This class encapsulates all outputs from a training session, including
    the configuration used, performance metrics achieved, model location,
    and any additional artifacts.

    Attributes:
        config: Training configuration used for this session.
        metrics: Performance metrics achieved during training.
        trained_model_path: Path to saved trained model.
        artifacts: Additional artifacts (logs, checkpoints, plots, etc.).
        timestamp: When training completed (ISO format).
        version: AgentGym version used for training.

    Example:
        >>> from agentgym.core.config import TrainingConfig
        >>> config = TrainingConfig(scenario="customer_support")
        >>> metrics = TrainingMetrics(
        ...     tool_reliability=0.95,
        ...     avg_tokens_used=200,
        ...     avg_response_time=1.0,
        ...     cost_reduction=0.3,
        ...     episodes_completed=10000
        ... )
        >>> result = TrainingResult(
        ...     config=config,
        ...     metrics=metrics,
        ...     trained_model_path="./models/customer_support_v1.0",
        ... )
        >>> print(result.metrics.tool_reliability)
        0.95
    """

    config: TrainingConfig
    metrics: TrainingMetrics
    trained_model_path: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of the training result.

        Example:
            >>> config = TrainingConfig(scenario="test")
            >>> metrics = TrainingMetrics(
            ...     tool_reliability=0.9,
            ...     avg_tokens_used=100,
            ...     avg_response_time=0.5,
            ...     cost_reduction=0.2,
            ...     episodes_completed=1000
            ... )
            >>> result = TrainingResult(
            ...     config=config,
            ...     metrics=metrics,
            ...     trained_model_path="./models/test"
            ... )
            >>> result_dict = result.to_dict()
            >>> result_dict["metrics"]["tool_reliability"]
            0.9
        """
        return {
            "config": self.config.to_dict(),
            "metrics": self.metrics.to_dict(),
            "trained_model_path": self.trained_model_path,
            "artifacts": self.artifacts,
            "timestamp": self.timestamp,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingResult":
        """Create TrainingResult from dictionary.

        Args:
            data: Dictionary containing training result data.

        Returns:
            TrainingResult instance.

        Raises:
            KeyError: If required keys are missing.
            ValueError: If data contains invalid values.

        Example:
            >>> data = {
            ...     "config": {"scenario": "test", "framework": "langchain"},
            ...     "metrics": {
            ...         "tool_reliability": 0.9,
            ...         "avg_tokens_used": 100,
            ...         "avg_response_time": 0.5,
            ...         "cost_reduction": 0.2,
            ...         "episodes_completed": 1000,
            ...         "total_training_time": 3600.0,
            ...         "final_reward": 95.5,
            ...         "convergence_episode": None
            ...     },
            ...     "trained_model_path": "./models/test",
            ...     "artifacts": {},
            ...     "timestamp": "2025-01-01T00:00:00",
            ...     "version": "0.1.0"
            ... }
            >>> result = TrainingResult.from_dict(data)
            >>> result.metrics.tool_reliability
            0.9
        """
        return cls(
            config=TrainingConfig.from_dict(data["config"]),
            metrics=TrainingMetrics(**data["metrics"]),
            trained_model_path=data["trained_model_path"],
            artifacts=data.get("artifacts", {}),
            timestamp=data.get("timestamp", datetime.now(UTC).isoformat()),
            version=data.get("version", "0.1.0"),
        )

    def save(self, path: str) -> None:
        """Save training result to JSON file.

        Args:
            path: File path to save result (will create parent directories).

        Example:
            >>> config = TrainingConfig(scenario="test")
            >>> metrics = TrainingMetrics(
            ...     tool_reliability=0.9,
            ...     avg_tokens_used=100,
            ...     avg_response_time=0.5,
            ...     cost_reduction=0.2,
            ...     episodes_completed=1000
            ... )
            >>> result = TrainingResult(
            ...     config=config,
            ...     metrics=metrics,
            ...     trained_model_path="./models/test"
            ... )
            >>> result.save("./results/test_result.json")  # doctest: +SKIP
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "TrainingResult":
        """Load training result from JSON file.

        Args:
            path: File path to load result from.

        Returns:
            TrainingResult instance.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file contains invalid JSON.

        Example:
            >>> result = TrainingResult.load("./results/test_result.json")  # doctest: +SKIP
            >>> print(result.metrics.tool_reliability)  # doctest: +SKIP
            0.95
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation of training result.

        Returns:
            Human-readable string representation.
        """
        return (
            f"TrainingResult(scenario='{self.config.scenario}', "
            f"tool_reliability={self.metrics.tool_reliability:.1%}, "
            f"episodes={self.metrics.episodes_completed})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of training result.

        Returns:
            Detailed string representation for debugging.
        """
        return (
            f"TrainingResult("
            f"scenario='{self.config.scenario}', "
            f"framework='{self.config.framework}', "
            f"tool_reliability={self.metrics.tool_reliability:.3f}, "
            f"cost_reduction={self.metrics.cost_reduction:.3f}, "
            f"episodes_completed={self.metrics.episodes_completed}, "
            f"model_path='{self.trained_model_path}')"
        )
