"""Example usage of Code Review scenario for agent training.

This example demonstrates how to:
1. Create a code review training scenario
2. Set up the environment
3. Simulate code review trajectories
4. Calculate rewards and metrics
5. Evaluate performance against success criteria

The code review scenario trains agents to:
- Identify bugs and security issues
- Provide constructive feedback
- Make appropriate approve/reject decisions
- Complete reviews efficiently
"""

from agentgym.core.trainer import Trajectory
from agentgym.scenarios.code_review import CodeReviewScenario

# Example 1: Create Code Review Scenario
print("=" * 60)
print("Example 1: Creating Code Review Scenario")
print("=" * 60)

scenario = CodeReviewScenario()

print(f"Scenario name: {scenario.name}")
print(f"Description: {scenario.description}")
print(f"Difficulty: {scenario.difficulty}")
print(f"String representation: {scenario}")
print()

# Example 2: Inspect Sample Submissions
print("=" * 60)
print("Example 2: Sample Code Submissions")
print("=" * 60)

for i, submission in enumerate(scenario.SAMPLE_SUBMISSIONS[:3], 1):
    print(f"\nSubmission {i}:")
    print(f"  ID: {submission['id']}")
    print(f"  Title: {submission['title']}")
    print(f"  Language: {submission['language']}")
    print(f"  Complexity: {submission['complexity']}")
    print(f"  Lines of Code: {submission['loc']}")
    print(f"  Issues: {len(submission['issues'])}")
    for issue in submission['issues']:
        print(f"    - {issue['severity']} {issue['type']}: {issue['description']}")
print()

# Example 3: Create Training Environment
print("=" * 60)
print("Example 3: Training Environment")
print("=" * 60)

env = scenario.create_environment()

print(f"Environment type: {env['type']}")
print(f"Available actions: {len(env['actions'])}")
print("Actions:", ", ".join(env['actions'][:5]), "...")
print(f"Sample submissions: {len(env['submissions'])}")
print(f"Baseline review time: {env['baseline_time']} seconds ({env['baseline_time'] / 60:.1f} minutes)")
print(f"Baseline accuracy: {env['baseline_accuracy'] * 100:.0f}%")
print()

# Example 4: Success Criteria
print("=" * 60)
print("Example 4: Success Criteria")
print("=" * 60)

criteria = scenario.success_criteria()

print("Target Performance Metrics:")
for metric, target in criteria.items():
    if "rate" in metric or "accuracy" in metric or "completeness" in metric:
        print(f"  {metric}: {target * 100:.0f}%")
    else:
        print(f"  {metric}: {target}")
print()

# Example 5: Successful Review Trajectory
print("=" * 60)
print("Example 5: Successful Code Review")
print("=" * 60)

# Simulate a successful code review
successful_review = Trajectory(
    steps=[
        {"action": "start_review"},
        {
            "action": "add_comment",
            "issue_found": True,
            "severity": "high",
            "false_positive": False,
            "constructive_feedback": True,
        },
        {
            "action": "add_comment",
            "issue_found": True,
            "severity": "medium",
            "false_positive": False,
            "constructive_feedback": True,
        },
        {
            "action": "request_changes",
            "appropriate_action": True,
            "thorough_review": True,
            "review_time": 400.0,
        },
    ],
    total_reward=75.0,
    success=True,
    metadata={"found_all_issues": True, "tokens_used": 300, "response_time": 400.0},
)

rewards = scenario.broadcast_rewards(successful_review)

print("Successful review trajectory:")
print(f"  Steps: {len(successful_review.steps)}")
print(f"  Total reward: {successful_review.total_reward}")
print(f"  Step rewards: {[f'{r:.1f}' for r in rewards]}")
print(f"  Success: {successful_review.success}")
print()

# Example 6: Poor Review with False Positives
print("=" * 60)
print("Example 6: Poor Review with False Positives")
print("=" * 60)

