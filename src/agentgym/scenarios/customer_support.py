"""Customer support scenario for training agents.

This module provides a concrete scenario implementation for training AI agents
to handle customer support tasks with high tool reliability and efficiency.
"""

from typing import Any

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.base import Scenario


class CustomerSupportScenario(Scenario):
    """Train agents to handle customer support with 95% tool reliability.

    This scenario trains agents to effectively use customer support tools
    (knowledge base search, ticket updates, user lookups) while maintaining
    high reliability and efficiency.

    Metrics Targets:
        - Tool reliability: 95% (agents use correct tools reliably)
        - Cost reduction: 30-50% (fewer tokens than untrained baseline)
        - Time savings: 98% (4 hours → 3 minutes)

    Environment:
        The customer support environment simulates real support tickets with:
        - Customer queries (varying complexity)
        - Available tools (search_kb, update_ticket, lookup_user, etc.)
        - Success/failure feedback
        - Performance metrics (tokens, response time)

    Example:
        >>> scenario = CustomerSupportScenario()
        >>> env = scenario.create_environment()
        >>> print(env["type"])
        customer_support

        >>> # During training, trajectories are evaluated
        >>> trajectory = Trajectory(...)  # doctest: +SKIP
        >>> rewards = scenario.broadcast_rewards(trajectory)  # doctest: +SKIP
    """

    name = "customer_support"
    description = "Customer service agent training for 95% tool reliability"
    difficulty = "beginner"

    # Sample customer support tickets for training
    SAMPLE_TICKETS = [
        {
            "id": "TICKET-001",
            "query": "How do I reset my password?",
            "category": "account",
            "complexity": "easy",
            "expected_tools": ["search_kb", "send_reset_link"],
        },
        {
            "id": "TICKET-002",
            "query": "My payment failed but I was charged",
            "category": "billing",
            "complexity": "medium",
            "expected_tools": ["lookup_user", "check_payment", "refund"],
        },
        {
            "id": "TICKET-003",
            "query": "How do I integrate your API with my app?",
            "category": "technical",
            "complexity": "hard",
            "expected_tools": [
                "search_kb",
                "check_api_docs",
                "escalate_to_engineering",
            ],
        },
        {
            "id": "TICKET-004",
            "query": "Can I upgrade my plan mid-month?",
            "category": "billing",
            "complexity": "easy",
            "expected_tools": ["search_kb", "update_subscription"],
        },
        {
            "id": "TICKET-005",
            "query": "My account was locked after multiple failed logins",
            "category": "security",
            "complexity": "medium",
            "expected_tools": ["lookup_user", "verify_identity", "unlock_account"],
        },
    ]

    # Available tools in the customer support environment
    AVAILABLE_TOOLS = [
        "search_kb",  # Search knowledge base
        "update_ticket",  # Update ticket status/notes
        "lookup_user",  # Look up user account info
        "send_reset_link",  # Send password reset
        "check_payment",  # Check payment history
        "refund",  # Issue refund
        "check_api_docs",  # Check API documentation
        "escalate_to_engineering",  # Escalate to engineering team
        "update_subscription",  # Update subscription plan
        "verify_identity",  # Verify user identity
        "unlock_account",  # Unlock locked account
    ]

    def create_environment(self) -> dict[str, Any]:
        """Create customer support training environment.

        Returns:
            Dictionary containing environment configuration:
            - type: Environment type identifier
            - tools: Available tools for the agent
            - tickets: Sample customer support tickets
            - baseline_tokens: Token usage baseline for cost comparison
            - baseline_time: Time baseline for speed comparison

        Example:
            >>> scenario = CustomerSupportScenario()
            >>> env = scenario.create_environment()
            >>> env["type"]
            'customer_support'
            >>> len(env["tools"])
            11
            >>> len(env["tickets"])
            5
        """
        return {
            "type": "customer_support",
            "tools": self.AVAILABLE_TOOLS,
            "tickets": self.SAMPLE_TICKETS,
            "baseline_tokens": 500,  # Untrained agent avg tokens per ticket
            "baseline_time": 240.0,  # Untrained agent avg seconds per ticket (4 min)
        }

    def broadcast_rewards(self, trajectory: Trajectory) -> list[float]:
        """Broadcast trajectory-level reward to all steps.

        Following AgentFlow research: broadcast the outcome reward to ALL steps
        in the trajectory, not just the terminal state. This solves credit
        assignment better than sparse rewards.

        Reward Calculation:
            - Tool reliability: +10 per successful tool use, -20 per failure
            - Cost efficiency: +5 for token savings vs baseline
            - Speed: +3 for fast response vs baseline

        Args:
            trajectory: Completed episode trajectory with steps and outcome.

        Returns:
            List of rewards (one per step), broadcast from outcome.

        Example:
            >>> scenario = CustomerSupportScenario()
            >>> trajectory = Trajectory(
            ...     steps=[
            ...         {"tool": "search_kb", "tool_success": True, "tokens_used": 200},
            ...         {"tool": "send_reset_link", "tool_success": True, "tokens_used": 150}
            ...     ],
            ...     total_reward=35.0,
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
            outcome_reward = 10.0  # Base reward for successful ticket resolution
        else:
            outcome_reward = -5.0  # Penalty for failed ticket resolution

        # Broadcast outcome to all steps
        step_rewards = [outcome_reward] * len(trajectory)

        # Add step-specific bonuses/penalties
        baseline_tokens = 500  # From environment
        baseline_time = 240.0  # From environment

        for i, step in enumerate(trajectory.steps):
            # Tool reliability bonus/penalty
            if step.get("tool_success", False):
                step_rewards[i] += 10.0  # Successful tool use
            else:
                step_rewards[i] -= 20.0  # Failed tool use (higher penalty)

            # Cost efficiency bonus
            tokens_used = step.get("tokens_used", baseline_tokens)
            if tokens_used < baseline_tokens:
                # Reward token savings
                savings_ratio = (baseline_tokens - tokens_used) / baseline_tokens
                step_rewards[i] += 5.0 * savings_ratio

            # Speed bonus
            step_time = step.get("response_time", baseline_time)
            if step_time < baseline_time:
                # Reward faster responses
                speed_ratio = (baseline_time - step_time) / baseline_time
                step_rewards[i] += 3.0 * speed_ratio

        return step_rewards

    def success_criteria(self) -> dict[str, float]:
        """Define target performance metrics for customer support.

        Returns:
            Dictionary mapping metric names to target values:
            - tool_reliability: 95% success rate on tool calls
            - cost_reduction: 30% reduction in token usage vs baseline
            - time_savings: 98% time savings (4 hours → 3 minutes)

        Example:
            >>> scenario = CustomerSupportScenario()
            >>> criteria = scenario.success_criteria()
            >>> criteria["tool_reliability"]
            0.95
            >>> criteria["cost_reduction"]
            0.3
        """
        return {
            "tool_reliability": 0.95,  # 95% tool success rate
            "cost_reduction": 0.30,  # 30% cost reduction
            "time_savings": 0.98,  # 98% time savings (4 hours → 3 min)
        }

    def calculate_metrics(self, trajectories: list[Trajectory]) -> dict[str, float]:
        """Calculate customer support specific metrics.

        Extends the base class metrics with customer support specific calculations
        that properly account for the baseline comparisons.

        Args:
            trajectories: List of completed trajectories.

        Returns:
            Dictionary of metrics including standard metrics plus
            customer support specific calculations.

        Example:
            >>> scenario = CustomerSupportScenario()
            >>> trajectories = [
            ...     Trajectory(steps=[{"tool_success": True}], success=True, total_reward=10.0)
            ... ]
            >>> metrics = scenario.calculate_metrics(trajectories)
            >>> "tool_reliability" in metrics
            True
        """
        # Get base metrics from parent class
        metrics = super().calculate_metrics(trajectories)

        if not trajectories:
            # Ensure time_savings is included even for empty trajectories
            metrics["time_savings"] = 0.0
            return metrics

        # Customer support specific: calculate cost reduction more accurately
        baseline_tokens = 500  # From environment
        actual_avg_tokens = metrics.get("avg_tokens_used", baseline_tokens)

        if baseline_tokens > 0:
            cost_reduction = max(
                0.0, (baseline_tokens - actual_avg_tokens) / baseline_tokens
            )
            metrics["cost_reduction"] = cost_reduction

        # Customer support specific: calculate time savings
        baseline_time = 240.0  # 4 minutes in seconds
        actual_avg_time = metrics.get("avg_response_time", baseline_time)

        if baseline_time > 0:
            time_savings = max(0.0, (baseline_time - actual_avg_time) / baseline_time)
            metrics["time_savings"] = time_savings
        else:
            metrics["time_savings"] = 0.0

        return metrics
