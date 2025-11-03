# Development Environment Setup

Complete guide for setting up your AgentGym development environment.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [GPU Configuration](#gpu-configuration)
4. [IDE Configuration](#ide-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.11+**
  ```bash
  python --version  # Should be 3.11.0 or higher
  ```

- **Git**
  ```bash
  git --version
  ```

- **pip** (comes with Python)
  ```bash
  pip --version
  ```

### Optional (but Recommended)

- **GPU** (for local training testing)
  - NVIDIA GPU with CUDA 11.8+ support
  - At least 8GB VRAM (16GB recommended)

- **Docker** (for containerized development)
  ```bash
  docker --version
  docker compose --version
  ```

- **Make** (for convenience commands)
  ```bash
  make --version
  ```

---

## Local Setup

### 1. Clone the Repository

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agentgym.git
cd agentgym

# Add upstream remote
git remote add upstream https://github.com/agentgym/agentgym.git

# Verify remotes
git remote -v
# origin    https://github.com/YOUR_USERNAME/agentgym.git (fetch)
# origin    https://github.com/YOUR_USERNAME/agentgym.git (push)
# upstream  https://github.com/agentgym/agentgym.git (fetch)
# upstream  https://github.com/agentgym/agentgym.git (push)
```

### 2. Create Virtual Environment

**Option A: venv (built-in)**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify
which python  # Should point to venv/bin/python
```

**Option B: conda (if you prefer)**
```bash
# Create environment
conda create -n agentgym python=3.11

# Activate
conda activate agentgym
```

### 3. Install Dependencies

```bash
# Install AgentGym in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
agentgym --version
agentgym --help
```

**What gets installed:**
- Core AgentGym package (editable mode)
- Agent Lightning (RL engine)
- Framework integrations (LangChain, AutoGen, CrewAI)
- Development tools (pytest, black, ruff, mypy)
- CLI dependencies (typer, rich)

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

**Pre-commit hooks run:**
- `black` - Code formatting
- `ruff` - Linting
- `mypy` - Type checking
- `pytest` - Fast tests

### 5. Verify Setup

```bash
# Run tests
pytest

# Should see:
# ===== test session starts =====
# collected 127 items
#
# tests/test_core.py ........
# tests/test_scenarios.py .......
# ...
# ===== 127 passed in 12.34s =====

# Try CLI
agentgym --help

# List scenarios
agentgym scenarios list
```

---

## GPU Configuration

### Local GPU (NVIDIA)

#### 1. Install CUDA Toolkit

**Ubuntu/Debian:**
```bash
# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"

# Install CUDA
sudo apt update
sudo apt install cuda-11-8

# Add to PATH (add to ~/.bashrc)
export PATH=/usr/local/cuda-11.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH
```

**Windows:**
- Download from https://developer.nvidia.com/cuda-downloads
- Run installer
- Verify: `nvcc --version`

#### 2. Install PyTorch with CUDA

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is detected
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
# CUDA available: True
# GPU: NVIDIA GeForce RTX 4090
```

#### 3. Test Training with Local GPU

```bash
# Run quick training test
agentgym train \
  --scenario customer_support \
  --episodes 100 \
  --gpu local

# Should complete in ~2-3 minutes
```

### BYOG Setup (RunPod / Lambda Labs)

#### RunPod

```bash
# 1. Get API key from https://runpod.io/console/user/settings
export RUNPOD_API_KEY="your-api-key"

# Or add to .env file
echo "RUNPOD_API_KEY=your-api-key" >> .env

# 2. Test connection
agentgym gpu test --provider runpod

# 3. Train with RunPod
agentgym train \
  --scenario customer_support \
  --gpu runpod \
  --gpu-type RTX_4090
```

#### Lambda Labs

```bash
# 1. Get API key from https://cloud.lambdalabs.com/api-keys
export LAMBDA_API_KEY="your-api-key"

# Or add to .env
echo "LAMBDA_API_KEY=your-api-key" >> .env

# 2. Test connection
agentgym gpu test --provider lambda

# 3. Train with Lambda
agentgym train \
  --scenario customer_support \
  --gpu lambda \
  --gpu-type gpu_1x_a100
```

---

## IDE Configuration

### VS Code

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "ms-azuretools.vscode-docker",
    "eamodio.gitlens",
    "GitHub.copilot"
  ]
}
```

**Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.rulers": [88]
  }
}
```

**Launch Configuration (`.vscode/launch.json`):**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "AgentGym CLI",
      "type": "python",
      "request": "launch",
      "module": "agentgym.cli",
      "args": ["train", "--scenario", "customer_support", "--episodes", "100"],
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest: Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm

**Setup:**
1. Open project in PyCharm
2. File → Settings → Project → Python Interpreter
3. Add interpreter → Virtualenv Environment → Existing environment
4. Select `venv/bin/python`

**Configure Tools:**
1. File → Settings → Tools → Black
   - Enable "On save"
2. File → Settings → Tools → External Tools
   - Add Ruff, Mypy

### Cursor / Other Editors

Similar configuration to VS Code, using:
- Black for formatting
- Ruff for linting
- Mypy for type checking
- Pytest for testing

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:**
```bash
ModuleNotFoundError: No module named 'agentgym'
```

**Solution:**
```bash
# Reinstall in editable mode
pip install -e ".[dev]"