# Simulate a review with false positives
poor_review = Trajectory(
    steps=[
        {"action": "start_review"},
        {
            "action": "add_comment",
            "issue_found": True,
            "severity": "high",
            "false_positive": True,  # False positive penalty
        },
        {
            "action": "request_changes",
            "appropriate_action": False,  # Inappropriate action
            "review_time": 2000.0,  # Slow review
        },
    ],
    total_reward=-10.0,
    success=False,
)

poor_rewards = scenario.broadcast_rewards(poor_review)

print("Poor review trajectory:")
print(f"  Steps: {len(poor_review.steps)}")
print(f"  Total reward: {poor_review.total_reward}")
print(f"  Step rewards: {[f'{r:.1f}' for r in poor_rewards]}")
print(f"  Success: {poor_review.success}")
print(f"  Note: Negative rewards due to false positives and inappropriate actions")
print()

# Example 7: Critical Security Issue Detection
print("=" * 60)
print("Example 7: Critical Security Issue Detection")
print("=" * 60)

# Simulate finding a critical security issue
security_review = Trajectory(
    steps=[
        {"action": "start_review"},
        {"action": "check_security"},
        {
            "action": "add_comment",
            "issue_found": True,
            "severity": "critical",  # Critical severity gets highest reward
            "false_positive": False,
            "constructive_feedback": True,
        },
        {
            "action": "request_changes",
            "appropriate_action": True,
            "review_time": 300.0,  # Fast review
        },
    ],
    total_reward=65.0,
    success=True,
)

security_rewards = scenario.broadcast_rewards(security_review)

print("Security issue detection:")
print(f"  Steps: {len(security_review.steps)}")
print(f"  Total reward: {security_review.total_reward}")
print(f"  Step rewards: {[f'{r:.1f}' for r in security_rewards]}")
print(f"  Note: Critical severity issues receive 20-point bonus")
print()

# Example 8: Clean Code Approval
print("=" * 60)
print("Example 8: Clean Code Approval")
print("=" * 60)

# Simulate approving clean code
clean_approval = Trajectory(
    steps=[
        {"action": "start_review"},
        {"action": "read_code"},
        {"action": "check_tests"},
        {"action": "run_linter"},
        {
            "action": "approve",
            "appropriate_action": True,
            "thorough_review": True,
            "review_time": 500.0,
        },
    ],
    total_reward=48.0,
    success=True,
)

clean_rewards = scenario.broadcast_rewards(clean_approval)

print("Clean code approval:")
print(f"  Steps: {len(clean_approval.steps)}")
print(f"  Total reward: {clean_approval.total_reward}")
print(f"  Step rewards: {[f'{r:.1f}' for r in clean_rewards]}")
print(f"  Note: Appropriate approval of clean code is rewarded")
print()

# Example 9: Calculate Metrics from Multiple Reviews
print("=" * 60)
print("Example 9: Aggregate Metrics")
print("=" * 60)

# Simulate multiple review trajectories
trajectories = [
    Trajectory(
        steps=[
            {"issue_found": True, "false_positive": False, "total_issues": 2, "review_time": 400.0}
        ],
        total_reward=35.0,
        success=True,
        metadata={"found_all_issues": True, "tokens_used": 250, "response_time": 400.0},
    ),
    Trajectory(
        steps=[
            {"issue_found": True, "false_positive": False, "total_issues": 3, "review_time": 500.0},
            {"issue_found": True, "false_positive": False, "total_issues": 3, "review_time": 500.0},
        ],
        total_reward=45.0,
        success=True,
        metadata={"found_all_issues": False, "tokens_used": 300, "response_time": 500.0},
    ),
    Trajectory(
        steps=[
            {"issue_found": True, "false_positive": True, "total_issues": 1, "review_time": 800.0}
        ],
        total_reward=10.0,
        success=False,
        metadata={"found_all_issues": False, "tokens_used": 400, "response_time": 800.0},
    ),
]

