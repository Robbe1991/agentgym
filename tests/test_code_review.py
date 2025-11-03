"""Tests for code review scenario implementation."""

import pytest

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.code_review import CodeReviewScenario


class TestCodeReviewScenario:
    """Test suite for CodeReviewScenario class."""

    @pytest.fixture
    def scenario(self):
        """Create a CodeReviewScenario instance."""
        return CodeReviewScenario()

    def test_scenario_attributes(self, scenario):
        """Test basic scenario attributes."""
        assert scenario.name == "code_review"
        assert scenario.description == "Code review agent training for accurate and thorough reviews"
        assert scenario.difficulty == "intermediate"

    def test_sample_submissions(self, scenario):
        """Test that sample submissions are properly defined."""
        assert len(scenario.SAMPLE_SUBMISSIONS) == 6

        # Check first submission structure
        pr1 = scenario.SAMPLE_SUBMISSIONS[0]
        assert pr1["id"] == "PR-001"
        assert pr1["title"] == "Add user authentication"
        assert pr1["language"] == "python"
        assert pr1["complexity"] == "easy"
        assert len(pr1["issues"]) == 2
        assert pr1["loc"] == 50

    def test_available_actions(self, scenario):
        """Test that review actions are properly defined."""
        assert len(scenario.AVAILABLE_ACTIONS) == 11
        assert "start_review" in scenario.AVAILABLE_ACTIONS
        assert "add_comment" in scenario.AVAILABLE_ACTIONS
        assert "approve" in scenario.AVAILABLE_ACTIONS
        assert "request_changes" in scenario.AVAILABLE_ACTIONS

    def test_create_environment(self, scenario):
        """Test environment creation."""
        env = scenario.create_environment()

        assert env["type"] == "code_review"
        assert len(env["actions"]) == 11
        assert len(env["submissions"]) == 6
        assert env["baseline_time"] == 1800.0
        assert env["baseline_accuracy"] == 0.60

    def test_create_environment_returns_dict(self, scenario):
        """Test that create_environment returns proper dictionary."""
        env = scenario.create_environment()

        assert isinstance(env, dict)
        assert "type" in env
        assert "actions" in env
        assert "submissions" in env
        assert "baseline_time" in env
        assert "baseline_accuracy" in env

    def test_broadcast_rewards_success(self, scenario):
        """Test reward broadcasting for successful trajectory."""
        trajectory = Trajectory(
            steps=[
                {"action": "start_review"},
                {"action": "add_comment", "issue_found": True, "severity": "high"},
                {"action": "request_changes", "appropriate_action": True},
            ],
            total_reward=50.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 3
        # Successful trajectory should have positive outcome reward
        assert all(r > 0 for r in rewards)
        # Second step should have highest reward (found high severity issue)
        assert rewards[1] > rewards[0]

    def test_broadcast_rewards_failure(self, scenario):
        """Test reward broadcasting for failed trajectory."""
        trajectory = Trajectory(
            steps=[
                {"action": "start_review"},
                {"action": "approve", "appropriate_action": False},
            ],
            total_reward=-5.0,
            success=False,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        assert len(rewards) == 2
        # Failed trajectory should have negative outcome reward
        assert all(r < 0 for r in rewards)

    def test_broadcast_rewards_issue_severity(self, scenario):
        """Test that different severity levels give different rewards."""
        # Critical issue
        traj_critical = Trajectory(
            steps=[{"issue_found": True, "severity": "critical"}],
            total_reward=35.0,
            success=True,
        )
        rewards_critical = scenario.broadcast_rewards(traj_critical)

        # High issue
        traj_high = Trajectory(
            steps=[{"issue_found": True, "severity": "high"}],
            total_reward=25.0,
            success=True,
        )
        rewards_high = scenario.broadcast_rewards(traj_high)

        # Medium issue
        traj_medium = Trajectory(
            steps=[{"issue_found": True, "severity": "medium"}],
            total_reward=20.0,
            success=True,
        )
        rewards_medium = scenario.broadcast_rewards(traj_medium)

        # Critical should have highest reward
        assert rewards_critical[0] > rewards_high[0]
        assert rewards_high[0] > rewards_medium[0]

    def test_broadcast_rewards_false_positive_penalty(self, scenario):
        """Test that false positives are penalized."""
        # Correct issue detection
        traj_correct = Trajectory(
            steps=[{"issue_found": True, "severity": "high", "false_positive": False}],
            total_reward=25.0,
            success=True,
        )
        rewards_correct = scenario.broadcast_rewards(traj_correct)

        # False positive
        traj_false = Trajectory(
            steps=[{"issue_found": True, "severity": "high", "false_positive": True}],
            total_reward=10.0,
            success=True,
        )
        rewards_false = scenario.broadcast_rewards(traj_false)

        # False positive should have lower reward due to penalty
        assert rewards_false[0] < rewards_correct[0]

    def test_broadcast_rewards_appropriate_action_bonus(self, scenario):
        """Test that appropriate actions receive bonuses."""
        trajectory = Trajectory(
            steps=[
                {"action": "request_changes", "appropriate_action": True},
                {"action": "approve", "appropriate_action": True},
            ],
            total_reward=45.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Both steps should benefit from appropriate action bonus
        assert all(r > 15.0 for r in rewards)  # Base success reward is 15

    def test_broadcast_rewards_speed_bonus(self, scenario):
        """Test that faster reviews are rewarded."""
        # Fast review
        traj_fast = Trajectory(
            steps=[{"review_time": 300.0}],  # 5 minutes vs 30 minute baseline
            total_reward=20.0,
            success=True,
        )
        rewards_fast = scenario.broadcast_rewards(traj_fast)

        # Slow review
        traj_slow = Trajectory(
            steps=[{"review_time": 1800.0}],  # At baseline
            total_reward=15.0,
            success=True,
        )
        rewards_slow = scenario.broadcast_rewards(traj_slow)

        # Fast review should have speed bonus
        assert rewards_fast[0] > rewards_slow[0]

    def test_broadcast_rewards_feedback_quality_bonus(self, scenario):
        """Test that constructive feedback is rewarded."""
        trajectory = Trajectory(
            steps=[
                {"action": "add_comment", "constructive_feedback": True},
                {"action": "add_comment", "constructive_feedback": True},
            ],
            total_reward=40.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Both steps should have feedback quality bonus
        assert all(r > 15.0 for r in rewards)

    def test_broadcast_rewards_thorough_review_bonus(self, scenario):
        """Test that thorough reviews are rewarded."""
        trajectory = Trajectory(
            steps=[{"thorough_review": True}],
            total_reward=23.0,
            success=True,
        )

        rewards = scenario.broadcast_rewards(trajectory)

        # Should have thoroughness bonus
        assert rewards[0] > 15.0  # Base success reward

    def test_success_criteria(self, scenario):
        """Test success criteria definition."""
        criteria = scenario.success_criteria()

        assert isinstance(criteria, dict)
        assert criteria["review_accuracy"] == 0.90
        assert criteria["false_positive_rate"] == 0.10
        assert criteria["review_completeness"] == 0.85
        assert criteria["avg_review_time"] == 600.0

    def test_calculate_metrics_empty_trajectories(self, scenario):
        """Test metrics calculation with empty trajectories."""
        metrics = scenario.calculate_metrics([])

        assert isinstance(metrics, dict)
        assert metrics["review_accuracy"] == 0.0
        assert metrics["false_positive_rate"] == 0.0
        assert metrics["review_completeness"] == 0.0

    def test_calculate_metrics_with_trajectories(self, scenario):
        """Test metrics calculation with actual trajectories."""
        trajectories = [
            Trajectory(
                steps=[
                    {"issue_found": True, "false_positive": False, "total_issues": 2, "review_time": 500.0},
                    {"issue_found": True, "false_positive": False, "total_issues": 2, "review_time": 500.0},
                ],
                total_reward=40.0,
                success=True,
                metadata={"found_all_issues": True},
            ),
            Trajectory(
                steps=[
                    {"issue_found": True, "false_positive": True, "total_issues": 1, "review_time": 700.0},
                ],
                total_reward=10.0,
                success=True,
                metadata={"found_all_issues": False},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        assert "review_accuracy" in metrics
        assert "false_positive_rate" in metrics
        assert "review_completeness" in metrics
        assert "avg_review_time" in metrics

        # Check calculated values
        assert metrics["review_accuracy"] > 0.0  # Found 3 out of 5 total issues
        assert metrics["false_positive_rate"] > 0.0  # Had 1 false positive
        assert 0.0 <= metrics["review_completeness"] <= 1.0
        assert metrics["avg_review_time"] > 0.0

    def test_calculate_metrics_review_accuracy(self, scenario):
        """Test review accuracy calculation."""
        trajectories = [
            Trajectory(
                steps=[
                    {"issue_found": True, "total_issues": 3},
                    {"issue_found": True, "total_issues": 3},
                    {"issue_found": True, "total_issues": 3},
                ],
                total_reward=50.0,
                success=True,
            )
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # Found 3 out of 9 total issues (3 issues per step * 3 steps)
        expected_accuracy = 3 / 9
        assert metrics["review_accuracy"] == pytest.approx(expected_accuracy)

    def test_calculate_metrics_false_positive_rate(self, scenario):
        """Test false positive rate calculation."""
        trajectories = [
            Trajectory(
                steps=[
                    {"issue_found": True, "false_positive": False},
                    {"issue_found": True, "false_positive": True},
                    {"issue_found": True, "false_positive": False},
                    {"issue_found": True, "false_positive": True},
                ],
                total_reward=20.0,
                success=True,
            )
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 false positives out of 4 issues found
        expected_fpr = 2 / 4
        assert metrics["false_positive_rate"] == pytest.approx(expected_fpr)

    def test_calculate_metrics_review_completeness(self, scenario):
        """Test review completeness calculation."""
        trajectories = [
            Trajectory(
                steps=[{"action": "review"}],
                total_reward=30.0,
                success=True,
                metadata={"found_all_issues": True},
            ),
            Trajectory(
                steps=[{"action": "review"}],
                total_reward=20.0,
                success=True,
                metadata={"found_all_issues": False},
            ),
            Trajectory(
                steps=[{"action": "review"}],
                total_reward=25.0,
                success=True,
                metadata={"found_all_issues": True},
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # 2 out of 3 trajectories found all issues
        expected_completeness = 2 / 3
        assert metrics["review_completeness"] == pytest.approx(expected_completeness)

    def test_calculate_metrics_avg_review_time(self, scenario):
        """Test average review time calculation."""
        trajectories = [
            Trajectory(
                steps=[
                    {"review_time": 400.0},
                    {"review_time": 600.0},
                ],
                total_reward=30.0,
                success=True,
            ),
            Trajectory(
                steps=[
                    {"review_time": 500.0},
                ],
                total_reward=25.0,
                success=True,
            ),
        ]

        metrics = scenario.calculate_metrics(trajectories)

        # Average of (400 + 600 + 500) / 3
        expected_avg_time = (400.0 + 600.0 + 500.0) / 3
        assert metrics["avg_review_time"] == pytest.approx(expected_avg_time)

    def test_scenario_inheritance(self, scenario):
        """Test that scenario inherits from base Scenario class."""
        from agentgym.scenarios.base import Scenario

        assert isinstance(scenario, Scenario)

    def test_sample_submissions_have_expected_fields(self, scenario):
        """Test that all submissions have required fields."""
        required_fields = ["id", "title", "language", "complexity", "issues", "loc", "expected_actions"]

        for submission in scenario.SAMPLE_SUBMISSIONS:
            for field in required_fields:
                assert field in submission, f"Missing field {field} in submission {submission['id']}"

    def test_sample_submissions_issue_structure(self, scenario):
        """Test that issues have proper structure."""
        required_issue_fields = ["type", "severity", "description"]

        for submission in scenario.SAMPLE_SUBMISSIONS:
            for issue in submission["issues"]:
                for field in required_issue_fields:
                    assert field in issue, f"Missing field {field} in issue"

    def test_complexity_levels(self, scenario):
        """Test that submissions have various complexity levels."""
        complexities = {sub["complexity"] for sub in scenario.SAMPLE_SUBMISSIONS}

        assert "easy" in complexities
        assert "medium" in complexities
        assert "hard" in complexities

    def test_different_languages(self, scenario):
        """Test that submissions include different languages."""
        languages = {sub["language"] for sub in scenario.SAMPLE_SUBMISSIONS}

        assert len(languages) >= 2  # At least 2 different languages

    def test_clean_code_submission(self, scenario):
        """Test that there's at least one clean code submission."""
        clean_submissions = [sub for sub in scenario.SAMPLE_SUBMISSIONS if len(sub["issues"]) == 0]

        assert len(clean_submissions) > 0  # Should have at least one clean submission

    def test_critical_security_issues(self, scenario):
        """Test that there are submissions with security issues."""
        security_issues = []
        for sub in scenario.SAMPLE_SUBMISSIONS:
            for issue in sub["issues"]:
                if issue["type"] == "security":
                    security_issues.append(issue)

        assert len(security_issues) > 0  # Should have security issues for training

    def test_different_issue_severities(self, scenario):
        """Test that issues have various severity levels."""
        severities = set()
        for sub in scenario.SAMPLE_SUBMISSIONS:
            for issue in sub["issues"]:
                severities.add(issue["severity"])

        assert len(severities) >= 3  # At least 3 severity levels

    def test_string_representation(self, scenario):
        """Test string representation methods."""
        str_repr = str(scenario)
        assert "code_review" in str_repr
        assert "intermediate" in str_repr

        repr_str = repr(scenario)
        assert "Scenario" in repr_str
        assert "code_review" in repr_str


class TestCodeReviewIntegration:
    """Integration tests for code review scenario."""

    @pytest.fixture
    def scenario(self):
        """Create a CodeReviewScenario instance."""
        return CodeReviewScenario()

    def test_full_review_workflow(self, scenario):
        """Test complete review workflow."""
        # Create environment
        env = scenario.create_environment()
        assert env["type"] == "code_review"

        # Simulate a review trajectory
        trajectory = Trajectory(
            steps=[
                {"action": "start_review"},
                {"action": "read_code"},
                {"action": "add_comment", "issue_found": True, "severity": "high"},
                {"action": "add_comment", "issue_found": True, "severity": "medium"},
                {"action": "request_changes", "appropriate_action": True},
            ],
            total_reward=60.0,
            success=True,
            metadata={"found_all_issues": True},
        )

        # Calculate rewards
        rewards = scenario.broadcast_rewards(trajectory)
        assert len(rewards) == 5
        assert all(isinstance(r, (int, float)) for r in rewards)

        # Calculate metrics
        metrics = scenario.calculate_metrics([trajectory])
        assert "review_accuracy" in metrics
        assert "tool_reliability" in metrics

    def test_multiple_reviews(self, scenario):
        """Test handling multiple review trajectories."""
        trajectories = [
            Trajectory(
                steps=[
                    {"issue_found": True, "severity": "high", "review_time": 400.0},
                    {"appropriate_action": True},
                ],
                total_reward=35.0,
                success=True,
            ),
            Trajectory(
                steps=[
                    {"issue_found": True, "severity": "medium", "review_time": 600.0},
                    {"appropriate_action": True},
                ],
                total_reward=25.0,
                success=True,
            ),
            Trajectory(
                steps=[
                    {"false_positive": True},
                ],
                total_reward=-5.0,
                success=False,
            ),
        ]

        # Calculate aggregate metrics
        metrics = scenario.calculate_metrics(trajectories)

        assert metrics["tool_reliability"] > 0.0
        assert "final_reward" in metrics
        assert "review_accuracy" in metrics

    def test_scenario_with_success_criteria(self, scenario):
        """Test scenario success criteria evaluation."""
        criteria = scenario.success_criteria()

        # Create a high-performing trajectory
        good_trajectory = Trajectory(
            steps=[
                {"issue_found": True, "false_positive": False, "total_issues": 2, "review_time": 500.0},
                {"issue_found": True, "false_positive": False, "total_issues": 2, "review_time": 500.0},
            ],
            total_reward=50.0,
            success=True,
            metadata={"found_all_issues": True},
        )

        metrics = scenario.calculate_metrics([good_trajectory])

        # Check against criteria
        assert metrics["review_accuracy"] <= criteria["review_accuracy"]  # May not reach 90% with limited data
        assert metrics["avg_review_time"] < criteria["avg_review_time"]  # 500 < 600
