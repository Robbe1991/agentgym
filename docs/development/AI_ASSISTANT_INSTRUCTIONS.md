# AI Assistant Instructions for AgentGym Development

This document provides instructions for AI assistants (like Claude, GitHub Copilot, etc.) working on the AgentGym project.

---

## Project Overview

**AgentGym** is an open-core platform for training AI agents using reinforcement learning, positioned as "The Vercel for Agent Training - Powered by Agent Lightning."

**Core Value Propositions:**
- 95% tool reliability (vs 60-70% untrained)
- 98% time savings (4 hours → 3 minutes validated)
- 30-50% cost reduction through RL training
- One-click deployment to production

**Technical Foundation:**
- Built on top of **Agent Lightning** (Microsoft Research, MIT license)
- Framework-agnostic: LangChain, AutoGen, CrewAI support
- Open Core model: OSS CLI + Paid Cloud

---

## Strategic Context

### Why This Matters

Based on 200K+ tokens of community analysis across LangChain, AutoGen, and CrewAI:

**Universal Pain Points:**
1. **Tool Reliability:** "Tools work 60-70% of the time" - massive problem
2. **No Systematic Improvement:** Manual prompt engineering doesn't scale
3. **Production Readiness:** Hard to deploy agents reliably
4. **Cost:** LLM API costs add up quickly

**AgentGym Solution:**
- RL training improves tool reliability to 95%
- Systematic, automated improvement
- One-click deployment
- Cost optimization through better tool selection

### Competitive Positioning

**Agent Lightning vs AgentGym:**
- **Agent Lightning** = Low-level RL library (like TensorFlow)
- **AgentGym** = High-level platform (like Weights & Biases)
- We use Agent Lightning as our engine, not competition

**Analogies:**
- Agent Lightning : AgentGym :: Docker : Heroku
- Agent Lightning : AgentGym :: TensorFlow : Weights & Biases

**Our Moat (Open Core):**
- OSS builds credibility + community
- Cloud captures 5-10% who want convenience
- Fork risk <1% (see OPEN-CORE-COMPETITIVE-MOAT.md)
- Network effects, managed complexity, brand trust

---

## Project Structure

```
AgentGym/
├── src/agentgym/              # Source code
│   ├── core/                  # Core training logic
│   ├── scenarios/             # Pre-built scenarios
│   ├── integrations/          # LangChain, AutoGen, CrewAI adapters
│   ├── cli/                   # Command-line interface
│   ├── ui/                    # Terminal dashboard
│   └── utils/                 # GPU orchestration, etc.
├── tests/                     # Test suite
├── docs/                      # Documentation
│   ├── strategy/              # Strategic documents
│   ├── architecture/          # Technical design
│   ├── development/           # Dev guides (this file)
│   ├── research/              # Community analysis
│   └── validation/            # Interview guides, templates
├── examples/                  # Example code
├── .github/workflows/         # CI/CD
├── pyproject.toml             # Project config
└── README.md                  # Entry point
```

---

## Core Concepts

### 1. Scenarios

Pre-built training scenarios for common agent tasks:

```python
class CustomerSupportScenario(Scenario):
    """Train agents for customer support with 95% tool reliability"""

    def create_environment(self) -> Environment:
        """Define state/action spaces"""

    def calculate_reward(self, state, action, next_state) -> float:
        """Reward function emphasizing tool reliability"""

    def success_criteria(self) -> Dict[str, float]:
        """Target metrics: tool_reliability=0.95, cost_reduction=0.30"""
```

**Why Scenarios Matter:**
- Users don't want to write reward functions
- Pre-tuned hyperparameters save time
- Validated success criteria build trust

### 2. Framework Integrations

Adapters to work with existing agent frameworks:

```python
# LangChain
trained = TrainedAgent.load("customer_support_v1.2")
agent = trained.to_langchain()  # Convert to LangChain AgentExecutor

# AutoGen
agent = trained.to_autogen()  # Convert to AutoGen AssistantAgent

# CrewAI
agent = trained.to_crewai()  # Convert to CrewAI Agent
```

**Why Framework-Agnostic:**
- LangChain community: 100K-500K developers
- AutoGen community: 30K-150K developers
- CrewAI community: 20K-100K developers
- Total TAM: 150K-800K developers (vs 100K-500K LangChain-only)

### 3. BYOG (Bring Your Own GPU)

