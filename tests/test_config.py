"""Tests for training configuration module.

This module contains comprehensive tests for the TrainingConfig class,
ensuring proper validation, serialization, and default behavior.
"""

import json

import pytest
from pydantic import ValidationError

from agentgym.core.config import TrainingConfig


class TestTrainingConfigDefaults:
    """Test default values and initialization."""

    def test_minimal_config(self):
        """Test creating config with only required fields."""
        config = TrainingConfig(scenario="customer_support")

        assert config.scenario == "customer_support"
        assert config.framework == "langchain"
        assert config.episodes == 10000
        assert config.gpu_provider == "auto"
        assert config.gpu_type == "auto"
        assert config.learning_rate == 0.0003
        assert config.discount_factor == 0.95
        assert config.batch_size == 64
        assert config.max_steps_per_episode == 100
        assert config.checkpoint_interval == 1000
        assert config.verbose is True
        assert config.seed is None

    def test_all_defaults(self):
        """Test that all default values are set correctly."""
        config = TrainingConfig(scenario="test_scenario")

        # Verify core defaults
        assert config.framework == "langchain"
        assert config.episodes == 10000
        assert config.gpu_provider == "auto"

        # Verify RL hyperparameter defaults
        assert config.learning_rate == 0.0003
        assert config.discount_factor == 0.95
        assert config.batch_size == 64

    def test_custom_values(self):
        """Test creating config with custom values."""
        config = TrainingConfig(
            scenario="code_review",
            framework="autogen",
            episodes=5000,
            gpu_provider="runpod",
            gpu_type="RTX_4090",
            learning_rate=0.0001,
            discount_factor=0.99,
            batch_size=128,
            verbose=False,
            seed=42,
        )

        assert config.scenario == "code_review"
        assert config.framework == "autogen"
        assert config.episodes == 5000
        assert config.gpu_provider == "runpod"
        assert config.gpu_type == "RTX_4090"
        assert config.learning_rate == 0.0001
        assert config.discount_factor == 0.99
        assert config.batch_size == 128
        assert config.verbose is False
        assert config.seed == 42


