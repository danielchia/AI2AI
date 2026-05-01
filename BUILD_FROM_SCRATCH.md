# Build Finance Mandate Matching Lab From Scratch

This guide walks through the entire system step-by-step, explaining **why** each piece exists.

The core insight: **Investor mandates + deal proposals should be machine-readable JSON, evaluated by AI agents asking forcing questions (Gstack methodology). This replaces vague criteria with transparent, repeatable decisions.**

---

## The Problem We're Solving

**Current state:** Investor onboarding is slow and manual.
- Investor has vague criteria ("we like fintech, $5-30M checks, 3-7 year hold")
- Founder pitches using whatever format they want
- Lots of back-and-forth: "Does this fit?"
- No transparency: founder doesn't know exactly why they were rejected

**Our solution:** Structure everything as JSON. Let AI agents ask specific forcing questions. Replace "good fit" with measurable yes/no answers.

---

## Architecture (3 Files, ~1200 Lines)

```
mandate.py       → Define what investor wants & what founder pitches (Pydantic schemas)
agents.py        → Three agents ask forcing questions (Process, Legal, Compliance)
app.py           → FastAPI endpoint that ties it all together
requirements.txt → Minimal dependencies
```

---

## Part 1: mandate.py (Schema Definitions)

**Goal:** Structure investor mandates and deal proposals so they're computer-checkable.

### Why Schemas?

Without schemas:
- Investor: "We want good deals in fintech, reasonable terms"
- Founder: "Here's my pitch" (23 slides, unclear financial data)
- → Subjective, manual evaluation

With schemas:
- Investor JSON: `{process_criteria: {sectors: [fintech], check_size: [5,30]}, ...}`
- Founder JSON: `{process_section: {primary_sector: "fintech", check_size_usd_millions: 20}, ...}`
- → Computer-checkable: is `20` in `[5,30]`? Yes/No.

### What Goes in mandate.py?

**ProcessCriteria** - What investor wants from a deal financially:
```python
primary_use_of_capital: List[UseOfCapital]  # acquisition, growth, infrastructure?
hold_period_years: tuple                    # 3-7 years?
check_size_usd_millions: tuple              # $5-30M?
target_irr_percent: float                   # 25%+?
geography: List[str]                        # US, SG, Canada?
sectors: List[str]                          # fintech, software?
```

**LegalCriteria** - What investor requires in contract:
```python
required_governance: List[GovernanceRight]  # board seat, veto rights?
liquidation_preference: LiquidationPreference  # participating or non-participating?
anti_dilution: str                          # broad-based weighted average?
```

**ComplianceCriteria** - Regulatory/reputational requirements:
```python
allowed_jurisdictions: List[str]            # US, SG, UK?
aml_kyc_required: bool                      # Must pass KYC?
blocked_sectors: List[str]                  # No weapons, gambling, tobacco?
```

Then **DealProcess**, **DealLegal**, **DealCompliance** mirror these from the founder's side.

**Why this structure?**
- Investor fills in mandate once (JSON)
- Founder fills in deal proposal (JSON)
- Pydantic validates both → no garbage in
- Agents can read them predictably

---

## Part 2: agents.py (Three Forcing-Question Agents)

**Goal:** Replace vague evaluations with forcing questions (Gstack methodology).

### Why Three Agents?

Because investment has three distinct dimensions:
1. **Process Agent** - Does this fit the thesis? (Financial fit)
2. **Legal Agent** - Are we protected? (Contract risk)
3. **Compliance Agent** - Is there regulatory/reputational risk?

Separating them keeps decisions clear. Each agent has exactly 8 forcing questions.

### Process Agent (8 Questions)

```
Q1: Is use_of_capital approved?
Q2: Is hold_period within range?
Q3: Is check_size acceptable?
Q4: Does projected_irr meet minimum?
Q5: Are geographies allowed?
Q6: Is sector approved?
Q7: Are value drivers aligned?
Q8: Is decision timeline feasible?
```

**Why these questions?**
- They're **specific** (not "is this a good deal?")
- They're **checkable** (compare deal value to mandate value)
- They're **forcing** (forces founder to think carefully)

For each question, Claude answers YES or NO and explains why.

**Decision logic:**
- All YES → APPROVE
- Some NO but fixable → ADAPT (negotiate)
- Critical NO → REJECT

### Legal Agent & Compliance Agent

Same pattern: 8 specific forcing questions each, then APPROVE/ADAPT/REJECT.

### Why Use Claude?

We *could* write pure conditional logic: `if deal.check_size > mandate.check_size: reject()`.

But forcing questions require reasoning:
- Q: "Are value drivers aligned?" (needs understanding of both sides)
- Q: "Is non-compete duration acceptable for this founder profile?"
- Q: "Does this jurisdiction present acceptable risk?"

Claude handles the nuance. We just make sure it asks the right questions.

---

## Part 3: app.py (FastAPI Application)

**Goal:** Expose the three agents via a REST API.

### The Flow

```
POST /evaluate {mandate, deal}
  ↓
Validate with Pydantic (mandate.py)
  ↓
Run Process Agent
  ↓
Run Legal Agent
  ↓
Run Compliance Agent
  ↓
Aggregate results → make_final_decision()
  ↓
Return: FUND_IT / FLAG_FOR_NEGOTIATION / PASS
```

