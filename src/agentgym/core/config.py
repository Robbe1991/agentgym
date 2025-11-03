"""Training configuration for AgentGym.

This module provides Pydantic-based configuration management for agent training sessions,
ensuring type safety, validation, and sensible defaults.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TrainingConfig(BaseModel):
    """Configuration for agent training session.

    This configuration class manages all parameters required for training an agent,
    including scenario selection, framework integration, hyperparameters, and GPU settings.

    Attributes:
        scenario: Name of the training scenario to use (e.g., "customer_support").
        framework: Agent framework to integrate with (langchain, autogen, or crewai).
        episodes: Number of training episodes to run. Must be positive.
        gpu_provider: GPU provider to use for training. Options:
            - "auto": Automatically detect and select best available option
            - "local": Use local GPU (requires CUDA)
            - "runpod": Use RunPod cloud GPUs (BYOG)
            - "lambda": Use Lambda Labs cloud GPUs (BYOG)
            - "cloud": Use AgentGym managed cloud (paid tier)
        gpu_type: Specific GPU type to use (e.g., "RTX_4090", "A100"). Default "auto".
        learning_rate: Learning rate for RL training algorithm. Must be positive.
        discount_factor: Discount factor (gamma) for future rewards. Range: (0, 1).
        batch_size: Batch size for training updates. Must be positive.
        max_steps_per_episode: Maximum steps per episode before termination.
        checkpoint_interval: Save checkpoint every N episodes. 0 to disable.
        verbose: Enable detailed logging output.
        seed: Random seed for reproducibility. None for random seed.

    Example:
        >>> config = TrainingConfig(
        ...     scenario="customer_support",
        ...     framework="langchain",
        ...     episodes=1000
        ... )
        >>> print(config.learning_rate)
        0.0003
        >>> print(config.gpu_provider)
        auto

        >>> # With custom hyperparameters
        >>> custom_config = TrainingConfig(
        ...     scenario="code_review",
        ...     framework="autogen",
        ...     episodes=5000,
        ...     learning_rate=0.0001,
        ...     gpu_provider="runpod",
        ...     gpu_type="RTX_4090"
        ... )
    """

    # Required fields
    scenario: str = Field(
        ...,
        description="Scenario name to train on",
        min_length=1,
        examples=["customer_support", "code_review", "qa_testing"],
    )

    # Framework integration
    framework: Literal["langchain", "autogen", "crewai"] = Field(
        "langchain",
        description="Agent framework to use",
    )

    # Training parameters
    episodes: int = Field(
        10000,
        gt=0,
        description="Number of training episodes",
        examples=[1000, 10000, 50000],
    )

    # GPU settings
    gpu_provider: Literal["auto", "local", "runpod", "lambda", "cloud"] = Field(
        "auto",
        description="GPU provider for training",
    )

    gpu_type: str = Field(
        "auto",
        description="Specific GPU type (e.g., RTX_4090, A100)",
        examples=["auto", "RTX_4090", "RTX_3090", "A100"],
    )

    # RL hyperparameters (sensible defaults from research)
    learning_rate: float = Field(
        0.0003,
        gt=0,
        description="Learning rate for RL algorithm",
        examples=[0.0001, 0.0003, 0.001],
    )

    discount_factor: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Discount factor (gamma) for future rewards",
        examples=[0.9, 0.95, 0.99],
    )

    batch_size: int = Field(
        64,
        gt=0,
        description="Batch size for training updates",
        examples=[32, 64, 128],
    )

    max_steps_per_episode: int = Field(
        100,
        gt=0,
        description="Maximum steps per episode",
        examples=[50, 100, 200],
    )

    # Training management
    checkpoint_interval: int = Field(
        1000,
        ge=0,
        description="Save checkpoint every N episodes (0 to disable)",
        examples=[0, 500, 1000],
    )

    verbose: bool = Field(
        True,
        description="Enable detailed logging",
    )

    seed: int | None = Field(
        None,
        ge=0,
        description="Random seed for reproducibility",
        examples=[None, 42, 123],
    )

    model_config = {
        "extra": "allow",  # Allow additional fields for extensibility
        "validate_assignment": True,  # Validate on attribute assignment
        "json_schema_extra": {
            "examples": [
                {
                    "scenario": "customer_support",
                    "framework": "langchain",
                    "episodes": 10000,
                    "gpu_provider": "auto",
                    "learning_rate": 0.0003,
                    "discount_factor": 0.95,
                }
            ]
        },
    }

    @field_validator("scenario")
    @classmethod
    def validate_scenario_name(cls, v: str) -> str:
        """Validate scenario name format.

        Args:
            v: Scenario name to validate.

        Returns:
            Validated scenario name.

        Raises:
            ValueError: If scenario name contains invalid characters.
        """
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Scenario name must contain only alphanumeric characters, "
                "underscores, and hyphens"
            )
        return v.lower()

    def to_dict(self) -> dict:
        """Export configuration as dictionary.

        Returns:
            Dictionary representation of the configuration.

        Example:
            >>> config = TrainingConfig(scenario="customer_support")
            >>> config_dict = config.to_dict()
            >>> print(config_dict["episodes"])
            10000
        """
        return self.model_dump()

    def to_json(self) -> str:
        """Export configuration as JSON string.

        Returns:
            JSON string representation of the configuration.

        Example:
            >>> config = TrainingConfig(scenario="customer_support")
            >>> json_str = config.to_json()
            >>> print('"scenario": "customer_support"' in json_str)
            True
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "TrainingConfig":
        """Create configuration from dictionary.

        Args:
            data: Dictionary containing configuration parameters.

        Returns:
            TrainingConfig instance.

        Raises:
            ValidationError: If data contains invalid values.

        Example:
            >>> data = {"scenario": "customer_support", "episodes": 5000}
            >>> config = TrainingConfig.from_dict(data)
            >>> print(config.episodes)
            5000
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "TrainingConfig":
        """Create configuration from JSON string.

        Args:
            json_str: JSON string containing configuration.

        Returns:
            TrainingConfig instance.

        Raises:
            ValidationError: If JSON contains invalid values.

        Example:
            >>> json_str = '{"scenario": "customer_support", "episodes": 5000}'
            >>> config = TrainingConfig.from_json(json_str)
            >>> print(config.episodes)
            5000
        """
        return cls.model_validate_json(json_str)

    def __str__(self) -> str:
        """String representation of configuration.

        Returns:
            Human-readable string representation.
        """
        return (
            f"TrainingConfig(scenario='{self.scenario}', "
            f"framework='{self.framework}', episodes={self.episodes})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of configuration.

        Returns:
            Detailed string representation for debugging.
        """
        return (
            f"TrainingConfig("
            f"scenario='{self.scenario}', "
            f"framework='{self.framework}', "
            f"episodes={self.episodes}, "
            f"gpu_provider='{self.gpu_provider}', "
            f"learning_rate={self.learning_rate}, "
            f"discount_factor={self.discount_factor})"
        )