class TestTrainingConfigValidation:
    """Test validation rules and constraints."""

    def test_missing_scenario_raises_error(self):
        """Test that missing scenario raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingConfig()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("scenario",) for error in errors)

    def test_empty_scenario_raises_error(self):
        """Test that empty scenario string raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="")

    def test_invalid_framework_raises_error(self):
        """Test that invalid framework raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", framework="invalid_framework")

    def test_valid_frameworks(self):
        """Test all valid framework values."""
        for framework in ["langchain", "autogen", "crewai"]:
            config = TrainingConfig(scenario="test", framework=framework)
            assert config.framework == framework

    def test_negative_episodes_raises_error(self):
        """Test that negative episodes raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", episodes=-100)

    def test_zero_episodes_raises_error(self):
        """Test that zero episodes raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", episodes=0)

    def test_positive_episodes(self):
        """Test that positive episodes are accepted."""
        config = TrainingConfig(scenario="test", episodes=1)
        assert config.episodes == 1

    def test_negative_learning_rate_raises_error(self):
        """Test that negative learning rate raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", learning_rate=-0.001)

    def test_zero_learning_rate_raises_error(self):
        """Test that zero learning rate raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", learning_rate=0)

    def test_discount_factor_too_low_raises_error(self):
        """Test that discount factor <= 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", discount_factor=0)

        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", discount_factor=-0.5)

    def test_discount_factor_too_high_raises_error(self):
        """Test that discount factor >= 1 raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", discount_factor=1.0)

        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", discount_factor=1.5)

    def test_valid_discount_factor_range(self):
        """Test valid discount factor values."""
        for gamma in [0.001, 0.5, 0.9, 0.95, 0.99, 0.999]:
            config = TrainingConfig(scenario="test", discount_factor=gamma)
            assert config.discount_factor == gamma

    def test_invalid_gpu_provider_raises_error(self):
        """Test that invalid GPU provider raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", gpu_provider="invalid")

    def test_valid_gpu_providers(self):
        """Test all valid GPU provider values."""
        for provider in ["auto", "local", "runpod", "lambda", "cloud"]:
            config = TrainingConfig(scenario="test", gpu_provider=provider)
            assert config.gpu_provider == provider

    def test_negative_batch_size_raises_error(self):
        """Test that negative batch size raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", batch_size=-1)

    def test_zero_batch_size_raises_error(self):
        """Test that zero batch size raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", batch_size=0)

    def test_negative_checkpoint_interval_raises_error(self):
        """Test that negative checkpoint interval raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", checkpoint_interval=-1)

    def test_zero_checkpoint_interval_disables_checkpoints(self):
        """Test that zero checkpoint interval is valid (disables checkpoints)."""
        config = TrainingConfig(scenario="test", checkpoint_interval=0)
        assert config.checkpoint_interval == 0

    def test_negative_seed_raises_error(self):
        """Test that negative seed raises ValidationError."""
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test", seed=-1)

    def test_scenario_name_validation_lowercase(self):
        """Test that scenario names are converted to lowercase."""
        config = TrainingConfig(scenario="CustomerSupport")
        assert config.scenario == "customersupport"

    def test_scenario_name_validation_valid_characters(self):
        """Test valid scenario name characters."""
        valid_names = [
            "customer_support",
            "code-review",
            "qa_testing_123",
            "test-scenario-v2",
        ]
        for name in valid_names:
            config = TrainingConfig(scenario=name)
            assert config.scenario == name.lower()

    def test_scenario_name_validation_invalid_characters(self):
        """Test that invalid characters in scenario name raise ValidationError."""
        invalid_names = [
            "scenario!",
            "test@scenario",
            "scenario with spaces",
            "scenario$$$",
        ]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                TrainingConfig(scenario=name)


class TestTrainingConfigSerialization:
    """Test serialization and deserialization."""

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = TrainingConfig(
            scenario="test_scenario",
            framework="autogen",
            episodes=5000,
        )

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["scenario"] == "test_scenario"
        assert config_dict["framework"] == "autogen"
        assert config_dict["episodes"] == 5000
        assert "learning_rate" in config_dict
        assert "discount_factor" in config_dict

    def test_to_json(self):
        """Test converting config to JSON string."""
        config = TrainingConfig(
            scenario="test_scenario",
            framework="langchain",
            episodes=1000,
        )

        json_str = config.to_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["scenario"] == "test_scenario"
        assert parsed["framework"] == "langchain"
        assert parsed["episodes"] == 1000

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "scenario": "customer_support",
            "framework": "crewai",
            "episodes": 2000,
            "learning_rate": 0.0001,
        }

        config = TrainingConfig.from_dict(data)

        assert config.scenario == "customer_support"
        assert config.framework == "crewai"
        assert config.episodes == 2000
        assert config.learning_rate == 0.0001

    def test_from_json(self):
        """Test creating config from JSON string."""
        json_str = json.dumps(
            {
                "scenario": "qa_testing",
                "framework": "autogen",
                "episodes": 3000,
                "gpu_provider": "runpod",
            }
        )

        config = TrainingConfig.from_json(json_str)

        assert config.scenario == "qa_testing"
        assert config.framework == "autogen"
        assert config.episodes == 3000
        assert config.gpu_provider == "runpod"

    def test_roundtrip_dict(self):
        """Test roundtrip conversion through dictionary."""
        original = TrainingConfig(
            scenario="test",
            framework="langchain",
            episodes=1234,
            learning_rate=0.0005,
        )

        roundtrip = TrainingConfig.from_dict(original.to_dict())

        assert roundtrip.scenario == original.scenario
        assert roundtrip.framework == original.framework
        assert roundtrip.episodes == original.episodes
        assert roundtrip.learning_rate == original.learning_rate

    def test_roundtrip_json(self):
        """Test roundtrip conversion through JSON."""
        original = TrainingConfig(
            scenario="test",
            framework="autogen",
            episodes=5678,
            discount_factor=0.99,
        )

        roundtrip = TrainingConfig.from_json(original.to_json())

        assert roundtrip.scenario == original.scenario
        assert roundtrip.framework == original.framework
        assert roundtrip.episodes == original.episodes
        assert roundtrip.discount_factor == original.discount_factor


class TestTrainingConfigStringRepresentation:
    """Test string representations."""

    def test_str(self):
        """Test __str__ method."""
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=10000,
        )

        str_repr = str(config)

        assert "customer_support" in str_repr
        assert "langchain" in str_repr
        assert "10000" in str_repr

    def test_repr(self):
        """Test __repr__ method."""
        config = TrainingConfig(
            scenario="test",
            framework="autogen",
            episodes=5000,
            learning_rate=0.0001,
        )

        repr_str = repr(config)

        assert "TrainingConfig" in repr_str
        assert "test" in repr_str
        assert "autogen" in repr_str
        assert "5000" in repr_str
        assert "0.0001" in repr_str


class TestTrainingConfigExtensibility:
    """Test extensibility features."""

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed (for extensibility)."""
        config = TrainingConfig(
            scenario="test",
            custom_field="custom_value",
            another_field=123,
        )

        # Extra fields should be accessible
        assert config.custom_field == "custom_value"  # type: ignore
        assert config.another_field == 123  # type: ignore

    def test_validate_on_assignment(self):
        """Test that validation occurs on attribute assignment."""
        config = TrainingConfig(scenario="test")

        # Valid assignment
        config.episodes = 5000
        assert config.episodes == 5000

        # Invalid assignment should raise ValidationError
        with pytest.raises(ValidationError):
            config.episodes = -100

        with pytest.raises(ValidationError):
            config.learning_rate = 0


class TestTrainingConfigEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_episodes(self):
        """Test handling of very large episode counts."""
        config = TrainingConfig(scenario="test", episodes=1_000_000)
        assert config.episodes == 1_000_000

    def test_very_small_learning_rate(self):
        """Test handling of very small learning rates."""
        config = TrainingConfig(scenario="test", learning_rate=0.000001)
        assert config.learning_rate == 0.000001

    def test_discount_factor_near_boundaries(self):
        """Test discount factor near boundary values."""
        config = TrainingConfig(scenario="test", discount_factor=0.0001)
        assert config.discount_factor == 0.0001

        config = TrainingConfig(scenario="test", discount_factor=0.9999)
        assert config.discount_factor == 0.9999

    def test_special_characters_in_scenario_name(self):
        """Test that special characters in scenario name raise ValidationError."""
        # Note: Unicode letters are allowed in Python 3, but special chars are not
        with pytest.raises(ValidationError):
            TrainingConfig(scenario="test@scenario")  # @ is not allowed

    def test_max_seed_value(self):
        """Test large seed values."""
        config = TrainingConfig(scenario="test", seed=2**31 - 1)
        assert config.seed == 2**31 - 1

    def test_none_seed_default(self):
        """Test that None seed is the default."""
        config = TrainingConfig(scenario="test")
        assert config.seed is None

        config = TrainingConfig(scenario="test", seed=None)
        assert config.seed is None


class TestTrainingConfigRealWorldScenarios:
    """Test realistic usage scenarios."""

    def test_customer_support_config(self):
        """Test typical customer support scenario configuration."""
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=10000,
            gpu_provider="auto",
        )

        assert config.scenario == "customer_support"
        assert config.framework == "langchain"
        assert config.episodes == 10000

    def test_code_review_config_with_custom_gpu(self):
        """Test code review scenario with RunPod GPU."""
        config = TrainingConfig(
            scenario="code_review",
            framework="autogen",
            episodes=5000,
            gpu_provider="runpod",
            gpu_type="RTX_4090",
            learning_rate=0.0001,
        )

        assert config.gpu_provider == "runpod"
        assert config.gpu_type == "RTX_4090"

    def test_quick_test_run_config(self):
        """Test configuration for quick test runs."""
        config = TrainingConfig(
            scenario="test_scenario",
            episodes=100,
            checkpoint_interval=0,  # No checkpoints for quick tests
            verbose=True,
            seed=42,  # Reproducible
        )

        assert config.episodes == 100
        assert config.checkpoint_interval == 0
        assert config.seed == 42

    def test_production_training_config(self):
        """Test configuration for production training."""
        config = TrainingConfig(
            scenario="customer_support",
            framework="langchain",
            episodes=50000,
            gpu_provider="cloud",
            learning_rate=0.0003,
            discount_factor=0.95,
            batch_size=128,
            checkpoint_interval=500,
            verbose=True,
        )

        assert config.episodes == 50000
        assert config.gpu_provider == "cloud"
        assert config.batch_size == 128
        assert config.checkpoint_interval == 500
