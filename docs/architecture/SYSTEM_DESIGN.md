# System Design: AgentGym Platform Architecture

**Last Updated:** 2025-11-03
**Status:** Active Design
**Version:** 1.0

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture Layers](#2-architecture-layers)
3. [Component Design](#3-component-design)
4. [Data Flow](#4-data-flow)
5. [OSS vs Cloud Architecture](#5-oss-vs-cloud-architecture)
6. [Technology Stack](#6-technology-stack)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Scalability Strategy](#9-scalability-strategy)
10. [Monitoring & Observability](#10-monitoring--observability)

---

## 1. System Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Developer Interface                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   CLI    │  │ Python   │  │   Web    │  │   API    │    │
│  │  (Typer) │  │   SDK    │  │    UI    │  │  (REST)  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                   AgentGym Core Platform                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Trainer    │  │  Scenarios   │  │ Integrations │       │
│  │  Manager    │  │  Registry    │  │   (LangC,    │       │
│  │             │  │              │  │  AutoGen,    │       │
│  │             │  │              │  │   CrewAI)    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Observ-     │  │     GPU      │  │  Deployment  │       │
│  │ ability     │  │ Orchestrator │  │   Manager    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Agent Lightning Core                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ RL Algos    │  │ Environment  │  │    GPU       │       │
│  │ (PPO, DQN)  │  │   Manager    │  │ Acceleration │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Local     │  │   RunPod     │  │   Lambda     │       │
│  │    GPU      │  │   (BYOG)     │  │    Labs      │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ AgentGym    │  │  Kubernetes  │  │  Database    │       │
│  │   Cloud     │  │   (Cloud)    │  │  (Postgres)  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Layers

### Layer 1: Developer Interface
**Purpose:** How developers interact with AgentGym

**Components:**
- **CLI** (Primary): `agentgym train`, `agentgym deploy`, `agentgym status`
- **Python SDK**: Programmatic access
- **Web UI**: AgentGym Cloud dashboard (paid tier)
- **REST API**: Integration with CI/CD

**Design Principles:**
- Convention over configuration
- Beautiful terminal experience (Rich library)
- Instant feedback
- Zero-config for common use cases

### Layer 2: AgentGym Core Platform
**Purpose:** Business logic, orchestration, DX features

**Components:**
1. **Trainer Manager**: Manages training sessions
2. **Scenario Registry**: Pre-built + custom scenarios
3. **Framework Integrations**: LangChain, AutoGen, CrewAI adapters
4. **Observability**: Metrics, logging, telemetry
5. **GPU Orchestrator**: Provision and manage GPU resources
6. **Deployment Manager**: Export to production

### Layer 3: Agent Lightning Core
**Purpose:** Low-level RL training engine

**What We Use:**
- RL algorithms (PPO, DQN, A3C)
- Environment management
- GPU acceleration
- Distributed training

### Layer 4: Infrastructure
**Purpose:** Compute, storage, networking

**OSS Tier:**
- Local GPU (Docker auto-detect)
- BYOG (RunPod, Lambda Labs)
- SQLite (local state)

**Cloud Tier:**
- Kubernetes (orchestration)
- PostgreSQL (data persistence)
- Redis (caching)
- S3 (artifact storage)
- Temporal (workflow orchestration)

---

## 3. Component Design

### 3.1 Trainer Manager

**Responsibility:** Coordinate agent training sessions

```python
# agentgym/core/trainer_manager.py

class TrainerManager:
    """
    Coordinates training sessions including:
    - Environment setup
    - GPU provisioning
    - Agent Lightning integration
    - Progress tracking
    - Result storage
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.scenario = ScenarioRegistry.load(config.scenario)
        self.gpu_orchestrator = GPUOrchestrator()
        self.metrics = MetricsCollector()

    def train(self) -> TrainingResult:
        # 1. Provision GPU
        gpu_resource = self.gpu_orchestrator.provision(
            provider=self.config.gpu_provider,
            gpu_type=self.config.gpu_type
        )

        # 2. Load framework adapter
        adapter = self.get_adapter(self.config.framework)

        # 3. Initialize Agent Lightning
        rl_trainer = self.initialize_rl_trainer(
            scenario=self.scenario,
            adapter=adapter
        )

        # 4. Train with progress tracking
        with self.metrics.track_training():
            result = rl_trainer.train(
                episodes=self.config.episodes,
                callback=self.on_episode_complete
            )

        # 5. Save trained agent
        self.save_agent(result)

        # 6. Release GPU
        self.gpu_orchestrator.release(gpu_resource)

        return result

    def on_episode_complete(self, episode_num, metrics):
        """Callback for real-time updates"""
        self.metrics.log(episode_num, metrics)
        self.display_progress(episode_num, metrics)
```

**Data Flow:**
```
Config → GPU Provision → Load Scenario → Train (Agent Lightning) →
Save Agent → Release GPU → Return Result
```

### 3.2 Scenario Registry

**Responsibility:** Manage pre-built and custom training scenarios

```python
# agentgym/scenarios/registry.py

class ScenarioRegistry:
    """
    Registry of all available training scenarios.
    Includes pre-built scenarios and custom user scenarios.
    """

    BUILT_IN = {
        "customer_support": CustomerSupportScenario,
        "code_review": CodeReviewScenario,
        "qa_testing": QATestingScenario,
        "data_analysis": DataAnalysisScenario,
        "email_automation": EmailAutomationScenario,
    }

    @classmethod
    def load(cls, scenario_name: str) -> Scenario:
        """Load scenario by name"""
        if scenario_name in cls.BUILT_IN:
            return cls.BUILT_IN[scenario_name]()

        # Check custom scenarios
        return cls.load_custom(scenario_name)

    @classmethod
    def list(cls) -> List[ScenarioInfo]:
        """List all available scenarios"""
        return [
            ScenarioInfo(
                name=name,
                description=scenario_class.description,
                difficulty=scenario_class.difficulty,
                estimated_time=scenario_class.estimated_time
            )
            for name, scenario_class in cls.BUILT_IN.items()
        ]
```

**Scenario Structure:**
```python
# agentgym/scenarios/base.py

class Scenario(ABC):
    """Base class for all training scenarios"""

    name: str
    description: str
    difficulty: str  # beginner, intermediate, advanced
    estimated_time: str  # "30 minutes", "2 hours"

    @abstractmethod
    def create_environment(self) -> Environment:
        """Create Agent Lightning environment"""
        pass

    @abstractmethod
    def calculate_reward(self, state, action, next_state) -> float:
        """Define reward function"""
        pass

    @abstractmethod
    def success_criteria(self) -> Dict[str, float]:
        """Define success metrics"""
        return {
            "tool_reliability": 0.95,
            "cost_reduction": 0.30,
            "speed_improvement": 0.50
        }

    def get_training_config(self) -> Dict:
        """Optimized training hyperparameters"""
        return {
            "learning_rate": 0.0003,
            "discount_factor": 0.95,
            "episodes": 10000,
            # ... pre-tuned for this scenario
        }
```

### 3.3 Framework Integrations

**Responsibility:** Adapt trained agents to LangChain, AutoGen, CrewAI

```python
# agentgym/integrations/base.py

class FrameworkAdapter(ABC):
    """Base adapter for framework integrations"""

    @abstractmethod
    def wrap_agent(self, trained_model) -> Any:
        """Wrap trained model for framework"""
        pass

    @abstractmethod
    def extract_tools(self, agent) -> List[Tool]:
        """Extract tools from framework agent"""
        pass

    @abstractmethod
    def create_environment(self, agent) -> Environment:
        """Create training environment from agent"""
        pass


# agentgym/integrations/langchain_adapter.py

class LangChainAdapter(FrameworkAdapter):
    """Adapter for LangChain agents"""

    def wrap_agent(self, trained_model):
        """Convert trained model to LangChain agent"""
        from langchain.agents import AgentExecutor

        # Create LangChain-compatible agent
        agent = self.create_langchain_agent(trained_model)
        return AgentExecutor(agent=agent, tools=self.tools)

    def extract_tools(self, agent):
        """Extract tools from LangChain agent"""
        return agent.tools

    def create_environment(self, agent):
        """Wrap LangChain agent for RL training"""
        return LangChainEnvironment(
            agent=agent,
            tools=self.extract_tools(agent),
            reward_calculator=self.reward_calculator
        )
```

**Supported Frameworks:**
```
┌─────────────────────────────────────────────────┐
│  Framework Adapters                             │
├─────────────────────────────────────────────────┤
│  ✅ LangChain  → LangChainAdapter               │
│  ✅ AutoGen    → AutoGenAdapter                 │
│  ✅ CrewAI     → CrewAIAdapter                  │
│  🔜 Haystack   → HaystackAdapter (future)       │
│  🔜 Semantic K → SemanticKernelAdapter (future) │
└─────────────────────────────────────────────────┘
```

### 3.4 GPU Orchestrator

**Responsibility:** Provision and manage GPU resources

```python
# agentgym/utils/gpu_orchestrator.py

class GPUOrchestrator:
    """
    Manages GPU provisioning across:
    - Local GPU (Docker detection)
    - RunPod (BYOG)
    - Lambda Labs (BYOG)
    - AgentGym Cloud (managed)
    """

    def provision(self, provider: str, gpu_type: str = "auto"):
        """Provision GPU resource"""
        if provider == "auto":
            provider = self.auto_select_provider()

        provider_class = self.PROVIDERS[provider]
        return provider_class.provision(gpu_type)

    def auto_select_provider(self) -> str:
        """Auto-select best provider"""
        # 1. Check local GPU
        if self.detect_local_gpu():
            return "local"

        # 2. Check cloud credentials
        if self.has_runpod_credentials():
            return "runpod"  # Cheapest

        if self.has_lambda_credentials():
            return "lambda"  # Fast setup

        # 3. Suggest AgentGym Cloud
        raise GPUNotAvailableError(
            "No GPU available. Options:\n"
            "1. Use local GPU\n"
            "2. Set up RunPod/Lambda credentials\n"
            "3. Use AgentGym Cloud: agentgym cloud login"
        )

    def detect_local_gpu(self) -> bool:
        """Detect local CUDA GPU"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
```

**Provider Implementations:**
```python
# agentgym/utils/gpu_providers/runpod.py

class RunPodProvider(GPUProvider):
    """RunPod GPU provisioning"""

    PRICING = {
        "RTX_4090": 0.34,  # $/hour
        "RTX_3090": 0.24,
        "A100": 1.89
    }

    def provision(self, gpu_type: str):
        """Provision GPU via RunPod API"""
        import runpod

        # Create pod
        pod = runpod.create_pod(
            name=f"agentgym-{uuid.uuid4()}",
            image_name="agentgym/trainer:latest",
            gpu_type_id=self.get_gpu_id(gpu_type),
            cloud_type="SECURE",
        )

        # Wait for ready
        self.wait_for_ready(pod)

        return GPUResource(
            provider="runpod",
            pod_id=pod.id,
            gpu_type=gpu_type,
            cost_per_hour=self.PRICING[gpu_type]
        )

    def release(self, resource: GPUResource):
        """Terminate pod"""
        runpod.terminate_pod(resource.pod_id)
```

### 3.5 Observability System

**Responsibility:** Track metrics, logs, telemetry

```python
# agentgym/observability/metrics.py

class MetricsCollector:
    """
    Collects and reports training metrics:
    - Tool success rate (core metric)
    - Token usage
    - Response latency
    - Cost per episode
    - Training stability
    """

    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = None

    def track_training(self):
        """Context manager for training metrics"""
        return TrainingMetricsContext(self)

    def log(self, episode_num: int, metrics: Dict):
        """Log metrics for episode"""
        self.metrics["episode"].append(episode_num)
        self.metrics["tool_success_rate"].append(
            metrics.get("tool_success_rate", 0)
        )
        self.metrics["avg_tokens"].append(
            metrics.get("avg_tokens", 0)
        )
        self.metrics["avg_latency"].append(
            metrics.get("avg_latency", 0)
        )

        # Calculate derived metrics
        self.metrics["cost_per_episode"].append(
            self.calculate_cost(metrics)
        )

    def export(self) -> MetricsReport:
        """Export metrics report"""
        return MetricsReport(
            total_episodes=len(self.metrics["episode"]),
            final_tool_success_rate=self.metrics["tool_success_rate"][-1],
            avg_cost_reduction=self.calculate_cost_reduction(),
            training_time=self.get_training_time(),
            # ... all metrics
        )
```

**Terminal Dashboard:**
```python
# agentgym/ui/terminal_dashboard.py

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress

class TerminalDashboard:
    """Beautiful terminal UI for training progress"""

    def render(self, metrics: MetricsCollector):
        """Render live dashboard"""
        layout = Layout()

        # Header
        layout.split_column(
            Layout(self.render_header(), size=3),
            Layout(self.render_progress(metrics)),
            Layout(self.render_metrics(metrics)),
            Layout(self.render_footer(), size=2)
        )

        return layout

    def render_metrics(self, metrics):
        """Render metrics table"""
        table = Table(title="Training Metrics")

        table.add_column("Metric", style="cyan")
        table.add_column("Current", style="green")
        table.add_column("Target", style="yellow")
        table.add_column("Status", style="bold")

        # Tool reliability
        current_reliability = metrics.get_current("tool_success_rate")
        table.add_row(
            "Tool Reliability",
            f"{current_reliability:.1%}",
            "95%",
            "✓" if current_reliability >= 0.95 else "↑"
        )

        # Add more metrics...
        return table
```

---

## 4. Data Flow

### 4.1 Training Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. User Initiates Training                                  │
│     $ agentgym train --scenario customer_support             │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Parse Config & Load Scenario                             │
│     - Validate inputs                                        │
│     - Load CustomerSupportScenario                           │
│     - Determine framework (LangChain auto-detected)          │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Provision GPU                                            │
│     - Auto-detect local GPU or                               │
│     - Provision RunPod/Lambda or                             │
│     - Use AgentGym Cloud                                     │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  4. Initialize Agent Lightning                               │
│     - Create environment from scenario                       │
│     - Load optimized hyperparameters                         │
│     - Initialize RL trainer (PPO/DQN)                        │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Training Loop (10,000 episodes)                          │
│     For each episode:                                        │
│       - Agent takes action                                   │
│       - Calculate reward (tool success, cost, speed)         │
│       - Update model                                         │
│       - Log metrics                                          │
│       - Display progress                                     │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Save Trained Agent                                       │
│     - Save model weights                                     │
│     - Save metadata                                          │
│     - Generate deployment artifacts                          │
│     - Update registry                                        │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  7. Release Resources                                        │
│     - Terminate GPU pod (if BYOG)                            │
│     - Upload metrics to cloud (if enabled)                   │
│     - Display final report                                   │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Deployment Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. User Initiates Deployment                                │
│     $ agentgym deploy --agent customer_support_v1.2          │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Load Trained Agent                                       │
│     - Load model weights                                     │
│     - Load metadata (framework, tools, config)               │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Select Deployment Target                                 │
│     Options:                                                 │
│     - Framework export (LangChain/AutoGen/CrewAI)            │
│     - Docker container                                       │
│     - AgentGym Cloud (one-click)                             │
│     - API endpoint                                           │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  4. Generate Deployment Artifacts                            │
│     - Convert to target format                               │
│     - Create Dockerfile (if container)                       │
│     - Generate README                                        │
│     - Package dependencies                                   │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Deploy (based on target)                                 │
│     Local: Save to dist/                                     │
│     Cloud: Push to AgentGym Cloud                            │
│     Container: Build and push to registry                    │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Verify Deployment                                        │
│     - Run health check                                       │
│     - Test with sample inputs                                │
│     - Display deployment URL/instructions                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. OSS vs Cloud Architecture

### OSS Architecture (Free Tier)

```
┌─────────────────────────────────────────┐
│  Developer Machine                      │
│  ┌───────────────────────────────────┐  │
│  │  AgentGym CLI                     │  │
│  └───────────────────────────────────┘  │
│            ↓                             │
│  ┌───────────────────────────────────┐  │
│  │  Local SQLite DB                  │  │
│  │  (training runs, agents)          │  │
│  └───────────────────────────────────┘  │
│            ↓                             │
│  ┌───────────────────────────────────┐  │
│  │  GPU Options:                     │  │
│  │  • Local GPU (Docker)             │  │
│  │  • RunPod (BYOG)                  │  │
│  │  • Lambda Labs (BYOG)             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Fully local (no cloud required)
- ✅ SQLite for state persistence
- ✅ BYOG (bring your own GPU)
- ✅ Terminal UI only
- ✅ Manual deployment
- ❌ No team collaboration
- ❌ No managed GPUs
- ❌ No advanced observability

### Cloud Architecture (Paid Tiers)

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 15)                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Dashboard UI                                         │  │
│  │  - Training runs                                      │  │
│  │  - Team management                                    │  │
│  │  - Analytics                                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI)                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │  Training    │  │  Deployment  │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Orchestration Layer (Temporal)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Training Workflows                                  │   │
│  │  - Provision GPU                                     │   │
│  │  - Run training                                      │   │
│  │  - Save results                                      │   │
│  │  - Release resources                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Layer                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │      S3      │     │
│  │  (metadata)  │  │   (cache)    │  │  (artifacts) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Compute Layer (Kubernetes)                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Training Pods                                       │   │
│  │  - GPU nodes (NVIDIA T4, A100)                       │   │
│  │  - Auto-scaling                                      │   │
│  │  - Spot instances (cost optimization)                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Web dashboard
- ✅ Managed GPU orchestration
- ✅ Team collaboration (shared training runs)
- ✅ Advanced observability (Prometheus, Grafana)
- ✅ One-click deployment
- ✅ SLA guarantees (99.9%)
- ✅ Enterprise SSO/RBAC
- ✅ Multi-region deployment

---

## 6. Technology Stack

### Core Technologies

| Layer | Technology | Purpose | Why |
|-------|-----------|---------|-----|
| **RL Engine** | Agent Lightning | Low-level RL training | Microsoft credibility, MIT license |
| **Language** | Python 3.11+ | Primary language | ML ecosystem, type hints |
| **CLI** | Typer + Rich | Command-line interface | Beautiful terminal UX |
| **Web Framework** | FastAPI | REST API | Async, fast, type-safe |
| **Frontend** | Next.js 15 | Web dashboard | SSR, RSC, great DX |
| **Database** | PostgreSQL | Relational data | ACID, jsonb support |
| **Cache** | Redis | Caching layer | Speed, pub/sub |
| **Storage** | S3 | Artifact storage | Scalable, cheap |
| **Orchestration** | Temporal | Workflow engine | Reliable, fault-tolerant |
| **Container** | Docker | Containerization | Portability |
| **Deploy** | Kubernetes | Container orchestration | Auto-scaling, HA |
| **Monitoring** | Prometheus + Grafana | Metrics + dashboards | Industry standard |
| **Logging** | Loki | Log aggregation | Integrates with Grafana |
| **Tracing** | Jaeger | Distributed tracing | Debug training flows |

### Python Dependencies

```toml
# pyproject.toml
[project]
name = "agentgym"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Core
    "agent-lightning>=0.1.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",

    # CLI
    "typer>=0.9",
    "rich>=13.0",
    "click>=8.0",

    # Framework integrations
    "langchain>=0.1.0",
    "autogen>=0.2.0",
    "crewai>=0.1.0",

    # ML/Data
    "numpy>=1.24",
    "pandas>=2.0",
    "torch>=2.0",

    # Utils
    "python-dotenv>=1.0",
    "httpx>=0.24",
    "tenacity>=8.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.1",
    "black>=23.0",
    "ruff>=0.1",
    "mypy>=1.5",
]

cloud = [
    "fastapi>=0.104",
    "uvicorn>=0.24",
    "sqlalchemy>=2.0",
    "alembic>=1.12",
    "asyncpg>=0.29",
    "redis>=5.0",
    "boto3>=1.28",
]
```

---

## 7. Deployment Architecture

### Development Environment

```bash
# Local development setup
$ git clone https://github.com/agentgym/agentgym.git
$ cd agentgym
$ python -m venv venv
$ source venv/bin/activate
$ pip install -e ".[dev]"

# Run tests
$ pytest

# Run local training
$ agentgym train --scenario customer_support --gpu local
```

### OSS Deployment (PyPI)

```bash
# Users install via pip
$ pip install agentgym

# Or with specific integrations
$ pip install agentgym[langchain]
$ pip install agentgym[autogen]
$ pip install agentgym[crewai]
```

### Cloud Deployment (Kubernetes)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentgym-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentgym-api
  template:
    metadata:
      labels:
        app: agentgym-api
    spec:
      containers:
      - name: api
        image: agentgym/api:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agentgym-secrets
              key: database-url
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentgym-trainer
spec:
  replicas: 5
  selector:
    matchLabels:
      app: agentgym-trainer
  template:
    metadata:
      labels:
        app: agentgym-trainer
    spec:
      nodeSelector:
        gpu: "nvidia-t4"  # GPU nodes
      containers:
      - name: trainer
        image: agentgym/trainer:latest
        resources:
          requests:
            nvidia.com/gpu: 1
          limits:
            nvidia.com/gpu: 1
```

---

## 8. Security Architecture

### Authentication & Authorization

```python
# agentgym/cloud/auth.py

class AuthService:
    """
    Authentication for AgentGym Cloud:
    - OSS: No auth required (local only)
    - Cloud Free: Email + password
    - Cloud Pro/Team: SSO support (Google, GitHub)
    - Cloud Enterprise: SAML, custom SSO
    """

    def authenticate(self, credentials):
        # JWT-based auth
        pass

    def authorize(self, user, resource, action):
        # RBAC: owner, admin, member, viewer
        pass
```

### Data Security

```python
# Security measures:

# 1. Encryption at rest
- S3 artifacts: AES-256
- Database: PostgreSQL encryption
- Secrets: Vault/AWS Secrets Manager

# 2. Encryption in transit
- API: HTTPS only (TLS 1.3)
- Database: SSL required
- Redis: TLS enabled

# 3. Access control
- API tokens (scoped)
- Row-level security (RLS)
- Network policies (K8s)

# 4. Compliance
- SOC 2 (Year 2)
- GDPR compliant
- Data residency options
```

---

## 9. Scalability Strategy

### Horizontal Scaling

```
Training Workloads:
┌────────────────────────────────────────┐
│  Load Balancer                         │
└────────────────────────────────────────┘
         ↓           ↓           ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Trainer Pod  │ │ Trainer Pod  │ │ Trainer Pod  │
│   (GPU)      │ │   (GPU)      │ │   (GPU)      │
└──────────────┘ └──────────────┘ └──────────────┘

Auto-scaling rules:
- Scale up: Queue depth > 10
- Scale down: Idle for 5 minutes
- Max pods: 50 (cost limit)
```

### Database Scaling

```
PostgreSQL:
- Primary-replica setup
- Read replicas for analytics
- Connection pooling (PgBouncer)
- Partitioning for large tables

TimescaleDB:
- Time-series metrics
- Automatic downsampling
- Retention policies
```

### Caching Strategy

```
Redis:
Layer 1: Frequently accessed data
  - Scenario definitions
  - User sessions
  - Training status

Layer 2: CDN (CloudFlare)
  - Static assets
  - Public documentation
  - Landing pages
```

---

## 10. Monitoring & Observability

### Metrics (Prometheus)

```python
# Key metrics tracked:

# Business Metrics
- Active users (DAU, MAU)
- Training runs per day
- Conversion rate (OSS → Cloud)
- Revenue (MRR, ARR)

# Technical Metrics
- API latency (p50, p95, p99)
- Training job success rate
- GPU utilization
- Cost per training run

# Quality Metrics
- Tool reliability (95% target)
- Training time
- Model accuracy
- Deployment success rate
```

### Dashboards (Grafana)

```yaml
Dashboards:
1. Executive Dashboard
   - Revenue metrics
   - User growth
   - System health

2. Engineering Dashboard
   - API performance
   - Error rates
   - Resource usage

3. Training Dashboard
   - Active training runs
   - GPU utilization
   - Success rates
   - Cost tracking
```

### Alerting

```yaml
Alerts:
- P0 (Critical): API down, training failures >10%
- P1 (High): Latency >500ms, GPU unavailable
- P2 (Medium): Cost threshold exceeded
- P3 (Low): Documentation outdated
```

---

## Next Steps

1. ✅ Complete system design documentation
2. [ ] Implement core trainer manager
3. [ ] Build scenario registry with 3 scenarios
4. [ ] Create LangChain adapter
5. [ ] Implement GPU orchestrator (local + RunPod)
6. [ ] Build terminal dashboard
7. [ ] Write comprehensive tests
8. [ ] Deploy OSS to PyPI

---

**Document Status:** ✅ Complete
**Last Review:** 2025-11-03
**Next Review:** Weekly during development
