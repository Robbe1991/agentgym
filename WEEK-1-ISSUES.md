# Week 1 Development - GitHub Issues (Workpackages)

**Create these on GitHub:** https://github.com/Robbe1991/agentgym/issues

---

## 🏗️ Track 1: Core Foundation (Day 1-2)

### Issue #1: Implement Core Configuration (TrainingConfig)

**Title:** `feat: Implement core configuration (TrainingConfig)`

**Labels:** `feature`, `week-1`, `core`

**Description:**
```markdown
## Description
Implement Pydantic-based configuration system for training sessions.

## Acceptance Criteria
- [ ] `TrainingConfig` class in `src/agentgym/core/config.py`
- [ ] Pydantic BaseModel with validation
- [ ] Sensible defaults for all fields
- [ ] Type hints and Google-style docstrings
- [ ] Unit tests with 80%+ coverage in `tests/test_config.py`

## Technical Details
```python
from pydantic import BaseModel, Field

class TrainingConfig(BaseModel):
    """Configuration for agent training session."""

    scenario: str = Field(..., description="Scenario name")
    framework: str = Field("langchain", description="Framework to use")
    episodes: int = Field(10000, gt=0, description="Number of episodes")
    gpu_provider: str = Field("auto", description="GPU provider")
    learning_rate: float = Field(0.0003, gt=0)
    discount_factor: float = Field(0.95, gt=0, lt=1)

    class Config:
        extra = "allow"  # Allow extension
```

## References
- [SYSTEM_DESIGN.md](docs/architecture/SYSTEM_DESIGN.md) - Component design
- [pyproject.toml](pyproject.toml) - Dependencies

## Estimated Time
2-3 hours
```

---

### Issue #2: Implement Training Results (TrainingResult)

**Title:** `feat: Implement training results dataclass (TrainingResult)`

**Labels:** `feature`, `week-1`, `core`

**Description:**
```markdown
## Description
Implement dataclass for storing training results and metrics.

## Acceptance Criteria
- [ ] `TrainingResult` class in `src/agentgym/core/result.py`
- [ ] Dataclass with metrics (tool reliability, cost, time)
- [ ] Serialization methods (to_dict, from_dict, save, load)
- [ ] Type hints and docstrings
- [ ] Unit tests with 80%+ coverage

## Technical Details
```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TrainingMetrics:
    """Metrics from training session."""
    tool_reliability: float  # 0.0-1.0 (target: 0.95)
    avg_tokens_used: float
    avg_response_time: float
    cost_reduction: float    # Percentage
    episodes_completed: int

@dataclass
class TrainingResult:
    """Complete training result."""
    config: TrainingConfig
    metrics: TrainingMetrics
    trained_model_path: str
    artifacts: Dict[str, Any]

    def to_dict(self) -> Dict:
        ...

    def save(self, path: str):
        ...

    @classmethod
    def load(cls, path: str) -> 'TrainingResult':
        ...
```

## References
- [TECHNICAL_APPROACH.md](docs/architecture/TECHNICAL_APPROACH.md) - Success metrics

## Estimated Time
2-3 hours
```

---

### Issue #3: Implement Core Trainer (with On-Policy RL)

**Title:** `feat: Implement core trainer with on-policy RL (#3)`

**Labels:** `feature`, `week-1`, `core`

