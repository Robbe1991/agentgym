# Technical Approach: AgentGym Platform over Agent Lightning

**Last Updated:** 2025-11-03
**Status:** Active Strategy
**Owner:** AgentGym Core Team

---

## Executive Summary

AgentGym is a **platform** built on top of **Agent Lightning** (Microsoft Research's RL training library). This document explains our technical positioning, architecture decisions, and differentiation strategy.

**TL;DR:**
- **Agent Lightning** = Low-level RL training library (like TensorFlow for agents)
- **AgentGym** = High-level platform with DX, scenarios, deployment (like Weights & Biases for agents)
- **Relationship:** We use Agent Lightning as our engine, focus on developer experience and production features

---

## 1. What is Agent Lightning?

### Overview
- **Source:** Microsoft Research (MIT License)
- **Purpose:** Low-level reinforcement learning library for training AI agents
- **Target Users:** ML researchers, RL experts who want fine-grained control
- **Complexity:** High - requires deep RL knowledge

### Agent Lightning Capabilities
```python
# Agent Lightning - Low-level RL training
from agent_lightning import RLTrainer, Environment

# Requires manual setup
env = Environment(custom_reward_function)
trainer = RLTrainer(
    learning_rate=0.001,
    discount_factor=0.99,
    # ... dozens of hyperparameters
)
trainer.train(episodes=10000)
```

### What Agent Lightning Does Well
✅ Efficient RL algorithms (PPO, DQN, A3C)
✅ GPU acceleration
✅ Distributed training support
✅ Flexible reward engineering
✅ Research-grade quality

### What Agent Lightning Doesn't Provide
❌ Pre-built scenarios (customer support, QA, etc.)
❌ Framework integrations (LangChain, AutoGen, CrewAI)
❌ Developer-friendly CLI
❌ Observability/monitoring
❌ One-click deployment
❌ Managed GPU orchestration
❌ Team collaboration features
❌ Production SLA guarantees

---

## 2. AgentGym Platform Architecture

### Positioning: Library vs. Platform

| Aspect | Agent Lightning (Library) | AgentGym (Platform) |
|--------|--------------------------|---------------------|
| **Abstraction** | Low-level RL primitives | High-level scenarios |
| **Target User** | RL researchers | App developers |
| **Setup Time** | Days-weeks (manual) | Minutes (CLI) |
| **Expertise Required** | Deep RL knowledge | Basic agent knowledge |
| **Use Case** | Custom RL research | Production agent training |
| **Deployment** | Manual | One-click |
| **GPU Management** | Bring your own | BYOG + Managed options |
| **Pricing** | Free (OSS) | Freemium (OSS + Cloud) |

**Analogy:**
- **Agent Lightning** = TensorFlow (library for building models)
- **AgentGym** = Weights & Biases (platform for training/deployment)

OR

- **Agent Lightning** = Docker Engine (container runtime)
- **AgentGym** = Heroku (platform for deploying containers)

---

## 3. Technical Stack

### Layer 1: Foundation (Agent Lightning)
```
┌─────────────────────────────────────────┐
│   Agent Lightning (MIT License)         │
│   - RL algorithms (PPO, DQN, A3C)       │
│   - GPU acceleration                    │
│   - Distributed training                │
└─────────────────────────────────────────┘
```

### Layer 2: AgentGym Core (OSS)
```
┌─────────────────────────────────────────┐
│   AgentGym Core Library                 │
│   - High-level trainer wrapper          │
│   - Pre-built scenarios library         │
│   - Framework adapters                  │
│   - Tool reliability metrics (95%)      │
│   - Terminal UI/dashboard               │
│   - BYOG orchestration                  │
└─────────────────────────────────────────┘
```

### Layer 3: AgentGym Cloud (Paid)
```
┌─────────────────────────────────────────┐
│   AgentGym Cloud Platform               │
│   - Managed GPU orchestration           │
│   - One-click deployment                │
│   - Team collaboration                  │
│   - Advanced observability              │
│   - SLA guarantees (99.9%)              │
│   - Enterprise SSO/RBAC                 │
└─────────────────────────────────────────┘
```

---

## 4. How We Use Agent Lightning

### 4.1 Core Training Engine

```python
# AgentGym wraps Agent Lightning for simplicity
from agentgym import Trainer

# High-level API - hides complexity
trainer = Trainer(
    scenario="customer_support",  # Pre-built scenario
    framework="langchain",         # Auto-detected integration
    gpu="auto"                     # BYOG auto-provisioning
)

# One line to train
results = trainer.train()
# Internally uses Agent Lightning's RL algorithms
```

**Under the hood:**
```python
# agentgym/core/trainer.py (simplified)
import agent_lightning as al

class Trainer:
    def __init__(self, scenario, framework, gpu):
        # Load pre-built scenario
        self.env = ScenarioRegistry.load(scenario)

        # Initialize Agent Lightning with optimized defaults
        self.rl_trainer = al.RLTrainer(
            learning_rate=0.0003,  # Optimized for agent tasks
            discount_factor=0.95,
            # ... pre-tuned hyperparameters
        )

        # Set up framework integration
        self.adapter = FrameworkAdapter.create(framework)

    def train(self):
        # Use Agent Lightning for actual training
        return self.rl_trainer.train(
            environment=self.env,
            episodes=self.config.episodes
        )
```

### 4.2 What We Build on Top

#### A. Pre-built Scenario Library
```python
# agentgym/scenarios/
├── customer_support.py      # Customer service agents
├── code_review.py           # Code review agents
├── data_analysis.py         # Data analysis agents
├── qa_testing.py            # QA testing agents
└── email_automation.py      # Email agents

# Each scenario includes:
# - Environment definition
# - Reward function
# - Success metrics (tool reliability, speed, cost)
# - Training configurations
```

**Example Scenario:**
```python
# agentgym/scenarios/customer_support.py
from agentgym.core import Scenario
from agent_lightning import Environment

class CustomerSupportScenario(Scenario):
    """
    Trains agents to handle customer support with:
    - 95% tool reliability
    - 30-50% cost reduction
    - 98% time savings
    """

    def create_environment(self):
        return Environment(
            state_space=self.define_states(),
            action_space=self.define_actions(),
            reward_function=self.calculate_reward
        )

    def calculate_reward(self, state, action, next_state):
        """
        Reward based on:
        - Tool success rate (high weight)
        - Response time (medium weight)
        - Cost efficiency (medium weight)
        - Customer satisfaction (high weight)
        """
        reward = 0

        # Tool reliability: +10 for success, -20 for failure
        if action.tool_success:
            reward += 10
        else:
            reward -= 20

        # Cost efficiency: +5 for saving tokens
        if action.tokens_used < baseline:
            reward += 5

        # Speed: +3 for fast response
        if action.response_time < 2.0:
            reward += 3

        return reward
```

#### B. Framework Integrations
```python
# agentgym/integrations/

# LangChain adapter
from langchain.agents import AgentExecutor
from agentgym import TrainedAgent

trained = TrainedAgent.load("customer_support_v1.2")
agent = trained.to_langchain()  # Convert to LangChain agent
executor = AgentExecutor(agent=agent)

# AutoGen adapter
from autogen import AssistantAgent
agent = trained.to_autogen()

# CrewAI adapter
from crewai import Agent
agent = trained.to_crewai()
```

#### C. Developer Experience (CLI)
```bash
# Beautiful CLI with rich terminal UI
$ agentgym train \
    --scenario customer_support \
    --framework langchain \
    --gpu runpod \
    --watch

┌─────────────────────────────────────────────────┐
│  AgentGym Training Dashboard                    │
├─────────────────────────────────────────────────┤
│  Scenario: Customer Support                     │
│  Framework: LangChain                           │
│  GPU: RunPod RTX 4090 ($0.34/hr)                │
│                                                  │
│  Episode: 2,847 / 10,000                        │
│  Progress: ████████████░░░░░░░░░ 28%           │
│                                                  │
│  Metrics:                                       │
│    Tool Reliability:  92.3% ↑ (target: 95%)    │
│    Avg Response Time: 1.8s ↓                    │
│    Cost Efficiency:   -38% tokens ↓             │
│                                                  │
│  Estimated completion: 23 minutes               │
└─────────────────────────────────────────────────┘
```

#### D. BYOG (Bring Your Own GPU) Orchestration
```python
# agentgym/utils/gpu_providers.py

class GPUOrchestrator:
    """
    Automatically provisions GPUs from:
    - RunPod (cheapest, $0.34/hr RTX 4090)
    - Lambda Labs (fast setup)
    - Local GPU (docker auto-detect)
    """

    def auto_select(self, budget, speed_priority):
        if budget == "minimal":
            return RunPodProvider()
        elif speed_priority == "high":
            return LambdaLabsProvider()
        else:
            return self.detect_local_gpu()
```

#### E. Observability & Metrics
```python
# agentgym/observability/

# Track metrics Agent Lightning doesn't provide
class TrainingMetrics:
    - Tool success rate (our core metric)
    - Token usage over time
    - Cost per episode
    - Response latency
    - Training stability
    - Deployment readiness score

# Export to:
# - Terminal dashboard (OSS)
# - Weights & Biases (integration)
# - AgentGym Cloud (managed)
```

---

## 5. Competitive Differentiation

### Why Use Agent Lightning Instead of Building RL From Scratch?

**Time Savings:**
- Building production RL library: 6-12 months
- Using Agent Lightning: Focus on platform features from Day 1

**Credibility:**
- Microsoft Research backing
- Battle-tested algorithms
- Active maintenance

**Focus:**
- We focus on **DX, scenarios, deployment**
- They focus on **RL algorithm efficiency**
- Clear separation of concerns

### Why Users Choose AgentGym Over Raw Agent Lightning

| Need | Agent Lightning | AgentGym |
|------|----------------|----------|
| "I'm an RL researcher" | ✅ Perfect | ❌ Too high-level |
| "I want to train production agents fast" | ❌ Too complex | ✅ Perfect |
| "I need pre-built scenarios" | ❌ None | ✅ 20+ scenarios |
| "I use LangChain/AutoGen/CrewAI" | ❌ No integration | ✅ Native support |
| "I want one-click deployment" | ❌ Manual | ✅ Built-in |
| "I need team collaboration" | ❌ None | ✅ Cloud tier |
| "I want managed GPUs" | ❌ BYOG only | ✅ BYOG + Managed |

---

## 6. RL Training Approach: Insights from AgentFlow (Stanford)

### Background: AgentFlow Research

In October 2025, Stanford released [AgentFlow](https://agentflow.stanford.edu/), a trainable agentic system that uses a novel "In-the-Flow" RL algorithm (Flow-GRPO). Key result: **A 7B model beats GPT-4o** on tool-use and reasoning tasks.

**AgentFlow's Architecture:**
- 4-module system (Planner, Executor, Verifier, Generator)
- Only Planner is trained (modular approach)
- On-policy RL during live tool interaction
- Trajectory-level reward broadcasting

### Why We Don't Switch to AgentFlow

| Factor | Agent Lightning (Our Choice) | AgentFlow (Stanford) |
|--------|----------------------------|---------------------|
| **Use Case** | Train EXISTING agents | Build NEW agents |
| **Integration** | Works with LangChain/AutoGen/CrewAI | Requires their 4-module architecture |
| **Backing** | Microsoft Research | Stanford |
| **Maturity** | Established, active community | Brand new (Oct 2025) |
| **License** | MIT (verified) | Unclear |
| **Our Positioning** | Platform over Library | Would be Platform over Platform |

**Conclusion:** AgentFlow is a **complete system** (like us), not a library. Our users want to train **existing agents**, not rebuild them in AgentFlow's architecture.

### Critical Insights We ARE Adopting

However, AgentFlow's research reveals **three critical findings** we must integrate:

#### 1. ⚠️ Offline SFT FAILS for Agent Training

**AgentFlow Result:**
- Offline Supervised Fine-Tuning: **-19.0% performance** ❌
- Online RL (Flow-GRPO): **+17.2% performance** ✅

**Implication for AgentGym:**
```python
# ❌ DON'T: Collect trajectories offline, then supervised training
# This approach FAILS according to AgentFlow research

# ✅ DO: On-policy RL during live tool interaction
class Trainer:
    def train(self):
        """On-policy training - agent interacts with tools DURING training"""
        for episode in range(self.episodes):
            # Live interaction with real tools
            trajectory = self.agent.interact_with_environment()

            # Immediate policy update (on-policy)
            self.update_policy(trajectory)
```

**Why This Matters:**
- Distribution shift: Offline data doesn't match online behavior
- Exploration: Agent needs to try new strategies during training
- Feedback loops: Immediate updates allow faster adaptation

#### 2. Trajectory-Level Reward Broadcasting

**AgentFlow Approach:**
```python
# Instead of sparse reward only at the end:
trajectory = [
    (state1, action1),  # 0 reward
    (state2, action2),  # 0 reward
    (state3, action3),  # +1 reward (success at end only)
]

# Broadcast outcome reward to ALL steps:
trajectory = [
    (state1, action1),  # +1 reward (broadcast)
    (state2, action2),  # +1 reward (broadcast)
    (state3, action3),  # +1 reward (broadcast)
]
```

**Benefits:**
- Solves credit assignment problem in long horizons
- Faster convergence (all steps get signal)
- More stable training

**AgentGym Implementation:**
```python
# agentgym/scenarios/base.py

class Scenario(ABC):
    def calculate_rewards(self, trajectory):
        """
        Broadcast trajectory-level reward to all steps.
        Inspired by AgentFlow's reward design.
        """
        # Evaluate final outcome
        outcome_reward = self.evaluate_outcome(trajectory)

        # Broadcast to all steps (not just final step)
        step_rewards = [outcome_reward] * len(trajectory.steps)

        # Optional: Add step-specific bonuses
        for i, step in enumerate(trajectory.steps):
            if step.tool_success:
                step_rewards[i] += 10  # Bonus for correct tool use
            if step.tokens_used < baseline:
                step_rewards[i] += 5   # Bonus for efficiency

        return step_rewards
```

#### 3. Modular Training (Train Only Tool Selection)

**AgentFlow Insight:**
- Training only the **Planner** (tool selection) is more efficient
- Executor, Verifier, Generator stay deterministic

**Translation for LangChain/AutoGen/CrewAI:**
```python
# agentgym/scenarios/base.py

class Scenario(ABC):
    def define_trainable_components(self):
        """
        Define which components to train vs freeze.
        AgentFlow showed training only planning is efficient.
        """
        return {
            # Train these:
            "tool_selection": True,      # Which tool to use
            "parameter_selection": True,  # With what parameters

            # Freeze these (deterministic or LLM-based):
            "tool_execution": False,     # Actual tool calls (deterministic)
            "output_generation": False,  # Final answer (LLM handles this)
        }
```

**Why This Works:**
- Reduces training complexity (smaller policy space)
- Focuses on what matters (tool selection = 95% reliability)
- Faster convergence (fewer parameters to update)

### Implementation Plan

**Week 1:**
```python
# src/agentgym/core/trainer.py

class Trainer:
    """
    Agent Lightning wrapper with AgentFlow-inspired improvements:
    1. On-policy training (live tool interaction)
    2. Trajectory-level reward broadcasting
    3. Modular training (tool selection only)
    """

    def train(self):
        for episode in range(self.config.episodes):
            # 1. ON-POLICY: Live interaction
            trajectory = self.collect_trajectory_online()

            # 2. BROADCAST REWARDS: All steps get outcome signal
            rewards = self.scenario.broadcast_rewards(trajectory)

            # 3. MODULAR: Update only tool selection policy
            self.update_policy(
                trajectory,
                rewards,
                trainable_components=["tool_selection", "parameter_selection"]
            )
```

**Week 2-3:**
```python
# src/agentgym/scenarios/customer_support.py

class CustomerSupportScenario(Scenario):
    def broadcast_rewards(self, trajectory):
        """AgentFlow-style reward broadcasting"""
        outcome = self.evaluate_outcome(trajectory)
        return [outcome] * len(trajectory.steps)

    def define_trainable_components(self):
        """Only train tool selection (AgentFlow insight)"""
        return {
            "tool_selection": True,
            "parameter_selection": True,
            "tool_execution": False,
            "output_generation": False
        }
```

### Validation

**AgentFlow Benchmarks We'll Use:**
- GAIA (agentic tasks)
- HotpotQA (search-intensive)
- Game of 24 (mathematical reasoning)

**Our Additional Benchmarks:**
- Tool reliability (95% target)
- Cost reduction (30-50% target)
- Time savings (98% target)

### Credit & References

- **AgentFlow Paper:** [In-the-Flow Agentic System Optimization](https://arxiv.org/abs/2510.05592) (Stanford, Oct 2025)
- **GitHub:** [lupantech/AgentFlow](https://github.com/lupantech/AgentFlow)
- **Key Insight:** On-policy RL > Offline SFT for agent training (+17.2% vs -19.0%)

---

## 7. Technical Roadmap

### Month 1-2: OSS Core (Built on Agent Lightning)
- [x] Wrap Agent Lightning with high-level API
- [ ] Create 5 pre-built scenarios
- [ ] LangChain integration
- [ ] AutoGen/MS Agent Framework integration
- [ ] CrewAI integration
- [ ] BYOG orchestration (RunPod, Lambda, local)
- [ ] Terminal UI dashboard
- [ ] CLI: `agentgym train`, `agentgym deploy`

### Month 3-4: Enhanced DX
- [ ] 20+ pre-built scenarios
- [ ] Scenario marketplace (community scenarios)
- [ ] Training templates
- [ ] Export to production formats
- [ ] Advanced observability
- [ ] Training optimization recommendations

### Month 5-6: Cloud Platform
- [ ] Managed GPU orchestration
- [ ] One-click deployment
- [ ] Team collaboration (shared training runs)
- [ ] Advanced analytics dashboard
- [ ] SLA guarantees (99.9% uptime)
- [ ] Enterprise SSO/RBAC

### Month 7-12: Enterprise & Scale
- [ ] Multi-region deployment
- [ ] Custom scenarios (Enterprise)
- [ ] White-label options
- [ ] Advanced security (SOC 2, GDPR)
- [ ] Dedicated support
- [ ] Training marketplace (sell trained agents)

---

## 8. Open Source Strategy

### What We Open Source (Built on Agent Lightning)
✅ Core training wrapper
✅ Pre-built scenarios (5-10 basic ones)
✅ Framework integrations (LangChain, AutoGen, CrewAI)
✅ BYOG orchestration
✅ Terminal UI
✅ CLI tools
✅ Local deployment

### What We Keep Proprietary (Cloud)
🔒 Managed GPU orchestration
🔒 Team collaboration features
🔒 Advanced observability
🔒 One-click deployment to production
🔒 SLA guarantees
🔒 Enterprise SSO/RBAC
🔒 Premium scenarios (20+ advanced)
🔒 Training optimization AI

### Why This Works (GitLab Model)
- OSS builds credibility + community
- Cloud captures 5-10% of users who want convenience
- Fork risk <1% (see OPEN-CORE-COMPETITIVE-MOAT.md)
- Network effects protect moat

---

## 9. Technical Dependencies

### Core Dependencies
```toml
# pyproject.toml
[dependencies]
agent-lightning = "^0.1.0"  # Foundation
langchain = "^0.1.0"        # Integration
autogen = "^0.2.0"          # Integration
crewai = "^0.1.0"           # Integration
rich = "^13.0"              # Terminal UI
typer = "^0.9"              # CLI
pydantic = "^2.0"           # Data validation
```

### Cloud Dependencies
```toml
[cloud-dependencies]
fastapi = "^0.104"          # API server
postgresql = "^15"          # Database
redis = "^7"                # Caching
temporal = "^1.0"           # Orchestration
prometheus = "^2.45"        # Metrics
```

---

## 10. Risk Mitigation

### What if Agent Lightning Changes/Breaks?

**Mitigation Strategy:**
1. **MIT License** - We can fork if needed
2. **Abstraction Layer** - Our API doesn't expose Agent Lightning directly
3. **Version Pinning** - Lock to stable releases
4. **Alternative Engines** - Architecture allows swapping RL backend

**Example Abstraction:**
```python
# agentgym/core/engines/

class RLEngine(ABC):
    """Abstract interface for RL engines"""
    def train(self, env, config): ...
    def evaluate(self, env): ...

class AgentLightningEngine(RLEngine):
    """Current implementation"""
    def train(self, env, config):
        # Use Agent Lightning
        pass

class CustomEngine(RLEngine):
    """Fallback if needed"""
    def train(self, env, config):
        # Our own RL implementation
        pass

# Easy to swap:
engine = AgentLightningEngine()  # or CustomEngine()
```

### What if Microsoft Launches Competing Platform?

**Our Moat:**
1. **Framework-Agnostic** - We support LangChain, AutoGen, CrewAI
2. **Community** - Open source = developer loyalty
3. **Speed** - First mover advantage (launch Month 2)
4. **DX Focus** - Microsoft builds for enterprises, we build for developers

---

## 11. Success Metrics

### Technical Metrics
- **Agent Lightning Integration:** Stable API, <5% breaking changes
- **Training Speed:** 50% faster than manual RL (via optimized scenarios)
- **Tool Reliability:** 95% success rate (vs 60-70% untrained)
- **Setup Time:** <5 minutes from install to first training run

### Platform Metrics
- **GitHub Stars:** 1,000+ in Month 3
- **PyPI Downloads:** 10,000+/month by Month 6
- **Community Scenarios:** 50+ by Month 6
- **Framework Coverage:** 100% (LangChain, AutoGen, CrewAI)

### Business Metrics
- **OSS Adoption:** 5,000+ developers using CLI
- **Cloud Conversion:** 5-10% of OSS users
- **Revenue:** $50K MRR by Month 12
- **Enterprise Customers:** 3-5 by Month 12

---

## 12. Conclusion

### Why This Approach Works

**For Developers:**
- ✅ Simple API (hide Agent Lightning complexity)
- ✅ Pre-built scenarios (start training in minutes)
- ✅ Framework integrations (works with existing stack)
- ✅ BYOG (no vendor lock-in)

**For AgentGym:**
- ✅ Faster time-to-market (don't build RL from scratch)
- ✅ Microsoft credibility boost
- ✅ Focus on platform features (our core value)
- ✅ Clear differentiation (library vs platform)

**For the Ecosystem:**
- ✅ Agent Lightning gets wider adoption
- ✅ Developers get production-ready agent training
- ✅ Community builds scenarios (marketplace potential)

### Next Steps
1. ✅ Document technical approach (this document)
2. [ ] Create system design document (SYSTEM_DESIGN.md)
3. [ ] Implement core wrapper around Agent Lightning
4. [ ] Build first 3 scenarios (customer support, QA, code review)
5. [ ] Launch OSS on GitHub (Month 2)

---

**Questions or Feedback?**
- Technical Lead: [TBD]
- Architecture Discussions: [GitHub Discussions]
- Slack: #architecture channel
