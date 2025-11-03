"""AgentGym CLI - Command line interface for training AI agents.

This module provides the main CLI commands for AgentGym, including:
- Training agents on scenarios
- Listing available scenarios
- Viewing version and help information

Example:
    Train a customer support agent:
        $ agentgym train customer_support --episodes 100

    List available scenarios:
        $ agentgym list

    Show version:
        $ agentgym --version
"""

import sys
from pathlib import Path
from typing import Optional

import click

from agentgym import __version__
from agentgym.core.config import TrainingConfig
from agentgym.core.trainer import Trainer
from agentgym.scenarios.registry import ScenarioNotFoundError, ScenarioRegistry


@click.group()
@click.version_option(version=__version__, prog_name="AgentGym")
def cli():
    """AgentGym - The Vercel for Agent Training.

    Train AI agents using reinforcement learning with one command.

    \b
    Quick Start:
        agentgym train customer_support --episodes 100
        agentgym list

    For more information, visit: https://agentgym.com
    """
    pass


@cli.command()
@click.argument("scenario", type=str)
@click.option(
    "--episodes",
    "-e",
    type=int,
    default=50,
    help="Number of training episodes (default: 50)",
)
@click.option(
    "--learning-rate",
    "-lr",
    type=float,
    default=0.001,
    help="Learning rate for training (default: 0.001)",
)
@click.option(
    "--batch-size",
    "-b",
    type=int,
    default=32,
    help="Batch size for training (default: 32)",
)
@click.option(
    "--discount-factor",
    "-g",
    type=float,
    default=0.99,
    help="Discount factor for rewards (default: 0.99)",
)
@click.option(
    "--checkpoint-interval",
    "-c",
    type=int,
    default=10,
    help="Save checkpoint every N episodes (default: 10, 0 to disable)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="./models",
    help="Output directory for trained models (default: ./models)",
)
@click.option(
    "--seed",
    "-s",
    type=int,
    default=None,
    help="Random seed for reproducibility (default: random)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def train(
    scenario: str,
    episodes: int,
    learning_rate: float,
    batch_size: int,
    discount_factor: float,
    checkpoint_interval: int,
    output_dir: str,
    seed: Optional[int],
    verbose: bool,
):
    """Train an agent on a scenario.

    \b
    Examples:
        agentgym train customer_support --episodes 100
        agentgym train customer_support -e 100 -lr 0.0003
        agentgym train customer_support --seed 42 --verbose
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Create training configuration
        config = TrainingConfig(
            scenario=scenario,
            episodes=episodes,
            learning_rate=learning_rate,
            batch_size=batch_size,
            discount_factor=discount_factor,
            checkpoint_interval=checkpoint_interval,
            output_dir=output_dir,
            seed=seed,
        )

        # Display training info
        click.echo(f"🚀 AgentGym v{__version__}")
        click.echo(f"\n📋 Training Configuration:")
        click.echo(f"  Scenario: {config.scenario}")
        click.echo(f"  Episodes: {config.episodes}")
        click.echo(f"  Learning Rate: {config.learning_rate}")
        click.echo(f"  Batch Size: {config.batch_size}")
        click.echo(f"  Discount Factor: {config.discount_factor}")
        if config.checkpoint_interval > 0:
            click.echo(f"  Checkpoint Interval: {config.checkpoint_interval}")
        if config.seed is not None:
            click.echo(f"  Seed: {config.seed}")
        click.echo(f"\n📂 Output Directory: {config.output_dir}")
        click.echo()

        # Create trainer and start training
        click.echo("🏋️  Starting training...")
        trainer = Trainer(config)

        # Train with progress updates
        result = trainer.train()

        # Display results
        click.echo("\n✅ Training completed!")
        click.echo(f"\n📊 Final Metrics:")
        click.echo(f"  Tool Reliability: {result.metrics.tool_reliability:.1%}")
        click.echo(f"  Episodes Completed: {result.metrics.episodes_completed}")
        click.echo(f"  Average Tokens: {result.metrics.avg_tokens_used:.0f}")
        click.echo(f"  Average Response Time: {result.metrics.avg_response_time:.1f}s")

        # Check if target met
        scenario_obj = trainer.scenario
        criteria = scenario_obj.success_criteria()
        if result.metrics.tool_reliability >= criteria.get("tool_reliability", 0.95):
            click.echo(
                f"\n🎉 Success! Target reliability "
                f"({criteria.get('tool_reliability', 0.95):.0%}) achieved!"
            )
        else:
            click.echo(
                f"\n⚠️  Target reliability "
                f"({criteria.get('tool_reliability', 0.95):.0%}) not yet achieved. "
                f"Try increasing --episodes."
            )

        click.echo(f"\n💾 Trained model saved to: {result.trained_model_path}")

        if verbose:
            click.echo(f"\n🔍 Detailed Metrics:")
            for key, value in result.metrics.to_dict().items():
                click.echo(f"  {key}: {value}")

    except ScenarioNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo(f"\n💡 Run 'agentgym list' to see available scenarios.", err=True)
        sys.exit(1)

    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Show detailed information about each scenario",
)
def list(detailed: bool):
    """List all available training scenarios.

    \b
    Examples:
        agentgym list
        agentgym list --detailed
    """
    try:
        scenarios = ScenarioRegistry.list()

        if not scenarios:
            click.echo("No scenarios available.")
            return

        click.echo(f"📚 Available Scenarios ({len(scenarios)}):\n")

        for scenario_info in scenarios:
            name = scenario_info["name"]
            description = scenario_info["description"]
            difficulty = scenario_info["difficulty"]

            # Color code by difficulty
            if difficulty == "beginner":
                difficulty_color = "green"
            elif difficulty == "intermediate":
                difficulty_color = "yellow"
            else:
                difficulty_color = "red"

            difficulty_badge = click.style(
                f"[{difficulty.upper()}]", fg=difficulty_color, bold=True
            )

            click.echo(
                f"  {click.style(name, fg='cyan', bold=True)} {difficulty_badge}"
            )
            click.echo(f"    {description}")

            if detailed:
                # Load scenario to get more details
                scenario = ScenarioRegistry.load(name)
                criteria = scenario.success_criteria()
                click.echo(f"    Success Criteria:")
                for key, value in criteria.items():
                    if isinstance(value, float) and value < 1:
                        click.echo(f"      - {key}: {value:.0%}")
                    else:
                        click.echo(f"      - {key}: {value}")

            click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """Show information about AgentGym.

    \b
    Examples:
        agentgym info
    """
    click.echo(f"🤖 AgentGym v{__version__}")
    click.echo("\nThe Vercel for Agent Training - Powered by Agent Lightning")
    click.echo("\nAgentGym is an open-core platform for training AI agents using")
    click.echo("reinforcement learning.")
    click.echo("\nKey Features:")
    click.echo("  • 95% tool reliability (vs 60-70% untrained)")
    click.echo("  • 98% time savings (4 hours → 3 minutes)")
    click.echo("  • 30-50% cost reduction")
    click.echo("  • One-click deployment")
    click.echo("  • Framework-agnostic (LangChain, AutoGen, CrewAI)")
    click.echo("\nQuick Start:")
    click.echo("  agentgym train customer_support --episodes 100")
    click.echo("  agentgym list")
    click.echo("\nDocumentation: https://docs.agentgym.com")
    click.echo("GitHub: https://github.com/agentgym/agentgym")
    click.echo("Website: https://agentgym.com")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
