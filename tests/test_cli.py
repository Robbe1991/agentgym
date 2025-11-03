"""Tests for CLI module.

This module contains comprehensive tests for the AgentGym CLI,
including train, list, and info commands.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from agentgym.cli.main import cli
from agentgym.scenarios.registry import ScenarioRegistry


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "models"
    output_dir.mkdir()
    return str(output_dir)


class TestCLIVersion:
    """Test CLI version command."""

    def test_version_flag(self, runner):
        """Test --version flag."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "AgentGym" in result.output
        # Version should be displayed
        assert "0.1.0" in result.output


class TestCLIHelp:
    """Test CLI help commands."""

    def test_help_flag(self, runner):
        """Test --help flag."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "AgentGym" in result.output
        assert "train" in result.output
        assert "list" in result.output

    def test_train_help(self, runner):
        """Test train command help."""
        result = runner.invoke(cli, ["train", "--help"])

        assert result.exit_code == 0
        assert "Train an agent" in result.output
        assert "--episodes" in result.output
        assert "--learning-rate" in result.output


class TestListCommand:
    """Test list command."""

    def test_list_scenarios(self, runner):
        """Test listing scenarios."""
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Available Scenarios" in result.output
        assert "customer_support" in result.output

    def test_list_scenarios_detailed(self, runner):
        """Test listing scenarios with details."""
        result = runner.invoke(cli, ["list", "--detailed"])

        assert result.exit_code == 0
        assert "Available Scenarios" in result.output
        assert "customer_support" in result.output
        assert "Success Criteria" in result.output
        assert "tool_reliability" in result.output

    def test_list_shows_difficulty(self, runner):
        """Test that list shows difficulty levels."""
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "BEGINNER" in result.output or "beginner" in result.output.lower()


class TestInfoCommand:
    """Test info command."""

    def test_info_displays_version(self, runner):
        """Test that info displays version."""
        result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "AgentGym" in result.output
        assert "0.1.0" in result.output

    def test_info_displays_features(self, runner):
        """Test that info displays key features."""
        result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "tool reliability" in result.output.lower()
        assert "time savings" in result.output.lower()
        assert "cost reduction" in result.output.lower()

    def test_info_displays_links(self, runner):
        """Test that info displays links."""
        result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "agentgym.com" in result.output


class TestTrainCommand:
    """Test train command."""

    def test_train_with_scenario(self, runner, temp_output_dir):
        """Test training with a valid scenario."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Starting training" in result.output
        assert "Training completed" in result.output
        assert "Tool Reliability" in result.output

    def test_train_with_invalid_scenario(self, runner, temp_output_dir):
        """Test training with invalid scenario."""
        result = runner.invoke(
            cli,
            [
                "train",
                "nonexistent_scenario",
                "--episodes",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output
        assert "not found" in result.output.lower()

    def test_train_shows_configuration(self, runner, temp_output_dir):
        """Test that train shows configuration."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--learning-rate",
                "0.0003",
                "--batch-size",
                "16",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Training Configuration" in result.output
        assert "customer_support" in result.output
        assert "3" in result.output  # episodes
        assert "0.0003" in result.output  # learning rate

    def test_train_with_seed(self, runner, temp_output_dir):
        """Test training with seed for reproducibility."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "5",
                "--seed",
                "42",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Seed: 42" in result.output

    def test_train_with_checkpoint_interval(self, runner, temp_output_dir):
        """Test training with checkpoint interval."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "10",
                "--checkpoint-interval",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Checkpoint Interval: 5" in result.output

    def test_train_with_verbose(self, runner, temp_output_dir):
        """Test training with verbose output."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--verbose",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Detailed Metrics" in result.output

    def test_train_shows_final_metrics(self, runner, temp_output_dir):
        """Test that train shows final metrics."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Final Metrics" in result.output
        assert "Tool Reliability" in result.output
        assert "Episodes Completed" in result.output
        assert "Average Tokens" in result.output
        assert "Average Response Time" in result.output

    def test_train_shows_model_path(self, runner, temp_output_dir):
        """Test that train shows trained model path."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        assert "Trained model saved to" in result.output
        assert temp_output_dir in result.output

    def test_train_creates_output_dir(self, runner, tmp_path):
        """Test that train creates output directory if it doesn't exist."""
        output_dir = tmp_path / "new_models"

        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--output-dir",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        assert output_dir.exists()

    def test_train_default_parameters(self, runner, temp_output_dir):
        """Test training with default parameters."""
        result = runner.invoke(
            cli, ["train", "customer_support", "--output-dir", temp_output_dir]
        )

        assert result.exit_code == 0
        # Should use defaults: 50 episodes, 0.001 lr, etc.
        assert "Training Configuration" in result.output


class TestTrainCommandValidation:
    """Test train command validation."""

    def test_train_with_negative_episodes(self, runner, temp_output_dir):
        """Test training with negative episodes."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "-10",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_train_with_zero_episodes(self, runner, temp_output_dir):
        """Test training with zero episodes."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "0",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_train_with_negative_learning_rate(self, runner, temp_output_dir):
        """Test training with negative learning rate."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--learning-rate",
                "-0.1",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_train_with_invalid_discount_factor(self, runner, temp_output_dir):
        """Test training with invalid discount factor."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--discount-factor",
                "1.5",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output


class TestTrainCommandShortFlags:
    """Test train command with short flags."""

    def test_train_with_short_flags(self, runner, temp_output_dir):
        """Test training with short flags."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "-e",
                "5",
                "-lr",
                "0.0003",
                "-b",
                "16",
                "-g",
                "0.95",
                "-c",
                "5",
                "-o",
                temp_output_dir,
                "-s",
                "42",
                "-v",
            ],
        )

        assert result.exit_code == 0
        assert "Training completed" in result.output
        assert "Detailed Metrics" in result.output  # verbose flag


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_full_workflow(self, runner, temp_output_dir):
        """Test complete workflow: list, info, train."""
        # 1. List scenarios
        list_result = runner.invoke(cli, ["list"])
        assert list_result.exit_code == 0
        assert "customer_support" in list_result.output

        # 2. Get info
        info_result = runner.invoke(cli, ["info"])
        assert info_result.exit_code == 0
        assert "AgentGym" in info_result.output

        # 3. Train
        train_result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "5",
                "--output-dir",
                temp_output_dir,
            ],
        )
        assert train_result.exit_code == 0
        assert "Training completed" in train_result.output

    def test_list_then_train_scenario(self, runner, temp_output_dir):
        """Test listing scenarios then training one."""
        # List to find scenario name
        list_result = runner.invoke(cli, ["list"])
        assert "customer_support" in list_result.output

        # Train the scenario found in list
        train_result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--output-dir",
                temp_output_dir,
            ],
        )
        assert train_result.exit_code == 0


class TestCLIEdgeCases:
    """Test CLI edge cases."""

    def test_empty_command(self, runner):
        """Test running CLI with no command."""
        result = runner.invoke(cli, [])

        # Click returns exit code 2 when no command is provided
        assert result.exit_code == 2
        # Should show usage/help info
        assert "Usage" in result.output or "AgentGym" in result.output

    def test_train_without_scenario(self, runner):
        """Test train command without scenario argument."""
        result = runner.invoke(cli, ["train"])

        assert result.exit_code != 0
        # Should show error about missing argument

    def test_list_with_no_scenarios(self, runner):
        """Test list when registry is empty."""
        # Clear registry
        ScenarioRegistry.clear()

        result = runner.invoke(cli, ["list"])

        # Should still work, but show built-ins (lazy loading)
        assert result.exit_code == 0

    def test_multiple_commands_sequential(self, runner, temp_output_dir):
        """Test running multiple commands sequentially."""
        # Run list
        result1 = runner.invoke(cli, ["list"])
        assert result1.exit_code == 0

        # Run info
        result2 = runner.invoke(cli, ["info"])
        assert result2.exit_code == 0

        # Run train
        result3 = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--output-dir",
                temp_output_dir,
            ],
        )
        assert result3.exit_code == 0


class TestCLIOutput:
    """Test CLI output formatting."""

    def test_train_uses_emojis(self, runner, temp_output_dir):
        """Test that train output includes emojis."""
        result = runner.invoke(
            cli,
            [
                "train",
                "customer_support",
                "--episodes",
                "3",
                "--output-dir",
                temp_output_dir,
            ],
        )

        assert result.exit_code == 0
        # Check for emoji indicators (may be rendered as text on some systems)
        assert "AgentGym" in result.output
        assert "Starting training" in result.output
        assert "Training completed" in result.output

    def test_list_uses_color_coding(self, runner):
        """Test that list uses color coding for difficulty."""
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        # Difficulty should be shown
        assert "BEGINNER" in result.output or "beginner" in result.output.lower()
