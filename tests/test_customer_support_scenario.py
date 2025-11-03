"""Tests for customer support scenario.

This module contains comprehensive tests for the CustomerSupportScenario,
including environment creation, reward broadcasting, metrics calculation,
and integration with the training system.
"""

import pytest

from agentgym.core.config import TrainingConfig
from agentgym.core.trainer import Trainer, Trajectory
from agentgym.scenarios.customer_support import CustomerSupportScenario
from agentgym.scenarios.registry import ScenarioRegistry


class TestCustomerSupportScenarioBasics:
    """Test basic CustomerSupportScenario properties."""

    def test_class_attributes(self):
        """Test that class attributes are correctly set."""
        scenario = CustomerSupportScenario()

        assert scenario.name == "customer_support"
        assert (
            scenario.description
            == "Customer service agent training for 95% tool reliability"
        )
        assert scenario.difficulty == "beginner"

    def test_sample_tickets_defined(self):
        """Test that sample tickets are defined."""
        assert len(CustomerSupportScenario.SAMPLE_TICKETS) == 5

        # Check structure of first ticket
        ticket = CustomerSupportScenario.SAMPLE_TICKETS[0]
        assert "id" in ticket
        assert "query" in ticket
        assert "category" in ticket
        assert "complexity" in ticket
        assert "expected_tools" in ticket

    def test_available_tools_defined(self):
        """Test that available tools are defined."""
        assert len(CustomerSupportScenario.AVAILABLE_TOOLS) == 11

        # Check some expected tools
        tools = CustomerSupportScenario.AVAILABLE_TOOLS
        assert "search_kb" in tools
        assert "update_ticket" in tools
        assert "lookup_user" in tools


class TestCreateEnvironment:
    """Test environment creation."""

    def test_create_environment_structure(self):
        """Test that environment has correct structure."""
        scenario = CustomerSupportScenario()
        env = scenario.create_environment()

        assert isinstance(env, dict)
        assert env["type"] == "customer_support"
        assert "tools" in env
        assert "tickets" in env
        assert "baseline_tokens" in env
        assert "baseline_time" in env

    def test_create_environment_tools(self):
        """Test that environment includes all available tools."""
        scenario = CustomerSupportScenario()
        env = scenario.create_environment()

        assert len(env["tools"]) == 11
        assert "search_kb" in env["tools"]
        assert "refund" in env["tools"]

    def test_create_environment_tickets(self):
        """Test that environment includes sample tickets."""
        scenario = CustomerSupportScenario()
        env = scenario.create_environment()

        assert len(env["tickets"]) == 5
        assert all("id" in ticket for ticket in env["tickets"])

    def test_create_environment_baselines(self):
        """Test that environment includes baseline metrics."""
        scenario = CustomerSupportScenario()
        env = scenario.create_environment()

        assert env["baseline_tokens"] == 500
        assert env["baseline_time"] == 240.0


