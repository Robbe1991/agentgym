"""Tests for scenario registry module.

This module contains comprehensive tests for the ScenarioRegistry system,
including scenario loading, listing, registration, and error handling.
"""

import pytest

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.base import Scenario
from agentgym.scenarios.registry import ScenarioNotFoundError, ScenarioRegistry


class MockScenario(Scenario):
    """Mock scenario for testing registry."""

    name = "mock"
    description = "Mock scenario for testing"
    difficulty = "beginner"

    def create_environment(self):
        """Create mock environment."""
        return {"type": "mock"}

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast rewards."""
        return [1.0] * len(trajectory)

    def success_criteria(self) -> dict[str, float]:
        """Define success criteria."""
        return {"tool_reliability": 0.9}


class AdvancedMockScenario(Scenario):
    """Advanced mock scenario for testing."""

    name = "advanced_mock"
    description = "Advanced mock scenario"
    difficulty = "advanced"

    def create_environment(self):
        """Create mock environment."""
        return {"type": "advanced_mock"}

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast rewards."""
        return [2.0] * len(trajectory)

    def success_criteria(self) -> dict[str, float]:
        """Define success criteria."""
        return {"tool_reliability": 0.95}


class TestScenarioNotFoundError:
    """Test ScenarioNotFoundError exception."""

    def test_initialization(self):
        """Test creating error with scenario name and available scenarios."""
        error = ScenarioNotFoundError("test", ["scenario1", "scenario2"])

        assert error.scenario_name == "test"
        assert error.available_scenarios == ["scenario1", "scenario2"]

    def test_error_message_with_available_scenarios(self):
        """Test error message includes available scenarios."""
        error = ScenarioNotFoundError("missing", ["a", "b", "c"])

        error_msg = str(error)
        assert "missing" in error_msg
        assert "a, b, c" in error_msg

    def test_error_message_with_no_available_scenarios(self):
        """Test error message when no scenarios are available."""
        error = ScenarioNotFoundError("test", [])

        error_msg = str(error)
        assert "test" in error_msg
        assert "none" in error_msg


