# Claude Code Automation Rules for AgentGym

**Purpose:** Ensure development workflow is automatically followed without human intervention.

---

## 🤖 Automatic Behaviors (ALWAYS Execute)

### 1. Issue-Driven Development (MANDATORY)

**When user requests feature/bug fix:**
```
AUTOMATIC STEPS:
1. Check if GitHub issue exists for this task
2. If NO issue → Create issue via gh CLI automatically
3. If YES issue → Reference it in all commits/PRs
4. Create feature branch: feature/issue-name
5. Implement from issue spec
6. Test (pytest)
7. Create PR via gh CLI
8. Link PR to issue ("Closes #X")
```

**Never ask "Should I create an issue?" → JUST DO IT**

### 2. GitHub CLI Operations (ALWAYS Automated)

**I have gh CLI access. I MUST use it for:**
- ✅ Creating issues (`gh issue create`)
- ✅ Creating PRs (`gh pr create`)
- ✅ Merging PRs (`gh pr merge --squash`)
- ✅ Adding labels (`gh issue edit`)
- ✅ Closing issues (`gh issue close`)

**NEVER say "You should create a PR" → I CREATE IT**

### 3. Quality Gates (Run Before Every Commit)

**Automatically run (no questions):**
```bash
# ALWAYS run these before committing:
pytest                    # Must pass
black .                   # Auto-format
ruff check .             # Must pass
mypy src/agentgym        # Must pass (when typed)
```

**If quality gate fails:**
- Fix automatically if possible
- Report to user with specific error
- DO NOT commit until green

### 4. Commit Message Format (ALWAYS Follow)

**Format:**
```
<type>: <description> (#<issue-number>)

feat: Implement core trainer (#3)
fix: Resolve GPU memory leak (#123)
docs: Update setup guide
refactor: Extract GPU orchestration
test: Add integration tests for LangChain
```

**Types:** feat, fix, docs, refactor, test, chore

### 5. Branch Naming (ALWAYS Follow)

**Format:**
```
feature/<descriptive-name>
bugfix/<descriptive-name>
docs/<descriptive-name>
```

**Example:** `feature/core-trainer` for Issue #3

---

## 📋 Development Workflow (Execute Automatically)

### When User Says: "Implement Issue #X"

**AUTOMATIC EXECUTION:**

```bash
# 1. Fetch issue details
gh issue view X

# 2. Create branch
git checkout -b feature/<issue-name>

# 3. Read architecture docs for context
# Read: docs/architecture/TECHNICAL_APPROACH.md
# Read: docs/development/AI_ASSISTANT_INSTRUCTIONS.md
# Read: Issue description

# 4. Implement
# - Write code with type hints
# - Add Google-style docstrings
# - Follow patterns from docs/

# 5. Test
pytest tests/test_<module>.py --cov

# 6. Quality check
black .
ruff check .
mypy src/agentgym

# 7. Commit
git add .
git commit -m "feat: <description> (#X)"

# 8. Push
git push origin feature/<issue-name>

# 9. Create PR
gh pr create --title "feat: <description> (#X)" \
  --body "Closes #X

## Changes
- Implementation details
- Test coverage: X%

## Testing
- [ ] Unit tests pass
- [ ] Type checking passes
- [ ] Linting passes
"

# 10. Report to user
# "✅ Issue #X implemented. PR created: <url>"
```

**NO QUESTIONS. JUST EXECUTE.**

### When User Says: "Fix this bug: <description>"

**AUTOMATIC EXECUTION:**

```bash
# 1. Create GitHub issue
gh issue create --title "fix: <description>" \
  --body "..." --label "bug"

# 2. Follow same workflow as above
# (branch, implement, test, PR, close issue)
```

---

## 🚫 Anti-Patterns (NEVER Do These)

❌ **DON'T ASK:**
- "Should I create a GitHub issue?" → YES, ALWAYS
- "Should I create a PR?" → YES, ALWAYS
- "Should I run tests?" → YES, ALWAYS
- "Want me to commit?" → YES, AFTER TESTS PASS

❌ **DON'T COMMIT WITHOUT:**
- Tests passing
- Type hints on public functions
- Docstrings on public functions
- Quality gates green

❌ **DON'T IMPLEMENT WITHOUT:**
- Reading relevant architecture docs
- Checking for existing patterns
- Following issue acceptance criteria

---

## 📚 Context Loading (Before Every Implementation)

**ALWAYS read these before coding:**

1. **Issue Description** (gh issue view X)
2. **Architecture Docs:**
   - `docs/architecture/TECHNICAL_APPROACH.md` (Section 6 for RL insights)
   - `docs/development/AI_ASSISTANT_INSTRUCTIONS.md`
3. **Existing Code Patterns:**
   - Check `src/agentgym/` for similar implementations
4. **Project Context:**
   - `.claude/project-context.md` (high-level overview)

---

## 🎯 Success Criteria Checks

**Before marking task complete, verify:**

- [ ] Acceptance criteria from issue = met
- [ ] Tests written (80%+ coverage)
- [ ] Type hints added
- [ ] Docstrings added (Google style)
- [ ] Quality gates pass
- [ ] PR created and linked to issue
- [ ] Example usage exists (in tests/ or examples/)

---

## 🔄 Parallel Development

**When multiple independent issues exist:**

1. Identify dependencies (read WEEK-1-ISSUES.md)
2. Group independent issues
3. Offer to work in parallel:
   - "Issues #4 and #5 are independent. Implement both?"
4. Create separate branches for each
5. Merge in sequence (tests must pass)

