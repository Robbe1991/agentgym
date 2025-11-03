"""Core trainer for agent training using reinforcement learning.

This module implements the Trainer class that coordinates agent training sessions
using on-policy RL, following insights from AgentFlow research.
"""

from typing import Any, Protocol

from agentgym.core.config import TrainingConfig
from agentgym.core.result import TrainingMetrics, TrainingResult


class Trajectory:
    """Represents a single episode trajectory.

    A trajectory contains all steps taken by the agent during one episode,
    from initial state to terminal state.

    Attributes:
        steps: List of steps in the trajectory.
        total_reward: Cumulative reward for the trajectory.
        success: Whether the episode was successful.
        metadata: Additional trajectory metadata.
    """

    def __init__(
        self,
        steps: list[dict[str, Any]] | None = None,
        total_reward: float = 0.0,
        success: bool = False,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize trajectory.

        Args:
            steps: List of step dictionaries containing state, action, reward.
            total_reward: Cumulative reward for trajectory.
            success: Whether episode succeeded.
            metadata: Additional metadata (tokens used, time, etc.).
        """
        self.steps = steps or []
        self.total_reward = total_reward
        self.success = success
        self.metadata = metadata or {}

    def __len__(self) -> int:
        """Return number of steps in trajectory."""
        return len(self.steps)


class Scenario(Protocol):
    """Protocol for training scenarios.

    This protocol defines the interface that scenarios must implement.
    Actual scenario implementations will be in the scenarios module.
    """

    def create_environment(self) -> Any:
        """Create training environment for this scenario."""
        ...

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        Args:
            trajectory: Completed episode trajectory.

        Returns:
            List of rewards, one per step (broadcast from outcome).
        """
        ...

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate performance metrics from trajectories.

        Args:
            trajectories: List of completed trajectories.

        Returns:
            Dictionary of metric name to value.
        """
        ...


class Trainer:
    """Agent trainer using reinforcement learning.

    This class coordinates agent training using on-policy RL, following
    insights from AgentFlow research (Stanford, Oct 2025):
    - On-policy RL with live tool interaction (NOT offline SFT)
    - Trajectory-level reward broadcasting (NOT sparse terminal rewards)
    - Modular training (only tool selection, not execution)

    The trainer manages the complete training loop including:
    - Environment setup
    - Trajectory collection via live interaction
    - Reward calculation and broadcasting
    - Policy updates (modular, tool-selection only)
    - Metrics tracking

    Attributes:
        config: Training configuration.
        scenario: Training scenario (defines environment and rewards).
        trajectories: Collected trajectories from training.
        metrics_history: Metrics collected during training.

    Example:
        >>> from agentgym.core.config import TrainingConfig
        >>> config = TrainingConfig(scenario="customer_support", episodes=100)
        >>> trainer = Trainer(config)  # doctest: +SKIP
        >>> result = trainer.train()  # doctest: +SKIP
        >>> print(result.metrics.tool_reliability)  # doctest: +SKIP
        0.95
    """

    def __init__(
        self,
        config: TrainingConfig,
        scenario: Scenario | None = None,
    ):
        """Initialize trainer.

        Args:
            config: Training configuration with hyperparameters.
            scenario: Training scenario (optional, will use registry if None).

        Note:
            If scenario is None, will attempt to load from ScenarioRegistry
            using config.scenario. For now (pre-registry), scenario must be provided.
        """
        self.config = config
        self.scenario = scenario or self._load_scenario()
        self.trajectories: list[Trajectory] = []
        self.metrics_history: list[dict[str, float]] = []
        self._episode_count = 0

    def _load_scenario(self) -> Scenario:
        """Load scenario from registry.

        Returns:
            Scenario instance.

        Raises:
            ScenarioNotFoundError: If scenario_name is not registered.

        Note:
            Loads scenarios using ScenarioRegistry. Scenarios must be registered
            before they can be loaded by name.
        """
        from agentgym.scenarios.registry import ScenarioRegistry

        return ScenarioRegistry.load(self.config.scenario)

    def train(self) -> TrainingResult:
        """Train agent using on-policy reinforcement learning.

        Implements AgentFlow-inspired training loop:
        1. Collect trajectory via live interaction (ON-POLICY)
        2. Broadcast outcome reward to all steps (TRAJECTORY-LEVEL)
        3. Update only tool selection policy (MODULAR)

        Returns:
            TrainingResult with final metrics and model path.

        Example:
            >>> config = TrainingConfig(scenario="test", episodes=10)
            >>> # trainer = Trainer(config, scenario=mock_scenario)  # doctest: +SKIP
            >>> # result = trainer.train()  # doctest: +SKIP
        """
        # Initialize environment
        environment = self.scenario.create_environment()

        # Training loop
        for episode in range(self.config.episodes):
            # ON-POLICY: Collect trajectory via live interaction
            trajectory = self._collect_trajectory_online(environment, episode)
            self.trajectories.append(trajectory)

            # TRAJECTORY-LEVEL: Broadcast outcome reward to all steps
            step_rewards = self.scenario.broadcast_rewards(trajectory)

            # MODULAR: Update only tool selection policy
            self._update_policy(
                trajectory,
                step_rewards,
                trainable_components=["tool_selection", "parameter_selection"],
            )

            # Track metrics periodically
            if (episode + 1) % max(1, self.config.episodes // 10) == 0:
                self._track_metrics(episode + 1)

            self._episode_count = episode + 1

        # Generate final result
        return self._create_result()

    def _collect_trajectory_online(self, environment: Any, episode: int) -> Trajectory:
        """Collect trajectory via live agent interaction (on-policy).

        This is the core of on-policy RL: the agent interacts with the
        environment in real-time, not from offline data.

        Args:
            environment: Training environment.
            episode: Current episode number.

        Returns:
            Completed trajectory with steps and rewards.

        Note:
            This is a mock implementation. Real implementation would:
            1. Reset environment
            2. Agent selects actions based on current policy
            3. Execute actions and observe outcomes
            4. Record steps with states, actions, rewards
            5. Continue until terminal state
        """
        # Mock implementation - simulates successful episode
        # Real implementation would actually interact with environment

        # Simulate varying performance (improves with training)
        success_rate = min(0.6 + (episode / self.config.episodes) * 0.35, 0.95)
        import random

        random.seed(self.config.seed if self.config.seed else episode)

        success = random.random() < success_rate
        num_steps = random.randint(3, 8)

        steps = [
            {
                "state": f"state_{i}",
                "action": f"tool_call_{i}",
                "reward": 1.0 if success else 0.0,
                "tool_success": success,
            }
            for i in range(num_steps)
        ]

        return Trajectory(
            steps=steps,
            total_reward=float(num_steps) if success else 0.0,
            success=success,
            metadata={
                "episode": episode,
                "tokens_used": random.randint(150, 300),
                "response_time": random.uniform(0.5, 2.0),
            },
        )

    def _update_policy(
        self,
        trajectory: Trajectory,
        step_rewards: list[float],
        trainable_components: list[str],
    ) -> None:
        """Update policy based on trajectory and rewards (modular training).

        AgentFlow insight: Training only planning (tool selection) is more
        efficient than training the entire model.

        Args:
            trajectory: Collected trajectory.
            step_rewards: Rewards for each step (broadcast from outcome).
            trainable_components: Which components to train.

        Note:
            This is a mock implementation. Real implementation would:
            1. Compute policy gradients for specified components
            2. Apply gradients using Agent Lightning
            3. Update only tool_selection and parameter_selection
            4. Freeze tool_execution and output_generation
        """
        # Mock implementation - real would use Agent Lightning
        # For now, we just record that update happened
        pass

    def _track_metrics(self, episode: int) -> None:
        """Track metrics from recent trajectories.

        Args:
            episode: Current episode number.
        """
        if not self.trajectories:
            return

        # Calculate metrics from recent trajectories
        recent = self.trajectories[-100:]  # Last 100 episodes
        metrics = self.scenario.calculate_metrics(recent)
        metrics["episode"] = episode

        self.metrics_history.append(metrics)

    def _create_result(self) -> TrainingResult:
        """Create final training result.

        Returns:
            TrainingResult with metrics and model path.
        """
        # Calculate final metrics from all trajectories
        final_metrics_dict = self.scenario.calculate_metrics(self.trajectories)

        metrics = TrainingMetrics(
            tool_reliability=final_metrics_dict.get("tool_reliability", 0.0),
            avg_tokens_used=final_metrics_dict.get("avg_tokens_used", 0.0),
            avg_response_time=final_metrics_dict.get("avg_response_time", 0.0),
            cost_reduction=final_metrics_dict.get("cost_reduction", 0.0),
            episodes_completed=self._episode_count,
            total_training_time=final_metrics_dict.get("total_training_time", 0.0),
            final_reward=final_metrics_dict.get("final_reward", 0.0),
            convergence_episode=final_metrics_dict.get("convergence_episode"),
        )

        # Generate model path
        model_path = (
            f"./models/{self.config.scenario}_"
            f"{self.config.framework}_"
            f"ep{self.config.episodes}"
        )

        return TrainingResult(
            config=self.config,
            metrics=metrics,
            trained_model_path=model_path,
            artifacts={
                "trajectories_count": len(self.trajectories),
                "metrics_history": self.metrics_history,
            },
        )

    def get_metrics_history(self) -> list[dict[str, float]]:
        """Get metrics history from training.

        Returns:
            List of metrics dictionaries, one per tracking point.
        """
        return self.metrics_history

    def __repr__(self) -> str:
        """Detailed string representation.

        Returns:
            String representation for debugging.
        """
        return (
            f"Trainer("
            f"scenario='{self.config.scenario}', "
            f"framework='{self.config.framework}', "
            f"episodes={self.config.episodes}, "
            f"trajectories_collected={len(self.trajectories)})"
        )