# Verify
pip show agentgym
```

#### 2. CUDA Not Available

**Problem:**
```python
torch.cuda.is_available()  # Returns False
```

**Solution:**
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

#### 3. Pre-commit Hooks Failing

**Problem:**
```bash
black....................................................................Failed
```

**Solution:**
```bash
# Run black manually
black .

# Run all pre-commit hooks
pre-commit run --all-files

# If still issues, skip hooks temporarily
git commit --no-verify -m "Your message"
# (But fix before pushing!)
```

#### 4. Tests Failing

**Problem:**
```bash
pytest
# ... many failures ...
```

**Solution:**
```bash
# Install test dependencies
pip install -e ".[dev]"

# Clear pytest cache
pytest --cache-clear

# Run verbose to see details
pytest -vv

# Run single test to debug
pytest tests/test_core.py::test_trainer_init -vv
```

#### 5. Permission Errors (Windows)

**Problem:**
```bash
PermissionError: [WinError 5] Access is denied
```

**Solution:**
```bash
# Run terminal as Administrator, or
# Use Windows Subsystem for Linux (WSL)

# Install WSL
wsl --install

# Then follow Linux setup instructions
```

### Environment Variables

Create `.env` file in project root:

```bash
# GPU Providers
RUNPOD_API_KEY=your-runpod-key
LAMBDA_API_KEY=your-lambda-key

# AgentGym Cloud (optional)
AGENTGYM_API_KEY=your-agentgym-key

# Development
DEBUG=true
LOG_LEVEL=DEBUG

# Testing
PYTEST_CACHE_DIR=.pytest_cache
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Getting Help

If you're still stuck:

1. **Check Documentation:**
   - [README.md](../../README.md)
   - [CONTRIBUTING.md](../../CONTRIBUTING.md)
   - [Architecture docs](../architecture/)

2. **Search Issues:**
   - [Open issues](https://github.com/agentgym/agentgym/issues)
   - [Closed issues](https://github.com/agentgym/agentgym/issues?q=is%3Aissue+is%3Aclosed)

3. **Ask for Help:**
   - [GitHub Discussions](https://github.com/agentgym/agentgym/discussions)
   - Discord (link in README)

4. **Create Issue:**
   - Include your environment details
   - Provide error messages
   - Share minimal reproducible example

---

## Next Steps

Once your environment is set up:

1. **Read the workflow guide:** [WORKFLOW.md](WORKFLOW.md)
2. **Explore the codebase:** Start with `src/agentgym/core/`
3. **Run examples:** `examples/basic_training.py`
4. **Pick an issue:** Look for `good first issue` label
5. **Make your first PR:** Follow [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

**Setup Complete!** 🎉

You're ready to start contributing to AgentGym.