class TestBroadcastRewards:
    """Test reward broadcasting logic."""

    def test_broadcast_rewards_successful_trajectory(self):
        """Test reward broadcasting for successful ticket resolution."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 200,
                    "response_time": 50.0,
                },
                {
                    "tool": "send_reset_link",
                    "tool_success": True,
                    "tokens_used": 150,
                    "response_time": 30.0,
                },
            ],
            total_reward=40.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 2
        # All rewards should be positive for successful trajectory
        assert all(r > 0 for r in rewards)
        # Each step gets outcome reward + tool success bonus + efficiency bonuses
        # Outcome (10) + Tool success (10) + token savings (5 * ~0.6) + speed bonus (3 * ~0.8) ≈ 25+
        assert rewards[0] > 20.0
        assert rewards[1] > 20.0

    def test_broadcast_rewards_failed_trajectory(self):
        """Test reward broadcasting for failed ticket resolution."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[
                {
                    "tool": "wrong_tool",
                    "tool_success": False,
                    "tokens_used": 600,
                    "response_time": 300.0,
                },
                {
                    "tool": "another_wrong_tool",
                    "tool_success": False,
                    "tokens_used": 700,
                    "response_time": 350.0,
                },
            ],
            total_reward=0.0,
            success=False,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 2
        # All rewards should be negative for failed trajectory
        assert all(r < 0 for r in rewards)
        # Outcome (-5) + Tool failure (-20) + no bonuses ≈ -25
        assert rewards[0] < -20.0
        assert rewards[1] < -20.0

    def test_broadcast_rewards_mixed_success(self):
        """Test reward broadcasting with mixed tool success."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 200,
                    "response_time": 50.0,
                },
                {
                    "tool": "wrong_tool",
                    "tool_success": False,
                    "tokens_used": 600,
                    "response_time": 300.0,
                },
                {
                    "tool": "update_ticket",
                    "tool_success": True,
                    "tokens_used": 150,
                    "response_time": 40.0,
                },
            ],
            total_reward=10.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 3
        # First and third steps should have positive rewards (tool success)
        assert rewards[0] > 0
        assert rewards[2] > 0
        # Second step should have negative reward (tool failure)
        assert rewards[1] < 0

    def test_broadcast_rewards_empty_trajectory(self):
        """Test reward broadcasting with empty trajectory."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(steps=[], success=False)

        rewards = scenario.broadcast_rewards(trajectory)

        assert rewards == []

    def test_broadcast_rewards_token_efficiency_bonus(self):
        """Test that token efficiency provides bonus."""
        scenario = CustomerSupportScenario()

        # Very efficient (low token usage)
        efficient_trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 100,
                    "response_time": 240.0,
                }
            ],
            success=True,
        )

        # Inefficient (high token usage)
        inefficient_trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 600,
                    "response_time": 240.0,
                }
            ],
            success=True,
        )

        efficient_rewards = scenario.broadcast_rewards(efficient_trajectory)
        inefficient_rewards = scenario.broadcast_rewards(inefficient_trajectory)

        # Efficient should get higher reward due to token savings bonus
        assert efficient_rewards[0] > inefficient_rewards[0]

    def test_broadcast_rewards_speed_bonus(self):
        """Test that faster response time provides bonus."""
        scenario = CustomerSupportScenario()

        # Fast response
        fast_trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 500,
                    "response_time": 50.0,
                }
            ],
            success=True,
        )

        # Slow response
        slow_trajectory = Trajectory(
            steps=[
                {
                    "tool": "search_kb",
                    "tool_success": True,
                    "tokens_used": 500,
                    "response_time": 300.0,
                }
            ],
            success=True,
        )

        fast_rewards = scenario.broadcast_rewards(fast_trajectory)
        slow_rewards = scenario.broadcast_rewards(slow_trajectory)

        # Fast should get higher reward due to speed bonus
        assert fast_rewards[0] > slow_rewards[0]


class TestSuccessCriteria:
    """Test success criteria definition."""

    def test_success_criteria_structure(self):
        """Test that success criteria has correct structure."""
        scenario = CustomerSupportScenario()
        criteria = scenario.success_criteria()

        assert isinstance(criteria, dict)
        assert "tool_reliability" in criteria
        assert "cost_reduction" in criteria
        assert "time_savings" in criteria

    def test_success_criteria_values(self):
        """Test that success criteria has correct target values."""
        scenario = CustomerSupportScenario()
        criteria = scenario.success_criteria()

        assert criteria["tool_reliability"] == 0.95
        assert criteria["cost_reduction"] == 0.30
        assert criteria["time_savings"] == 0.98