Users can train on:
- **Local GPU:** Auto-detected via Docker
- **RunPod:** $0.34/hr for RTX 4090 (cheapest)
- **Lambda Labs:** Fast provisioning
- **AgentGym Cloud:** Fully managed (paid tier)

**Why BYOG:**
- OSS tier has minimal infrastructure costs
- Users control their compute spending
- No vendor lock-in

### 4. Tool Reliability

**Core Metric:** Percentage of tool calls that succeed

```python
# Before training: 60-70% success rate
agent.run("Book a flight to NYC")
# → Often fails: wrong parameters, wrong tool, hallucinated tools

# After training: 95% success rate
trained_agent.run("Book a flight to NYC")
# → Reliable: correct tool, correct parameters
```

**Why This Metric:**
- Most impactful for production
- Easy to measure
- Validated across all 3 frameworks

---

## Development Guidelines

### When Writing Code

#### 1. Type Hints Always

```python
# ✅ Good
def train(
    scenario: str,
    framework: str = "langchain",
    episodes: int = 10000
) -> TrainingResult:
    pass

# ❌ Bad
def train(scenario, framework="langchain", episodes=10000):
    pass
```

#### 2. Docstrings (Google Style)

```python
def train(self, scenario: str) -> TrainingResult:
    """Train an agent using reinforcement learning.

    Args:
        scenario: Name of pre-built scenario (e.g., "customer_support")

    Returns:
        TrainingResult with metrics and trained model

    Raises:
        ScenarioNotFoundError: If scenario doesn't exist

    Example:
        >>> trainer = Trainer(config)
        >>> result = trainer.train("customer_support")
        >>> print(f"Tool reliability: {result.metrics.tool_reliability:.1%}")
        Tool reliability: 94.2%
    """
    pass
```

#### 3. Tests for Everything

```python
# tests/test_scenarios.py

def test_customer_support_scenario():
    """Test customer support scenario creation"""
    scenario = CustomerSupportScenario()

    # Test environment creation
    env = scenario.create_environment()
    assert env is not None
    assert env.state_space is not None

    # Test reward function
    reward = scenario.calculate_reward(state, action, next_state)
    assert -30 <= reward <= 20  # Valid range

    # Test success criteria
    criteria = scenario.success_criteria()
    assert criteria["tool_reliability"] == 0.95
```

