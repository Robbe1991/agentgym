"""Code review scenario for training agents.

This module provides a scenario implementation for training AI agents
to perform effective code reviews with high accuracy and thoroughness.
"""

from typing import Any

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.base import Scenario


class CodeReviewScenario(Scenario):
    """Train agents to perform thorough and accurate code reviews.

    This scenario trains agents to effectively review code submissions by:
    - Identifying bugs and potential issues
    - Checking code style and best practices
    - Providing constructive feedback
    - Approving or requesting changes appropriately

    Metrics Targets:
        - Review accuracy: 90% (correctly identify issues)
        - False positive rate: <10% (avoid unnecessary change requests)
        - Review completeness: 85% (find most issues in one pass)
        - Feedback quality: High constructive comments

    Environment:
        The code review environment simulates pull requests with:
        - Code submissions (varying complexity and issue types)
        - Available review actions (comment, request_changes, approve)
        - Quality metrics (bugs found, false positives, review time)

    Example:
        >>> scenario = CodeReviewScenario()
        >>> env = scenario.create_environment()
        >>> print(env["type"])
        code_review

        >>> # During training, trajectories are evaluated
        >>> trajectory = Trajectory(...)  # doctest: +SKIP
        >>> rewards = scenario.broadcast_rewards(trajectory)  # doctest: +SKIP
    """

    name = "code_review"
    description = "Code review agent training for accurate and thorough reviews"
    difficulty = "intermediate"

    # Sample code submissions for training
    SAMPLE_SUBMISSIONS = [
        {
            "id": "PR-001",
            "title": "Add user authentication",
            "language": "python",
            "complexity": "easy",
            "issues": [
                {"type": "bug", "severity": "high", "description": "Missing null check on user input"},
                {"type": "style", "severity": "low", "description": "Inconsistent variable naming"},
            ],
            "loc": 50,  # Lines of code
            "expected_actions": ["add_comment", "request_changes"],
        },
        {
            "id": "PR-002",
            "title": "Refactor database queries",
            "language": "python",
            "complexity": "medium",
            "issues": [
                {"type": "security", "severity": "critical", "description": "SQL injection vulnerability"},
                {"type": "performance", "severity": "medium", "description": "N+1 query problem"},
                {"type": "style", "severity": "low", "description": "Long function should be split"},
            ],
            "loc": 150,
            "expected_actions": ["add_comment", "request_changes"],
        },
        {
            "id": "PR-003",
            "title": "Update documentation",
            "language": "markdown",
            "complexity": "easy",
            "issues": [
                {"type": "typo", "severity": "low", "description": "Minor typos"},
            ],
            "loc": 30,
            "expected_actions": ["add_comment", "approve"],
        },
        {
            "id": "PR-004",
            "title": "Implement caching layer",
            "language": "python",
            "complexity": "hard",
            "issues": [
                {"type": "bug", "severity": "high", "description": "Race condition in cache invalidation"},
                {"type": "architecture", "severity": "medium", "description": "Tight coupling with database layer"},
                {"type": "testing", "severity": "medium", "description": "Missing edge case tests"},
                {"type": "documentation", "severity": "low", "description": "No docstrings on public methods"},
            ],
            "loc": 300,
            "expected_actions": ["add_comment", "request_changes"],
        },
        {
            "id": "PR-005",
            "title": "Fix CSS styling bug",
            "language": "css",
            "complexity": "easy",
            "issues": [],  # Clean code, should approve
            "loc": 20,
            "expected_actions": ["approve"],
        },
        {
            "id": "PR-006",
            "title": "Add API rate limiting",
            "language": "python",
            "complexity": "medium",
            "issues": [
                {"type": "bug", "severity": "medium", "description": "Rate limit not enforced per user"},
                {"type": "security", "severity": "high", "description": "Missing authentication check"},
            ],
            "loc": 100,
            "expected_actions": ["add_comment", "request_changes"],
        },
    ]

    # Available review actions
    AVAILABLE_ACTIONS = [
        "start_review",         # Begin reviewing the PR
        "read_code",           # Read code changes
        "add_comment",         # Add review comment
        "suggest_change",      # Suggest specific code change
        "request_changes",     # Request changes before approval
        "approve",             # Approve the PR
        "reject",              # Reject the PR (rare)
        "check_tests",         # Check if tests are included
        "check_docs",          # Check if documentation is updated
        "run_linter",          # Run code style checker
        "check_security",      # Security vulnerability scan
    ]

    def create_environment(self) -> dict[str, Any]:
        """Create code review training environment.

        Returns:
            Dictionary containing environment configuration:
            - type: Environment type identifier
            - actions: Available review actions
            - submissions: Sample code submissions to review
            - baseline_time: Time baseline for review speed
            - baseline_accuracy: Accuracy baseline for comparison

        Example:
            >>> scenario = CodeReviewScenario()
            >>> env = scenario.create_environment()
            >>> env["type"]
            'code_review'
            >>> len(env["actions"])
            11
            >>> len(env["submissions"])
            6
        """
        return {
            "type": "code_review",
            "actions": self.AVAILABLE_ACTIONS,
            "submissions": self.SAMPLE_SUBMISSIONS,
            "baseline_time": 1800.0,  # 30 minutes per review (untrained)
            "baseline_accuracy": 0.60,  # 60% issue detection (untrained)
        }

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        Reward Calculation:
            - Bug detection: +20 per critical bug found, +10 per high, +5 per medium
            - False positives: -15 per unnecessary change request
            - Review speed: +5 for faster than baseline
            - Feedback quality: +10 for constructive comments
            - Appropriate action: +15 for correct approve/reject decision

        Args:
            trajectory: Completed episode trajectory with steps and outcome.

        Returns:
            List of rewards (one per step), broadcast from outcome.

        Example:
            >>> scenario = CodeReviewScenario()
            >>> trajectory = Trajectory(
            ...     steps=[
            ...         {"action": "add_comment", "issue_found": True, "severity": "high"},
            ...         {"action": "request_changes", "appropriate": True}
            ...     ],
            ...     total_reward=45.0,
            ...     success=True
            ... )
            >>> rewards = scenario.broadcast_rewards(trajectory)
            >>> len(rewards)
            2
            >>> all(r > 0 for r in rewards)
            True
        """
        # Calculate outcome reward based on overall success
        if trajectory.success:
            outcome_reward = 15.0  # Base reward for successful review
        else:
            outcome_reward = -10.0  # Penalty for poor review quality

        # Broadcast outcome to all steps
        step_rewards = [outcome_reward] * len(trajectory)

        # Add step-specific bonuses/penalties
        baseline_time = 1800.0  # 30 minutes
        baseline_accuracy = 0.60

        for i, step in enumerate(trajectory.steps):
            # Issue detection rewards (by severity)
            if step.get("issue_found", False):
                severity = step.get("severity", "low")
                severity_rewards = {
                    "critical": 20.0,
                    "high": 10.0,
                    "medium": 5.0,
                    "low": 2.0,
                }
                step_rewards[i] += severity_rewards.get(severity, 0.0)

            # False positive penalty
            if step.get("false_positive", False):
                step_rewards[i] -= 15.0

            # Appropriate action bonus
            if step.get("appropriate_action", False):
                step_rewards[i] += 15.0

            # Review speed bonus
            review_time = step.get("review_time", baseline_time)
            if review_time < baseline_time:
                speed_ratio = (baseline_time - review_time) / baseline_time
                step_rewards[i] += 5.0 * speed_ratio

            # Feedback quality bonus
            if step.get("constructive_feedback", False):
                step_rewards[i] += 10.0

            # Completeness bonus (finding multiple issues in one pass)
            if step.get("thorough_review", False):
                step_rewards[i] += 8.0

        return step_rewards

    def success_criteria(self) -> dict[str, float]:
        """Define target performance metrics for code review.

        Returns:
            Dictionary mapping metric names to target values:
            - review_accuracy: 90% correct issue identification
            - false_positive_rate: <10% unnecessary change requests
            - review_completeness: 85% of issues found in one pass
            - avg_review_time: <600 seconds (10 minutes)

        Example:
            >>> scenario = CodeReviewScenario()
            >>> criteria = scenario.success_criteria()
            >>> criteria["review_accuracy"]
            0.9
            >>> criteria["false_positive_rate"]
            0.1
        """
        return {
            "review_accuracy": 0.90,  # 90% accuracy
            "false_positive_rate": 0.10,  # <10% false positives
            "review_completeness": 0.85,  # 85% completeness
            "avg_review_time": 600.0,  # 10 minutes average
        }

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate code review specific metrics.

        Extends the base class metrics with code review specific calculations
        for accuracy, false positives, and completeness.

        Args:
            trajectories: List of completed trajectories.

        Returns:
            Dictionary of metrics including standard metrics plus
            code review specific calculations.

        Example:
            >>> scenario = CodeReviewScenario()
            >>> trajectories = [
            ...     Trajectory(
            ...         steps=[{"issue_found": True, "false_positive": False}],
            ...         success=True,
            ...         total_reward=25.0
            ...     )
            ... ]
            >>> metrics = scenario.calculate_metrics(trajectories)
            >>> "review_accuracy" in metrics
            True
        """
        # Get base metrics from parent class
        metrics = super().calculate_metrics(trajectories)

        if not trajectories:
            # Ensure code review metrics are included even for empty trajectories
            metrics["review_accuracy"] = 0.0
            metrics["false_positive_rate"] = 0.0
            metrics["review_completeness"] = 0.0
            return metrics

        # Calculate review accuracy
        total_issues = 0
        issues_found = 0
        false_positives = 0
        total_possible_issues = 0

        for trajectory in trajectories:
            for step in trajectory.steps:
                if step.get("issue_found"):
                    issues_found += 1
                    if step.get("false_positive", False):
                        false_positives += 1

                # Track total possible issues from submissions
                if "total_issues" in step:
                    total_possible_issues += step["total_issues"]

        # Review accuracy: issues found / total issues
        if total_possible_issues > 0:
            metrics["review_accuracy"] = issues_found / total_possible_issues
        else:
            metrics["review_accuracy"] = 0.0

        # False positive rate
        if issues_found > 0:
            metrics["false_positive_rate"] = false_positives / issues_found
        else:
            metrics["false_positive_rate"] = 0.0

        # Review completeness: percentage of reviews finding all issues
        complete_reviews = sum(
            1
            for t in trajectories
            if t.success
            and hasattr(t, "metadata")
            and t.metadata
            and t.metadata.get("found_all_issues", False)
        )
        if trajectories:
            metrics["review_completeness"] = complete_reviews / len(trajectories)
        else:
            metrics["review_completeness"] = 0.0

        # Average review time
        review_times = [
            step.get("review_time", 0.0)
            for t in trajectories
            for step in t.steps
            if "review_time" in step
        ]
        if review_times:
            metrics["avg_review_time"] = sum(review_times) / len(review_times)
        else:
            metrics["avg_review_time"] = 0.0

        return metrics
