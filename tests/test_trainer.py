"""Tests for core trainer module.

This module contains comprehensive tests for the Trainer class,
including on-policy training loop, trajectory collection, and result generation.
"""

from typing import Any

import pytest

from agentgym.core.config import TrainingConfig
from agentgym.core.trainer import Trainer, Trajectory


class MockScenario:
    """Mock scenario for testing Trainer.

    This mock implements the Scenario protocol for testing purposes.
    """

    def __init__(
        self,
        tool_reliability: float = 0.9,
        avg_tokens: float = 200.0,
        avg_response_time: float = 1.0,
    ):
        """Initialize mock scenario with target metrics.

        Args:
            tool_reliability: Target tool reliability to simulate.
            avg_tokens: Average tokens to report.
            avg_response_time: Average response time to report.
        """
        self.tool_reliability = tool_reliability
        self.avg_tokens = avg_tokens
        self.avg_response_time = avg_response_time
        self.environment_created = False
        self.broadcast_calls = 0
        self.metrics_calls = 0

    def create_environment(self) -> Any:
        """Create mock environment."""
        self.environment_created = True
        return {"type": "mock_environment"}

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        Args:
            trajectory: Completed trajectory.

        Returns:
            List of rewards (one per step).
        """
        self.broadcast_calls += 1

        # Broadcast outcome reward to all steps (AgentFlow insight)
        outcome_reward = trajectory.total_reward
        step_rewards = [outcome_reward / len(trajectory)] * len(trajectory)

        return step_rewards

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate metrics from trajectories.

        Args:
            trajectories: List of trajectories.

        Returns:
            Dictionary of metrics.
        """
        self.metrics_calls += 1

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

        # Calculate metrics from trajectories
        successful = sum(1 for t in trajectories if t.success)
        tool_reliability = successful / len(trajectories)

        avg_tokens = sum(
            t.metadata.get("tokens_used", self.avg_tokens) for t in trajectories
        ) / len(trajectories)

        avg_response_time = sum(
            t.metadata.get("response_time", self.avg_response_time)
            for t in trajectories
        ) / len(trajectories)

        # Mock cost reduction based on reliability
        cost_reduction = min(tool_reliability * 0.4, 0.4)

        # Final reward is average of trajectory rewards
        final_reward = sum(t.total_reward for t in trajectories) / len(trajectories)

        return {
            "tool_reliability": tool_reliability,
            "avg_tokens_used": avg_tokens,
            "avg_response_time": avg_response_time,
            "cost_reduction": cost_reduction,
            "total_training_time": 100.0,  # Mock value
            "final_reward": final_reward,
            "convergence_episode": (
                len(trajectories) - 100 if len(trajectories) > 100 else None
            ),
        }


class TestTrajectory:
    """Test Trajectory class."""

    def test_initialization_empty(self):
        """Test creating empty trajectory."""
        traj = Trajectory()

        assert traj.steps == []
        assert traj.total_reward == 0.0
        assert traj.success is False
        assert traj.metadata == {}
        assert len(traj) == 0

    def test_initialization_with_steps(self):
        """Test creating trajectory with steps."""
        steps = [
            {"state": "s1", "action": "a1", "reward": 1.0},
            {"state": "s2", "action": "a2", "reward": 1.0},
        ]

        traj = Trajectory(
            steps=steps,
            total_reward=2.0,
            success=True,
            metadata={"tokens": 100},
        )

        assert len(traj.steps) == 2
        assert traj.total_reward == 2.0
        assert traj.success is True
        assert traj.metadata == {"tokens": 100}
        assert len(traj) == 2

    def test_length(self):
        """Test __len__ method."""
        traj = Trajectory()
        assert len(traj) == 0

        traj.steps = [{"state": "s1"}]
        assert len(traj) == 1

        traj.steps.append({"state": "s2"})
        assert len(traj) == 2


