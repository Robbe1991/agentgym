"""Base scenario class for agent training.

This module provides the abstract base class that all training scenarios must inherit from,
defining the interface for environment creation, reward calculation, and success criteria.
"""

from abc import ABC, abstractmethod
from typing import Any

from agentgym.core.trainer import Trajectory


class Scenario(ABC):
    """Abstract base class for all training scenarios.

    Scenarios define the training environment, reward structure, and success criteria
    for agent training. Each scenario represents a specific use case (e.g., customer
    support, code review, data analysis).

    Following AgentFlow research insights:
    - Trajectory-level reward broadcasting (not sparse terminal rewards)
    - Modular training (only tool selection, not entire model)

    Subclasses must implement:
    - create_environment(): Define the training environment
    - broadcast_rewards(): Calculate and broadcast rewards
    - success_criteria(): Define target performance metrics
    - name, description, difficulty: Class attributes

    Attributes:
        name: Unique scenario identifier (e.g., "customer_support").
        description: Human-readable scenario description.
        difficulty: Difficulty level ("beginner", "intermediate", "advanced").

    Example:
        >>> class MyScenario(Scenario):
        ...     name = "my_scenario"
        ...     description = "Example scenario"
        ...     difficulty = "beginner"
        ...
        ...     def create_environment(self):
        ...         return {"type": "custom_env"}
        ...
        ...     def broadcast_rewards(self, trajectory):
        ...         outcome = 1.0 if trajectory.success else 0.0
        ...         return [outcome] * len(trajectory)
        ...
        ...     def success_criteria(self):
        ...         return {"tool_reliability": 0.95}
    """

    # Class attributes that must be defined in subclasses
    name: str
    description: str
    difficulty: str  # "beginner", "intermediate", or "advanced"

    @abstractmethod
    def create_environment(self) -> Any:
        """Create training environment for this scenario.

        This method should return an environment object that the agent will
        interact with during training. The environment defines the state space,
        action space, and dynamics.

        Returns:
            Environment object (structure depends on scenario).

        Example:
            >>> def create_environment(self):
            ...     return {
            ...         "type": "customer_support",
            ...         "tools": ["search_kb", "update_ticket"],
            ...         "initial_state": {...}
            ...     }
        """
        pass

    @abstractmethod
    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        AgentFlow research showed that broadcasting the outcome reward to all steps
        in a trajectory solves credit assignment better than sparse rewards only
        at the terminal state.

        This method should:
        1. Evaluate the final outcome of the trajectory
        2. Calculate an outcome reward based on success/failure
        3. Broadcast this reward to all steps (with optional step-specific bonuses)

        Args:
            trajectory: Completed episode trajectory with steps and outcome.

        Returns:
            List of rewards, one per step in the trajectory.

        Example:
            >>> def broadcast_rewards(self, trajectory):
            ...     # Outcome reward based on success
            ...     outcome_reward = 10.0 if trajectory.success else -5.0
            ...
            ...     # Broadcast to all steps
            ...     step_rewards = [outcome_reward] * len(trajectory)
            ...
            ...     # Add step-specific bonuses
            ...     for i, step in enumerate(trajectory.steps):
            ...         if step.get("tool_success"):
            ...             step_rewards[i] += 2.0  # Bonus for successful tool use
            ...
            ...     return step_rewards

        Note:
            The sum of step_rewards does not need to equal trajectory.total_reward.
            Each step gets the outcome signal plus optional bonuses.
        """
        pass

    def define_trainable_components(self) -> dict[str, bool]:
        """Define which components to train versus freeze.

        AgentFlow research showed that training only planning components
        (tool selection and parameter selection) is more efficient than
        training the entire model end-to-end.

        Default implementation trains only tool and parameter selection,
        freezing tool execution and output generation. Subclasses can
        override for different training strategies.

        Returns:
            Dictionary mapping component names to trainable flags.

        Example:
            >>> scenario = MyScenario()
            >>> components = scenario.define_trainable_components()
            >>> components
            {'tool_selection': True, 'parameter_selection': True, 'tool_execution': False, 'output_generation': False}

        Note:
            Most scenarios should use the default implementation.
            Only override if you have specific requirements.
        """
        return {
            "tool_selection": True,  # Train: which tool to use
            "parameter_selection": True,  # Train: what parameters to use
            "tool_execution": False,  # Freeze: how tools are executed
            "output_generation": False,  # Freeze: how outputs are generated
        }

    @abstractmethod
    def success_criteria(self) -> dict[str, float]:
        """Define target performance metrics for this scenario.

        Each scenario has specific success criteria based on the use case.
        Common metrics include tool_reliability, cost_reduction, time_savings.

        Returns:
            Dictionary mapping metric names to target values.

        Example:
            >>> def success_criteria(self):
            ...     return {
            ...         "tool_reliability": 0.95,  # 95% success rate
            ...         "cost_reduction": 0.30,     # 30% cost reduction
            ...         "time_savings": 0.98        # 98% time savings
            ...     }

        Note:
            Metrics should match those calculated in calculate_metrics().
        """
        pass

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate performance metrics from trajectories.

        This method analyzes completed trajectories to calculate performance metrics
        such as tool reliability, average tokens used, response time, etc.

        Default implementation provides common metrics. Subclasses can override
        to add scenario-specific metrics.

        Args:
            trajectories: List of completed episode trajectories.

        Returns:
            Dictionary of metric names to values.

        Example:
            >>> trajectories = [traj1, traj2, traj3]
            >>> metrics = scenario.calculate_metrics(trajectories)
            >>> metrics
            {'tool_reliability': 0.92, 'avg_tokens_used': 245.5, ...}
        """
        if not trajectories:
            return {
                "tool_reliability": 0.0,
                "avg_tokens_used": 0.0,
                "avg_response_time": 0.0,
                "cost_reduction": 0.0,
                "total_training_time": 0.0,
                "final_reward": 0.0,
                "convergence_episode": None,
            }

        # Calculate tool reliability (success rate)
        successful = sum(1 for t in trajectories if t.success)
        tool_reliability = successful / len(trajectories)

        # Calculate average tokens used
        total_tokens = sum(t.metadata.get("tokens_used", 0.0) for t in trajectories)
        avg_tokens_used = total_tokens / len(trajectories)

        # Calculate average response time
        total_time = sum(t.metadata.get("response_time", 0.0) for t in trajectories)
        avg_response_time = total_time / len(trajectories)

        # Estimate cost reduction based on reliability and efficiency
        # (simplified calculation - real would compare to baseline)
        cost_reduction = min(tool_reliability * 0.4, 0.5)

        # Calculate average reward
        total_reward = sum(t.total_reward for t in trajectories)
        final_reward = total_reward / len(trajectories)

        # Estimate convergence episode (when performance stabilized)
        convergence_episode = None
        if len(trajectories) >= 100:
            # Simple heuristic: convergence at 80% through training
            convergence_episode = int(len(trajectories) * 0.8)

        return {
            "tool_reliability": tool_reliability,
            "avg_tokens_used": avg_tokens_used,
            "avg_response_time": avg_response_time,
            "cost_reduction": cost_reduction,
            "total_training_time": 0.0,  # Calculated externally by Trainer
            "final_reward": final_reward,
            "convergence_episode": convergence_episode,
        }

    def validate_trajectory(self, trajectory: Trajectory) -> bool:
        """Validate that trajectory meets scenario requirements.

        Default implementation checks basic trajectory properties.
        Subclasses can override for scenario-specific validation.

        Args:
            trajectory: Trajectory to validate.

        Returns:
            True if trajectory is valid, False otherwise.

        Example:
            >>> trajectory = Trajectory(steps=[...])
            >>> if scenario.validate_trajectory(trajectory):
            ...     rewards = scenario.broadcast_rewards(trajectory)
        """
        # Basic validation: must have steps
        if len(trajectory) == 0:
            return False

        # All steps must be dictionaries
        if not all(isinstance(step, dict) for step in trajectory.steps):
            return False

        return True

    def __str__(self) -> str:
        """String representation of scenario.

        Returns:
            Human-readable string.
        """
        return f"{self.name} ({self.difficulty})"

    def __repr__(self) -> str:
        """Detailed string representation of scenario.

        Returns:
            Detailed string for debugging.
        """
        return (
            f"Scenario(name='{self.name}', "
            f"description='{self.description}', "
            f"difficulty='{self.difficulty}')"
        )
