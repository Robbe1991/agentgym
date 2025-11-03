# AgentGym - Project Context for Claude Code

**Last Updated:** 2025-11-03
**Version:** 0.1.0 (Pre-launch)
**Status:** Week 1 OSS Development

---

## Quick Overview

**What:** AgentGym is a platform for training AI agents using reinforcement learning
**Tagline:** "The Vercel for Agent Training - Powered by Agent Lightning"
**Goal:** 95% tool reliability, 98% time savings, 30-50% cost reduction

**Target Users:** Developers using LangChain, AutoGen, or CrewAI who want to train their agents

---

## Core Architecture

### Foundation
- **RL Engine:** Agent Lightning (Microsoft Research, MIT License)
- **NOT AgentFlow:** We train EXISTING agents, AgentFlow builds NEW agents
- **Positioning:** Platform over Library (like Vercel over Next.js)

### Key Technical Decisions (from AgentFlow Research)
1. ✅ **On-policy RL** (NOT offline SFT) - AgentFlow showed offline SFT = -19% performance
2. ✅ **Trajectory-level reward broadcasting** - Solves credit assignment
3. ✅ **Modular training** - Only train tool selection, not everything

### Stack
```
Layer 1: Agent Lightning (RL algorithms)
Layer 2: AgentGym Core (scenarios, integrations, BYOG)
Layer 3: AgentGym Cloud (managed, later)
```

---

## Project Structure

```
src/agentgym/
├── core/           # Trainer, Config, Result - wraps Agent Lightning
├── scenarios/      # Pre-built scenarios (customer_support, etc.)
├── integrations/   # LangChain, AutoGen, CrewAI adapters
├── cli/            # Command-line interface
├── ui/             # Terminal dashboard
└── utils/          # GPU orchestration, etc.

docs/
├── strategy/       # Business strategy, roadmap
├── architecture/   # TECHNICAL_APPROACH.md, SYSTEM_DESIGN.md
├── development/    # SETUP.md, WORKFLOW.md, AI_ASSISTANT_INSTRUCTIONS.md
├── research/       # Community analysis (LangChain, AutoGen, CrewAI)
└── validation/     # Interview guides

tests/              # Pytest tests (80% coverage target)
examples/           # Example scripts
```

---

## Core Concepts

### 1. Scenario
Pre-built training environment for specific agent tasks.

```python
class Scenario(ABC):
    def create_environment(self) -> Environment:
        """Define state/action spaces"""

    def broadcast_rewards(self, trajectory) -> List[float]:
        """Trajectory-level reward (AgentFlow insight)"""

    def define_trainable_components(self):
        """Which components to train vs freeze"""
        return {
            "tool_selection": True,      # Train
            "parameter_selection": True,  # Train
            "tool_execution": False,      # Freeze
            "output_generation": False    # Freeze
        }
```

### 2. Trainer
High-level wrapper around Agent Lightning.

```python
class Trainer:
    def train(self):
        """On-policy RL (live tool interaction)"""
        for episode in range(self.episodes):
            trajectory = self.collect_trajectory_online()  # Live
            rewards = self.scenario.broadcast_rewards(trajectory)
            self.update_policy(trajectory, rewards)
```

### 3. Framework Adapters
Convert trained agents to LangChain/AutoGen/CrewAI.

```python
trained = TrainedAgent.load("customer_support_v1.2")
langchain_agent = trained.to_langchain()
autogen_agent = trained.to_autogen()
crewai_agent = trained.to_crewai()
```

---

## Current Phase: Week 1 Development

### Goals
- Core Trainer working (basic example runs)
- 1 Scenario implemented (customer_support)
- 1 Framework integration (LangChain)
- On-policy training loop
- Trajectory-level rewards

### NOT Building Yet
- ❌ Cloud platform (Month 5-6)
- ❌ Advanced UI (Month 3-4)
- ❌ Marketplace (Year 2)
- ❌ Multiple scenarios (Week 2-3)

---

## Key Constraints

### Technical
- Python 3.11+ required
- Agent Lightning as dependency (check if actually available on PyPI!)
- GPU optional (local, RunPod, Lambda)

### Scope
- Framework-agnostic (LangChain + AutoGen + CrewAI)
- Tool reliability = core metric (95% target)
- BYOG approach (no managed GPU in OSS)

### Timeline
- Week 1: Core implementation
- Month 2: OSS launch
- Month 6: Cloud launch
- Month 12: $50K MRR target

---

## Common Patterns

### Code Style
- Type hints everywhere
- Google-style docstrings
- Black formatting (88 char)
- Ruff linting
- Mypy type checking

### Testing
- Pytest for all tests
- 80% coverage minimum
- TDD approach preferred
- Mark slow tests: `@pytest.mark.slow`