class TestCalculateMetrics:
    """Test metrics calculation."""

    def test_calculate_metrics_empty(self):
        """Test metrics calculation with no trajectories."""
        scenario = CustomerSupportScenario()
        metrics = scenario.calculate_metrics([])

        assert metrics["tool_reliability"] == 0.0
        assert metrics["cost_reduction"] == 0.0
        assert metrics["time_savings"] == 0.0

    def test_calculate_metrics_single_trajectory(self):
        """Test metrics calculation with single trajectory."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[{"tool_success": True}],
            total_reward=10.0,
            success=True,
            metadata={"tokens_used": 300, "response_time": 50.0},
        )

        metrics = scenario.calculate_metrics([trajectory])

        # Tool reliability should be 100% (1 success)
        assert metrics["tool_reliability"] == 1.0

        # Cost reduction: (500 - 300) / 500 = 0.4 = 40%
        assert metrics["cost_reduction"] == pytest.approx(0.4)

        # Time savings: (240 - 50) / 240 ≈ 0.79 = 79%
        assert metrics["time_savings"] == pytest.approx(0.79, rel=0.01)

    def test_calculate_metrics_multiple_trajectories(self):
        """Test metrics calculation with multiple trajectories."""
        scenario = CustomerSupportScenario()

        trajectories = [
            Trajectory(
                steps=[{"tool_success": True}],
                success=True,
                metadata={"tokens_used": 300, "response_time": 50.0},
            ),
            Trajectory(
                steps=[{"tool_success": True}],
                success=True,
                metadata={"tokens_used": 200, "response_time": 40.0},
            ),
            Trajectory(
                steps=[{"tool_success": True}],
                success=False,
                metadata={"tokens_used": 400, "response_time": 60.0},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # Tool reliability: 2/3 ≈ 66.7%
        assert metrics["tool_reliability"] == pytest.approx(2 / 3, rel=0.01)

        # Avg tokens: (300 + 200 + 400) / 3 = 300
        # Cost reduction: (500 - 300) / 500 = 0.4 = 40%
        assert metrics["cost_reduction"] == pytest.approx(0.4)

        # Avg time: (50 + 40 + 60) / 3 = 50
        # Time savings: (240 - 50) / 240 ≈ 0.79 = 79%
        assert metrics["time_savings"] == pytest.approx(0.79, rel=0.01)

    def test_calculate_metrics_no_cost_reduction(self):
        """Test metrics when token usage exceeds baseline."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[{"tool_success": True}],
            success=True,
            metadata={"tokens_used": 600, "response_time": 50.0},  # More than baseline
        )

        metrics = scenario.calculate_metrics([trajectory])

        # Cost reduction should be 0 when using more tokens than baseline
        assert metrics["cost_reduction"] == 0.0

    def test_calculate_metrics_no_time_savings(self):
        """Test metrics when response time exceeds baseline."""
        scenario = CustomerSupportScenario()

        trajectory = Trajectory(
            steps=[{"tool_success": True}],
            success=True,
            metadata={
                "tokens_used": 300,
                "response_time": 300.0,
            },  # Slower than baseline
        )

        metrics = scenario.calculate_metrics([trajectory])

        # Time savings should be 0 when slower than baseline
        assert metrics["time_savings"] == 0.0


class TestScenarioRegistryIntegration:
    """Test integration with ScenarioRegistry."""

    def setup_method(self):
        """Register scenario before each test."""
        ScenarioRegistry.register("customer_support", CustomerSupportScenario)

    def teardown_method(self):
        """Clean up registry after each test."""
        if ScenarioRegistry.is_registered("customer_support"):
            ScenarioRegistry.unregister("customer_support")

    def test_scenario_registered(self):
        """Test that scenario can be registered."""
        assert ScenarioRegistry.is_registered("customer_support")

    def test_scenario_loadable(self):
        """Test that scenario can be loaded from registry."""
        scenario = ScenarioRegistry.load("customer_support")

        assert isinstance(scenario, CustomerSupportScenario)
        assert scenario.name == "customer_support"

    def test_scenario_in_list(self):
        """Test that scenario appears in registry list."""
        scenarios = ScenarioRegistry.list()

        customer_support = next(
            (s for s in scenarios if s["name"] == "customer_support"), None
        )

        assert customer_support is not None
        assert customer_support["difficulty"] == "beginner"
        assert "customer service" in customer_support["description"].lower()