**Example:**
```
User: "Implement Issues #4, #5, #6"

Response:
"Issues #4 (Base Scenario) and #5 (Registry) are independent.
Issue #6 depends on #4.

Plan:
1. Implement #4 and #5 in parallel
2. After both merged, implement #6

Proceeding automatically..."
```

---

## 🧪 Testing Requirements

**ALWAYS include:**

1. **Unit tests** for all public functions
2. **Integration tests** for cross-module interactions
3. **Example usage** in docstrings or tests/
4. **Coverage report** (pytest --cov)

**Test naming:**
```python
# File: tests/test_trainer.py
def test_trainer_initialization():
    """Test Trainer initializes correctly."""
    ...

def test_trainer_on_policy_training():
    """Test on-policy training loop executes."""
    ...
```

---

## 📝 Documentation Requirements

**ALWAYS add:**

1. **Docstrings** (Google style):
```python
def train(self, config: TrainingConfig) -> TrainingResult:
    """Train agent using on-policy reinforcement learning.

    Args:
        config: Training configuration with scenario and hyperparameters.

    Returns:
        TrainingResult with metrics and trained model path.

    Raises:
        ScenarioNotFoundError: If scenario doesn't exist.

    Example:
        >>> config = TrainingConfig(scenario="customer_support")
        >>> trainer = Trainer(config)
        >>> result = trainer.train()
        >>> print(result.metrics.tool_reliability)
        0.95
    """
```

2. **Type hints** (everywhere):
```python
from typing import List, Dict, Optional

def broadcast_rewards(self, trajectory: Trajectory) -> List[float]:
    ...
```

3. **Code comments** (for complex logic):
```python
# AgentFlow insight: Broadcast outcome reward to ALL steps
# This solves credit assignment better than sparse rewards
step_rewards = [outcome_reward] * len(trajectory.steps)
```

---

## 🎨 Code Style (ALWAYS Enforce)

**Black formatting:**
- 88 character line length
- Run before every commit

**Import order:**
```python
# 1. Standard library
import os
from typing import List

# 2. Third-party
import typer
from pydantic import BaseModel

# 3. Local
from agentgym.core.config import TrainingConfig
```

**Naming conventions:**
```python
ClassNamesInPascalCase
function_names_in_snake_case
CONSTANTS_IN_UPPER_CASE
_private_methods_with_underscore
```

---

## 🚀 Week 1 Execution Plan

**Issues #1-9 from WEEK-1-ISSUES.md:**

**Track 1 (Core):**
- Issue #1 → Issue #2 → Issue #3 (sequential)

**Track 2 (Scenarios):**
- Issue #4 → Issue #5 (sequential)
- Issue #6 (after #4 done)

**Track 3 (Integrations):**
- Issue #7 (after Track 1 done)
- Issue #8, #9 (after #7 done, can be parallel)

**When starting Week 1:**
1. Ask: "Implement all Week 1 issues (automatic execution)?"
2. If YES → Execute full pipeline for each issue
3. Report progress after each issue closed

---

## 💬 Communication Style

**Concise, action-oriented:**

✅ **GOOD:**
```
Implementing Issue #3 (Core Trainer)...

1. Creating branch feature/core-trainer
2. Reading TECHNICAL_APPROACH.md Section 6
3. Implementing on-policy training loop
4. Writing tests (target: 80% coverage)
5. Running quality gates...

[implementation details]

✅ Tests pass (coverage: 87%)
✅ Type checking pass
✅ Linting pass

Committing and creating PR...

✅ Issue #3 complete: https://github.com/.../pull/3
```

❌ **BAD:**
```
I can help implement Issue #3. Should I create a branch first?
Would you like me to write tests too? What test coverage do you want?
Should I follow the architecture docs?
Let me know when you want me to create the PR.
```

**NO QUESTIONS. AUTOMATIC EXECUTION.**

---

## 🔐 Git Operations

**ALWAYS use GitHub CLI:**

```bash
# Create issue
gh issue create --title "..." --body "..." --label "..."

# Create PR
gh pr create --title "..." --body "Closes #X" --label "..."

# Merge PR (after user approval OR if tests auto-pass)
gh pr merge --squash

# Close issue (automatically when PR merged)
gh issue close X
```

**Commit and push automatically** (after quality gates pass):
```bash
git add .
git commit -m "feat: <description> (#X)"
git push origin feature/<branch>
```

---

## ✅ Final Checklist (Before Saying "Done")

**Every task completion MUST have:**

- [x] GitHub issue exists (or created)
- [x] Feature branch created
- [x] Code implemented (matches acceptance criteria)
- [x] Tests written (80%+ coverage)
- [x] Type hints added
- [x] Docstrings added
- [x] Quality gates pass (pytest, black, ruff, mypy)
- [x] Committed with proper message
- [x] PR created and linked to issue
- [x] Example usage exists

**If ANY checkbox unchecked → NOT DONE**

---

## 🎯 Remember

**You (Claude) are responsible for:**
- ✅ Automatic workflow execution
- ✅ GitHub CLI operations
- ✅ Quality enforcement
- ✅ Documentation
- ✅ Testing
- ✅ Following architecture

**User is responsible for:**
- ✅ Strategic decisions
- ✅ Code review (you implement, they review)
- ✅ Final approval
- ✅ Domain registration
- ✅ Deployment (later)

**Together:** Ship Week 1 MVP automatically! 🚀

---

**Last Updated:** 2025-11-03
**Status:** Active - Enforce all rules automatically
