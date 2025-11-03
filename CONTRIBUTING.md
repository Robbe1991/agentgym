# Contributing to AgentGym

Thank you for your interest in contributing to AgentGym! This document provides guidelines and instructions for contributing.

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Community](#community)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

**Expected Behavior:**
- ✅ Be respectful and inclusive
- ✅ Provide constructive feedback
- ✅ Focus on the best outcome for the community
- ✅ Show empathy towards others

**Unacceptable Behavior:**
- ❌ Harassment or discrimination
- ❌ Personal attacks
- ❌ Publishing others' private information
- ❌ Spam or off-topic discussions

---

## Getting Started

### Prerequisites

- **Python 3.11+** (required)
- **Git** (version control)
- **GPU** (optional, for testing training locally)
  - NVIDIA GPU with CUDA support, or
  - RunPod/Lambda Labs account, or
  - Just test without GPU (slower)

### First-Time Contributors

1. **Find an Issue:**
   - Look for issues labeled [`good first issue`](https://github.com/agentgym/agentgym/labels/good%20first%20issue)
   - Or browse [`help wanted`](https://github.com/agentgym/agentgym/labels/help%20wanted)

2. **Introduce Yourself:**
   - Comment on the issue to claim it
   - Ask questions if anything is unclear
   - We're here to help!

3. **Fork & Clone:**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/agentgym.git
   cd agentgym
   ```

---

## Development Setup

See [docs/development/SETUP.md](docs/development/SETUP.md) for detailed instructions.

**Quick Start:**

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install in development mode
pip install -e ".[dev]"

# 3. Install pre-commit hooks
pre-commit install

# 4. Run tests to verify setup
pytest

# 5. Try the CLI
agentgym --help
```

---

## How to Contribute

### Types of Contributions

#### 1. Code Contributions
- **New Features:** Add new scenarios, integrations, or platform features
- **Bug Fixes:** Fix reported issues
- **Performance:** Optimize training speed or resource usage
- **Refactoring:** Improve code quality

#### 2. Documentation
- **Guides:** Write tutorials or how-to guides
- **API Docs:** Document functions, classes, modules
- **Examples:** Add example scenarios or use cases
- **Translations:** Translate docs to other languages

#### 3. Scenarios
- **Pre-built Scenarios:** Contribute training scenarios (most valuable!)
- **Scenario Templates:** Create reusable patterns
- **Reward Functions:** Share optimized reward functions

#### 4. Testing
- **Unit Tests:** Increase code coverage
- **Integration Tests:** Test framework adapters
- **Benchmarks:** Performance testing

#### 5. Community
- **Help Others:** Answer questions in discussions
- **Report Bugs:** Submit detailed bug reports
- **Feature Requests:** Suggest improvements

---

## Pull Request Process

### Before You Start

1. **Check Existing Work:**
   - Search open/closed PRs to avoid duplicates
   - Comment on related issues

2. **Discuss Large Changes:**
   - For major features, open an issue first
   - Get feedback before investing time

### Step-by-Step Process

#### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/issue-123-description
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Test additions

#### 2. Make Your Changes

```bash
# Write code
# Add tests
# Update documentation

# Run tests locally
pytest

# Run linters
black .
ruff check .
mypy src/agentgym
```

#### 3. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: Add customer support scenario

- Implement CustomerSupportScenario class
- Add reward function for tool reliability
- Include tests and documentation
- Closes #123"
```

**Commit Message Format:**
```
<type>: <short summary>

<optional body>

<optional footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting, missing semicolons, etc.
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

#### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# - Fill out the PR template
# - Link related issues
# - Add screenshots if UI changes
# - Request review
```

#### 5. Address Review Feedback

```bash
# Make requested changes
# Commit with descriptive messages
git commit -m "fix: Address review feedback"

# Push updates
git push origin feature/your-feature-name
```

#### 6. Merge

Once approved:
- Maintainers will merge your PR
- Your contribution is live!
- Thank you! 🎉

---

## Coding Standards

### Python Style

We follow **PEP 8** with some modifications:

```python
# Use type hints
def train_agent(scenario: str, framework: str = "langchain") -> TrainingResult:
    """Train an agent with the specified scenario.

    Args:
        scenario: Name of the training scenario
        framework: Framework to use (langchain, autogen, crewai)

    Returns:
        TrainingResult with metrics and trained model

    Raises:
        ScenarioNotFoundError: If scenario doesn't exist
    """
    pass

# Use dataclasses or Pydantic for data structures
from pydantic import BaseModel

class TrainingConfig(BaseModel):
    scenario: str
    framework: str = "langchain"
    episodes: int = 10000
    gpu_provider: str = "auto"

# Prefer composition over inheritance
class Trainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.orchestrator = GPUOrchestrator()
        self.metrics = MetricsCollector()
```

### Code Quality Tools

```bash
# Format code (auto-fix)
black .

# Lint code
ruff check .
ruff check --fix .  # Auto-fix some issues

# Type checking
mypy src/agentgym

# All checks (run before PR)
make lint  # Runs all of the above
```

### Project Structure

```
src/agentgym/
├── __init__.py
├── core/              # Core training logic
│   ├── trainer.py
│   ├── scenarios.py
│   └── metrics.py
├── integrations/      # Framework adapters
│   ├── langchain.py
│   ├── autogen.py
│   └── crewai.py
├── scenarios/         # Pre-built scenarios
│   ├── customer_support.py
│   ├── code_review.py
│   └── ...
├── cli/               # Command-line interface
│   └── commands.py
├── ui/                # Terminal UI
│   └── dashboard.py
└── utils/             # Utilities
    ├── gpu_providers.py
    └── ...
```

---

## Testing Guidelines

### Test Coverage

- **Minimum Coverage:** 80%
- **Critical Paths:** 100% (trainer, GPU orchestration, scenarios)

### Test Structure

```python
# tests/test_scenarios.py

import pytest
from agentgym.scenarios import CustomerSupportScenario

class TestCustomerSupportScenario:
    """Tests for customer support scenario"""

    @pytest.fixture
    def scenario(self):
        """Fixture for scenario instance"""
        return CustomerSupportScenario()

    def test_create_environment(self, scenario):
        """Test environment creation"""
        env = scenario.create_environment()
        assert env is not None
        assert env.state_space is not None

    def test_reward_calculation(self, scenario):
        """Test reward function"""
        reward = scenario.calculate_reward(
            state=mock_state,
            action=mock_action,
            next_state=mock_next_state
        )
        assert -30 <= reward <= 20  # Valid reward range

    def test_success_criteria(self, scenario):
        """Test success criteria definition"""
        criteria = scenario.success_criteria()
        assert criteria["tool_reliability"] == 0.95
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scenarios.py

# Run with coverage
pytest --cov=agentgym --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"

# Watch mode (re-run on file change)
pytest-watch
```

### Test Categories

```python
# Mark slow tests
@pytest.mark.slow
def test_full_training_run():
    """This test takes 5+ minutes"""
    pass

# Mark integration tests
@pytest.mark.integration
def test_langchain_integration():
    """Requires LangChain to be installed"""
    pass

# Mark GPU tests
@pytest.mark.gpu
def test_gpu_training():
    """Requires GPU to be available"""
    pass
```

---

## Documentation

### Docstrings

Use **Google-style** docstrings:

```python
def train(
    self,
    scenario: str,
    framework: str = "langchain",
    episodes: int = 10000
) -> TrainingResult:
    """Train an agent using reinforcement learning.

    This function orchestrates the entire training process including
    GPU provisioning, environment setup, training loop, and result storage.

    Args:
        scenario: Name of the pre-built scenario to use (e.g., "customer_support")
        framework: Framework for agent integration (langchain, autogen, crewai)
        episodes: Number of training episodes to run (default: 10000)

    Returns:
        TrainingResult containing:
            - trained_model: The trained RL model
            - metrics: Training metrics (tool reliability, cost, speed)
            - artifacts: Deployment artifacts

    Raises:
        ScenarioNotFoundError: If the specified scenario doesn't exist
        GPUNotAvailableError: If no GPU resource can be provisioned
        TrainingFailedError: If training fails after max retries

    Example:
        >>> trainer = Trainer(config)
        >>> result = trainer.train(
        ...     scenario="customer_support",
        ...     framework="langchain",
        ...     episodes=5000
        ... )
        >>> print(f"Tool reliability: {result.metrics.tool_reliability:.1%}")
        Tool reliability: 94.2%

    Note:
        Training time depends on:
        - Scenario complexity
        - Number of episodes
        - GPU type

        Typical training time: 30-60 minutes on RTX 4090
    """
    pass
```

### README Files

Each major component should have a README:

```
src/agentgym/scenarios/README.md
src/agentgym/integrations/README.md
tests/README.md
```

### Examples

Add examples to `examples/`:

```
examples/
├── basic_training.py
├── custom_scenario.py
├── langchain_integration.py
├── deploy_to_production.py
└── README.md
```

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, show & tell
- **Discord:** Real-time chat (link in README)
- **Twitter:** [@agentgym](https://twitter.com/agentgym) - Updates and announcements

### Getting Help

**Before Asking:**
1. Search existing issues and discussions
2. Check documentation
3. Review examples

**When Asking:**
- Provide context and details
- Include error messages (full stack trace)
- Share minimal reproducible example
- Specify your environment (Python version, OS, GPU)

**Example Good Question:**
```
Title: Training fails with "CUDA out of memory" on RTX 3090

Environment:
- AgentGym version: 0.1.0
- Python: 3.11.4
- GPU: NVIDIA RTX 3090 (24GB)
- OS: Ubuntu 22.04

Steps to reproduce:
1. Run: agentgym train --scenario customer_support --episodes 10000
2. Training starts normally
3. Fails at episode ~3000 with CUDA OOM

Error:
```
RuntimeError: CUDA out of memory. Tried to allocate 2.5 GiB
```

Expected: Training should complete without OOM error

Logs: [attached]
```

---

## Recognition

### Contributors

All contributors are recognized in:
- README.md (Contributors section)
- Release notes
- GitHub contributors page

### Special Recognition

- **Top Contributors:** Featured in README
- **Scenario Authors:** Credited in scenario documentation
- **Documentation Heroes:** Special badge
- **Community Champions:** Helping others in discussions

---

## Development Workflow Summary

```bash
# 1. Setup
git clone https://github.com/YOUR_USERNAME/agentgym.git
cd agentgym
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# 2. Create Branch
git checkout -b feature/my-feature

# 3. Develop
# ... write code ...
# ... add tests ...
# ... update docs ...

# 4. Test
pytest
black .
ruff check .
mypy src/agentgym

# 5. Commit
git add .
git commit -m "feat: Add amazing feature"

# 6. Push & PR
git push origin feature/my-feature
# Create PR on GitHub

# 7. Respond to Review
# ... make changes ...
git commit -m "fix: Address review feedback"
git push origin feature/my-feature

# 8. Merge!
# Maintainers will merge once approved
```

---

## Questions?

- **General Questions:** [GitHub Discussions](https://github.com/agentgym/agentgym/discussions)
- **Bug Reports:** [GitHub Issues](https://github.com/agentgym/agentgym/issues)
- **Security Issues:** security@agentgym.com
- **Private Inquiries:** hello@agentgym.com

---

**Thank you for contributing to AgentGym!** 🚀

Every contribution, no matter how small, makes AgentGym better for everyone.