**Description:**
```markdown
## Description
Implement core Trainer class that wraps Agent Lightning with on-policy RL.

## ⚠️ CRITICAL: AgentFlow Insights
- **ON-POLICY RL** (live tool interaction) - NOT offline SFT
- **Trajectory-level reward broadcasting** - NOT sparse rewards
- **Modular training** - Only train tool selection

See: [TECHNICAL_APPROACH.md Section 6](docs/architecture/TECHNICAL_APPROACH.md)

## Acceptance Criteria
- [ ] `Trainer` class in `src/agentgym/core/trainer.py`
- [ ] On-policy training loop (agent interacts during training)
- [ ] Integration with Agent Lightning (or mock for now)
- [ ] Trajectory collection and reward broadcasting
- [ ] Type hints and comprehensive docstrings
- [ ] Unit tests with 80%+ coverage
- [ ] Example usage in `tests/test_trainer.py`

## Technical Details
```python
class Trainer:
    """
    Agent trainer using reinforcement learning.

    Inspired by AgentFlow (Stanford, Oct 2025):
    - On-policy RL (NOT offline SFT)
    - Trajectory-level reward broadcasting
    - Modular training (only tool selection)
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.scenario = ScenarioRegistry.load(config.scenario)
        self.rl_engine = self._init_rl_engine()

    def train(self) -> TrainingResult:
        """Train agent using on-policy RL."""
        for episode in range(self.config.episodes):
            # ON-POLICY: Live interaction
            trajectory = self.collect_trajectory_online()

            # BROADCAST: All steps get outcome signal
            rewards = self.scenario.broadcast_rewards(trajectory)

            # MODULAR: Only update tool selection
            self.update_policy(
                trajectory,
                rewards,
                trainable=["tool_selection", "parameter_selection"]
            )

        return self.create_result()

    def collect_trajectory_online(self):
        """Collect trajectory via live interaction (on-policy)."""
        # Agent actually interacts with tools/environment
        pass

    def update_policy(self, trajectory, rewards, trainable):
        """Update only specified trainable components."""
        # Use Agent Lightning (or mock)
        pass
```

## References
- [TECHNICAL_APPROACH.md Section 6](docs/architecture/TECHNICAL_APPROACH.md) - AgentFlow insights
- [AgentFlow Paper](https://arxiv.org/abs/2510.05592) - On-policy RL results

## Notes
- If Agent Lightning not available on PyPI yet, create mock for now
- Focus on architecture correctness, actual RL can be placeholder

## Estimated Time
4-6 hours
```

---

## 🎨 Track 2: Scenarios (Day 3-4)

### Issue #4: Implement Base Scenario Class

**Title:** `feat: Implement base scenario class with trajectory-level rewards`

**Labels:** `feature`, `week-1`, `scenarios`

**Description:**
```markdown
## Description
Implement abstract base class for all training scenarios.

## Acceptance Criteria
- [ ] `Scenario` ABC in `src/agentgym/scenarios/base.py`
- [ ] Abstract methods: `create_environment`, `broadcast_rewards`, `define_trainable_components`
- [ ] Trajectory-level reward broadcasting (AgentFlow insight)
- [ ] Type hints and docstrings
- [ ] Unit tests for concrete implementations

## Technical Details
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class Scenario(ABC):
    """Base class for training scenarios."""

    name: str
    description: str
    difficulty: str  # beginner, intermediate, advanced

    @abstractmethod
    def create_environment(self):
        """Create training environment."""
        pass

    @abstractmethod
    def broadcast_rewards(self, trajectory) -> List[float]:
        """
        Broadcast trajectory-level reward to all steps.

        AgentFlow showed this solves credit assignment better
        than sparse rewards only at the end.
        """
        pass

    def define_trainable_components(self) -> Dict[str, bool]:
        """
        Define which components to train vs freeze.

        AgentFlow insight: Training only planning (tool selection)
        is more efficient than training everything.
        """
        return {
            "tool_selection": True,
            "parameter_selection": True,
            "tool_execution": False,
            "output_generation": False
        }

    @abstractmethod
    def success_criteria(self) -> Dict[str, float]:
        """Define target metrics for this scenario."""
        pass
```

## References
- [TECHNICAL_APPROACH.md Section 6.2](docs/architecture/TECHNICAL_APPROACH.md) - Trajectory-level rewards
- [TECHNICAL_APPROACH.md Section 6.3](docs/architecture/TECHNICAL_APPROACH.md) - Modular training

## Estimated Time
3-4 hours
```

---

### Issue #5: Implement Scenario Registry

**Title:** `feat: Implement scenario registry for dynamic loading`

**Labels:** `feature`, `week-1`, `scenarios`

**Description:**
```markdown
## Description
Implement registry system for discovering and loading scenarios.

## Acceptance Criteria
- [ ] `ScenarioRegistry` class in `src/agentgym/scenarios/registry.py`
- [ ] Dynamic scenario loading by name
- [ ] List available scenarios
- [ ] Scenario metadata (name, description, difficulty)
- [ ] Type hints and docstrings
- [ ] Unit tests with 80%+ coverage

## Technical Details
```python
class ScenarioRegistry:
    """Registry for managing training scenarios."""

    BUILT_IN = {
        "customer_support": CustomerSupportScenario,
        # More later...
    }

    @classmethod
    def load(cls, scenario_name: str) -> Scenario:
        """Load scenario by name."""
        if scenario_name not in cls.BUILT_IN:
            available = ", ".join(cls.BUILT_IN.keys())
            raise ScenarioNotFoundError(
                f"Scenario '{scenario_name}' not found. "
                f"Available: {available}"
            )
        return cls.BUILT_IN[scenario_name]()

    @classmethod
    def list(cls) -> List[Dict]:
        """List all available scenarios."""
        return [
            {
                "name": name,
                "description": scenario_class.description,
                "difficulty": scenario_class.difficulty,
            }
            for name, scenario_class in cls.BUILT_IN.items()
        ]
```

## Estimated Time
2-3 hours
```

---

### Issue #6: Implement Customer Support Scenario

**Title:** `feat: Implement customer support scenario (95% tool reliability target)`

**Labels:** `feature`, `week-1`, `scenarios`

**Description:**
```markdown
## Description
Implement first concrete scenario for training customer support agents.

## Acceptance Criteria
- [ ] `CustomerSupportScenario` in `src/agentgym/scenarios/customer_support.py`
- [ ] Inherits from `Scenario` base class
- [ ] Environment definition (state/action spaces)
- [ ] Reward function emphasizing tool reliability
- [ ] Trajectory-level reward broadcasting
- [ ] Success criteria: 95% tool reliability
- [ ] Type hints and docstrings
- [ ] Integration test showing full training loop

## Technical Details
```python
class CustomerSupportScenario(Scenario):
    """
    Train agents to handle customer support with 95% tool reliability.

    Metrics targets:
    - Tool reliability: 95%
    - Cost reduction: 30-50%
    - Time savings: 98%
    """

    name = "customer_support"
    description = "Customer service agent training"
    difficulty = "beginner"

    def create_environment(self):
        """Create customer support environment."""
        # Define state space (customer queries, history, etc.)
        # Define action space (tool calls, parameters)
        pass

    def broadcast_rewards(self, trajectory):
        """
        Broadcast outcome reward to all steps.

        Reward calculation:
        - Tool reliability: +10 per success, -20 per failure
        - Cost efficiency: +5 for token savings
        - Speed: +3 for fast response
        """
        outcome_reward = self.evaluate_outcome(trajectory)
        step_rewards = [outcome_reward] * len(trajectory.steps)

        # Add step-specific bonuses
        for i, step in enumerate(trajectory.steps):
            if step.tool_success:
                step_rewards[i] += 10
            if step.tokens_used < baseline:
                step_rewards[i] += 5

        return step_rewards

    def success_criteria(self):
        return {
            "tool_reliability": 0.95,
            "cost_reduction": 0.30,
            "time_savings": 0.98
        }
```

## References
- [TECHNICAL_APPROACH.md Section 4.2.A](docs/architecture/TECHNICAL_APPROACH.md) - Example scenario
- Community analysis - Customer support pain points

## Estimated Time
4-6 hours
```

---

## 🔌 Track 3: Integrations (Day 5-7)

### Issue #7: Implement Base Framework Adapter

**Title:** `feat: Implement base framework adapter interface`

**Labels:** `feature`, `week-1`, `integrations`

**Description:**
```markdown
## Description
Implement abstract base class for framework adapters (LangChain, AutoGen, CrewAI).

## Acceptance Criteria
- [ ] `FrameworkAdapter` ABC in `src/agentgym/integrations/base.py`
- [ ] Abstract methods for conversion, tool extraction, environment creation
- [ ] Type hints and docstrings
- [ ] Documentation of adapter interface

## Technical Details
```python
from abc import ABC, abstractmethod
from typing import Any, List

class FrameworkAdapter(ABC):
    """Base adapter for framework integrations."""

    @abstractmethod
    def wrap_agent(self, trained_model) -> Any:
        """Wrap trained model for framework."""
        pass

    @abstractmethod
    def extract_tools(self, agent) -> List:
        """Extract tools from framework agent."""
        pass

    @abstractmethod
    def create_environment(self, agent):
        """Create training environment from agent."""
        pass
```

## Estimated Time
2-3 hours
```

---

### Issue #8: Implement LangChain Adapter

**Title:** `feat: Implement LangChain adapter for agent conversion`

**Labels:** `feature`, `week-1`, `integrations`

**Description:**
```markdown
## Description
Implement adapter to convert trained models to LangChain agents.

## Acceptance Criteria
- [ ] `LangChainAdapter` in `src/agentgym/integrations/langchain.py`
- [ ] Inherits from `FrameworkAdapter`
- [ ] Converts trained model to LangChain AgentExecutor
- [ ] Tool extraction from LangChain agents
- [ ] Type hints and docstrings
- [ ] Integration test with real LangChain agent

## Technical Details
```python
from langchain.agents import AgentExecutor

class LangChainAdapter(FrameworkAdapter):
    """Adapter for LangChain agents."""

    def wrap_agent(self, trained_model):
        """Convert trained model to LangChain agent."""
        # Create LangChain-compatible agent
        agent = self.create_langchain_agent(trained_model)
        return AgentExecutor(agent=agent, tools=self.tools)

    def extract_tools(self, agent):
        """Extract tools from LangChain agent."""
        return agent.tools

    def create_environment(self, agent):
        """Wrap LangChain agent for RL training."""
        return LangChainEnvironment(
            agent=agent,
            tools=self.extract_tools(agent),
        )
```

## References
- LangChain docs: https://python.langchain.com/docs/modules/agents/
- Community analysis: LangChain pain points

## Estimated Time
4-6 hours
```

---

### Issue #9: Implement Basic CLI

**Title:** `feat: Implement basic CLI (agentgym train)`

**Labels:** `feature`, `week-1`, `integrations`

**Description:**
```markdown
## Description
Implement command-line interface for AgentGym.

## Acceptance Criteria
- [ ] CLI entry point in `src/agentgym/cli/main.py`
- [ ] `agentgym --version` command
- [ ] `agentgym train --scenario X --framework Y` command
- [ ] Beautiful terminal output using Rich
- [ ] Help text and usage examples
- [ ] Integration test showing full CLI usage

## Technical Details
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def train(
    scenario: str = typer.Option(..., help="Scenario name"),
    framework: str = typer.Option("langchain", help="Framework to use"),
    episodes: int = typer.Option(10000, help="Number of episodes"),
):
    """Train an agent using reinforcement learning."""
    console.print(f"[bold]Training {framework} agent...[/bold]")

    # Create trainer
    config = TrainingConfig(
        scenario=scenario,
        framework=framework,
        episodes=episodes
    )
    trainer = Trainer(config)

    # Train
    result = trainer.train()

    # Display results
    console.print(f"[green]✓[/green] Training complete!")
    console.print(f"Tool reliability: {result.metrics.tool_reliability:.1%}")
```

## References
- Typer docs: https://typer.tiangolo.com/
- Rich docs: https://rich.readthedocs.io/

## Estimated Time
3-4 hours
```

---

## 📝 Summary

### Total Issues: 9
- **Core:** 3 issues (Day 1-2)
- **Scenarios:** 3 issues (Day 3-4)
- **Integrations:** 3 issues (Day 5-7)

### Estimated Time: 30-40 hours
- ~5-6 hours/day for 7 days
- Allows for debugging, testing, documentation

### Dependencies
```
Issue #1 (Config)      → Issue #2 (Result)   → Issue #3 (Trainer)
                                                      ↓
Issue #4 (Base Scenario) → Issue #5 (Registry) → Issue #6 (Customer Support)
                                                      ↓
Issue #7 (Base Adapter) → Issue #8 (LangChain) → Issue #9 (CLI)
```

---

## 🚀 How to Create These Issues

### Option A: GitHub Web UI
1. Go to: https://github.com/Robbe1991/agentgym/issues/new
2. Copy-paste each issue description
3. Add labels manually

### Option B: GitHub CLI (Batch)
```bash
# Create all 9 issues at once
# (Run from repo root)
bash scripts/create-week-1-issues.sh
```

### Option C: Manually One-by-One
```bash
gh issue create --title "feat: Implement core configuration" \
  --body "$(cat << 'EOF'
[Copy description from above]
EOF
)" --label "feature,week-1,core"
```

---

## ✅ Ready to Start Development!

Once issues are created:
1. Pick Issue #1
2. Create feature branch
3. Ask Claude to implement (with context from issue + docs)
4. Test, review, commit
5. Create PR, merge
6. Move to next issue

**Week 1 Goal:** All 9 issues closed, basic example working end-to-end! 🎯
