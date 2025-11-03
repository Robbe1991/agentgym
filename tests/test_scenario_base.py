"""Tests for base scenario class.

This module contains comprehensive tests for the Scenario ABC,
including abstract method enforcement and default implementations.
"""

import pytest

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.base import Scenario


class ConcreteScenario(Scenario):
    """Concrete scenario for testing base class."""

    name = "test_scenario"
    description = "Test scenario for unit tests"
    difficulty = "beginner"

    def create_environment(self):
        """Create test environment."""
        return {"type": "test_environment", "tools": ["tool1", "tool2"]}

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast rewards to all steps."""
        # Simple implementation: outcome reward to all steps
        outcome_reward = 10.0 if trajectory.success else -5.0
        step_rewards = [outcome_reward] * len(trajectory)

        # Add bonuses for successful tool use
        for i, step in enumerate(trajectory.steps):
            if step.get("tool_success", False):
                step_rewards[i] += 2.0

        return step_rewards

    def success_criteria(self) -> dict[str, float]:
        """Define success criteria."""
        return {
            "tool_reliability": 0.95,
            "cost_reduction": 0.30,
            "time_savings": 0.98,
        }


class MinimalScenario(Scenario):
    """Minimal scenario with only required methods."""

    name = "minimal"
    description = "Minimal test scenario"
    difficulty = "beginner"

    def create_environment(self):
        return {}

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        return [1.0] * len(trajectory)

    def success_criteria(self) -> dict[str, float]:
        return {"tool_reliability": 0.9}


class TestScenarioAbstractMethods:
    """Test abstract method enforcement."""

    def test_cannot_instantiate_abstract_scenario(self):
        """Test that Scenario ABC cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Scenario()  # type: ignore

    def test_must_implement_create_environment(self):
        """Test that create_environment must be implemented."""

        class IncompleteScenario1(Scenario):
            name = "incomplete"
            description = "Incomplete"
            difficulty = "beginner"

            def broadcast_rewards(self, trajectory):
                return []

            def success_criteria(self):
                return {}

        with pytest.raises(TypeError):
            IncompleteScenario1()  # type: ignore

    def test_must_implement_broadcast_rewards(self):
        """Test that broadcast_rewards must be implemented."""

        class IncompleteScenario2(Scenario):
            name = "incomplete"
            description = "Incomplete"
            difficulty = "beginner"

            def create_environment(self):
                return {}

            def success_criteria(self):
                return {}

        with pytest.raises(TypeError):
            IncompleteScenario2()  # type: ignore

    def test_must_implement_success_criteria(self):
        """Test that success_criteria must be implemented."""

        class IncompleteScenario3(Scenario):
            name = "incomplete"
            description = "Incomplete"
            difficulty = "beginner"

            def create_environment(self):
                return {}

            def broadcast_rewards(self, trajectory):
                return []

        with pytest.raises(TypeError):
            IncompleteScenario3()  # type: ignore


