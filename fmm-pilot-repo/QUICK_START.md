# Quick Start: Finance Mandate Matching Lab Pilot

Get a working evaluation system running in 30 minutes.

---

## 5-Minute Overview

**What is this?**
Three AI agents (Process, Legal, Compliance) evaluate deals against investor mandates using Gstack forcing questions. No more vague criteria—every decision is transparent and repeatable.

**Why it works:**
- **Mandates as JSON:** Remove ambiguity. Store investor criteria in machine-readable format.
- **Forcing Questions:** Each agent asks 7-8 specific, checkable questions (not subjective opinions).
- **Automated Screening:** Evaluate 50 deals/hour instead of 1-2 manually.
- **Transparent Feedback:** Deals get specific reasons for approval/rejection/negotiation.

**Example flow:**
```
Deal submitted → Process Agent (does it fit thesis?) 
             → Legal Agent (are terms acceptable?)
             → Compliance Agent (any regulatory red flags?)
             → Final decision: FUND IT / NEGOTIATE / PASS
```

---

## 15-Minute Setup (Local)

### Prerequisites
- Python 3.11+
- Anthropic API key (free tier works)
- ~200MB disk space

### Steps

1. **Clone/download this repo**
   ```bash
   cd fmm-pilot-repo
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   *No requirements.txt yet? Use:*
   ```bash
   pip install fastapi uvicorn pydantic anthropic python-dotenv
   ```

4. **Set up API key**
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
   ```

5. **Start the server**
   ```bash
   python -m uvicorn backend.app:app --reload
   ```

6. **Test with an example**
   ```bash
   curl -X POST http://localhost:8000/evaluate \
     -H "Content-Type: application/json" \
     -d '{
       "mandate": {
         "investor": "TechVest Partners IV",
         "process_criteria": {
           "primary_use_of_capital": ["acquisition"],
           "hold_period_years": [3, 7],
           "check_size_usd_millions": [5, 30],
           "target_irr_percent": 25
         }
       },
       "deal": {
         "deal_id": "DEAL-2026-0001",
         "company_name": "Example Inc",
         "process_section": {
           "use_of_capital": "acquisition",
           "hold_period_years": 4,
           "check_size_usd_millions": 20,
           "projected_irr": 28
         }
       }
     }'
   ```

---

## Understanding the Output

**Success response:**
```json
{
  "deal_id": "DEAL-2026-0001",
  "final_decision": "FUND_IT",
  "agents": {
    "process": {
      "decision": "APPROVE",
      "passed_questions": [1, 2, 3, 4, 5, 6, 7, 8],
      "issues": []
    },
    "legal": {
      "decision": "APPROVE",
      "issues": []
    },
    "compliance": {
      "decision": "APPROVE",
      "issues": []
    }
  },
  "next_steps": ["Schedule investment committee", "Finalize docs"]
}
```

**Decision types:**
- **FUND_IT** — All agents approved. Ready for IC meeting.
- **FLAG_FOR_NEGOTIATION** — Minor issues fixable (e.g., term sheet changes).
- **PASS** — Hard blockers. Deal doesn't fit mandate.

---

## Using the Examples

**Review a mandate:**
```bash
cat examples/mandates/example_pe_fund_iv.json
```

**Review a deal proposal:**
```bash
cat examples/deals/deal_linklogis_trade_receivables.json
```

**See an evaluation result:**
```bash
cat examples/evaluations/example_evaluation_approved.md
```

**Copy and customize:**
```bash
# Create your own mandate
cp examples/mandates/example_pe_fund_iv.json my_mandate.json
# Edit it
nano my_mandate.json
```

---

## Running Your First Evaluation

### Option A: Using the API (Programmatic)

**Create a Python script `test_eval.py`:**
```python
import requests
import json

mandate = {
    "investor": "My Fund",
    "mandate_id": "mf-2024",
    "process_criteria": {
        "primary_use_of_capital": ["growth"],
        "hold_period_years": [3, 5],
        "check_size_usd_millions": [2, 10],
        "target_irr_percent": 20,
        "geography": ["US"],
        "sectors": ["software"]
    },
    "legal_criteria": {
        "required_governance": ["board_seat"],
        "liquidation_preference": "non_participating"
    },
    "compliance_criteria": {
        "allowed_jurisdictions": ["US"],
        "aml_kyc_required": True
    }
}

deal = {
    "deal_id": "TEST-001",
    "company_name": "StartupXYZ",
    "process_section": {
        "use_of_capital": "growth",
        "hold_period_years": 4,
        "check_size_usd_millions": 5,
        "projected_irr": 22,
        "geographies": ["US"],
        "primary_sector": "software"
    },
    "legal_section": {
        "governance_rights": ["board_seat"],
        "liquidation_preference": "non_participating"
    },
    "compliance_section": {
        "jurisdictions": [{"country": "US", "risk_level": "low"}],
        "aml_kyc_status": "complete",
        "sanctions_screening_result": "clean"
    }
}

response = requests.post(
    "http://localhost:8000/evaluate",
    json={"mandate": mandate, "deal": deal}
)

print(json.dumps(response.json(), indent=2))
```

**Run it:**
```bash
python test_eval.py
```

### Option B: Using curl (Command Line)

```bash
# Evaluate using example mandate and deal
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d "$(cat examples/deals/deal_linklogis_trade_receivables.json | python3 -c 'import sys, json; \
    mandate = json.load(open("examples/mandates/example_pe_fund_iv.json")); \
    deal = json.load(sys.stdin); \
    print(json.dumps({"mandate": mandate, "deal": deal}))')"
```

---

## Next Steps

1. **Read the docs:**
   - [`README.md`](./README.md) — Full overview
   - [`GSTACK_QUESTIONS.md`](./GSTACK_QUESTIONS.md) — All forcing questions
   - [`IMPLEMENTATION.md`](./IMPLEMENTATION.md) — How to build this

2. **Customize:**
   - Edit `examples/mandates/example_pe_fund_iv.json` with your criteria
   - Create your own mandates for different fund types
   - Test against your deal flow

3. **Deploy:**
   - Option 1: Heroku (1 click, see IMPLEMENTATION.md)
   - Option 2: Railway (via Docker)
   - Option 3: AWS Lambda (serverless)

4. **Integrate:**
   - Connect to your deal flow (email integration, webhook, etc.)
   - Add user authentication
   - Build a dashboard to browse deals

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install fastapi uvicorn
```

**"No ANTHROPIC_API_KEY found"**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**"Connection refused on localhost:8000"**
Make sure the server is running:
```bash
python -m uvicorn backend.app:app --reload
```

---

## Common Questions

**Q: Can I use this with my own LLM?**
A: Yes! The agents are just Claude API calls. Replace with OpenAI, Mixtral, etc.

**Q: How do I add more mandates?**
A: Copy `examples/mandates/example_pe_fund_iv.json`, edit, and test.

**Q: Can the agents learn from past decisions?**
A: Future enhancement—add fine-tuning or RAG to improve over time.

**Q: What's the cost to evaluate 1000 deals?**
A: ~$80 (at current Claude pricing). Cheaper with Sonnet model.

---

## Getting Help

- Check `GSTACK_QUESTIONS.md` if decisions seem off
- Review example evaluation in `examples/evaluations/`
- Read agent implementation in `IMPLEMENTATION.md`
- Modify forcing questions to fit your fund's unique criteria

---

**You're ready to go. Start the server and make your first evaluation!**

```bash
python -m uvicorn backend.app:app --reload
```

Then visit `http://localhost:8000/docs` for interactive API documentation.