metrics = scenario.calculate_metrics(trajectories)

print("Calculated Metrics:")
print(f"  Tool Reliability: {metrics['tool_reliability'] * 100:.1f}%")
print(f"  Review Accuracy: {metrics['review_accuracy'] * 100:.1f}%")
print(f"  False Positive Rate: {metrics['false_positive_rate'] * 100:.1f}%")
print(f"  Review Completeness: {metrics['review_completeness'] * 100:.1f}%")
print(f"  Avg Review Time: {metrics['avg_review_time']:.1f}s")
print(f"  Avg Response Time: {metrics['avg_response_time']:.1f}s")
print(f"  Final Reward: {metrics['final_reward']:.1f}")
print()

# Example 10: Compare Against Success Criteria
print("=" * 60)
print("Example 10: Performance Evaluation")
print("=" * 60)

print("Comparing current performance against targets:")
for metric_name, target_value in criteria.items():
    if metric_name in metrics:
        current_value = metrics[metric_name]
        if "rate" in metric_name or "accuracy" in metric_name or "completeness" in metric_name:
            print(f"  {metric_name}:")
            print(f"    Target: {target_value * 100:.0f}%")
            print(f"    Current: {current_value * 100:.1f}%")
            if current_value >= target_value:
                print(f"    Status: ✓ PASS")
            else:
                print(f"    Status: ✗ NEEDS IMPROVEMENT")
        else:
            print(f"  {metric_name}:")
            print(f"    Target: {target_value}")
            print(f"    Current: {current_value:.1f}")
            if current_value <= target_value:
                print(f"    Status: ✓ PASS")
            else:
                print(f"    Status: ✗ NEEDS IMPROVEMENT")
print()

# Example 11: Reward Breakdown by Severity
print("=" * 60)
print("Example 11: Reward Breakdown by Issue Severity")
print("=" * 60)

severity_examples = {
    "critical": Trajectory(
        steps=[{"issue_found": True, "severity": "critical"}],
        total_reward=35.0,
        success=True,
    ),
    "high": Trajectory(
        steps=[{"issue_found": True, "severity": "high"}],
        total_reward=25.0,
        success=True,
    ),
    "medium": Trajectory(
        steps=[{"issue_found": True, "severity": "medium"}],
        total_reward=20.0,
        success=True,
    ),
    "low": Trajectory(
        steps=[{"issue_found": True, "severity": "low"}],
        total_reward=17.0,
        success=True,
    ),
}

print("Reward for detecting issues by severity:")
for severity, traj in severity_examples.items():
    rewards = scenario.broadcast_rewards(traj)
    print(f"  {severity.capitalize()}: {rewards[0]:.1f} points")
print()

# Example 12: Trainable Components
print("=" * 60)
print("Example 12: Trainable Components")
print("=" * 60)

components = scenario.define_trainable_components()

print("Training Configuration (following AgentFlow research):")
for component, trainable in components.items():
    status = "TRAIN" if trainable else "FREEZE"
    print(f"  {component}: {status}")
print()

# Example 13: Validation
print("=" * 60)
print("Example 13: Trajectory Validation")
print("=" * 60)

# Valid trajectory
valid_traj = Trajectory(
    steps=[{"action": "review"}],
    total_reward=15.0,
    success=True,
)

# Invalid trajectory (empty)
invalid_traj = Trajectory(
    steps=[],
    total_reward=0.0,
    success=False,
)

print(f"Valid trajectory: {scenario.validate_trajectory(valid_traj)}")
print(f"Invalid trajectory (empty): {scenario.validate_trajectory(invalid_traj)}")
print()

print("=" * 60)
print("All examples completed!")
print("=" * 60)
print()
print("Next steps:")
print("1. Integrate this scenario with AgentGym trainer")
print("2. Train agents on code review tasks")
print("3. Monitor metrics and adjust rewards as needed")
print("4. Deploy trained agents for real code reviews")