class TestScenarioRegistry:
    """Test ScenarioRegistry class."""

    def setup_method(self):
        """Clear registry before each test."""
        ScenarioRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ScenarioRegistry.clear()

    def test_initial_state_has_built_ins(self):
        """Test registry starts with built-in scenarios after clear."""
        scenarios = ScenarioRegistry.list()
        # After clear, built-ins are lazily reloaded on first access
        assert len(scenarios) >= 1  # At least customer_support
        assert any(s["name"] == "customer_support" for s in scenarios)

    def test_register_scenario(self):
        """Test registering a scenario."""
        ScenarioRegistry.register("mock", MockScenario)

        assert ScenarioRegistry.is_registered("mock")
        assert "mock" in ScenarioRegistry.BUILT_IN

    def test_register_multiple_scenarios(self):
        """Test registering multiple scenarios."""
        ScenarioRegistry.register("mock", MockScenario)
        ScenarioRegistry.register("advanced_mock", AdvancedMockScenario)

        assert ScenarioRegistry.is_registered("mock")
        assert ScenarioRegistry.is_registered("advanced_mock")
        assert len(ScenarioRegistry.BUILT_IN) == 2

    def test_register_duplicate_name_raises_error(self):
        """Test that registering duplicate name raises ValueError."""
        ScenarioRegistry.register("mock", MockScenario)

        with pytest.raises(ValueError, match="already registered"):
            ScenarioRegistry.register("mock", AdvancedMockScenario)

    def test_register_non_scenario_class_raises_error(self):
        """Test that registering non-Scenario class raises ValueError."""

        class NotAScenario:
            """Not a scenario class."""

            pass

        with pytest.raises(ValueError, match="must be a subclass of Scenario"):
            ScenarioRegistry.register("invalid", NotAScenario)  # type: ignore

    def test_load_registered_scenario(self):
        """Test loading a registered scenario."""
        ScenarioRegistry.register("mock", MockScenario)

        scenario = ScenarioRegistry.load("mock")

        assert isinstance(scenario, MockScenario)
        assert scenario.name == "mock"
        assert scenario.description == "Mock scenario for testing"

    def test_load_creates_new_instance(self):
        """Test that load creates a new instance each time."""
        ScenarioRegistry.register("mock", MockScenario)

        scenario1 = ScenarioRegistry.load("mock")
        scenario2 = ScenarioRegistry.load("mock")

        assert scenario1 is not scenario2
        assert isinstance(scenario1, MockScenario)
        assert isinstance(scenario2, MockScenario)

    def test_load_nonexistent_scenario_raises_error(self):
        """Test loading non-existent scenario raises ScenarioNotFoundError."""
        ScenarioRegistry.register("mock", MockScenario)

        with pytest.raises(ScenarioNotFoundError) as exc_info:
            ScenarioRegistry.load("nonexistent")

        error = exc_info.value
        assert error.scenario_name == "nonexistent"
        assert "mock" in error.available_scenarios

    def test_load_from_empty_registry_raises_error(self):
        """Test loading non-existent scenario raises ScenarioNotFoundError."""
        with pytest.raises(ScenarioNotFoundError) as exc_info:
            ScenarioRegistry.load("anything")

        error = exc_info.value
        assert error.scenario_name == "anything"
        # Built-ins are lazily loaded, so customer_support will be available
        assert "customer_support" in error.available_scenarios

    def test_list_empty_registry(self):
        """Test listing scenarios includes built-ins."""
        scenarios = ScenarioRegistry.list()

        # Built-ins are lazily loaded
        assert len(scenarios) >= 1
        assert any(s["name"] == "customer_support" for s in scenarios)

    def test_list_single_scenario(self):
        """Test listing registered scenario plus built-ins."""
        ScenarioRegistry.register("mock", MockScenario)

        scenarios = ScenarioRegistry.list()

        # Should have mock + built-ins (customer_support)
        assert len(scenarios) >= 2
        mock_scenario = next((s for s in scenarios if s["name"] == "mock"), None)
        assert mock_scenario is not None
        assert mock_scenario["description"] == "Mock scenario for testing"
        assert mock_scenario["difficulty"] == "beginner"

    def test_list_multiple_scenarios(self):
        """Test listing multiple registered scenarios plus built-ins."""
        ScenarioRegistry.register("mock", MockScenario)
        ScenarioRegistry.register("advanced_mock", AdvancedMockScenario)

        scenarios = ScenarioRegistry.list()

        # Should have mock + advanced_mock + built-ins (customer_support)
        assert len(scenarios) >= 3

        # Find scenarios by name
        mock_info = next(s for s in scenarios if s["name"] == "mock")
        advanced_info = next(s for s in scenarios if s["name"] == "advanced_mock")

        assert mock_info["difficulty"] == "beginner"
        assert advanced_info["difficulty"] == "advanced"

    def test_is_registered_true(self):
        """Test is_registered returns True for registered scenario."""
        ScenarioRegistry.register("mock", MockScenario)

        assert ScenarioRegistry.is_registered("mock") is True

    def test_is_registered_false(self):
        """Test is_registered returns False for unregistered scenario."""
        assert ScenarioRegistry.is_registered("nonexistent") is False

    def test_unregister_scenario(self):
        """Test unregistering a scenario."""
        ScenarioRegistry.register("mock", MockScenario)
        assert ScenarioRegistry.is_registered("mock")

        ScenarioRegistry.unregister("mock")

        assert ScenarioRegistry.is_registered("mock") is False
        assert "mock" not in ScenarioRegistry.BUILT_IN

    def test_unregister_nonexistent_scenario_raises_error(self):
        """Test unregistering non-existent scenario raises error."""
        with pytest.raises(ScenarioNotFoundError):
            ScenarioRegistry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing all scenarios."""
        ScenarioRegistry.register("mock", MockScenario)
        ScenarioRegistry.register("advanced_mock", AdvancedMockScenario)

        # Should have at least mock + advanced_mock (built-ins may or may not be loaded yet)
        assert len(ScenarioRegistry.BUILT_IN) >= 2

        ScenarioRegistry.clear()

        # BUILT_IN dict is cleared
        assert len(ScenarioRegistry.BUILT_IN) == 0
        # But list() will lazily reload built-ins
        scenarios = ScenarioRegistry.list()
        assert len(scenarios) >= 1  # Built-ins reloaded
        assert any(s["name"] == "customer_support" for s in scenarios)


class TestScenarioRegistryIntegration:
    """Integration tests for ScenarioRegistry."""

    def setup_method(self):
        """Clear registry before each test."""
        ScenarioRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ScenarioRegistry.clear()

    def test_register_load_and_use_scenario(self):
        """Test complete workflow: register, load, and use scenario."""
        # Register
        ScenarioRegistry.register("mock", MockScenario)

        # Load
        scenario = ScenarioRegistry.load("mock")

        # Use
        env = scenario.create_environment()
        assert env == {"type": "mock"}

        trajectory = Trajectory(steps=[{"a": 1}, {"b": 2}])
        rewards = scenario.broadcast_rewards(trajectory)
        assert len(rewards) == 2

        criteria = scenario.success_criteria()
        assert "tool_reliability" in criteria

    def test_list_and_load_scenarios(self):
        """Test listing scenarios then loading them."""
        ScenarioRegistry.register("mock", MockScenario)
        ScenarioRegistry.register("advanced_mock", AdvancedMockScenario)

        # List all scenarios
        scenarios = ScenarioRegistry.list()
        assert len(scenarios) >= 3  # mock + advanced_mock + built-ins

        # Load each scenario by name from list
        for scenario_info in scenarios:
            scenario = ScenarioRegistry.load(scenario_info["name"])
            assert scenario.name == scenario_info["name"]
            assert scenario.description == scenario_info["description"]

    def test_registry_independent_of_scenario_instances(self):
        """Test that registry is independent of scenario instances."""
        ScenarioRegistry.register("mock", MockScenario)

        # Create multiple instances
        scenario1 = ScenarioRegistry.load("mock")
        scenario2 = ScenarioRegistry.load("mock")

        # Modify instance (if it had state)
        # Should not affect registry or other instances
        assert scenario1 is not scenario2
        assert isinstance(scenario1, MockScenario)
        assert isinstance(scenario2, MockScenario)

    def test_register_unregister_register_again(self):
        """Test registering, unregistering, then re-registering."""
        # Register
        ScenarioRegistry.register("mock", MockScenario)
        scenario1 = ScenarioRegistry.load("mock")
        assert isinstance(scenario1, MockScenario)

        # Unregister
        ScenarioRegistry.unregister("mock")
        with pytest.raises(ScenarioNotFoundError):
            ScenarioRegistry.load("mock")

        # Register again (should work)
        ScenarioRegistry.register("mock", MockScenario)
        scenario2 = ScenarioRegistry.load("mock")
        assert isinstance(scenario2, MockScenario)

    def test_registry_works_with_trainer_protocol(self):
        """Test that loaded scenarios work with Trainer's Scenario protocol."""
        ScenarioRegistry.register("mock", MockScenario)

        scenario = ScenarioRegistry.load("mock")

        # Verify it has all methods expected by Trainer
        assert hasattr(scenario, "create_environment")
        assert hasattr(scenario, "broadcast_rewards")
        assert hasattr(scenario, "calculate_metrics")
        assert hasattr(scenario, "success_criteria")

        # Verify methods work
        env = scenario.create_environment()
        assert env is not None

        trajectory = Trajectory(steps=[{"a": 1}], success=True, total_reward=10.0)
        rewards = scenario.broadcast_rewards(trajectory)
        assert isinstance(rewards, list)

        metrics = scenario.calculate_metrics([trajectory])
        assert isinstance(metrics, dict)
        assert "tool_reliability" in metrics

        criteria = scenario.success_criteria()
        assert isinstance(criteria, dict)
