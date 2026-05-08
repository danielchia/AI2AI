# Live Testing Guide: Trade Receivables Mandate Matching

Your trade receivables system is ready for testing with a live originator **today**.

---

## Pre-Launch Checklist

- [x] Trade receivables mandate schema created
- [x] 24 forcing questions (8 per agent) implemented
- [x] FastAPI endpoints integrated into app.py
- [x] Test script and documentation complete
- [x] All files committed to git

---

## Quick Start (5 minutes)

### 1. Install & Start Server

```bash
cd /tmp/AI2AI

# Install dependencies
pip install -r requirements_trade_receivables.txt

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Start server
python -m uvicorn app:app --reload
```

**Server runs on:** http://localhost:8000

### 2. Test the System

Open another terminal:

```bash
# Option A: Test with anonymized example (no data entry)
curl -X POST http://localhost:8000/test_trade_receivables | jq

# Option B: Interactive API docs
open http://localhost:8000/docs

# Option C: Standalone test script (validation only, no API call)
python3 test_trade_receivables.py
```

---

## Live Deal Submission (Your Originator)

### The Ask

Get your originator to provide **one representative deal** with this info:

```json
{
  "invoice_number": "INV-XXXX-XXXX",
  "company_name": "Seller Name",
  "seller_incorporation": "Singapore",
  
  "buyer_name": "Buyer Name",
  "buyer_jurisdiction": "Singapore",
  "buyer_credit_score": null,  // optional
  "buyer_relationship_months": 12,
  "buyer_payment_history": "100% on-time (12 months)",
  
  "invoice_date": "2025-09-01",
  "invoice_amount_usd": 500000,
  "due_date": "2025-11-30",
  "tenor_days": 90,
  
  "goods_services_description": "What was delivered",
  "delivery_date": "2025-09-05",
  "delivery_proof_type": "BoL + receipt",
  
  "buyer_confirmation_obtained": true,
  "buyer_disputes_history": "None",
  
  "seller_financials_summary": {
    "annual_revenue_usd": 50000000,
    "ebitda_margin_pct": 8
  },
  
  "funding_requested_percentage": 90,
  "purpose": "Working capital"
}
```

### Submit to API

```bash
# Save as deal.json, then:
curl -X POST http://localhost:8000/evaluate_trade_receivables \
  -H "Content-Type: application/json" \
  -d @deal.json | jq
```

Or use the interactive docs at http://localhost:8000/docs

### Read the Response

```json
{
  "invoice_number": "INV-...",
  "final_decision": "CONDITIONAL_APPROVE",
  "agents": {
    "process": {"decision": "APPROVE", "passed_questions": ["P1", "P2", ...]},
    "legal": {"decision": "APPROVE"},
    "credit_risk": {"decision": "CONDITIONAL", "conditions": ["Unrated buyer..."]}
  },
  "pricing_recommendations": [
    "Reduce advance from 90% to 85%",
    "Increase discount from 5.0% to 5.5%"
  ],
  "next_steps": [
    "Apply pricing adjustments",
    "Execute Master Receivables Purchase Agreement",
    "Fund deal"
  ]
}
```

---

## Expected Outcomes (Real Example)

### Example: Unrated Buyer (But Strong Payment History)

| Agent | Result | Evidence |
|-------|--------|----------|
| **Process** | ✅ APPROVE | Perfect invoice quality, proof of delivery, buyer confirmation |
| **Legal** | ✅ APPROVE | Singapore contract law, clean KYC/AML, perfected structure |
| **Credit** | ⚠️ CONDITIONAL | Unrated buyer, BUT 18 months / 100% on-time payment history |

**Final Decision:** CONDITIONAL_APPROVE  
**Adjustment:** Advance 85% (vs 90%), Discount 5.5% (vs 5.0%)  
**Rationale:** De-risk unrated buyer with tighter economics; monitor payment closely

---

## What the 24 Questions Evaluate

### Process Agent Surfaces

- ✅ Is the invoice legitimate? (Delivery proof required)
- ✅ Has buyer acknowledged it? (Confirmation required)
- ✅ Does seller have clean title? (No prior pledges)
- ✅ Any disputes or offsets? (Payment risk)

### Legal Agent Surfaces

- ✅ Can we enforce payment? (Jurisdiction & contract terms)
- ✅ Can seller legally assign it? (Authority required)
- ✅ Is it properly perfected? (UCC filing, PPSA reg, etc.)
- ✅ Any regulatory compliance gaps? (KYC/AML, sanctions)

### Credit Agent Surfaces

- ✅ Will buyer actually pay? (Credit rating, payment history)
- ✅ Can seller indemnify if buyer fails? (Financial strength)
- ✅ Are we over-concentrated? (Single buyer/seller limits)
- ✅ What if everything fails? (Expected recovery rate)

---

## Decision Rules (Simplified)

```
if ANY agent says REJECT
    → DECLINE (hard blocker)

else if ANY agent says CONDITIONAL
    → CONDITIONAL_APPROVE (adjust pricing down)
    
else if ALL agents say APPROVE
    → FUND_IT (standard terms)
```

---

## Example Deal Walkthrough

See `trade_receivables_case_study_template.md` for a complete real example with:
- Full mandate definition
- Complete deal details
- All 24 Q&A with expected answers
- Final decision logic
- Pricing adjustments applied

---

## Troubleshooting

### Server won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Check dependencies installed
python3 -c "import pydantic; import fastapi; print('✓ deps OK')"

# Try explicit port
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### API returns 400 error
- Check JSON format (valid keys?)
- Check required fields (deal.invoice_number, etc.)
- Check amount is numeric (not string "500000")

### Want to customize the mandate?
Edit `TRADE_RECEIVABLES_README.md` → copy the mandate structure → submit with your deal

---

## What Happens Next

### Today (Live Test)
1. Get one real deal from originator
2. Submit to `/evaluate_trade_receivables`
3. Review decision + conditions
4. Note which questions surface the most issues

### This Week
1. Test 3-5 more deals (anonymized)
2. Iterate on mandate criteria based on results
3. Refine forcing questions if needed
4. Document your fund's decision patterns

### Beyond
1. Build originator onboarding playbook
2. Create deal performance dashboard
3. Add Anthropic Claude integration (optional) for reasoning
4. Scale to production with proper audit trail

---

## Files to Share with Originator

1. **TRADE_RECEIVABLES_README.md** — System overview & API docs
2. **trade_receivables_case_study_template.md** — Real example (anonymized)
3. **Example deal JSON** (from section above) — Template they fill in

---

## API Documentation

Full docs at: http://localhost:8000/docs (when server is running)

Key endpoints:
- `POST /test_trade_receivables` — Instant test (no deal data needed)
- `POST /evaluate_trade_receivables` — Your deals (requires deal + mandate JSON)
- `GET /health` — Status check

---

## Questions Before Launch?

- Mandate criteria: Customize in `trade_receivables_mandate.py`
- Forcing questions: Review in `trade_receivables_agents.py` (24 Q's per agent)
- Case study: Full walkthrough in `trade_receivables_case_study_template.md`
- Integration: How API wires together in `app.py`

---

**You're ready to go. Submit your first deal today!**

The system will tell you:
- ✅ What criteria passed
- ⚠️ What needs adjustment
- ❌ What's a hard blocker

Each answer informs the next deal's structure.

Good luck!

---

*All code committed to git. Ready for production with proper audit trail + monitoring layer on top.*