class TestTrainerIntegration:
    """Test integration with Trainer."""

    def setup_method(self):
        """Register scenario before each test."""
        ScenarioRegistry.register("customer_support", CustomerSupportScenario)

    def teardown_method(self):
        """Clean up registry after each test."""
        if ScenarioRegistry.is_registered("customer_support"):
            ScenarioRegistry.unregister("customer_support")

    def test_trainer_can_load_scenario(self):
        """Test that Trainer can load customer support scenario."""
        config = TrainingConfig(scenario="customer_support", episodes=5, seed=42)
        trainer = Trainer(config)

        assert isinstance(trainer.scenario, CustomerSupportScenario)

    def test_full_training_workflow(self):
        """Test complete training workflow with customer support scenario."""
        config = TrainingConfig(
            scenario="customer_support", episodes=10, learning_rate=0.0003, seed=42
        )

        trainer = Trainer(config)
        result = trainer.train()

        # Verify training completed
        assert result.metrics.episodes_completed == 10
        assert len(trainer.trajectories) == 10

        # Verify scenario was used
        assert isinstance(trainer.scenario, CustomerSupportScenario)

        # Verify metrics are calculated
        assert 0.0 <= result.metrics.tool_reliability <= 1.0
        assert result.metrics.avg_tokens_used >= 0.0
        assert result.metrics.avg_response_time >= 0.0

    def test_scenario_improves_over_episodes(self):
        """Test that training shows improvement trend."""
        config = TrainingConfig(scenario="customer_support", episodes=100, seed=42)

        trainer = Trainer(config)
        trainer.train()

        # Check that later episodes generally perform better
        first_20 = sum(1 for t in trainer.trajectories[:20] if t.success) / 20
        last_20 = sum(1 for t in trainer.trajectories[-20:] if t.success) / 20

        # Later episodes should be better or similar (allow small variance)
        assert last_20 >= first_20 - 0.1

    def test_trained_model_path_includes_scenario_name(self):
        """Test that trained model path includes scenario name."""
        config = TrainingConfig(scenario="customer_support", episodes=10, seed=42)

        trainer = Trainer(config)
        result = trainer.train()

        assert "customer_support" in result.trained_model_path


class TestScenarioWithBaseClass:
    """Test that CustomerSupportScenario properly extends Scenario base class."""

    def test_inherits_from_scenario(self):
        """Test that CustomerSupportScenario inherits from Scenario."""
        from agentgym.scenarios.base import Scenario

        scenario = CustomerSupportScenario()
        assert isinstance(scenario, Scenario)

    def test_implements_all_abstract_methods(self):
        """Test that all abstract methods are implemented."""
        scenario = CustomerSupportScenario()

        # Should be able to call all required methods
        env = scenario.create_environment()
        assert env is not None

        trajectory = Trajectory(steps=[{"test": 1}], success=True)
        rewards = scenario.broadcast_rewards(trajectory)
        assert isinstance(rewards, list)

        criteria = scenario.success_criteria()
        assert isinstance(criteria, dict)

    def test_uses_default_trainable_components(self):
        """Test that scenario uses default trainable components."""
        scenario = CustomerSupportScenario()
        components = scenario.define_trainable_components()

        assert components["tool_selection"] is True
        assert components["parameter_selection"] is True
        assert components["tool_execution"] is False
        assert components["output_generation"] is False

    def test_validates_trajectories(self):
        """Test that scenario can validate trajectories."""
        scenario = CustomerSupportScenario()

        valid_trajectory = Trajectory(steps=[{"action": "test"}])
        assert scenario.validate_trajectory(valid_trajectory) is True

        empty_trajectory = Trajectory(steps=[])
        assert scenario.validate_trajectory(empty_trajectory) is False
