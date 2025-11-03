"""Tests for training result module.

This module contains comprehensive tests for TrainingMetrics and TrainingResult classes,
ensuring proper validation, serialization, and file operations.
"""

import json
import tempfile
from pathlib import Path

import pytest

from agentgym.core.config import TrainingConfig
from agentgym.core.result import TrainingMetrics, TrainingResult


class TestTrainingMetrics:
    """Test TrainingMetrics dataclass."""

    def test_initialization_valid(self):
        """Test creating metrics with valid values."""
        metrics = TrainingMetrics(
            tool_reliability=0.95,
            avg_tokens_used=250.5,
            avg_response_time=1.2,
            cost_reduction=0.35,
            episodes_completed=10000,
        )

        assert metrics.tool_reliability == 0.95
        assert metrics.avg_tokens_used == 250.5
        assert metrics.avg_response_time == 1.2
        assert metrics.cost_reduction == 0.35
        assert metrics.episodes_completed == 10000
        assert metrics.total_training_time == 0.0  # Default
        assert metrics.final_reward == 0.0  # Default
        assert metrics.convergence_episode is None  # Default

    def test_initialization_with_optional_fields(self):
        """Test creating metrics with optional fields."""
        metrics = TrainingMetrics(
            tool_reliability=0.96,
            avg_tokens_used=200.0,
            avg_response_time=0.8,
            cost_reduction=0.40,
            episodes_completed=5000,
            total_training_time=3600.0,
            final_reward=95.5,
            convergence_episode=4500,
        )

        assert metrics.total_training_time == 3600.0
        assert metrics.final_reward == 95.5
        assert metrics.convergence_episode == 4500

    def test_tool_reliability_below_zero_raises_error(self):
        """Test that tool_reliability < 0 raises ValueError."""
        with pytest.raises(ValueError, match="tool_reliability must be between"):
            TrainingMetrics(
                tool_reliability=-0.1,
                avg_tokens_used=100,
                avg_response_time=1.0,
                cost_reduction=0.3,
                episodes_completed=1000,
            )

    def test_tool_reliability_above_one_raises_error(self):
        """Test that tool_reliability > 1 raises ValueError."""
        with pytest.raises(ValueError, match="tool_reliability must be between"):
            TrainingMetrics(
                tool_reliability=1.5,
                avg_tokens_used=100,
                avg_response_time=1.0,
                cost_reduction=0.3,
                episodes_completed=1000,
            )

    def test_cost_reduction_below_zero_raises_error(self):
        """Test that cost_reduction < 0 raises ValueError."""
        with pytest.raises(ValueError, match="cost_reduction must be between"):
            TrainingMetrics(
                tool_reliability=0.9,
                avg_tokens_used=100,
                avg_response_time=1.0,
                cost_reduction=-0.1,
                episodes_completed=1000,
            )

    def test_cost_reduction_above_one_raises_error(self):
        """Test that cost_reduction > 1 raises ValueError."""
        with pytest.raises(ValueError, match="cost_reduction must be between"):
            TrainingMetrics(
                tool_reliability=0.9,
                avg_tokens_used=100,
                avg_response_time=1.0,
                cost_reduction=1.5,
                episodes_completed=1000,
            )

    def test_negative_tokens_raises_error(self):
        """Test that negative avg_tokens_used raises ValueError."""
        with pytest.raises(ValueError, match="avg_tokens_used must be non-negative"):
            TrainingMetrics(
                tool_reliability=0.9,
                avg_tokens_used=-100,
                avg_response_time=1.0,
                cost_reduction=0.3,
                episodes_completed=1000,
            )

    def test_negative_response_time_raises_error(self):
        """Test that negative avg_response_time raises ValueError."""
        with pytest.raises(ValueError, match="avg_response_time must be non-negative"):
            TrainingMetrics(
                tool_reliability=0.9,
                avg_tokens_used=100,
                avg_response_time=-1.0,
                cost_reduction=0.3,
                episodes_completed=1000,
            )

    def test_negative_episodes_raises_error(self):
        """Test that negative episodes_completed raises ValueError."""
        with pytest.raises(ValueError, match="episodes_completed must be non-negative"):
            TrainingMetrics(
                tool_reliability=0.9,
                avg_tokens_used=100,
                avg_response_time=1.0,
                cost_reduction=0.3,
                episodes_completed=-1000,
            )

    def test_boundary_values_tool_reliability(self):
        """Test boundary values for tool_reliability."""
        # Exactly 0.0
        metrics = TrainingMetrics(
            tool_reliability=0.0,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )
        assert metrics.tool_reliability == 0.0

        # Exactly 1.0
        metrics = TrainingMetrics(
            tool_reliability=1.0,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )
        assert metrics.tool_reliability == 1.0

    def test_meets_target_default_threshold(self):
        """Test meets_target with default threshold (0.95)."""
        # Above target
        metrics = TrainingMetrics(
            tool_reliability=0.96,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )
        assert metrics.meets_target() is True

        # Exactly at target
        metrics = TrainingMetrics(
            tool_reliability=0.95,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )
        assert metrics.meets_target() is True

        # Below target
        metrics = TrainingMetrics(
            tool_reliability=0.94,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )
        assert metrics.meets_target() is False

    def test_meets_target_custom_threshold(self):
        """Test meets_target with custom threshold."""
        metrics = TrainingMetrics(
            tool_reliability=0.92,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )

        assert metrics.meets_target(target_reliability=0.90) is True
        assert metrics.meets_target(target_reliability=0.92) is True
        assert metrics.meets_target(target_reliability=0.93) is False

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = TrainingMetrics(
            tool_reliability=0.95,
            avg_tokens_used=250.5,
            avg_response_time=1.2,
            cost_reduction=0.35,
            episodes_completed=10000,
            total_training_time=7200.0,
            final_reward=98.5,
            convergence_episode=9500,
        )

        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert metrics_dict["tool_reliability"] == 0.95
        assert metrics_dict["avg_tokens_used"] == 250.5
        assert metrics_dict["avg_response_time"] == 1.2
        assert metrics_dict["cost_reduction"] == 0.35
        assert metrics_dict["episodes_completed"] == 10000
        assert metrics_dict["total_training_time"] == 7200.0
        assert metrics_dict["final_reward"] == 98.5
        assert metrics_dict["convergence_episode"] == 9500