### Commits
```
feat: Add customer support scenario
fix: Resolve GPU memory leak (#123)
docs: Update setup guide
refactor: Extract GPU orchestration
test: Add integration tests for LangChain
```

---

## Important Files to Read

**Before coding:**
1. [docs/architecture/TECHNICAL_APPROACH.md](../docs/architecture/TECHNICAL_APPROACH.md) - How we use Agent Lightning
2. [docs/architecture/SYSTEM_DESIGN.md](../docs/architecture/SYSTEM_DESIGN.md) - System architecture
3. [docs/development/AI_ASSISTANT_INSTRUCTIONS.md](../docs/development/AI_ASSISTANT_INSTRUCTIONS.md) - Detailed coding guidelines

**For strategic context:**
1. [docs/strategy/EXECUTIVE-SUMMARY.md](../docs/strategy/EXECUTIVE-SUMMARY.md)
2. [docs/strategy/OPTION-D-ACTION-PLAN.md](../docs/strategy/OPTION-D-ACTION-PLAN.md)

**For development:**
1. [CONTRIBUTING.md](../CONTRIBUTING.md)
2. [docs/development/SETUP.md](../docs/development/SETUP.md)
3. [docs/development/WORKFLOW.md](../docs/development/WORKFLOW.md)

---

## What to Build First (Week 1 Priority Order)

### Day 1-2: Core Foundation
1. `src/agentgym/core/config.py` - Training configuration (Pydantic model)
2. `src/agentgym/core/result.py` - Training results dataclass
3. `src/agentgym/core/trainer.py` - Trainer class (with on-policy RL)

### Day 3-4: Scenarios
1. `src/agentgym/scenarios/base.py` - Base Scenario class
2. `src/agentgym/scenarios/registry.py` - Scenario registry
3. `src/agentgym/scenarios/customer_support.py` - First scenario

### Day 5-7: Integration
1. `src/agentgym/integrations/base.py` - Base adapter
2. `src/agentgym/integrations/langchain.py` - LangChain adapter
3. `src/agentgym/cli/main.py` - Basic CLI

---

## Anti-Patterns to Avoid

❌ **DON'T:**
- Build offline SFT (AgentFlow showed this fails)
- Train everything (only train tool selection)
- Hardcode values (use config)
- Skip tests
- Build Cloud features in OSS tier
- Copy AgentFlow's 4-module architecture

✅ **DO:**
- On-policy RL (live tool interaction)
- Trajectory-level reward broadcasting
- Modular training (tool selection only)
- Type hints and docstrings
- Test-driven development
- Simple, clear code

---

## Key Metrics to Track

### Technical
- Training speed (target: <30min for 10K episodes on RTX 4090)
- Tool reliability (target: 95%)
- Setup time (target: <5min from install to first training)

### Quality
- Test coverage (target: 80%)
- Type coverage (target: 100% in core/)
- Documentation coverage (all public APIs)

### Business (later)
- GitHub stars (target: 1K by Month 3)
- PyPI downloads (target: 10K/month by Month 6)
- Active users (target: 500-1K by Month 3)

---

## When Stuck

1. **Architecture questions?** → Read [TECHNICAL_APPROACH.md](../docs/architecture/TECHNICAL_APPROACH.md)
2. **Implementation patterns?** → Read [AI_ASSISTANT_INSTRUCTIONS.md](../docs/development/AI_ASSISTANT_INSTRUCTIONS.md)
3. **Workflow questions?** → Read [WORKFLOW.md](../docs/development/WORKFLOW.md)
4. **Strategic questions?** → Read [EXECUTIVE-SUMMARY.md](../docs/strategy/EXECUTIVE-SUMMARY.md)

---

## Current Blockers / Open Questions

### Technical
- [ ] Is Agent Lightning actually on PyPI? (need to verify)
- [ ] What's the exact Agent Lightning API? (need docs)
- [ ] How to integrate with LangChain agents? (research needed)

### Strategic
- [ ] Domain registration (agentgym.de)
- [ ] When to announce OSS? (Month 2)
- [ ] First beta testers from LangChain community?

---

## Remember

**Core Value Prop:** 95% tool reliability with RL training
**Target User:** Developers with existing LangChain/AutoGen/CrewAI agents
**Differentiation:** We train EXISTING agents (not build new ones like AgentFlow)
**Foundation:** Agent Lightning + AgentFlow insights

**This Week:** Get basic example working end-to-end
**Next Month:** OSS launch
**This Year:** $50K MRR

---

**Last Updated:** 2025-11-03
**Ready for:** Week 1 Development
**Status:** All docs complete, structure ready, repo live