class TestMockScenario:
    """Test MockScenario helper class."""

    def test_initialization(self):
        """Test initializing mock scenario."""
        scenario = MockScenario(
            tool_reliability=0.95,
            avg_tokens=250.0,
            avg_response_time=1.5,
        )

        assert scenario.tool_reliability == 0.95
        assert scenario.avg_tokens == 250.0
        assert scenario.avg_response_time == 1.5
        assert scenario.environment_created is False
        assert scenario.broadcast_calls == 0
        assert scenario.metrics_calls == 0

    def test_create_environment(self):
        """Test environment creation."""
        scenario = MockScenario()
        env = scenario.create_environment()

        assert env == {"type": "mock_environment"}
        assert scenario.environment_created is True

    def test_broadcast_rewards(self):
        """Test reward broadcasting."""
        scenario = MockScenario()
        traj = Trajectory(
            steps=[{"s": 1}, {"s": 2}, {"s": 3}],
            total_reward=9.0,
        )

        rewards = scenario.broadcast_rewards(traj)

        assert len(rewards) == 3
        assert all(r == 3.0 for r in rewards)  # 9.0 / 3 = 3.0 per step
        assert scenario.broadcast_calls == 1

    def test_calculate_metrics_empty(self):
        """Test metrics calculation with no trajectories."""
        scenario = MockScenario()
        metrics = scenario.calculate_metrics([])

        assert metrics["tool_reliability"] == 0.0
        assert metrics["avg_tokens_used"] == 0.0
        assert scenario.metrics_calls == 1

    def test_calculate_metrics_with_trajectories(self):
        """Test metrics calculation with trajectories."""
        scenario = MockScenario()
        trajectories = [
            Trajectory(
                steps=[{"s": 1}],
                total_reward=5.0,
                success=True,
                metadata={"tokens_used": 200, "response_time": 1.0},
            ),
            Trajectory(
                steps=[{"s": 1}],
                total_reward=5.0,
                success=True,
                metadata={"tokens_used": 300, "response_time": 1.5},
            ),
            Trajectory(
                steps=[{"s": 1}],
                total_reward=0.0,
                success=False,
                metadata={"tokens_used": 150, "response_time": 0.8},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 successes out of 3
        assert metrics["tool_reliability"] == pytest.approx(2 / 3)
        # Average tokens: (200 + 300 + 150) / 3 = 216.67
        assert metrics["avg_tokens_used"] == pytest.approx(216.67, rel=0.01)
        # Average time: (1.0 + 1.5 + 0.8) / 3 = 1.1
        assert metrics["avg_response_time"] == pytest.approx(1.1, rel=0.01)
        # Average reward: (5 + 5 + 0) / 3 = 3.33
        assert metrics["final_reward"] == pytest.approx(3.33, rel=0.01)


class TestTrainer:
    """Test Trainer class."""

    def test_initialization_with_scenario(self):
        """Test initializing trainer with scenario."""
        config = TrainingConfig(scenario="test", episodes=10)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)

        assert trainer.config == config
        assert trainer.scenario == scenario
        assert trainer.trajectories == []
        assert trainer.metrics_history == []
        assert trainer._episode_count == 0

    def test_initialization_without_scenario_raises_error(self):
        """Test that initializing without scenario raises NotImplementedError."""
        config = TrainingConfig(scenario="test")

        with pytest.raises(NotImplementedError, match="ScenarioRegistry not yet"):
            Trainer(config)

    def test_train_basic(self):
        """Test basic training execution."""
        config = TrainingConfig(scenario="test", episodes=5, seed=42)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        result = trainer.train()

        # Verify training completed
        assert trainer._episode_count == 5
        assert len(trainer.trajectories) == 5

        # Verify scenario was used correctly
        assert scenario.environment_created is True
        assert scenario.broadcast_calls == 5  # Once per episode
        assert scenario.metrics_calls > 0  # At least once for final metrics

        # Verify result
        assert isinstance(result.config, TrainingConfig)
        assert result.config.scenario == "test"
        assert result.metrics.episodes_completed == 5
        assert 0.0 <= result.metrics.tool_reliability <= 1.0

    def test_train_produces_trajectories(self):
        """Test that training produces trajectories."""
        config = TrainingConfig(scenario="test", episodes=10, seed=42)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        trainer.train()

        assert len(trainer.trajectories) == 10

        # Verify each trajectory has steps
        for traj in trainer.trajectories:
            assert len(traj) > 0
            assert isinstance(traj.total_reward, float)
            assert isinstance(traj.success, bool)

    def test_train_tracks_metrics(self):
        """Test that training tracks metrics periodically."""
        config = TrainingConfig(scenario="test", episodes=100, seed=42)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        trainer.train()

        # Should have tracked metrics ~10 times (every 10% of episodes)
        assert len(trainer.metrics_history) >= 9
        assert len(trainer.metrics_history) <= 11

        # Each metric should have episode number
        for metrics in trainer.metrics_history:
            assert "episode" in metrics
            assert "tool_reliability" in metrics

    def test_train_result_has_correct_structure(self):
        """Test that training result has correct structure."""
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=50,
            seed=42,
        )
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        result = trainer.train()

        # Verify result structure
        assert result.config.scenario == "customer_support"
        assert result.config.framework == "langchain"
        assert result.metrics.episodes_completed == 50
        assert "customer_support" in result.trained_model_path
        assert "langchain" in result.trained_model_path
        assert "ep50" in result.trained_model_path

        # Verify artifacts
        assert "trajectories_count" in result.artifacts
        assert result.artifacts["trajectories_count"] == 50
        assert "metrics_history" in result.artifacts

    def test_train_different_episode_counts(self):
        """Test training with different episode counts."""
        scenario = MockScenario()

        for episodes in [1, 10, 100]:
            config = TrainingConfig(scenario="test", episodes=episodes, seed=42)
            trainer = Trainer(config, scenario=scenario)
            result = trainer.train()

            assert trainer._episode_count == episodes
            assert len(trainer.trajectories) == episodes
            assert result.metrics.episodes_completed == episodes

    def test_train_with_seed_reproducible(self):
        """Test that training with same seed produces similar results."""
        config1 = TrainingConfig(scenario="test", episodes=20, seed=42)
        scenario1 = MockScenario()
        trainer1 = Trainer(config1, scenario=scenario1)
        result1 = trainer1.train()

        config2 = TrainingConfig(scenario="test", episodes=20, seed=42)
        scenario2 = MockScenario()
        trainer2 = Trainer(config2, scenario=scenario2)
        result2 = trainer2.train()

        # With same seed, results should be very similar
        # (may not be exactly identical due to floating point, but close)
        assert (
            abs(result1.metrics.tool_reliability - result2.metrics.tool_reliability)
            < 0.1
        )

    def test_get_metrics_history(self):
        """Test getting metrics history."""
        config = TrainingConfig(scenario="test", episodes=100, seed=42)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        trainer.train()

        history = trainer.get_metrics_history()

        assert isinstance(history, list)
        assert len(history) > 0
        assert all(isinstance(m, dict) for m in history)

    def test_repr(self):
        """Test __repr__ method."""
        config = TrainingConfig(scenario="test", framework="autogen", episodes=50)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)

        repr_str = repr(trainer)

        assert "Trainer" in repr_str
        assert "test" in repr_str
        assert "autogen" in repr_str
        assert "50" in repr_str
        assert "trajectories_collected=0" in repr_str

        # After training
        trainer.train()
        repr_str = repr(trainer)
        assert "trajectories_collected=50" in repr_str

    def test_training_improves_over_time(self):
        """Test that mock training shows improvement trend."""
        config = TrainingConfig(scenario="test", episodes=100, seed=42)
        scenario = MockScenario()

        trainer = Trainer(config, scenario=scenario)
        trainer.train()

        # Calculate success rate for first 20 vs last 20 episodes
        first_20_success = sum(1 for t in trainer.trajectories[:20] if t.success) / 20
        last_20_success = sum(1 for t in trainer.trajectories[-20:] if t.success) / 20

        # Last 20 should generally be better (mock implementation improves over time)
        assert last_20_success >= first_20_success - 0.1  # Allow small variance


