"""Data analysis scenario for training agents.

This module provides a scenario implementation for training AI agents
to perform effective data analysis with high accuracy and insight quality.
"""

from typing import Any

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.base import Scenario


class DataAnalysisScenario(Scenario):
    """Train agents to perform comprehensive data analysis tasks.

    This scenario trains agents to effectively analyze data by:
    - Loading and cleaning datasets
    - Performing statistical analysis
    - Generating visualizations
    - Extracting actionable insights
    - Creating clear reports

    Metrics Targets:
        - Analysis accuracy: 85% (correct insights and patterns)
        - Data quality: 90% (proper cleaning and validation)
        - Insight quality: 80% (actionable and relevant findings)
        - Visualization quality: 85% (clear and informative charts)

    Environment:
        The data analysis environment simulates analysis tasks with:
        - Datasets (varying size and complexity)
        - Available analysis tools (pandas, numpy, plotting, etc.)
        - Quality metrics (accuracy, completeness, clarity)

    Example:
        >>> scenario = DataAnalysisScenario()
        >>> env = scenario.create_environment()
        >>> print(env["type"])
        data_analysis

        >>> # During training, trajectories are evaluated
        >>> trajectory = Trajectory(...)  # doctest: +SKIP
        >>> rewards = scenario.broadcast_rewards(trajectory)  # doctest: +SKIP
    """

    name = "data_analysis"
    description = "Data analysis agent training for accurate insights and visualizations"
    difficulty = "intermediate"

    # Sample analysis tasks for training
    SAMPLE_TASKS = [
        {
            "id": "TASK-001",
            "title": "Sales trend analysis",
            "dataset": "sales_data.csv",
            "size": "small",  # < 10K rows
            "complexity": "easy",
            "required_steps": [
                "load_data",
                "clean_data",
                "calculate_trends",
                "create_visualization",
                "generate_insights",
            ],
            "expected_insights": 3,
            "expected_visualizations": 2,
        },
        {
            "id": "TASK-002",
            "title": "Customer segmentation",
            "dataset": "customer_data.csv",
            "size": "medium",  # 10K-100K rows
            "complexity": "medium",
            "required_steps": [
                "load_data",
                "handle_missing_values",
                "normalize_features",
                "perform_clustering",
                "analyze_segments",
                "create_visualization",
                "generate_report",
            ],
            "expected_insights": 5,
            "expected_visualizations": 3,
        },
        {
            "id": "TASK-003",
            "title": "Product performance metrics",
            "dataset": "product_metrics.csv",
            "size": "small",
            "complexity": "easy",
            "required_steps": [
                "load_data",
                "calculate_kpis",
                "compare_products",
                "create_dashboard",
            ],
            "expected_insights": 4,
            "expected_visualizations": 4,
        },
        {
            "id": "TASK-004",
            "title": "Time series forecasting",
            "dataset": "time_series.csv",
            "size": "medium",
            "complexity": "hard",
            "required_steps": [
                "load_data",
                "check_stationarity",
                "handle_seasonality",
                "build_model",
                "validate_forecast",
                "create_visualization",
                "generate_insights",
            ],
            "expected_insights": 6,
            "expected_visualizations": 3,
        },
        {
            "id": "TASK-005",
            "title": "A/B test analysis",
            "dataset": "ab_test_results.csv",
            "size": "medium",
            "complexity": "medium",
            "required_steps": [
                "load_data",
                "check_sample_size",
                "perform_statistical_test",
                "calculate_confidence",
                "create_visualization",
                "generate_recommendation",
            ],
            "expected_insights": 4,
            "expected_visualizations": 2,
        },
        {
            "id": "TASK-006",
            "title": "Anomaly detection",
            "dataset": "system_metrics.csv",
            "size": "large",  # > 100K rows
            "complexity": "hard",
            "required_steps": [
                "load_data",
                "preprocess_time_series",
                "detect_anomalies",
                "analyze_patterns",
                "prioritize_alerts",
                "create_visualization",
                "generate_report",
            ],
            "expected_insights": 5,
            "expected_visualizations": 4,
        },
    ]

    # Available analysis actions/tools
    AVAILABLE_ACTIONS = [
        "load_data",               # Load dataset
        "inspect_data",            # Examine data structure
        "clean_data",              # Remove/fix invalid data
        "handle_missing_values",   # Deal with missing data
        "remove_duplicates",       # Remove duplicate rows
        "normalize_features",      # Scale/normalize data
        "calculate_statistics",    # Descriptive statistics
        "perform_correlation",     # Correlation analysis
        "perform_clustering",      # Clustering analysis
        "build_model",             # Build predictive model
        "validate_model",          # Validate model performance
        "create_visualization",    # Create chart/plot
        "generate_insights",       # Extract insights
        "generate_report",         # Create final report
        "export_results",          # Export analysis results
    ]

    def create_environment(self) -> dict[str, Any]:
        """Create data analysis training environment.

        Returns:
            Dictionary containing environment configuration:
            - type: Environment type identifier
            - actions: Available analysis actions
            - tasks: Sample analysis tasks
            - baseline_time: Time baseline for analysis speed
            - baseline_accuracy: Accuracy baseline for comparison

        Example:
            >>> scenario = DataAnalysisScenario()
            >>> env = scenario.create_environment()
            >>> env["type"]
            'data_analysis'
            >>> len(env["actions"])
            15
            >>> len(env["tasks"])
            6
        """
        return {
            "type": "data_analysis",
            "actions": self.AVAILABLE_ACTIONS,
            "tasks": self.SAMPLE_TASKS,
            "baseline_time": 3600.0,  # 1 hour per analysis (untrained)
            "baseline_accuracy": 0.65,  # 65% insight accuracy (untrained)
        }

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        Reward Calculation:
            - Data quality: +15 for proper cleaning and validation
            - Insight accuracy: +20 per accurate insight, -10 per incorrect
            - Visualization quality: +10 per clear visualization
            - Analysis completeness: +12 for thorough analysis
            - Efficiency: +5 for faster than baseline

        Args:
            trajectory: Completed episode trajectory with steps and outcome.

        Returns:
            List of rewards (one per step), broadcast from outcome.

        Example:
            >>> scenario = DataAnalysisScenario()
            >>> trajectory = Trajectory(
            ...     steps=[
            ...         {"action": "clean_data", "data_quality": "high"},
            ...         {"action": "generate_insights", "insight_accurate": True}
            ...     ],
            ...     total_reward=50.0,
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
            outcome_reward = 12.0  # Base reward for successful analysis
        else:
            outcome_reward = -8.0  # Penalty for failed/incomplete analysis

        # Broadcast outcome to all steps
        step_rewards = [outcome_reward] * len(trajectory)

        # Add step-specific bonuses/penalties
        baseline_time = 3600.0  # 1 hour
        baseline_accuracy = 0.65

        for i, step in enumerate(trajectory.steps):
            # Data quality bonus
            if step.get("data_quality") == "high":
                step_rewards[i] += 15.0
            elif step.get("data_quality") == "low":
                step_rewards[i] -= 10.0

            # Insight accuracy rewards
            if step.get("insight_accurate", False):
                step_rewards[i] += 20.0
            elif step.get("insight_inaccurate", False):
                step_rewards[i] -= 10.0

            # Visualization quality bonus
            if step.get("visualization_clear", False):
                step_rewards[i] += 10.0

            # Analysis completeness bonus
            if step.get("thorough_analysis", False):
                step_rewards[i] += 12.0

            # Efficiency bonus
            analysis_time = step.get("analysis_time", baseline_time)
            if analysis_time < baseline_time:
                speed_ratio = (baseline_time - analysis_time) / baseline_time
                step_rewards[i] += 5.0 * speed_ratio

            # Statistical validity bonus
            if step.get("statistically_valid", False):
                step_rewards[i] += 8.0

            # Actionable insights bonus
            if step.get("actionable_insight", False):
                step_rewards[i] += 10.0

        return step_rewards

    def success_criteria(self) -> dict[str, float]:
        """Define target performance metrics for data analysis.

        Returns:
            Dictionary mapping metric names to target values:
            - analysis_accuracy: 85% correct insights
            - data_quality: 90% proper cleaning
            - insight_quality: 80% actionable insights
            - visualization_quality: 85% clear visualizations

        Example:
            >>> scenario = DataAnalysisScenario()
            >>> criteria = scenario.success_criteria()
            >>> criteria["analysis_accuracy"]
            0.85
            >>> criteria["data_quality"]
            0.9
        """
        return {
            "analysis_accuracy": 0.85,  # 85% accuracy
            "data_quality": 0.90,  # 90% data quality
            "insight_quality": 0.80,  # 80% insight quality
            "visualization_quality": 0.85,  # 85% viz quality
        }

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate data analysis specific metrics.

        Extends the base class metrics with data analysis specific calculations
        for accuracy, data quality, and insight quality.

        Args:
            trajectories: List of completed trajectories.

        Returns:
            Dictionary of metrics including standard metrics plus
            data analysis specific calculations.

        Example:
            >>> scenario = DataAnalysisScenario()
            >>> trajectories = [
            ...     Trajectory(
            ...         steps=[{"insight_accurate": True, "data_quality": "high"}],
            ...         success=True,
            ...         total_reward=40.0
            ...     )
            ... ]
            >>> metrics = scenario.calculate_metrics(trajectories)
            >>> "analysis_accuracy" in metrics
            True
        """
        # Get base metrics from parent class
        metrics = super().calculate_metrics(trajectories)

        if not trajectories:
            # Ensure data analysis metrics are included
            metrics["analysis_accuracy"] = 0.0
            metrics["data_quality"] = 0.0
            metrics["insight_quality"] = 0.0
            metrics["visualization_quality"] = 0.0
            return metrics

        # Calculate analysis accuracy
        total_insights = 0
        accurate_insights = 0
        high_quality_data = 0
        total_data_steps = 0
        clear_visualizations = 0
        total_visualizations = 0
        actionable_insights = 0

        for trajectory in trajectories:
            for step in trajectory.steps:
                # Track insights
                if step.get("insight_accurate") or step.get("insight_inaccurate"):
                    total_insights += 1
                    if step.get("insight_accurate"):
                        accurate_insights += 1

                # Track data quality
                if "data_quality" in step:
                    total_data_steps += 1
                    if step.get("data_quality") == "high":
                        high_quality_data += 1

                # Track visualizations
                if "visualization_clear" in step:
                    total_visualizations += 1
                    if step.get("visualization_clear"):
                        clear_visualizations += 1

                # Track actionable insights
                if step.get("actionable_insight"):
                    actionable_insights += 1

        # Analysis accuracy
        if total_insights > 0:
            metrics["analysis_accuracy"] = accurate_insights / total_insights
        else:
            metrics["analysis_accuracy"] = 0.0

        # Data quality
        if total_data_steps > 0:
            metrics["data_quality"] = high_quality_data / total_data_steps
        else:
            metrics["data_quality"] = 0.0

        # Visualization quality
        if total_visualizations > 0:
            metrics["visualization_quality"] = clear_visualizations / total_visualizations
        else:
            metrics["visualization_quality"] = 0.0

        # Insight quality (actionable/total)
        if total_insights > 0:
            metrics["insight_quality"] = actionable_insights / total_insights
        else:
            metrics["insight_quality"] = 0.0

        return metrics
