# Development Workflow

This document describes the development workflow for contributing to AgentGym.

---

## Table of Contents
1. [Daily Workflow](#daily-workflow)
2. [Git Workflow](#git-workflow)
3. [Branch Strategy](#branch-strategy)
4. [Code Review Process](#code-review-process)
5. [Release Process](#release-process)
6. [Hotfix Process](#hotfix-process)

---

## Daily Workflow

### Starting Your Day

```bash
# 1. Update your local main branch
git checkout main
git pull upstream main

# 2. Push to your fork
git push origin main

# 3. Update your feature branch (if working on one)
git checkout feature/my-feature
git rebase main

# 4. Activate virtual environment
source venv/bin/activate  # or: conda activate agentgym

# 5. Install any new dependencies
pip install -e ".[dev]"
```

### During Development

```bash
# Run tests frequently (watch mode)
pytest-watch

# Or run manually
pytest

# Run linters
black .
ruff check .

# Type checking
mypy src/agentgym

# Or run all checks at once
make lint
```

### Before Committing

```bash
# 1. Run full test suite
pytest

# 2. Run all quality checks
black .
ruff check .
mypy src/agentgym

# 3. Check test coverage
pytest --cov=agentgym --cov-report=html
# Open htmlcov/index.html to view coverage

# 4. Stage changes
git add .

# 5. Commit (pre-commit hooks will run automatically)
git commit -m "feat: Add awesome feature"

# If pre-commit hooks fail:
# - Fix the issues
# - Stage the fixes: git add .
# - Commit again
```

### End of Day

```bash
# Push your work to your fork
git push origin feature/my-feature

# Update draft PR if you have one
# (so others can see your progress)
```

---

## Git Workflow

### Overview

We use a **Fork and Pull Request** workflow:

```
Upstream Repo (agentgym/agentgym)
       ↓ fork
Your Fork (yourname/agentgym)
       ↓ clone
Local Machine
       ↓ feature branch
Make Changes
       ↓ push
Your Fork
       ↓ pull request
Upstream Repo
```

### Detailed Steps

#### 1. Fork the Repository

On GitHub:
1. Go to https://github.com/agentgym/agentgym
2. Click "Fork" button
3. Select your account

#### 2. Clone Your Fork

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agentgym.git
cd agentgym

# Add upstream remote
git remote add upstream https://github.com/agentgym/agentgym.git

# Verify
git remote -v
```

#### 3. Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Update main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

#### 4. Create Feature Branch

```bash
# Always branch from main
git checkout main
git pull upstream main

# Create and checkout feature branch
git checkout -b feature/your-feature-name
```

#### 5. Make Changes

```bash
# Edit files
# Add tests
# Update docs

# Commit frequently with clear messages
git add .
git commit -m "feat: Add X functionality"

# More changes...
git add .
git commit -m "test: Add tests for X"

# More changes...
git add .
git commit -m "docs: Document X feature"
```

#### 6. Push to Your Fork

```bash
# Push feature branch
git push origin feature/your-feature-name

# If you've rebased and need to force push:
git push origin feature/your-feature-name --force-with-lease
```

#### 7. Create Pull Request

On GitHub:
1. Go to your fork
2. Click "Pull Request" button
3. Fill out PR template:
   - Clear title
   - Description of changes
   - Link to related issues
   - Screenshots if UI changes
   - Checklist completed
4. Request review from maintainers

#### 8. Address Review Feedback

```bash
# Make requested changes
# ... edit files ...

# Commit with descriptive message
git add .
git commit -m "fix: Address review feedback from @reviewer"

# Push updates
git push origin feature/your-feature-name

# PR updates automatically
```

#### 9. Merge

Once approved, maintainers will merge using **Squash and Merge** strategy.

---

## Branch Strategy

### Branch Types

#### `main` Branch
- **Purpose:** Production-ready code
- **Protected:** Yes
- **Requires:** PR approval, CI passing
- **Direct commits:** Never

#### `feature/*` Branches
- **Purpose:** New features
- **Naming:** `feature/short-description`
- **Examples:**
  - `feature/customer-support-scenario`
  - `feature/autogen-integration`
  - `feature/terminal-dashboard`

#### `fix/*` Branches
- **Purpose:** Bug fixes
- **Naming:** `fix/issue-number-description`
- **Examples:**
  - `fix/123-gpu-memory-leak`
  - `fix/456-cli-crash`

#### `docs/*` Branches
- **Purpose:** Documentation only
- **Naming:** `docs/what-changed`
- **Examples:**
  - `docs/improve-setup-guide`
  - `docs/add-api-reference`

#### `refactor/*` Branches
- **Purpose:** Code refactoring (no behavior change)
- **Naming:** `refactor/what-changed`
- **Examples:**
  - `refactor/simplify-trainer`
  - `refactor/extract-gpu-logic`

#### `test/*` Branches
- **Purpose:** Adding tests only
- **Naming:** `test/what-tested`
- **Examples:**
  - `test/scenario-coverage`
  - `test/integration-tests`

### Branch Lifecycle

```
1. Create from main
   git checkout main
   git pull upstream main
   git checkout -b feature/my-feature

2. Develop
   # Make commits
   git commit -m "feat: ..."
   git commit -m "test: ..."
   git commit -m "docs: ..."

3. Keep updated (rebase onto main)
   git fetch upstream
   git rebase upstream/main

   # Resolve conflicts if any
   # Then:
   git rebase --continue

4. Push
   git push origin feature/my-feature --force-with-lease

5. Create PR
   # On GitHub

6. Review & Update
   # Address feedback
   git commit -m "fix: Review feedback"
   git push origin feature/my-feature

7. Merge
   # Maintainer squashes and merges

8. Cleanup
   git checkout main
   git pull upstream main
   git branch -d feature/my-feature
   git push origin --delete feature/my-feature
```

---

## Code Review Process

### For Authors

#### Before Requesting Review

**Checklist:**
- [ ] All tests pass locally
- [ ] Code follows style guidelines (black, ruff)
- [ ] Type hints added (mypy passes)
- [ ] Documentation updated
- [ ] Examples added if new feature
- [ ] CHANGELOG.md updated
- [ ] PR template filled out completely

#### Requesting Review

1. **Create PR** with clear title and description
2. **Link issues** using "Closes #123" in description
3. **Add labels** (feature, bug, documentation, etc.)
4. **Request reviewers** (will be auto-assigned based on CODEOWNERS)
5. **Mark as draft** if not ready for full review

#### During Review

**Respond to feedback:**
- Be open to suggestions
- Ask questions if unclear
- Explain your reasoning
- Make requested changes promptly

**Make updates:**
```bash
# Make changes
git add .
git commit -m "fix: Address @reviewer's feedback"
git push origin feature/my-feature

# Re-request review if needed
```

**Resolve conversations:**
- On GitHub, mark conversations as resolved when addressed
- Reply to each comment (even just "Done" or "Fixed")

### For Reviewers

#### Review Checklist

**Functionality:**
- [ ] Code does what PR claims
- [ ] Edge cases handled
- [ ] No obvious bugs

**Code Quality:**
- [ ] Clear, readable code
- [ ] Follows project conventions
- [ ] No unnecessary complexity
- [ ] Well-structured (SOLID principles)

**Testing:**
- [ ] Tests included
- [ ] Tests cover main scenarios
- [ ] Tests cover edge cases
- [ ] Tests are clear and maintainable

**Documentation:**
- [ ] Docstrings present and clear
- [ ] README updated if needed
- [ ] Examples added for new features
- [ ] CHANGELOG.md updated

**Performance:**
- [ ] No obvious performance issues
- [ ] Resource usage reasonable

#### Providing Feedback

**Be constructive:**
```
❌ "This code is bad"
✅ "Consider extracting this logic into a separate function for clarity"

❌ "This won't work"
✅ "This might fail if input is empty. Could we add validation?"

❌ "Use better naming"
✅ "The name 'data' is vague. Maybe 'training_metrics' would be more descriptive?"
```

**Categories:**
- **Required (blocking):** Must be fixed before merge
- **Suggestion (non-blocking):** Nice to have
- **Question:** Seeking clarification

**Example comments:**
```markdown
**Required:** This will crash if `scenario` is None. Please add validation.

**Suggestion:** Consider using a dataclass here for better type safety.

**Question:** Why did we choose approach X over Y?
```

#### Approving

Once satisfied:
1. Click "Approve"
2. Add comment: "LGTM! 🚀" or similar
3. If you're a maintainer, merge using "Squash and merge"

---

## Release Process

### Versioning

We use **Semantic Versioning** (semver):
- **Major:** Breaking changes (1.0.0 → 2.0.0)
- **Minor:** New features, backwards compatible (1.0.0 → 1.1.0)
- **Patch:** Bug fixes (1.0.0 → 1.0.1)

### Release Checklist

#### 1. Pre-release

```bash
# Update version in pyproject.toml
# version = "0.2.0"

# Update CHANGELOG.md
# Add release date, summarize changes

# Update README.md if needed
# Any version-specific info

# Commit changes
git add .
git commit -m "chore: Prepare v0.2.0 release"
git push origin main
```

#### 2. Create Release

```bash
# Create git tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push tag
git push origin v0.2.0
```

#### 3. GitHub Release

On GitHub:
1. Go to Releases
2. Click "Create a new release"
3. Select tag: v0.2.0
4. Release title: "v0.2.0 - Short Description"
5. Description: Copy from CHANGELOG.md
6. Publish release

#### 4. PyPI Release

```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Verify
pip install agentgym --upgrade
agentgym --version
```

#### 5. Post-release

```bash
# Bump to next dev version
# version = "0.3.0-dev"

git add pyproject.toml
git commit -m "chore: Bump to v0.3.0-dev"
git push origin main
```

### Release Schedule

- **Patch releases:** As needed (bug fixes)
- **Minor releases:** Every 2-4 weeks (new features)
- **Major releases:** Every 3-6 months (breaking changes)

---

## Hotfix Process

For critical bugs in production:

### 1. Create Hotfix Branch

```bash
# From latest release tag
git checkout v1.2.0
git checkout -b hotfix/critical-bug-fix
```

### 2. Fix and Test

```bash
# Make minimal fix
# Add regression test

# Test thoroughly
pytest
```

### 3. Create PR to Main

```bash
git push origin hotfix/critical-bug-fix
# Create PR to main
```

### 4. Fast-track Review

- Mark as "hotfix" label
- Request immediate review
- Merge once approved

### 5. Release Patch Version

```bash
# Update version: 1.2.0 → 1.2.1
# Create tag
git tag -a v1.2.1 -m "Hotfix: Fix critical bug"
git push origin v1.2.1

# Release to PyPI
python -m build
python -m twine upload dist/*
```

### 6. Communicate

- Post in Discord/Slack
- Tweet about fix
- Update status page if applicable

---

## Makefile Commands

Convenience commands (if you have `make`):

```bash
# Setup
make install          # Install dependencies
make install-dev      # Install dev dependencies

# Development
make test             # Run tests
make test-cov         # Run tests with coverage
make lint             # Run all linters
make format           # Auto-format code
make type-check       # Run mypy

# All quality checks
make check            # lint + type-check + test

# Clean
make clean            # Remove cache files
make clean-build      # Remove build artifacts

# Documentation
make docs             # Build docs
make docs-serve       # Serve docs locally

# Release
make build            # Build distribution
make publish          # Publish to PyPI
```

---

## Best Practices

### Commits

**Good commit messages:**
```bash
✅ feat: Add customer support scenario with tool reliability metrics
✅ fix: Resolve GPU memory leak in training loop (#123)
✅ docs: Add setup guide for Windows users
✅ refactor: Extract GPU orchestration into separate module
✅ test: Add integration tests for LangChain adapter
```

**Bad commit messages:**
```bash
❌ fixed stuff
❌ update
❌ wip
❌ asdfasdf
❌ more changes
```

### PRs

**Good PRs:**
- Focus on one thing
- Clear title and description
- Include tests
- Update docs
- Link to issues
- Small size (< 500 lines preferred)

**Bad PRs:**
- Mix multiple unrelated changes
- No description
- No tests
- Huge (1000+ lines)

### Testing

**Write tests FIRST (TDD):**
```python
# 1. Write test (fails)
def test_customer_support_scenario():
    scenario = CustomerSupportScenario()
    env = scenario.create_environment()
    assert env.state_space is not None

# 2. Implement (passes)
class CustomerSupportScenario:
    def create_environment(self):
        return Environment(...)

# 3. Refactor (still passes)
```

### Code Reviews

**Review quickly:**
- Respond within 24 hours
- Batch reviews (don't review line by line as author works)
- Provide clear, actionable feedback

**Be kind:**
- Assume good intentions
- Explain the "why" behind suggestions
- Praise good work

---

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Questions?** Ask in [GitHub Discussions](https://github.com/agentgym/agentgym/discussions)