class TestTrainingResult:
    """Test TrainingResult dataclass."""

    def test_initialization(self):
        """Test creating training result."""
        config = TrainingConfig(scenario="customer_support")
        metrics = TrainingMetrics(
            tool_reliability=0.95,
            avg_tokens_used=200,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=10000,
        )

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/customer_support_v1.0",
        )

        assert result.config == config
        assert result.metrics == metrics
        assert result.trained_model_path == "./models/customer_support_v1.0"
        assert result.artifacts == {}  # Default
        assert isinstance(result.timestamp, str)
        assert result.version == "0.1.0"

    def test_initialization_with_artifacts(self):
        """Test creating result with custom artifacts."""
        config = TrainingConfig(scenario="test")
        metrics = TrainingMetrics(
            tool_reliability=0.9,
            avg_tokens_used=100,
            avg_response_time=0.5,
            cost_reduction=0.2,
            episodes_completed=5000,
        )

        artifacts = {
            "checkpoints": ["checkpoint_1000.pt", "checkpoint_5000.pt"],
            "logs": "training.log",
            "plots": ["reward_curve.png", "loss_curve.png"],
        }

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test",
            artifacts=artifacts,
        )

        assert result.artifacts == artifacts

    def test_to_dict(self):
        """Test converting result to dictionary."""
        config = TrainingConfig(scenario="test", framework="autogen", episodes=5000)
        metrics = TrainingMetrics(
            tool_reliability=0.92,
            avg_tokens_used=150,
            avg_response_time=0.8,
            cost_reduction=0.25,
            episodes_completed=5000,
        )

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test_v1",
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "config" in result_dict
        assert "metrics" in result_dict
        assert "trained_model_path" in result_dict
        assert "artifacts" in result_dict
        assert "timestamp" in result_dict
        assert "version" in result_dict

        assert result_dict["config"]["scenario"] == "test"
        assert result_dict["metrics"]["tool_reliability"] == 0.92
        assert result_dict["trained_model_path"] == "./models/test_v1"

    def test_from_dict(self):
        """Test creating result from dictionary."""
        data = {
            "config": {
                "scenario": "customer_support",
                "framework": "langchain",
                "episodes": 10000,
            },
            "metrics": {
                "tool_reliability": 0.95,
                "avg_tokens_used": 200.0,
                "avg_response_time": 1.0,
                "cost_reduction": 0.3,
                "episodes_completed": 10000,
                "total_training_time": 3600.0,
                "final_reward": 95.5,
                "convergence_episode": None,
            },
            "trained_model_path": "./models/customer_support_v1",
            "artifacts": {"logs": "training.log"},
            "timestamp": "2025-01-01T00:00:00",
            "version": "0.1.0",
        }

        result = TrainingResult.from_dict(data)

        assert result.config.scenario == "customer_support"
        assert result.config.framework == "langchain"
        assert result.metrics.tool_reliability == 0.95
        assert result.trained_model_path == "./models/customer_support_v1"
        assert result.artifacts == {"logs": "training.log"}
        assert result.timestamp == "2025-01-01T00:00:00"

    def test_roundtrip_to_dict_from_dict(self):
        """Test roundtrip conversion through dictionary."""
        config = TrainingConfig(
            scenario="test", framework="crewai", episodes=2000, learning_rate=0.0001
        )
        metrics = TrainingMetrics(
            tool_reliability=0.88,
            avg_tokens_used=180,
            avg_response_time=1.5,
            cost_reduction=0.20,
            episodes_completed=2000,
        )

        original = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test",
            artifacts={"checkpoint": "final.pt"},
        )

        # Convert to dict and back
        result_dict = original.to_dict()
        roundtrip = TrainingResult.from_dict(result_dict)

        assert roundtrip.config.scenario == original.config.scenario
        assert roundtrip.config.framework == original.config.framework
        assert roundtrip.metrics.tool_reliability == original.metrics.tool_reliability
        assert roundtrip.trained_model_path == original.trained_model_path
        assert roundtrip.artifacts == original.artifacts

    def test_save_and_load(self):
        """Test saving and loading result from file."""
        config = TrainingConfig(scenario="test_save_load")
        metrics = TrainingMetrics(
            tool_reliability=0.94,
            avg_tokens_used=220,
            avg_response_time=1.1,
            cost_reduction=0.28,
            episodes_completed=8000,
        )

        original = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test_save_load",
            artifacts={"log": "train.log"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "result.json"

            # Save
            original.save(str(file_path))

            # Verify file exists
            assert file_path.exists()

            # Load
            loaded = TrainingResult.load(str(file_path))

            assert loaded.config.scenario == original.config.scenario
            assert loaded.metrics.tool_reliability == original.metrics.tool_reliability
            assert loaded.trained_model_path == original.trained_model_path
            assert loaded.artifacts == original.artifacts

    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if they don't exist."""
        config = TrainingConfig(scenario="test")
        metrics = TrainingMetrics(
            tool_reliability=0.9,
            avg_tokens_used=100,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=1000,
        )

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Nested path that doesn't exist
            file_path = Path(tmpdir) / "nested" / "dir" / "result.json"

            result.save(str(file_path))

            assert file_path.exists()
            assert file_path.parent.exists()

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            TrainingResult.load("./nonexistent_file.json")

    def test_load_invalid_json_raises_error(self):
        """Test that loading invalid JSON raises JSONDecodeError."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("invalid json content {{{")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                TrainingResult.load(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_str_representation(self):
        """Test __str__ method."""
        config = TrainingConfig(scenario="customer_support")
        metrics = TrainingMetrics(
            tool_reliability=0.947,
            avg_tokens_used=200,
            avg_response_time=1.0,
            cost_reduction=0.3,
            episodes_completed=10000,
        )

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test",
        )

        str_repr = str(result)

        assert "customer_support" in str_repr
        assert "94.7%" in str_repr  # tool_reliability as percentage
        assert "10000" in str_repr  # episodes

    def test_repr_representation(self):
        """Test __repr__ method."""
        config = TrainingConfig(scenario="test", framework="langchain")
        metrics = TrainingMetrics(
            tool_reliability=0.952,
            avg_tokens_used=200,
            avg_response_time=1.0,
            cost_reduction=0.305,
            episodes_completed=5000,
        )

        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/test_v1",
        )

        repr_str = repr(result)

        assert "TrainingResult" in repr_str
        assert "test" in repr_str
        assert "langchain" in repr_str
        assert "0.952" in repr_str  # tool_reliability
        assert "0.305" in repr_str  # cost_reduction
        assert "5000" in repr_str  # episodes
        assert "./models/test_v1" in repr_str


class TestTrainingResultIntegration:
    """Integration tests combining multiple components."""

    def test_end_to_end_workflow(self):
        """Test complete workflow: create, save, load, validate."""
        # Create config
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=10000,
            gpu_provider="runpod",
        )

        # Create metrics
        metrics = TrainingMetrics(
            tool_reliability=0.96,
            avg_tokens_used=245.8,
            avg_response_time=1.15,
            cost_reduction=0.38,
            episodes_completed=10000,
            total_training_time=7200.5,
            final_reward=97.2,
            convergence_episode=9200,
        )

        # Create result
        result = TrainingResult(
            config=config,
            metrics=metrics,
            trained_model_path="./models/customer_support_v1.2",
            artifacts={
                "checkpoints": ["cp_5000.pt", "cp_10000.pt"],
                "training_log": "training_20250101.log",
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save to file
            save_path = Path(tmpdir) / "results" / "training_result.json"
            result.save(str(save_path))

            # Load from file
            loaded = TrainingResult.load(str(save_path))

            # Verify all fields match
            assert loaded.config.scenario == config.scenario
            assert loaded.config.framework == config.framework
            assert loaded.config.episodes == config.episodes
            assert loaded.metrics.tool_reliability == metrics.tool_reliability
            assert loaded.metrics.meets_target()
            assert loaded.trained_model_path == result.trained_model_path
            assert loaded.artifacts == result.artifacts

    def test_multiple_results_different_configs(self):
        """Test handling multiple results with different configurations."""
        results = []

        for i, scenario in enumerate(["customer_support", "code_review", "qa_testing"]):
            config = TrainingConfig(scenario=scenario, episodes=(i + 1) * 5000)
            metrics = TrainingMetrics(
                tool_reliability=0.90 + (i * 0.02),
                avg_tokens_used=200 - (i * 10),
                avg_response_time=1.0 - (i * 0.1),
                cost_reduction=0.3 + (i * 0.05),
                episodes_completed=(i + 1) * 5000,
            )
            result = TrainingResult(
                config=config,
                metrics=metrics,
                trained_model_path=f"./models/{scenario}_v1",
            )
            results.append(result)

        # Verify each result is distinct
        assert len(results) == 3
        assert results[0].config.scenario == "customer_support"
        assert results[1].config.scenario == "code_review"
        assert results[2].config.scenario == "qa_testing"

        assert results[0].metrics.tool_reliability == pytest.approx(0.90)
        assert results[1].metrics.tool_reliability == pytest.approx(0.92)
        assert results[2].metrics.tool_reliability == pytest.approx(0.94)
