# AgentEval - Open Source Agent Quality Benchmarking Tool

## 🎯 Strategic Purpose

**Why We're Building This:**
1. ✅ **Solves Real Pain** - Community struggles with measuring agent quality
2. ✅ **Builds Credibility** - Shows we understand the problem deeply
3. ✅ **Demonstrates Expertise** - Showcases RL/evaluation knowledge
4. ✅ **Open Source Goodwill** - Free tool = community love
5. ✅ **Leads to AgentGym** - "If you want to IMPROVE these scores, check out AgentGym"

**What It's NOT:**
- ❌ Not a sales pitch
- ❌ Not AgentGym (it's separate, useful on its own)
- ❌ Not complex/academic (keep it simple!)

---

## 📦 What AgentEval Does

**Tagline:** "Know if your agent actually got better"

**Core Function:**
Benchmark your AI agent's performance across common failure modes and quality dimensions. Get a simple report card that shows exactly where your agent needs improvement.

**Use Cases:**
1. **Before/After Comparison** - Did my prompt change help? Did fine-tuning work?
2. **Regression Testing** - Is my new version better than v1?
3. **Failure Analysis** - Where exactly does my agent suck?
4. **Production Monitoring** - Track quality over time

---

## 🏗️ Technical Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                      AgentEval                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────┐                │
│  │ Your Agent   │─────▶│ Test Suite   │                │
│  │ (LangChain/  │      │ (Scenarios)  │                │
│  │  LangGraph)  │      └──────────────┘                │
│  └──────────────┘             │                          │
│                                │                          │
│                                ▼                          │
│                      ┌──────────────┐                    │
│                      │  Evaluators  │                    │
│                      │  (Metrics)   │                    │
│                      └──────────────┘                    │
│                                │                          │
│                                ▼                          │
│                      ┌──────────────┐                    │
│                      │  Report Card │                    │
│                      │  (Pretty UI) │                    │
│                      └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Test Suite Runner**
```python
from agenteval import AgentEvaluator

evaluator = AgentEvaluator(
    agent=your_agent,  # LangChain/LangGraph agent
    test_scenarios="default"  # or custom scenarios
)

results = evaluator.run()
print(results.report_card())  # Beautiful terminal output
```

#### 2. **Default Test Scenarios** (5 categories)

**A. Task Success Rate**
- Can the agent complete its intended task?
- 20 test cases per common use case:
  - Customer support Q&A
  - Data extraction
  - Multi-step reasoning
  - Tool usage
  - Code generation

**B. Tool Calling Quality**
- Does agent call right tools?
- Does it avoid unnecessary tool calls?
- Proper argument formatting?

**C. Response Quality**
- Relevance (on-topic?)
- Completeness (answered fully?)
- Accuracy (factually correct?)
- Conciseness (not rambling?)

**D. Failure Modes**
- Does it hallucinate?
- Does it get stuck in loops?
- Does it refuse valid requests?
- Does it leak system prompts?

**E. Performance**
- Average response time
- Token usage
- Cost per query
- Memory footprint

#### 3. **Evaluators** (How we score)

**Auto-Evaluators:**
- LLM-as-judge (GPT-4 judges responses)
- Pattern matching (detect loops, errors)
- Semantic similarity (expected vs actual)
- Tool call analysis (parse agent traces)

**Human-in-Loop Option:**
- CLI interface to label results
- Export to CSV for team review

#### 4. **Report Card Output**

**Terminal Output:**
```
╔══════════════════════════════════════════════════════════╗
║              AgentEval Report Card                       ║
║              Agent: customer-support-v2                  ║
║              Date: 2025-01-15                            ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📊 Overall Score: 73/100  (🟡 Needs Improvement)       ║
║                                                          ║
║  ✅ Task Success Rate      82%  ████████░░  [16/20]    ║
║  ⚠️  Tool Calling Quality   65%  ██████░░░░  [13/20]    ║
║  ✅ Response Quality        78%  ███████░░░  [15.6/20]  ║
║  ❌ Failure Modes           60%  ██████░░░░  [12/20]    ║
║  ✅ Performance            88%  ████████░░  [17.6/20]   ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  🔍 Key Issues Detected:                                 ║
║                                                          ║
║  1. Tool Call Loops (8 instances)                       ║
║     → Agent called same tool 3+ times with same args    ║
║                                                          ║
║  2. Hallucination in 15% of responses                   ║
║     → Made up product IDs, dates without verification   ║
║                                                          ║
║  3. Slow response time on complex queries               ║
║     → Avg 12.3s (target: <5s)                           ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  💡 Recommendations:                                     ║
║                                                          ║
║  → Consider adding tool call validation logic           ║
║  → Implement retrieval for fact verification            ║
║  → Optimize prompt to reduce reasoning steps            ║
║                                                          ║
║  📚 Learn more: https://agenteval.dev/docs/loops        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

💾 Full report saved to: ./agenteval_report_2025-01-15.json
📊 View in browser: agenteval serve ./agenteval_report_2025-01-15.json
```

**JSON Export:**
```json
{
  "agent_name": "customer-support-v2",
  "timestamp": "2025-01-15T14:30:00Z",
  "overall_score": 73,
  "categories": {
    "task_success": {
      "score": 82,
      "passed": 16,
      "total": 20,
      "details": [...]
    },
    "tool_calling": {
      "score": 65,
      "issues": [
        {
          "type": "loop",
          "count": 8,
          "example": "..."
        }
      ]
    }
  },
  "recommendations": [...]
}
```

**Web Dashboard:**
```bash
agenteval serve report.json
# Opens localhost:8080 with interactive charts
```

---

## 🛠️ Implementation Plan

### Phase 1: MVP (Week 1, Days 1-3)

**Core Features:**
- ✅ Simple test runner
- ✅ 5 default test scenarios (20 cases total)
- ✅ LLM-as-judge evaluator
- ✅ Basic report card (terminal output)
- ✅ LangChain integration

**Tech Stack:**
```
- Python 3.9+
- LangChain (compatibility)
- OpenAI API (for LLM-as-judge)
- Rich (terminal UI)
- Click (CLI)
```

**Files Structure:**
```
agenteval/
├── __init__.py
├── evaluator.py       # Main AgentEvaluator class
├── scenarios.py       # Default test scenarios
├── metrics.py         # Scoring functions
├── report.py          # Report card generation
└── cli.py             # Command-line interface

tests/
├── test_evaluator.py
└── fixtures/

examples/
├── langchain_example.py
├── langgraph_example.py
└── custom_scenarios.py

README.md
setup.py
pyproject.toml
```

### Phase 2: Polish (Week 1, Days 4-5)

**Add:**
- ✅ GitHub repo with good README
- ✅ pip install agenteval
- ✅ 3 working examples
- ✅ Documentation site (simple)
- ✅ Tests (pytest)

### Phase 3: Community Launch (Week 1, Day 6-7)

**Launch Sequence:**
1. GitHub repo public
2. PyPI package published
3. #i-made-this post in LangChain Slack
4. Twitter announcement
5. Dev.to tutorial post

---

## 📝 Code Snippets (What It Looks Like)

### Basic Usage

```python
from langchain.agents import create_react_agent
from agenteval import AgentEvaluator

# Your existing agent
agent = create_react_agent(...)

# Evaluate it
evaluator = AgentEvaluator(agent)
results = evaluator.run()

# See report
print(results.report_card())

# Compare versions
v1_results = evaluator.run(agent_v1)
v2_results = evaluator.run(agent_v2)

if v2_results.overall_score > v1_results.overall_score:
    print("✅ New version is better!")
else:
    print("❌ Regression detected!")
```

### Custom Test Scenarios

```python
from agenteval import Scenario, AgentEvaluator

custom_scenarios = [
    Scenario(
        name="Product Question",
        input="What's the price of SKU-12345?",
        expected_behavior={
            "must_call_tool": "get_product_info",
            "must_include": "price",
            "must_not_hallucinate": True
        }
    ),
    # ... more scenarios
]

evaluator = AgentEvaluator(
    agent=my_agent,
    test_scenarios=custom_scenarios
)
```

### Integration with CI/CD

```python
# tests/test_agent_quality.py
import pytest
from agenteval import AgentEvaluator

def test_agent_quality_threshold():
    """Fail CI if agent quality drops below 70%"""
    evaluator = AgentEvaluator(production_agent)
    results = evaluator.run()

    assert results.overall_score >= 70, \
        f"Agent quality dropped to {results.overall_score}%"
```

---

## 🎨 README.md Preview (What Community Sees)

```markdown
# AgentEval

**Know if your agent actually got better.**

Simple, open-source benchmarking for AI agents built with LangChain, LangGraph, or any framework.

## Why AgentEval?

- ✅ Measure agent quality objectively
- ✅ Catch regressions before production
- ✅ Compare prompt/model changes
- ✅ Works with any agent framework
- ✅ Takes 5 minutes to set up

## Quick Start

pip install agenteval

from agenteval import AgentEvaluator

evaluator = AgentEvaluator(your_agent)
results = evaluator.run()
print(results.report_card())


## What It Tests

1. **Task Success** - Does your agent complete its job?
2. **Tool Usage** - Efficient, correct tool calls?
3. **Response Quality** - Accurate, relevant, complete?
4. **Failure Modes** - Loops, hallucinations, errors?
5. **Performance** - Speed, cost, reliability?

## Example Output

[Screenshot of pretty terminal report card]

## Use Cases

- **Before/After** - Did my changes improve quality?
- **CI/CD** - Automated regression testing
- **Production Monitoring** - Track quality over time
- **Team Alignment** - Objective quality metrics

## Learn More

- [Full Documentation](https://agenteval.dev)
- [Examples](./examples)
- [Custom Scenarios](https://agenteval.dev/docs/custom)

## Contributing

We'd love your help! See [CONTRIBUTING.md](./CONTRIBUTING.md)

## Built With ❤️

Created by the team building better agent training tools.
Check out [AgentGym](https://agentgym.dev) for systematic agent improvement.

## License

MIT
```

---

## 📊 Success Metrics

**Week 1 Goals:**
- ✅ 50+ GitHub stars
- ✅ 10+ people try it
- ✅ 3-5 positive comments in #i-made-this
- ✅ "This is useful" sentiment

**Week 2 Goals:**
- ✅ 100+ stars
- ✅ 2-3 community contributions (issues/PRs)
- ✅ Mentioned in 1-2 external posts/tweets
- ✅ Credibility established → Time to send DMs!

---

## 💡 Why This Works

### The Psychology

**Community Sees:**
1. "This person understands our problems"
2. "They're giving away value for free"
3. "They're technical (real code, not marketing)"
4. "They're part of our community now"

**Result:**
- When you DM them later: "Oh, you built AgentEval! I saw that in Slack, cool tool!"
- Response rate jumps from 10% → 30-40%
- Quality of conversations much higher (they respect you)

### The Positioning

**AgentEval → AgentGym Connection (Subtle, Not Pushy):**

In README:
> "AgentEval tells you WHAT to improve. If you want to know HOW to improve it systematically, check out AgentGym - our RL training platform."

In #i-made-this post:
> "Built this while working on RL-based agent training. Realized measuring quality was Step 1 before improving it. Hope it helps!"

**Not selling, just connecting the dots naturally.**

---

## 🚀 Implementation Timeline

### Week 1 (Build Week)

**Monday-Tuesday:**
- Core evaluator engine
- Default test scenarios
- Terminal report card

**Wednesday-Thursday:**
- LangChain/LangGraph examples
- CLI polish
- Documentation

**Friday:**
- GitHub repo setup
- PyPI package
- README polish

**Saturday-Sunday:**
- Final testing
- Launch prep (screenshots, GIFs)

### Week 2 (Launch & Credibility Week)

**Monday:**
- 🚀 Launch! Post in #i-made-this
- Tweet announcement
- Dev.to tutorial

**Tuesday-Wednesday:**
- Respond to all feedback
- Fix any bugs
- Answer questions in Slack

**Thursday-Friday:**
- NOW send DMs (with credibility!)
- Reference your tool naturally
- Book interviews

---

## 🎯 The DM Difference (Before vs After)

### ❌ BEFORE (Cold DM - 10% response rate):

> "Hey! Saw your project. I'm researching agent training. Would you be up for a 20-min chat?"

**Response:** *crickets* or "I'm busy, sorry"

### ✅ AFTER (With Credibility - 35% response rate):

> "Hey! Saw your AgentHub post. I built AgentEval (the agent benchmarking tool in #i-made-this last week) and noticed similar quality challenges. Would love to compare notes on agent improvement workflows - 20 mins?"

**Response:** "Oh yeah I saw AgentEval! Would love to chat, here's my calendar..."

**The difference:** You're now "that helpful person" not "random stranger asking for favors"

---

## ❓ FAQ

**Q: Does AgentEval need to be perfect?**
A: No! It needs to be USEFUL. MVP is fine. Community values practical over polished.

**Q: What if someone finds bugs?**
A: GREAT! Shows it's real, being used. Fix quickly, thank them publicly.

**Q: Should we mention AgentGym in AgentEval?**
A: Yes, but SUBTLY. "Check out X for more" not "Buy my product!"

**Q: How much time to build this?**
A: 20-30 hours for MVP. 3-4 full days if focused.

**Q: Can we hire someone to help?**
A: Yes! Find Python dev on Upwork for $500-1K to speed it up.

---

## 🎁 The Payoff

**After 2 Weeks:**
- ✅ You're a known, helpful community member
- ✅ People recognize your name in Slack
- ✅ DM response rates 3-4x higher
- ✅ Interview quality much better (they trust you)
- ✅ Foundation laid for AgentGym launch
- ✅ Open source credibility = "we're not just selling"

**vs Cold DMs:**
- ❌ Unknown stranger
- ❌ Low response rates
- ❌ Defensive conversations
- ❌ No foundation for future

**2 weeks of patience = 6 months of benefits** 🎯

---

Ready to build it? I can help you:
1. Write the actual Python code
2. Create the GitHub repo structure
3. Write the launch post for #i-made-this
4. Plan the Week 1 build schedule

What do you want to tackle first?