#### 4. Beautiful CLI (Rich)

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Use rich for beautiful output
table = Table(title="Training Metrics")
table.add_column("Metric", style="cyan")
table.add_column("Value", style="green")
table.add_row("Tool Reliability", "94.2%")
console.print(table)
```

### When Reviewing Code

**Check:**
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Tests included (and passing)
- [ ] Follows project structure
- [ ] No hardcoded values
- [ ] Error handling present
- [ ] Performance considered

### When Writing Documentation

**Audience:**
- **Developers** using AgentGym (primary)
- **Contributors** to AgentGym
- **Researchers** interested in RL for agents

**Tone:**
- Clear and concise
- Avoid jargon (or explain it)
- Use examples liberally
- Assume basic ML knowledge, not RL expertise

**Structure:**
- Start with "Why" (motivation)
- Then "What" (concept)
- Then "How" (implementation)
- End with examples

---

## Common Tasks

### Adding a New Scenario

1. **Create scenario class:**
   ```python
   # src/agentgym/scenarios/my_scenario.py

   from agentgym.core import Scenario

   class MyScenario(Scenario):
       name = "my_scenario"
       description = "Description of what this scenario does"
       difficulty = "intermediate"
       estimated_time = "45 minutes"

       def create_environment(self):
           """Define state/action spaces"""
           pass

       def calculate_reward(self, state, action, next_state):
           """Define reward function"""
           pass

       def success_criteria(self):
           """Define target metrics"""
           return {
               "tool_reliability": 0.95,
               "cost_reduction": 0.30,
           }
   ```

2. **Register in registry:**
   ```python
   # src/agentgym/scenarios/registry.py

   BUILT_IN = {
       # ... existing scenarios
       "my_scenario": MyScenario,
   }
   ```

3. **Add tests:**
   ```python
   # tests/test_scenarios.py

   def test_my_scenario():
       scenario = MyScenario()
       # ... test all methods
   ```

4. **Add documentation:**
   ```markdown
   # docs/scenarios/my_scenario.md

   ## My Scenario

   Description, use cases, examples...
   ```

5. **Add example:**
   ```python
   # examples/my_scenario_example.py

   from agentgym import Trainer

   trainer = Trainer()
   result = trainer.train("my_scenario")
   ```

### Adding a Framework Integration

1. **Create adapter:**
   ```python
   # src/agentgym/integrations/my_framework.py

   from agentgym.integrations.base import FrameworkAdapter

   class MyFrameworkAdapter(FrameworkAdapter):
       def wrap_agent(self, trained_model):
           """Convert trained model to framework agent"""
           pass

       def extract_tools(self, agent):
           """Extract tools from framework agent"""
           pass

       def create_environment(self, agent):
           """Create training environment"""
           pass
   ```

2. **Register adapter:**
   ```python
   # src/agentgym/integrations/__init__.py

   ADAPTERS = {
       "langchain": LangChainAdapter,
       "autogen": AutoGenAdapter,
       "crewai": CrewAIAdapter,
       "my_framework": MyFrameworkAdapter,  # Add this
   }
   ```

3. **Add integration tests:**
   ```python
   # tests/integrations/test_my_framework.py

   @pytest.mark.integration
   def test_my_framework_adapter():
       # Test adapter functionality
       pass
   ```

### Fixing a Bug

1. **Understand the issue:**
   - Read bug report thoroughly
   - Reproduce locally
   - Identify root cause

2. **Write failing test:**
   ```python
   def test_bug_123_gpu_memory_leak():
       """Regression test for issue #123"""
       # This should fail before fix
       trainer = Trainer()
       initial_memory = get_gpu_memory()

       trainer.train("customer_support", episodes=100)

       final_memory = get_gpu_memory()
       assert final_memory == initial_memory  # Should not leak
   ```

3. **Fix the bug:**
   - Make minimal change
   - Ensure test passes
   - Check no regressions

4. **Update documentation if needed:**
   - Update API docs if behavior changed
   - Add note to CHANGELOG.md

---

## Key Files to Know

### Strategic Documents

**docs/strategy/EXECUTIVE-SUMMARY.md**
- High-level strategy overview
- Read this first to understand "why"

**docs/strategy/OPTION-D-ACTION-PLAN.md**
- Detailed 12-month execution plan
- Week-by-week breakdown

**docs/strategy/CROSS-FRAMEWORK-STRATEGIC-SUMMARY.md**
- Community analysis summary
- Pain points and opportunities

**docs/strategy/OPEN-CORE-COMPETITIVE-MOAT.md**
- Why open core works
- Fork risk analysis (<1%)

### Architecture Documents

**docs/architecture/TECHNICAL_APPROACH.md**
- How we use Agent Lightning
- Library vs Platform positioning
- What we build on top

**docs/architecture/SYSTEM_DESIGN.md**
- Component architecture
- Data flow
- Technology stack
- OSS vs Cloud architecture

### Development Guides

**CONTRIBUTING.md**
- How to contribute
- Code standards
- PR process

**docs/development/SETUP.md**
- Development environment setup
- GPU configuration
- IDE setup

**docs/development/WORKFLOW.md**
- Git workflow
- Branch strategy
- Release process

**docs/development/AI_ASSISTANT_INSTRUCTIONS.md** (this file)
- Context for AI assistants
- Development patterns
- Common tasks

---

## Coding Patterns

### Error Handling

```python
# Use custom exceptions
class ScenarioNotFoundError(Exception):
    """Raised when scenario doesn't exist"""
    pass

# Provide helpful error messages
def load_scenario(name: str) -> Scenario:
    if name not in BUILT_IN_SCENARIOS:
        available = ", ".join(BUILT_IN_SCENARIOS.keys())
        raise ScenarioNotFoundError(
            f"Scenario '{name}' not found. "
            f"Available scenarios: {available}"
        )
    return BUILT_IN_SCENARIOS[name]()
```

### Configuration

```python
# Use Pydantic for config validation
from pydantic import BaseModel, Field

class TrainingConfig(BaseModel):
    """Training configuration"""

    scenario: str = Field(..., description="Scenario name")
    framework: str = Field("langchain", description="Framework to use")
    episodes: int = Field(10000, gt=0, description="Number of episodes")
    gpu_provider: str = Field("auto", description="GPU provider")

    class Config:
        # Allow extra fields for extensibility
        extra = "allow"
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def train(self):
    logger.info("Starting training", extra={
        "scenario": self.config.scenario,
        "episodes": self.config.episodes
    })

    try:
        result = self._train_internal()
        logger.info("Training completed", extra={
            "tool_reliability": result.metrics.tool_reliability
        })
        return result
    except Exception as e:
        logger.error("Training failed", exc_info=True)
        raise