### make_final_decision() Logic

```python
if any agent REJECTS:
    → PASS (don't fund)
elif any agent says ADAPT:
    → FLAG_FOR_NEGOTIATION (terms are fixable)
else:
    → FUND_IT (all approved)
```

This is transparent and reproducible.

### The API

**POST /evaluate**
```json
{
  "mandate": {investor criteria},
  "deal": {founder pitch}
}
```

**Response:**
```json
{
  "deal_id": "...",
  "final_decision": "FUND_IT|FLAG_FOR_NEGOTIATION|PASS",
  "agents": {
    "process": {decision, passed_questions, failed_questions, issues},
    "legal": {...},
    "compliance": {...}
  },
  "next_steps": [...]
}
```

Founder can see exactly why they were rejected (specific failed questions) and what to fix.

---

## Part 4: How to Use It

### Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m uvicorn app:app --reload
```

Visit `http://localhost:8000/docs` for interactive API.

### Test It

```bash
# Use the /test endpoint for example mandate + deal
curl http://localhost:8000/test

# Or POST your own:
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Real Usage (Example)

**Step 1: Investor creates mandate JSON** (one-time)
```json
{
  "investor_name": "TechVest Partners IV",
  "mandate_id": "tvp4-2026",
  "process_criteria": {
    "primary_use_of_capital": ["acquisition", "growth"],
    "hold_period_years": [3, 7],
    ...
  },
  ...
}
```

**Step 2: Founder creates deal proposal JSON**
```json
{
  "deal_id": "LINKLOGIS-2026",
  "company_name": "LinkLogis",
  "process_section": {
    "use_of_capital": "acquisition",
    "hold_period_years": 4,
    ...
  },
  ...
}
```

**Step 3: Submit both to /evaluate**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"mandate": {...}, "deal": {...}}'
```

**Step 4: Get transparent feedback**
```json
{
  "final_decision": "FLAG_FOR_NEGOTIATION",
  "agents": {
    "process": {
      "decision": "APPROVE",
      "passed_questions": [1,2,3,4,5,6,7,8],
      "failed_questions": []
    },
    "legal": {
      "decision": "ADAPT",
      "failed_questions": [2],
      "issues": ["Liquidation preference: participating vs non-participating"]
    },
    ...
  },
  "next_steps": ["Negotiate liquidation preference", "Resubmit"]
}
```

---

## Why This Design?

### Minimal (1200 lines)
- One file for schemas
- One file for agents
- One file for API
- No fancy patterns, no infrastructure
- Readable in one sitting

### Teachable
- Each file has clear purpose
- Comments explain "why" not just "what"
- Forcing questions are explicit (easy to modify)
- Decision logic is transparent (no black boxes)

### Reproducible
- Exact same mandate + deal → exact same evaluation
- All logic in code (not in someone's head)
- Easy to benchmark/improve

### Extensible
- Add more agents (Financial, Tax, etc)
- Modify forcing questions per fund
- Add database persistence
- Build dashboard on top

---

## Key Design Decisions

### Why Forcing Questions?

Because they **pressure-test ideas early**. At YC office hours, ~1/3 of projects get abandoned because they don't survive scrutiny. Same applies to deals.

Instead of "Does this fit?" → "Is hold period 3-7 years?" (yes/no, no ambiguity)

### Why Three Agents?

Investment has three independent risk dimensions. Separating them:
- Makes decisions transparent ("Legal said no")
- Allows different weight per investor ("We're flexible on legal, strict on compliance")
- Makes the system debuggable ("Why did it fail? Check Legal Agent feedback")

### Why JSON Mandates?

Because investor criteria should be:
- **Queryable**: "How many deals fit my mandate?"
- **Comparable**: "Do two funds have similar mandates?"
- **Versionable**: "Did our mandate change in Q3?"
- **Machine-readable**: "AI can read it and self-adapt"

---

## Next Steps

### To Extend This:

1. **Add database**: Store mandates, deals, evaluations
2. **Add authentication**: API keys for investor access
3. **Add UI**: Dashboard to manage mandates, browse deals
4. **Add more agents**: Financial, Tax, ESG deep-dive
5. **Add learning**: Track which deals succeeded, refine questions
6. **Add concurrency**: Run agents in parallel instead of sequentially

### To Deploy:

```bash
# Docker
docker build -t fmm .
docker run -p 8000:8000 fmm

# Or serverless
pip install zappa
zappa deploy production
```

---

## Summary

**Three files, ~1200 lines, complete system:**

- **Schemas** define what investor wants + what founder pitches
- **Agents** ask forcing questions (transparent, repeatable)
- **API** accepts mandate + deal, returns decision + rationale

Result: Institutional investors can onboard in minutes, founders get transparent feedback, capital deployment accelerates from weeks to seconds.

The insight is **Gstack forcing questions + machine-readable mandates = AI2AI capital matching**.

---

**To understand the code deeply, read in this order:**
1. mandate.py (understand the data structures)
2. agents.py (understand how agents ask questions)
3. app.py (understand how it all ties together)

Each file has inline comments explaining design decisions.
