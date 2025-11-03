# State-of-the-Art: AI-Assisted SaaS Development Workflow

**For:** AgentGym Week 1 Development
**With:** Claude Code (AI Pair Programming)

---

## Philosophy: Issue-Driven Development with AI

**Core Idea:**
- Every feature = GitHub Issue
- AI implements from issue spec
- Human reviews & merges
- Continuous deployment

**Why this works:**
- ✅ Clear scope per task
- ✅ AI has full context from issue
- ✅ Parallelizable (multiple issues)
- ✅ Trackable progress
- ✅ Clean git history

---

## Workflow: The Cycle

### 1. Planning (Human)

**Create GitHub Issues for features:**

```markdown
Title: Implement Core Trainer with On-Policy RL

Description:
Implement the core Trainer class that wraps Agent Lightning with on-policy RL.

**Acceptance Criteria:**
- [ ] Trainer class in src/agentgym/core/trainer.py
- [ ] On-policy training loop (live tool interaction)
- [ ] Integration with Agent Lightning
- [ ] Type hints and docstrings
- [ ] Unit tests (80% coverage)
- [ ] Example usage in tests/

**References:**
- docs/architecture/TECHNICAL_APPROACH.md (Section 6)
- AgentFlow insight: On-policy RL > Offline SFT

**Technical Details:**
```python
class Trainer:
    def train(self):
        for episode in range(self.episodes):
            trajectory = self.collect_trajectory_online()  # On-policy
            rewards = self.scenario.broadcast_rewards(trajectory)
            self.update_policy(trajectory, rewards)
```

Labels: feature, week-1, core
Milestone: Week 1 - Core Foundation
Assignee: @Robbe1991
```

### 2. Implementation (AI-Assisted)

**Developer (You) with Claude Code:**

```bash
# Start feature branch
git checkout -b feature/core-trainer

# Ask Claude to implement
"Hey Claude, implement GitHub Issue #1 (Core Trainer)"
# Claude reads issue, implements code, writes tests

# Review Claude's code
# Make adjustments if needed

# Run tests
pytest tests/test_trainer.py

# Commit
git add .
git commit -m "feat: Implement core trainer with on-policy RL (#1)"

# Push
git push origin feature/core-trainer
```

### 3. Review (Human)

**Create PR, self-review:**
- Does it match acceptance criteria?
- Are tests passing?
- Is documentation complete?

**Merge to main:**
```bash
gh pr create --title "feat: Implement core trainer (#1)" --body "Closes #1"
gh pr merge --squash
```

### 4. Deployment (Automated)

**GitHub Actions:**
- Run tests on every PR
- Type check with mypy
- Lint with ruff
- Auto-publish to PyPI (later)

---

## Week 1 Development Strategy

### Day 1-2: Foundation (Issues #1-3)

**Issue #1: Core Configuration**
- File: `src/agentgym/core/config.py`
- Pydantic models for training config
- Validation, defaults

**Issue #2: Training Results**
- File: `src/agentgym/core/result.py`
- Dataclass for metrics
- Serialization

**Issue #3: Core Trainer**
- File: `src/agentgym/core/trainer.py`
- On-policy RL loop
- Agent Lightning integration

### Day 3-4: Scenarios (Issues #4-6)

**Issue #4: Base Scenario**
- File: `src/agentgym/scenarios/base.py`
- Abstract base class
- Trajectory-level rewards

**Issue #5: Scenario Registry**
- File: `src/agentgym/scenarios/registry.py`
- Dynamic loading
- List scenarios

**Issue #6: Customer Support Scenario**
- File: `src/agentgym/scenarios/customer_support.py`
- First concrete scenario
- 95% reliability target

### Day 5-7: Integration (Issues #7-9)

**Issue #7: Base Adapter**
- File: `src/agentgym/integrations/base.py`
- Abstract adapter interface

**Issue #8: LangChain Adapter**
- File: `src/agentgym/integrations/langchain.py`
- Convert to LangChain agent

**Issue #9: Basic CLI**
- File: `src/agentgym/cli/main.py`
- `agentgym --version`
- `agentgym train --scenario X`

---

## AI Prompt Patterns (for Claude Code)

### Pattern 1: From GitHub Issue

```
"Implement GitHub Issue #5 (Scenario Registry):
- Read the issue for requirements
- Follow our architecture in docs/architecture/TECHNICAL_APPROACH.md
- Use patterns from docs/development/AI_ASSISTANT_INSTRUCTIONS.md
- Write tests with 80% coverage
- Add docstrings (Google style)
"
```

### Pattern 2: Iterate on Code

```
"The Trainer class needs on-policy RL (not offline).
AgentFlow showed offline SFT = -19% performance.
Refactor to collect trajectories online during training.
See docs/architecture/TECHNICAL_APPROACH.md Section 6.1
"
```

### Pattern 3: Debug