```

### Progress Display

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def train_with_progress(self):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Training agent...", total=self.episodes)

        for episode in range(self.episodes):
            # Train episode
            progress.update(task, advance=1)
```

---

## Testing Philosophy

### Test Pyramid

```
       /\
      /  \     E2E Tests (few)
     /____\    - Full training runs
    /      \   - CLI integration
   /________\
  /          \ Integration Tests (some)
 /____________\ - Framework adapters
/              \ - GPU providers
/________________\
                  Unit Tests (many)
                  - Scenarios
                  - Utilities
                  - Core logic
```

### What to Test

**Always:**
- Public APIs
- Edge cases
- Error conditions
- State changes

**Sometimes:**
- Private methods (if complex logic)
- Integration points

**Never:**
- External libraries (they have their own tests)
- Trivial getters/setters

### Test Naming

```python
# Pattern: test_<what>_<condition>_<expected>

def test_train_with_invalid_scenario_raises_error():
    """Training with invalid scenario raises ScenarioNotFoundError"""
    pass

def test_customer_support_scenario_achieves_95_reliability():
    """Customer support scenario achieves 95% tool reliability"""
    pass

def test_gpu_orchestrator_with_no_gpu_suggests_providers():
    """GPU orchestrator without GPU suggests RunPod/Lambda"""
    pass
```

---

## Performance Considerations

### Training Speed

**Optimize:**
- Use GPU when available
- Batch operations
- Parallelize independent tasks
- Cache expensive operations

**Monitor:**
- Training time per episode
- GPU utilization
- Memory usage
- Cost per training run

### API Response Time

**Targets:**
- CLI commands: < 100ms startup
- Training status: < 50ms
- Deployment: < 500ms
- Cloud API: < 200ms (p95)

### Resource Usage

**OSS Tier:**
- Minimal cloud resources (BYOG)
- Local SQLite (no managed DB)
- Stateless where possible

**Cloud Tier:**
- Auto-scaling based on load
- Spot instances for cost savings
- Connection pooling
- Caching aggressively

---

## Documentation Standards

### API Documentation

Use docstrings that generate good docs:

```python
def train(
    scenario: str,
    framework: str = "langchain",
    *,
    episodes: int = 10000,
    gpu: str = "auto"
) -> TrainingResult:
    """Train an agent using reinforcement learning.

    This function orchestrates the entire training process including
    GPU provisioning, environment setup, and model training.

    Args:
        scenario: Name of the pre-built scenario. Use `agentgym scenarios list`
            to see available scenarios.
        framework: Agent framework to use. One of:
            - "langchain": LangChain agents
            - "autogen": AutoGen/Microsoft Agent Framework
            - "crewai": CrewAI agents
        episodes: Number of training episodes. More episodes = better performance
            but longer training time. Default 10,000 is sufficient for most use cases.
        gpu: GPU provider. One of:
            - "auto": Auto-detect (local GPU → RunPod → Lambda)
            - "local": Use local GPU
            - "runpod": Use RunPod (cheapest, $0.34/hr)
            - "lambda": Use Lambda Labs (fast setup)
            - "cloud": Use AgentGym Cloud (requires Pro plan)

    Returns:
        TrainingResult containing:
            - trained_model: Trained RL model ready for deployment
            - metrics: Performance metrics (tool reliability, cost, speed)
            - artifacts: Deployment artifacts for your framework

    Raises:
        ScenarioNotFoundError: Scenario name not recognized
        GPUNotAvailableError: No GPU could be provisioned
        TrainingFailedError: Training failed after retries

    Example:
        Basic training:

        >>> from agentgym import Trainer
        >>> trainer = Trainer()
        >>> result = trainer.train("customer_support")
        Training: 100%|██████████| 10000/10000 [23:45<00:00]
        >>> print(f"Tool reliability: {result.metrics.tool_reliability:.1%}")
        Tool reliability: 94.7%

        With custom config:

        >>> result = trainer.train(
        ...     scenario="customer_support",
        ...     framework="autogen",
        ...     episodes=5000,
        ...     gpu="runpod"
        ... )

        Deploy to LangChain:

        >>> agent = result.to_langchain()
        >>> agent.run("Help customer with refund request")

    Note:
        Training time varies based on:
        - Scenario complexity (simple: 15min, complex: 60min)
        - Number of episodes (5K: 15min, 10K: 30min, 20K: 60min)
        - GPU type (RTX 4090: 30min, T4: 60min, CPU: 8hr)

        Estimated cost (BYOG):
        - RTX 4090 on RunPod: ~$0.17 (30min @ $0.34/hr)
        - A100 on Lambda: ~$0.65 (30min @ $1.29/hr)

    See Also:
        - Trainer.deploy(): Deploy trained agent
        - Trainer.evaluate(): Evaluate agent performance
        - Scenario.success_criteria(): Get target metrics
    """
    pass
```

