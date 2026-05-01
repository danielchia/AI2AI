# Finance Mandate Matching Lab

**Minimal, teachable system for evaluating deals against investor mandates using AI agents + forcing questions (Gstack methodology).**

## The Problem

Institutional capital deployment is slow:
- Investor onboarding: weeks of meetings
- Deal evaluation: 2-4 weeks of back-and-forth
- Founder feedback: vague ("doesn't fit our mandate")
- No transparency: why exactly were we rejected?

## The Solution

1. **Machine-readable mandates**: Investor criteria become JSON schemas
2. **Three AI agents**: Process, Legal, Compliance ask forcing questions
3. **Transparent decisions**: Every rejection has specific, fixable reasons
4. **AI2AI matching**: Trader AIs can adapt pitches against mandates in real-time

## Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Start server
python -m uvicorn app:app --reload

# 4. Test with example
curl http://localhost:8000/test

# 5. Visit API docs
open http://localhost:8000/docs
```

## How It Works

### Input
```json
{
  "mandate": {
    "investor_name": "TechVest Partners IV",
    "process_criteria": {
      "primary_use_of_capital": ["acquisition"],
      "check_size_usd_millions": [5, 30],
      "target_irr_percent": 25
    },
    ...
  },
  "deal": {
    "company_name": "LinkLogis",
    "process_section": {
      "use_of_capital": "acquisition",
      "check_size_usd_millions": 20,
      "projected_irr": 28
    },
    ...
  }
}
```

### Processing
```
POST /evaluate
  ├─ Process Agent: 8 forcing questions on investment fit
  ├─ Legal Agent: 8 forcing questions on contract terms
  └─ Compliance Agent: 8 forcing questions on regulatory risk
```

### Output
```json
{
  "final_decision": "FUND_IT",
  "agents": {
    "process": {"decision": "APPROVE", "passed_questions": [1,2,3,4,5,6,7,8]},
    "legal": {"decision": "APPROVE", ...},
    "compliance": {"decision": "APPROVE", ...}
  },
  "next_steps": ["Schedule investment committee", "Finalize docs"]
}
```

## Architecture

**Three files, ~1200 lines of production code:**

| File | Purpose | Lines |
|------|---------|-------|
| **mandate.py** | Pydantic schemas for mandates + deals | ~470 |
| **agents.py** | Process, Legal, Compliance agents | ~350 |
| **app.py** | FastAPI endpoint + decision engine | ~380 |

## What Are Forcing Questions?

From Garry Tan (Y Combinator): **Force uncomfortable questions early to kill bad ideas before engineering time is wasted.**

Example:
- ❌ Vague: "Does this fit our mandate?"
- ✅ Forcing: "Is hold period 3-7 years? Is check size $5-30M? Is projected IRR ≥25%?"

Answer each specifically. No hand-waving allowed.

At YC office hours, ~1/3 of projects get abandoned because they don't survive forcing questions. Same here: **specific feedback**, **pressure-test early**.

## Decision Logic

```python
if any agent REJECTS:
    → PASS (don't fund)
elif any agent says ADAPT:
    → FLAG_FOR_NEGOTIATION (terms are fixable)
else:
    → FUND_IT (all approved)
```

**Why this matters:** Founders know exactly what to fix. Investors know exactly why they passed. No ambiguity.

## Use Cases

### For Investors
- **Standardize** mandate across team (no more "I have a good feeling")
- **Accelerate** deal screening (weeks → minutes)
- **Measure** consistency (same mandate, same decisions)
- **Debug** decisions (why did we reject LinkLogis? Legal said X, Compliance said Y)

### For Founders
- **Understand** why you're rejected (not vague, specific)
- **Know** what to fix (negotiate liquidation preference, add KYC docs)
- **Self-adapt** using AI (trader AI reads mandate, suggests pitch changes)
- **Resubmit** confidently

### For Platforms
- **Auto-route** deals to matching investors (mandate-aware syndication)
- **Rank** deals by investor fit (who needs what?)
- **Measure** deal quality over time (which mandates succeed?)

## API Endpoints

### POST /evaluate
Evaluate a deal against a mandate.

**Request:**
```json
{
  "mandate": {...},
  "deal": {...}
}
```

**Response:**
```json
{
  "final_decision": "FUND_IT|FLAG_FOR_NEGOTIATION|PASS",
  "agents": {...},
  "next_steps": [...]
}
```

### GET /test
Quick test with example mandate + deal (LinkLogis vs TechVest).

### GET /health
Health check.

### GET /docs
Interactive API documentation (Swagger UI).

## Configuration

### Required
- `ANTHROPIC_API_KEY`: Your Claude API key

### Optional
- `MODEL`: Claude model (default: `claude-opus-4-6`)
- `MAX_TOKENS`: Per-agent token limit (default: `1024`)

## Understanding the Code

**Want to learn how this works?**

Read `BUILD_FROM_SCRATCH.md` for a step-by-step walkthrough explaining **why** each part exists.

**Want to modify it?**

Edit `mandate.py` to change what gets evaluated (e.g., add `dividend_requirements`).
Edit `agents.py` to change forcing questions (e.g., add "Is CEO first-time founder?").

Both are straightforward Pydantic + Claude API calls.

## Extending This

### Add More Agents
```python
# agents.py
class TaxAgent(Agent):
    def evaluate(self, mandate, deal):
        # Ask 8 tax-specific forcing questions
        ...
```

### Add Database
```python
# Store evaluations for learning
from sqlalchemy import create_engine
engine = create_engine("postgresql://...")
```

### Add UI
```python
# React dashboard to browse mandates, deals, evaluations
# (separate repo)
```

### Add Learning
```python
# Track which deals succeeded, refine forcing questions
# Use past decisions to improve agent accuracy
```

## Cost

**Per-deal evaluation:** ~$0.08 (3 agents × 1500 tokens each)

For 100 deals/month: ~$8 API costs

## Examples

See `/examples/` directory:
- `example_mandate.json` - TechVest Partners IV mandate
- `example_deal.json` - LinkLogis deal proposal
- `example_evaluation.md` - Full evaluation report

Or use `/test` endpoint for quick demo.

## License

MIT - Fork, modify, extend freely.

## Questions?

- **How do I customize mandates?** Edit `mandate.py` to add more fields
- **How do I change forcing questions?** Edit agent methods in `agents.py`
- **Can I use a different LLM?** Yes, replace `anthropic.Anthropic()` with your provider
- **What if I want to batch-evaluate 1000 deals?** Add a loop around `/evaluate` and store results in a database
- **Can agents learn from past decisions?** Yes, with fine-tuning or RAG (future enhancement)

---

**Status:** MVP - Minimal, teachable, production-ready.
**Target:** PE firms, institutional investors, deal platforms.
**Built by:** Digital Treasury.