```
"Tests failing in test_trainer.py line 42.
Error: AttributeError 'Trainer' object has no attribute 'collect_trajectory_online'
Fix this and ensure all tests pass.
"
```

### Pattern 4: Review

```
"Review src/agentgym/core/trainer.py:
- Is on-policy RL implemented correctly?
- Are type hints complete?
- Is test coverage >= 80%?
- Suggest improvements
"
```

---

## Best Practices with AI

### Do:
- ✅ Give Claude full context (link to docs, issues, architecture)
- ✅ Be specific about requirements
- ✅ Ask for tests + documentation
- ✅ Iterate on code (Claude learns from feedback)
- ✅ Use Claude for code review

### Don't:
- ❌ Ask Claude to "build everything"
- ❌ Skip requirements/specs
- ❌ Blindly accept code (always review)
- ❌ Forget to test
- ❌ Over-complicate prompts

---

## Development Setup (Once)

```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install in editable mode
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Verify setup
pytest  # Should run (even if 0 tests initially)
agentgym --version  # Should work once CLI implemented
```

---

## Daily Workflow

```bash
# Morning: Pull latest
git checkout main
git pull origin main

# Pick an issue from GitHub
# Example: Issue #4 (Base Scenario)

# Create feature branch
git checkout -b feature/base-scenario

# Ask Claude to implement
# (via Claude Code in your editor)

# Test locally
pytest tests/test_scenarios.py
black .
ruff check .
mypy src/agentgym

# Commit
git add .
git commit -m "feat: Implement base scenario class (#4)"

# Push & create PR
git push origin feature/base-scenario
gh pr create --title "feat: Base scenario (#4)" --body "Closes #4"

# Review (yourself or with Claude)
# Merge when ready
gh pr merge --squash

# Move to next issue
```

---

## Quality Gates (Before Merge)

### Must Pass:
1. ✅ All tests passing (`pytest`)
2. ✅ Type check passing (`mypy src/agentgym`)
3. ✅ Linting passing (`ruff check .`)
4. ✅ Formatting correct (`black --check .`)
5. ✅ Test coverage >= 80% (check with `pytest --cov`)

### Should Have:
1. ✅ Docstrings on all public functions
2. ✅ Type hints on all functions
3. ✅ Example usage in tests or examples/
4. ✅ Updated docs if architecture changed

---

## Parallel Development Strategy

**Week 1 can be parallelized:**

**Track 1: Core (Days 1-2)**
- Issue #1, #2, #3 (sequential)

**Track 2: Scenarios (Days 3-4)**
- Issue #4, #5 (sequential)
- Issue #6 (can start when #4 done)

**Track 3: Integrations (Days 5-7)**
- Issue #7 (needs Track 1 done)
- Issue #8, #9 (parallel when #7 done)

**With AI:**
- You focus on Track 1
- Claude helps with Track 2 & 3 in parallel
- You review everything

---

## Issue Templates (Copy-Paste)

### Feature Template

```markdown
## Description
[What needs to be built]

## Acceptance Criteria
- [ ] Implementation in src/agentgym/...
- [ ] Unit tests with 80% coverage
- [ ] Type hints and docstrings
- [ ] Example usage

## Technical Details
[Code snippets, architecture references]

## References
- docs/architecture/TECHNICAL_APPROACH.md
- Related issues: #X, #Y

## Labels
feature, week-1, [component]
```

### Bug Template

```markdown
## Bug Description
[What's broken]

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Python version: 3.11
- OS: Windows
- AgentGym version: 0.1.0

## Labels
bug, priority-high
```

---

## Tools Setup

### GitHub CLI Commands

```bash
# List issues
gh issue list

# Create issue
gh issue create --title "..." --body "..."

# View issue
gh issue view 5

# Close issue
gh issue close 5

# Create PR
gh pr create --title "..." --body "Closes #5"

# Merge PR
gh pr merge --squash
```

### VS Code Extensions (Recommended)

```
- Python (Microsoft)
- Pylance (Microsoft)
- GitHub Copilot (if you have it)
- GitLens
- Python Test Explorer
```

---

## Success Metrics

**Week 1 Goal:**
- ✅ 9 issues closed (3 per track)
- ✅ Basic example working end-to-end
- ✅ 80%+ test coverage
- ✅ All quality gates passing

**Week 1 Output:**
```bash
# This should work:
agentgym train \
  --scenario customer_support \
  --framework langchain \
  --episodes 100

# Output:
# Training: 100%|██████████| 100/100
# Tool reliability: 87.3% (target: 95%)
# Saved to: ./trained_models/customer_support_v0.1.0
```

---

## Remember

**You:** Strategic decisions, issue creation, code review, testing
**Claude:** Implementation, tests, documentation, debugging
**Together:** Ship Week 1 MVP 🚀

---

**Ready to start?** Create GitHub Issues for Week 1 tasks!