### README Files

Each major directory should have a README:

```markdown
# Scenarios

This directory contains pre-built training scenarios for common agent tasks.

## Available Scenarios

- **customer_support**: Train agents for customer support (95% tool reliability)
- **code_review**: Train agents for code review tasks
- **qa_testing**: Train agents for QA and testing

## Creating a New Scenario

See [CREATING_SCENARIOS.md](CREATING_SCENARIOS.md) for a detailed guide.

Quick example:

```python
from agentgym.core import Scenario

class MyScenario(Scenario):
    # ... implement methods
```

## Testing Scenarios

All scenarios must have tests in `tests/test_scenarios.py`.
```

---

## Priorities

When helping with development, prioritize in this order:

1. **Correctness:** Code must work
2. **Tests:** Code must be tested
3. **Documentation:** Code must be documented
4. **Performance:** Code should be fast (but not at expense of above)
5. **Beauty:** Code should be clean (but not at expense of above)

---

## Questions to Ask

When working on a task, consider:

**Functionality:**
- Does this solve the user's problem?
- What edge cases exist?
- How will this fail? How do we handle that?

**Design:**
- Is this the simplest solution?
- Does this fit with existing patterns?
- Will this be easy to extend later?

**Testing:**
- What tests do we need?
- Can this be tested in isolation?
- Do we need integration tests?

**Documentation:**
- Will users understand this?
- What examples would help?
- What could go wrong? (document it)

**Performance:**
- Will this scale?
- What are the bottlenecks?
- Can we optimize later (don't premature optimize)?

---

## Getting Context

When starting a new task:

1. **Read related docs:**
   - Architecture docs for design
   - Strategy docs for "why"
   - API docs for usage

2. **Look at existing code:**
   - Find similar features
   - Follow existing patterns
   - Don't reinvent the wheel

3. **Check tests:**
   - Understand expected behavior
   - See edge cases
   - Follow testing patterns

4. **Ask questions:**
   - GitHub Discussions
   - Code comments
   - PR descriptions

---

## Anti-Patterns to Avoid

**Don't:**
- ❌ Hardcode values (use config)
- ❌ Ignore errors (handle gracefully)
- ❌ Skip tests ("I'll add them later")
- ❌ Write cryptic code (clarity > cleverness)
- ❌ Copy-paste without understanding
- ❌ Optimize prematurely
- ❌ Break existing tests
- ❌ Commit without running tests

**Do:**
- ✅ Use type hints
- ✅ Write docstrings
- ✅ Add tests first (TDD)
- ✅ Keep functions small
- ✅ Use meaningful names
- ✅ Handle errors explicitly
- ✅ Run tests before committing
- ✅ Follow existing patterns

---

## Success Metrics

When evaluating if a contribution is good:

**Code Quality:**
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Tests pass (and new tests added)
- [ ] Follows project conventions
- [ ] No linter errors

**User Experience:**
- [ ] Clear error messages
- [ ] Beautiful terminal output
- [ ] Fast response time
- [ ] Good documentation

**Maintainability:**
- [ ] Easy to understand
- [ ] Easy to extend
- [ ] Well-tested
- [ ] Well-documented

---

## Final Notes

**Remember:**
- **Users first:** Always consider developer experience
- **Quality over speed:** Better to do it right than fast
- **Community matters:** Be kind, be helpful, be inclusive
- **Have fun:** Building AgentGym should be enjoyable!

**When in doubt:**
- Check existing code for patterns
- Read the docs
- Ask questions
- Start simple, iterate

---

**Happy coding!** 🚀

This project aims to make agent training accessible to everyone. Every line of code you write helps developers build better AI agents.
