"""Tests for data analysis scenario implementation."""

import pytest

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.data_analysis import DataAnalysisScenario


class TestDataAnalysisScenario:
    """Test suite for DataAnalysisScenario class."""

    @pytest.fixture
    def scenario(self):
        """Create a DataAnalysisScenario instance."""
        return DataAnalysisScenario()

    def test_scenario_attributes(self, scenario):
        """Test basic scenario attributes."""
        assert scenario.name == "data_analysis"
        assert scenario.description == "Data analysis agent training for accurate insights and visualizations"
        assert scenario.difficulty == "intermediate"

    def test_sample_tasks(self, scenario):
        """Test that sample tasks are properly defined."""
        assert len(scenario.SAMPLE_TASKS) == 6

        # Check first task structure
        task1 = scenario.SAMPLE_TASKS[0]
        assert task1["id"] == "TASK-001"
        assert task1["title"] == "Sales trend analysis"
        assert task1["dataset"] == "sales_data.csv"
        assert task1["size"] == "small"
        assert task1["complexity"] == "easy"
        assert len(task1["required_steps"]) == 5

    def test_available_actions(self, scenario):
        """Test that analysis actions are properly defined."""
        assert len(scenario.AVAILABLE_ACTIONS) == 15
        assert "load_data" in scenario.AVAILABLE_ACTIONS
        assert "clean_data" in scenario.AVAILABLE_ACTIONS
        assert "generate_insights" in scenario.AVAILABLE_ACTIONS
        assert "create_visualization" in scenario.AVAILABLE_ACTIONS

    def test_create_environment(self, scenario):
        """Test environment creation."""
        env = scenario.create_environment()

        assert env["type"] == "data_analysis"
        assert len(env["actions"]) == 15
        assert len(env["tasks"]) == 6
        assert env["baseline_time"] == 3600.0
        assert env["baseline_accuracy"] == 0.65

    def test_broadcast_rewards_success(self, scenario):
        """Test reward broadcasting for successful trajectory."""
        trajectory = Trajectory(
            steps=[
                {"action": "load_data"},
                {"action": "clean_data", "data_quality": "high"},
                {"action": "generate_insights", "insight_accurate": True},
            ],
            total_reward=60.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 3
        assert all(r > 0 for r in rewards)

    def test_broadcast_rewards_data_quality(self, scenario):
        """Test data quality rewards."""
        # High quality data
        traj_high = Trajectory(
            steps=[{"data_quality": "high"}],
            total_reward=27.0,
            success=True,
        )
        rewards_high = scenario.broadcast_rewards(traj_high)

        # Low quality data
        traj_low = Trajectory(
            steps=[{"data_quality": "low"}],
            total_reward=2.0,
            success=True,
        )
        rewards_low = scenario.broadcast_rewards(traj_low)

        # High quality should have higher reward
        assert rewards_high[0] > rewards_low[0]

    def test_broadcast_rewards_insight_accuracy(self, scenario):
        """Test insight accuracy rewards and penalties."""
        # Accurate insight
        traj_accurate = Trajectory(
            steps=[{"insight_accurate": True}],
            total_reward=32.0,
            success=True,
        )
        rewards_accurate = scenario.broadcast_rewards(traj_accurate)

        # Inaccurate insight
        traj_inaccurate = Trajectory(
            steps=[{"insight_inaccurate": True}],
            total_reward=2.0,
            success=True,
        )
        rewards_inaccurate = scenario.broadcast_rewards(traj_inaccurate)

        # Accurate should have much higher reward
        assert rewards_accurate[0] > rewards_inaccurate[0]

    def test_broadcast_rewards_visualization(self, scenario):
        """Test visualization quality bonuses."""
        trajectory = Trajectory(
            steps=[{"visualization_clear": True}],
            total_reward=22.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Should have visualization bonus
        assert rewards[0] > 12.0  # Base success reward

    def test_broadcast_rewards_thoroughness(self, scenario):
        """Test thorough analysis bonuses."""
        trajectory = Trajectory(
            steps=[{"thorough_analysis": True}],
            total_reward=24.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Should have thoroughness bonus
        assert rewards[0] > 12.0

    def test_broadcast_rewards_statistical_validity(self, scenario):
        """Test statistical validity bonuses."""
        trajectory = Trajectory(
            steps=[{"statistically_valid": True}],
            total_reward=20.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Should have validity bonus
        assert rewards[0] > 12.0

    def test_broadcast_rewards_actionable(self, scenario):
        """Test actionable insight bonuses."""
        trajectory = Trajectory(
            steps=[{"actionable_insight": True}],
            total_reward=22.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Should have actionable bonus
        assert rewards[0] > 12.0

    def test_success_criteria(self, scenario):
        """Test success criteria definition."""
        criteria = scenario.success_criteria()

        assert isinstance(criteria, dict)
        assert criteria["analysis_accuracy"] == 0.85
        assert criteria["data_quality"] == 0.90
        assert criteria["insight_quality"] == 0.80
        assert criteria["visualization_quality"] == 0.85

    def test_calculate_metrics_empty_trajectories(self, scenario):
        """Test metrics calculation with empty trajectories."""
        metrics = scenario.calculate_metrics([])

        assert isinstance(metrics, dict)
        assert metrics["analysis_accuracy"] == 0.0
        assert metrics["data_quality"] == 0.0
        assert metrics["insight_quality"] == 0.0
        assert metrics["visualization_quality"] == 0.0

    def test_calculate_metrics_with_trajectories(self, scenario):
        """Test metrics calculation with actual trajectories."""
        trajectories = [
            Trajectory(
                steps=[
                    {"insight_accurate": True, "data_quality": "high", "actionable_insight": True},
                    {"visualization_clear": True},
                ],
                total_reward=50.0,
                success=True,
                metadata={"tokens_used": 200, "response_time": 300.0},
            ),
            Trajectory(
                steps=[
                    {"insight_accurate": True, "data_quality": "high"},
                ],
                total_reward=35.0,
                success=True,
                metadata={"tokens_used": 250, "response_time": 400.0},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        assert "analysis_accuracy" in metrics
        assert "data_quality" in metrics
        assert "insight_quality" in metrics
        assert "visualization_quality" in metrics
        assert metrics["analysis_accuracy"] == 1.0  # All insights accurate
        assert metrics["data_quality"] == 1.0  # All high quality

    def test_calculate_metrics_analysis_accuracy(self, scenario):
        """Test analysis accuracy calculation."""
        trajectories = [
            Trajectory(
                steps=[
                    {"insight_accurate": True},
                    {"insight_accurate": True},
                    {"insight_inaccurate": True},
                ],
                total_reward=40.0,
                success=True,
            )
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 accurate out of 3 total insights
        expected_accuracy = 2 / 3
        assert metrics["analysis_accuracy"] == pytest.approx(expected_accuracy)

    def test_calculate_metrics_data_quality(self, scenario):
        """Test data quality calculation."""
        trajectories = [
            Trajectory(
                steps=[
                    {"data_quality": "high"},
                    {"data_quality": "high"},
                    {"data_quality": "low"},
                ],
                total_reward=30.0,
                success=True,
            )
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 high quality out of 3 data steps
        expected_quality = 2 / 3
        assert metrics["data_quality"] == pytest.approx(expected_quality)

    def test_scenario_inheritance(self, scenario):
        """Test that scenario inherits from base Scenario class."""
        from agentgym.scenarios.base import Scenario

        assert isinstance(scenario, Scenario)

    def test_sample_tasks_have_expected_fields(self, scenario):
        """Test that all tasks have required fields."""
        required_fields = ["id", "title", "dataset", "size", "complexity", "required_steps"]

        for task in scenario.SAMPLE_TASKS:
            for field in required_fields:
                assert field in task, f"Missing field {field} in task {task['id']}"

    def test_complexity_levels(self, scenario):
        """Test that tasks have various complexity levels."""
        complexities = {task["complexity"] for task in scenario.SAMPLE_TASKS}

        assert "easy" in complexities
        assert "medium" in complexities
        assert "hard" in complexities

    def test_dataset_sizes(self, scenario):
        """Test that tasks include different dataset sizes."""
        sizes = {task["size"] for task in scenario.SAMPLE_TASKS}

        assert len(sizes) >= 2  # At least 2 different sizes

    def test_string_representation(self, scenario):
        """Test string representation methods."""
        str_repr = str(scenario)
        assert "data_analysis" in str_repr
        assert "intermediate" in str_repr

        repr_str = repr(scenario)
        assert "Scenario" in repr_str
        assert "data_analysis" in repr_str


class TestDataAnalysisIntegration:
    """Integration tests for data analysis scenario."""

    @pytest.fixture
    def scenario(self):
        """Create a DataAnalysisScenario instance."""
        return DataAnalysisScenario()

    def test_full_analysis_workflow(self, scenario):
        """Test complete analysis workflow."""
        # Create environment
        env = scenario.create_environment()
        assert env["type"] == "data_analysis"

        # Simulate an analysis trajectory
        trajectory = Trajectory(
            steps=[
                {"action": "load_data"},
                {"action": "clean_data", "data_quality": "high"},
                {"action": "calculate_statistics"},
                {"action": "generate_insights", "insight_accurate": True, "actionable_insight": True},
                {"action": "create_visualization", "visualization_clear": True},
            ],
            total_reward=75.0,
            success=True,
            metadata={"tokens_used": 300, "response_time": 500.0},
        )

        # Calculate rewards
        rewards = scenario.broadcast_rewards(trajectory)
        assert len(rewards) == 5
        assert all(isinstance(r, (int, float)) for r in rewards)

        # Calculate metrics
        metrics = scenario.calculate_metrics([trajectory])
        assert "analysis_accuracy" in metrics
        assert "tool_reliability" in metrics

    def test_multiple_analyses(self, scenario):
        """Test handling multiple analysis trajectories."""
        trajectories = [
            Trajectory(
                steps=[
                    {"insight_accurate": True, "data_quality": "high"},
                ],
                total_reward=45.0,
                success=True,
            ),
            Trajectory(
                steps=[
                    {"insight_accurate": True, "visualization_clear": True},
                ],
                total_reward=40.0,
                success=True,
            ),
            Trajectory(
                steps=[
                    {"insight_inaccurate": True},
                ],
                total_reward=0.0,
                success=False,
            ),
        ]

        # Calculate aggregate metrics
        metrics = scenario.calculate_metrics(trajectories)

        assert metrics["tool_reliability"] > 0.0
        assert "final_reward" in metrics
        assert "analysis_accuracy" in metrics

    def test_scenario_with_success_criteria(self, scenario):
        """Test scenario success criteria evaluation."""
        criteria = scenario.success_criteria()

        # Create a high-performing trajectory
        good_trajectory = Trajectory(
            steps=[
                {"insight_accurate": True, "data_quality": "high", "actionable_insight": True},
                {"visualization_clear": True},
            ],
            total_reward=60.0,
            success=True,
            metadata={"tokens_used": 200, "response_time": 400.0},
        )

        metrics = scenario.calculate_metrics([good_trajectory])

        # Check against criteria
        assert metrics["analysis_accuracy"] >= criteria["analysis_accuracy"]  # 100% >= 85%
        assert metrics["data_quality"] >= criteria["data_quality"]  # 100% >= 90%
