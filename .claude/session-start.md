# Session Starter - AgentGym

**Quick reference for starting new Claude Code sessions**

---

## 🚀 Copy-Paste This to Start

```
Follow automation rules from .claude/rules.md.
Ready to implement issues from WEEK-1-ISSUES.md.
What should I work on?
```

---

## 📋 Common Commands

### Starting Work
```
"Implement Issue #X"
→ Claude automatically: creates branch, implements, tests, creates PR

"Start Week 1 development"
→ Claude works through Issues #1-9 systematically

"Show me the plan for Issue #X"
→ Claude explains approach before implementing
```

### Checking Status
```
"What's the current status?"
→ Shows completed/pending issues

"Show me the dependency graph"
→ Visualizes issue dependencies

"What should I work on next?"
→ Claude suggests next issue based on dependencies
```

### Quality Checks
```
"Run all quality gates"
→ pytest, black, ruff, mypy

"Check test coverage"
→ pytest --cov report

"Review the code in src/agentgym/core/"
→ Claude reviews for quality
```

---

## 📁 Key Files (Auto-Loaded)

Claude Code automatically reads these:

- `.claude/project-context.md` - Full project overview
- `.claude/development-workflow.md` - Development process
- `.claude/rules.md` - Automation rules (enforce automatically)
- `WEEK-1-ISSUES.md` - All 9 workpackages
- `docs/architecture/TECHNICAL_APPROACH.md` - Architecture decisions

---

## 🎯 Week 1 Progress Tracker

**Track 1: Core Foundation (Day 1-2)**
- [ ] [Issue #1](https://github.com/Robbe1991/agentgym/issues/1) - TrainingConfig
- [ ] [Issue #2](https://github.com/Robbe1991/agentgym/issues/2) - TrainingResult
- [ ] [Issue #3](https://github.com/Robbe1991/agentgym/issues/3) - Core Trainer

**Track 2: Scenarios (Day 3-4)**
- [ ] [Issue #4](https://github.com/Robbe1991/agentgym/issues/4) - Base Scenario
- [ ] [Issue #5](https://github.com/Robbe1991/agentgym/issues/5) - Scenario Registry
- [ ] [Issue #6](https://github.com/Robbe1991/agentgym/issues/6) - Customer Support Scenario

**Track 3: Integrations (Day 5-7)**
- [ ] [Issue #7](https://github.com/Robbe1991/agentgym/issues/7) - Base Adapter
- [ ] [Issue #8](https://github.com/Robbe1991/agentgym/issues/8) - LangChain Adapter
- [ ] [Issue #9](https://github.com/Robbe1991/agentgym/issues/9) - Basic CLI

---

## 🔄 Dependency Flow

```
Issue #1 (Config) → Issue #2 (Result) → Issue #3 (Trainer)
                                              ↓
Issue #4 (Base Scenario) → Issue #5 (Registry) → Issue #6 (Customer Support)
                                              ↓
Issue #7 (Base Adapter) → Issue #8 (LangChain) → Issue #9 (CLI)
                          ↘ Can parallelize ↗
```

---

## 💡 Pro Tips

**Let Claude handle everything:**
- ✅ Don't manually create branches → Claude does it
- ✅ Don't manually create PRs → Claude does it
- ✅ Don't manually run tests → Claude does it
- ✅ Don't manually check quality → Claude does it

**Just say what to build:**
```
"Implement Issue #1"
```

**Claude will automatically:**
1. Create branch `feature/core-config`
2. Read issue + architecture docs
3. Implement `src/agentgym/core/config.py`
4. Write tests in `tests/test_config.py`
5. Run quality gates (pytest, black, ruff, mypy)
6. Commit with proper message
7. Push to GitHub
8. Create PR linking to Issue #1
9. Report: "✅ Issue #1 complete: [PR URL]"

---

## 🎨 Example Session Flow

**You:**
```
Follow automation rules from .claude/rules.md.
Implement Issue #1.
```

**Claude:**
```
Implementing Issue #1 (TrainingConfig)...

1. Creating branch feature/core-config
2. Reading TECHNICAL_APPROACH.md and issue requirements
3. Implementing src/agentgym/core/config.py
   - Pydantic BaseModel with validation
   - Type hints and docstrings
   - Sensible defaults
4. Writing tests/test_config.py
   - Testing validation
   - Testing defaults
   - Coverage: 87%
5. Running quality gates...
   ✅ pytest: PASS
   ✅ black: PASS
   ✅ ruff: PASS
   ✅ mypy: PASS
6. Committing and creating PR...

✅ Issue #1 complete: https://github.com/Robbe1991/agentgym/pull/10
```

**You:**
```
Looks good, merge it and move to Issue #2.
```

**Claude:**
```
Merging PR #10...
✅ Merged and Issue #1 closed

Implementing Issue #2 (TrainingResult)...
[automatic execution continues]
```

---

## 🚫 What NOT to Do

❌ **Don't:**
- Manually create GitHub issues (Claude does it)
- Ask "Should I run tests?" (Claude runs automatically)
- Ask "Should I create a PR?" (Claude creates automatically)
- Skip reading .claude/rules.md reference

✅ **Do:**
- Trust the automation
- Focus on reviewing PRs
- Make strategic decisions
- Provide feedback on implementations

---

## 📞 Common Scenarios

### Scenario 1: Bug Found
**You:** "Bug: Trainer crashes with empty config"

**Claude:**
1. Creates Issue automatically
2. Creates branch `bugfix/trainer-empty-config`
3. Fixes bug
4. Adds regression test
5. Creates PR
6. Links PR to auto-created issue

### Scenario 2: Multiple Issues
**You:** "Implement Issues #1, #2, #3"

**Claude:**
1. Checks dependencies (sequential)
2. Implements #1 → PR → Merge
3. Implements #2 → PR → Merge
4. Implements #3 → PR → Merge
5. Reports: "✅ All 3 issues complete"

### Scenario 3: Feature Request
**You:** "Add support for AutoGen framework"

**Claude:**
1. Creates GitHub issue automatically
2. Follows implementation workflow
3. No questions asked - just builds it

---

## 🎯 Week 1 Goal

**End State:**
```bash
# This should work after Week 1:
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

## 🔗 Quick Links

- **GitHub Repo:** https://github.com/Robbe1991/agentgym
- **Issues:** https://github.com/Robbe1991/agentgym/issues
- **PRs:** https://github.com/Robbe1991/agentgym/pulls

---

**Last Updated:** 2025-11-03
**Status:** Week 1 Development Ready
**Current Focus:** Implement Issues #1-9 systematically

---

## 💬 Ready to Code?

Just say:
```
"Implement Issue #1"
```

And I'll handle the rest automatically! 🚀