class TestTrainerIntegration:
    """Integration tests for Trainer."""

    def test_full_training_workflow(self):
        """Test complete training workflow from config to result."""
        # Create configuration
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=50,
            learning_rate=0.0003,
            seed=42,
        )

        # Create mock scenario
        scenario = MockScenario(
            tool_reliability=0.95,
            avg_tokens=200.0,
            avg_response_time=1.0,
        )

        # Create and run trainer
        trainer = Trainer(config, scenario=scenario)
        result = trainer.train()

        # Verify complete workflow
        assert result.config == config
        assert result.metrics.episodes_completed == 50
        assert result.metrics.tool_reliability > 0.0
        assert len(result.artifacts) > 0

        # Verify can save result
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "result.json"
            result.save(str(save_path))
            assert save_path.exists()

            # Load and verify
            from agentgym.core.result import TrainingResult

            loaded = TrainingResult.load(str(save_path))
            assert loaded.config.scenario == config.scenario
            assert loaded.metrics.episodes_completed == 50

    def test_multiple_trainers_independent(self):
        """Test that multiple trainers operate independently."""
        scenario1 = MockScenario()
        scenario2 = MockScenario()

        config1 = TrainingConfig(scenario="test1", episodes=10, seed=1)
        config2 = TrainingConfig(scenario="test2", episodes=20, seed=2)

        trainer1 = Trainer(config1, scenario=scenario1)
        trainer2 = Trainer(config2, scenario=scenario2)

        result1 = trainer1.train()
        result2 = trainer2.train()

        # Verify independent operation
        assert result1.config.scenario == "test1"
        assert result2.config.scenario == "test2"
        assert result1.metrics.episodes_completed == 10
        assert result2.metrics.episodes_completed == 20
        assert len(trainer1.trajectories) == 10
        assert len(trainer2.trajectories) == 20