class TestConcreteScenario:
    """Test concrete scenario implementations."""

    def test_initialization(self):
        """Test creating concrete scenario."""
        scenario = ConcreteScenario()

        assert scenario.name == "test_scenario"
        assert scenario.description == "Test scenario for unit tests"
        assert scenario.difficulty == "beginner"

    def test_create_environment(self):
        """Test environment creation."""
        scenario = ConcreteScenario()
        env = scenario.create_environment()

        assert isinstance(env, dict)
        assert env["type"] == "test_environment"
        assert "tools" in env
        assert len(env["tools"]) == 2

    def test_broadcast_rewards_successful_trajectory(self):
        """Test reward broadcasting for successful trajectory."""
        scenario = ConcreteScenario()

        trajectory = Trajectory(
            steps=[
                {"action": "tool1", "tool_success": True},
                {"action": "tool2", "tool_success": True},
                {"action": "tool3", "tool_success": False},
            ],
            total_reward=30.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 3
        # Outcome reward (10.0) + bonus (2.0) for successful steps
        assert rewards[0] == 12.0  # Success + bonus
        assert rewards[1] == 12.0  # Success + bonus
        assert rewards[2] == 10.0  # Success, no bonus

    def test_broadcast_rewards_failed_trajectory(self):
        """Test reward broadcasting for failed trajectory."""
        scenario = ConcreteScenario()

        trajectory = Trajectory(
            steps=[
                {"action": "tool1", "tool_success": False},
                {"action": "tool2", "tool_success": False},
            ],
            total_reward=0.0,
            success=False,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 2
        # Outcome reward (-5.0), no bonuses
        assert all(r == -5.0 for r in rewards)

    def test_success_criteria(self):
        """Test success criteria definition."""
        scenario = ConcreteScenario()
        criteria = scenario.success_criteria()

        assert isinstance(criteria, dict)
        assert "tool_reliability" in criteria
        assert criteria["tool_reliability"] == 0.95
        assert criteria["cost_reduction"] == 0.30
        assert criteria["time_savings"] == 0.98


class TestDefineTrainableComponents:
    """Test default trainable components implementation."""

    def test_default_trainable_components(self):
        """Test default trainable components."""
        scenario = ConcreteScenario()
        components = scenario.define_trainable_components()

        assert isinstance(components, dict)
        assert len(components) == 4

        # Should train tool and parameter selection
        assert components["tool_selection"] is True
        assert components["parameter_selection"] is True

        # Should freeze execution and generation
        assert components["tool_execution"] is False
        assert components["output_generation"] is False

    def test_can_override_trainable_components(self):
        """Test that subclasses can override trainable components."""

        class CustomTrainableScenario(ConcreteScenario):
            def define_trainable_components(self):
                # Train everything
                return {
                    "tool_selection": True,
                    "parameter_selection": True,
                    "tool_execution": True,
                    "output_generation": True,
                }

        scenario = CustomTrainableScenario()
        components = scenario.define_trainable_components()

        assert all(components.values())  # All True


class TestCalculateMetrics:
    """Test default calculate_metrics implementation."""

    def test_calculate_metrics_empty_trajectories(self):
        """Test metrics calculation with no trajectories."""
        scenario = ConcreteScenario()
        metrics = scenario.calculate_metrics([])

        assert metrics["tool_reliability"] == 0.0
        assert metrics["avg_tokens_used"] == 0.0
        assert metrics["avg_response_time"] == 0.0
        assert metrics["cost_reduction"] == 0.0
        assert metrics["final_reward"] == 0.0
        assert metrics["convergence_episode"] is None

    def test_calculate_metrics_single_trajectory(self):
        """Test metrics calculation with single trajectory."""
        scenario = ConcreteScenario()

        trajectory = Trajectory(
            steps=[{"action": "test"}],
            total_reward=10.0,
            success=True,
            metadata={"tokens_used": 200, "response_time": 1.5},
        )

        metrics = scenario.calculate_metrics([trajectory])

        assert metrics["tool_reliability"] == 1.0  # 100% success
        assert metrics["avg_tokens_used"] == 200.0
        assert metrics["avg_response_time"] == 1.5
        assert metrics["final_reward"] == 10.0
        assert metrics["convergence_episode"] is None  # Too few trajectories

    def test_calculate_metrics_multiple_trajectories(self):
        """Test metrics calculation with multiple trajectories."""
        scenario = ConcreteScenario()

        trajectories = [
            Trajectory(
                steps=[{"a": 1}],
                total_reward=10.0,
                success=True,
                metadata={"tokens_used": 200, "response_time": 1.0},
            ),
            Trajectory(
                steps=[{"a": 1}],
                total_reward=10.0,
                success=True,
                metadata={"tokens_used": 300, "response_time": 1.5},
            ),
            Trajectory(
                steps=[{"a": 1}],
                total_reward=0.0,
                success=False,
                metadata={"tokens_used": 150, "response_time": 0.8},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 successes out of 3 = 66.67%
        assert metrics["tool_reliability"] == pytest.approx(2 / 3)
        # Average tokens: (200 + 300 + 150) / 3 = 216.67
        assert metrics["avg_tokens_used"] == pytest.approx(216.67, rel=0.01)
        # Average time: (1.0 + 1.5 + 0.8) / 3 = 1.1
        assert metrics["avg_response_time"] == pytest.approx(1.1, rel=0.01)
        # Average reward: (10 + 10 + 0) / 3 = 6.67
        assert metrics["final_reward"] == pytest.approx(6.67, rel=0.01)

    def test_calculate_metrics_convergence_episode(self):
        """Test convergence episode calculation."""
        scenario = ConcreteScenario()

        # Create 150 trajectories (>= 100 triggers convergence calculation)
        trajectories = [
            Trajectory(steps=[{"a": 1}], total_reward=5.0, success=True)
            for _ in range(150)
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # Convergence at 80% of training
        assert metrics["convergence_episode"] == int(150 * 0.8)
        assert metrics["convergence_episode"] == 120

    def test_calculate_metrics_missing_metadata(self):
        """Test metrics calculation when metadata is missing."""
        scenario = ConcreteScenario()

        # Trajectory without metadata
        trajectory = Trajectory(
            steps=[{"action": "test"}],
            total_reward=5.0,
            success=True,
            metadata={},  # Empty metadata
        )

        metrics = scenario.calculate_metrics([trajectory])

        # Should handle missing metadata gracefully
        assert metrics["avg_tokens_used"] == 0.0
        assert metrics["avg_response_time"] == 0.0


class TestValidateTrajectory:
    """Test trajectory validation."""

    def test_validate_empty_trajectory(self):
        """Test that empty trajectory is invalid."""
        scenario = ConcreteScenario()
        trajectory = Trajectory(steps=[])

        assert scenario.validate_trajectory(trajectory) is False

    def test_validate_valid_trajectory(self):
        """Test that valid trajectory passes validation."""
        scenario = ConcreteScenario()
        trajectory = Trajectory(
            steps=[
                {"state": "s1", "action": "a1"},
                {"state": "s2", "action": "a2"},
            ]
        )

        assert scenario.validate_trajectory(trajectory) is True

    def test_validate_trajectory_with_non_dict_steps(self):
        """Test that trajectory with non-dict steps is invalid."""
        scenario = ConcreteScenario()
        trajectory = Trajectory(steps=["not", "dicts"])  # type: ignore

        assert scenario.validate_trajectory(trajectory) is False


class TestStringRepresentations:
    """Test string representations."""

    def test_str(self):
        """Test __str__ method."""
        scenario = ConcreteScenario()
        str_repr = str(scenario)

        assert "test_scenario" in str_repr
        assert "beginner" in str_repr

    def test_repr(self):
        """Test __repr__ method."""
        scenario = ConcreteScenario()
        repr_str = repr(scenario)

        assert "Scenario" in repr_str
        assert "test_scenario" in repr_str
        assert "Test scenario for unit tests" in repr_str
        assert "beginner" in repr_str


class TestScenarioIntegration:
    """Integration tests for Scenario usage."""

    def test_scenario_with_trainer_protocol(self):
        """Test that Scenario works with Trainer's expected protocol."""
        scenario = ConcreteScenario()

        # Trainer expects these methods to exist
        assert hasattr(scenario, "create_environment")
        assert hasattr(scenario, "broadcast_rewards")
        assert hasattr(scenario, "calculate_metrics")

        # Test the workflow
        env = scenario.create_environment()
        assert env is not None

        trajectory = Trajectory(
            steps=[{"action": "test"}],
            total_reward=10.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)
        assert len(rewards) == len(trajectory)

        metrics = scenario.calculate_metrics([trajectory])
        assert "tool_reliability" in metrics

    def test_multiple_scenarios_independent(self):
        """Test that multiple scenario instances are independent."""
        scenario1 = ConcreteScenario()
        scenario2 = MinimalScenario()

        assert scenario1.name != scenario2.name
        assert scenario1.description != scenario2.description

        # Each has independent success criteria
        criteria1 = scenario1.success_criteria()
        criteria2 = scenario2.success_criteria()

        assert criteria1 != criteria2

    def test_scenario_reusability(self):
        """Test that scenario can be reused for multiple trajectories."""
        scenario = ConcreteScenario()

        trajectories = [
            Trajectory(steps=[{"a": 1}], total_reward=5.0, success=True)
            for _ in range(10)
        ]

        # Should be able to broadcast rewards for all
        for traj in trajectories:
            rewards = scenario.broadcast_rewards(traj)
            assert len(rewards) == len(traj)

        # Should be able to calculate metrics from all
        metrics = scenario.calculate_metrics(trajectories)
        assert metrics["tool_reliability"] == 1.0  # All successful
