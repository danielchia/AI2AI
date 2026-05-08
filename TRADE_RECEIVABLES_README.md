# Trade Receivables Mandate Matching Module

**AI-driven mandate matching for short-term trade receivables financing**

This module extends the core AI2AI system with specialized evaluation for trade receivables (invoices, receivables purchase agreements, and trade finance deals). It uses **24 forcing questions** across 3 agents (Process, Legal, Credit Risk) to rapidly surface deal-breaker issues before funding.

Built from real experience with LinkLogis/ChemTank trade receivables transactions in Singapore.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_trade_receivables.txt
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run the Server

```bash
python -m uvicorn app:app --reload
```

### 4. Test the System

**Option A: Automated test script**
```bash
python3 test_trade_receivables.py
```

**Option B: API test endpoint**
```bash
curl -X POST http://localhost:8000/test_trade_receivables
```

**Option C: Interactive API docs**
```
http://localhost:8000/docs
```

---

## System Architecture

### Files

| File | Purpose |
|------|---------|
| `trade_receivables_mandate.py` | Pydantic schemas for mandate & deal |
| `trade_receivables_agents.py` | 24 forcing questions + agent logic |
| `trade_receivables_case_study_template.md` | Real example with expected answers |
| `test_trade_receivables.py` | Standalone test script |
| `app.py` | FastAPI integration (updated) |

### The 24 Forcing Questions

**Process Agent (P1-P8):** Invoice quality & deal structure
- P1: Is tenor within 90-120 days?
- P2: Has buyer confirmed invoice in writing?
- P3: What is buyer's payment history?
- P4: Any disputes or payment offsets?
- P5: Delivery proof available (BoL, receipt)?
- P6: How long seller-buyer relationship?
- P7: Title clear & unencumbered?
- P8: Are financing economics appropriate?

**Legal Agent (L1-L8):** Enforceability & compliance
- L1: Is invoice & contract enforceable?
- L2: Does seller have authority to assign?
- L3: Is security interest perfected?
- L4: Any payment restrictions on buyer?
- L5: Is governing law favorable?
- L6: KYC/AML complete?
- L7: Pending litigation risk?
- L8: Collection rights robust?

**Credit Risk Agent (C1-C8):** Financial strength & portfolio risk
- C1: What is buyer credit quality?
- C2: Buyer industry & market position?
- C3: Seller financial strength?
- C4: Seller credit history clean?
- C5: Portfolio concentration within limits?
- C6: Bankruptcy protection adequate?
- C7: Expected loss-given-default (LGD)?
- C8: Macro headwinds?

---

## API Endpoints

### POST /evaluate_trade_receivables

Evaluate a trade receivable deal against a mandate.

**Request:**
```json
{
  "mandate": {
    "mandate_name": "DTF Trade Receivables",
    "fund_manager": "Digital Treasury Fund Pte. Ltd.",
    "investor_jurisdiction": "Singapore",
    "buyer_quality": {...},
    "seller_quality": {...},
    "invoice_criteria": {...},
    "financing_terms": {...}
  },
  "deal": {
    "invoice_number": "INV-2025-0901",
    "company_name": "Seller Name",
    "buyer_name": "Buyer Name",
    "invoice_amount_usd": 500000,
    "tenor_days": 90,
    "buyer_confirmation_obtained": true,
    ...
  }
}
```

**Response:**
```json
{
  "invoice_number": "INV-2025-0901",
  "seller": "Seller Name",
  "buyer": "Buyer Name",
  "final_decision": "CONDITIONAL_APPROVE",
  "final_reasoning": "Conditional approval with pricing/terms adjustment",
  "agents": {
    "process": {"decision": "APPROVE", "passed_questions": [...], ...},
    "legal": {"decision": "APPROVE", ...},
    "credit_risk": {"decision": "CONDITIONAL", "conditions": [...]}
  },
  "conditions": ["Unrated buyer: reduce advance to 85%, increase discount to 5.5%"],
  "pricing_recommendations": ["Advance: 85%", "Discount: 5.5% p.a."],
  "next_steps": ["Apply pricing adjustments", "Execute Master Receivables Purchase Agreement", "Fund deal"]
}
```

### POST /test_trade_receivables

Quick test with anonymized example deal (no request body needed).

### GET /health

Health check.

---

## Mandate Schema

### TradeReceivablesMandate

```python
mandate_name: str
fund_manager: str
investor_jurisdiction: str

# Quality thresholds
buyer_quality: ReceiverQuality
  - credit_rating: Optional[str]
  - years_in_business: int
  - payment_history_score: int (0-100)
  - regulatory_status: str
  - jurisdiction: str
  - no_active_disputes: bool
  - financial_stability: Literal["strong", "stable", "at_risk", "distressed"]

seller_quality: SellerQuality
  - years_in_business: int
  - good_standing: bool
  - not_in_insolvency: bool
  - no_material_litigation: bool
  - regulatory_compliance: Literal["fully_compliant", "substantially_compliant", "at_risk"]

# Invoice eligibility
invoice_criteria: InvoiceCharacteristics
  - tenor_days_min: int (typically 90)
  - tenor_days_max: int (typically 120)
  - invoice_amount_min_usd: Optional[float]
  - invoice_amount_max_usd: Optional[float]
  - goods_services_delivered: bool
  - buyer_confirmation_required: bool
  - no_prior_payment: bool

# Financing terms
financing_terms: FinancingTerms
  - advance_percentage: float (typically 90.0)
  - holdback_percentage: float (typically 10.0)
  - discount_rate_percent_pa: float (typically 5.0)
  - buffer_period_days: int (typically 30)
  - recourse_type: Literal["non_recourse", "limited_recourse", "full_recourse"]

# Portfolio limits
max_concentration_single_buyer_pct: Optional[float] (typically 10%)
max_concentration_single_seller_pct: Optional[float] (typically 15%)
allowed_industries: Optional[List[str]]
excluded_jurisdictions: Optional[List[str]]
```

---

## Deal Schema

### Deal

```python
company_name: str  # Seller/originator name
seller_incorporation: str  # Jurisdiction + entity type

buyer_name: str  # Account debtor
buyer_jurisdiction: str
buyer_credit_score: Optional[int]
buyer_relationship_months: Optional[int]
buyer_payment_history: Optional[str]

invoice_number: str
invoice_date: str (YYYY-MM-DD)
invoice_amount_usd: float
due_date: str (YYYY-MM-DD)
tenor_days: int

goods_services_description: str
delivery_date: str
delivery_proof_type: str (e.g., "BoL", "receipt", "signed contract")

buyer_confirmation_obtained: bool
buyer_disputes_history: Optional[str]

seller_financials_summary: Optional[Dict]
funding_requested_percentage: float (typically 90.0)
purpose: str
```

---

## Decision Logic

### Final Recommendation Matrix

| Process | Legal | Credit | Final Decision |
|---------|-------|--------|-----------------|
| REJECT | Any | Any | **DECLINE** |
| Any | REJECT | Any | **DECLINE** |
| Any | Any | REJECT | **DECLINE** |
| CONDITIONAL | Any | Any | **CONDITIONAL_APPROVE** |
| Any | CONDITIONAL | Any | **CONDITIONAL_APPROVE** |
| Any | Any | CONDITIONAL | **CONDITIONAL_APPROVE** |
| APPROVE | APPROVE | APPROVE | **FUND_IT** |

### Conditional Approval Pricing Adjustments

If **Credit Agent** flags unrated buyer or concentration issues:
- Reduce advance from 90% → 85%
- Increase discount from 5.0% → 5.5% p.a.
- May add personal guarantee requirement
- May require credit insurance

---

## Real-World Example

### The Deal

**Seller:** Anonymized chemical commodities trader (Singapore, 8+ years, profitable)  
**Buyer:** Anonymized materials manufacturer (Singapore, 18-month relationship, 100% on-time payment)  
**Invoice:** USD 500K for bulk chemicals, 90-day tenor, delivered, buyer confirmed

### Expected Evaluation

| Agent | Key Finding | Decision |
|-------|------------|----------|
| **Process** | All invoice quality criteria met; clear title; delivery proof; buyer confirmation | ✅ APPROVE |
| **Legal** | Enforceable contract; Singapore law favorable; KYC/AML complete; perfected structure | ✅ APPROVE |
| **Credit** | Unrated buyer (medium risk), but 18-month 100% payment history; seller profitable | ⚠️ CONDITIONAL |

**Final:** CONDITIONAL_APPROVE with pricing adjustment (85% advance, 5.5% discount)

See `trade_receivables_case_study_template.md` for full walk-through with all 24 Q&A.

---

## Integration with Existing System

The trade receivables module extends `app.py` with:

1. **New imports:** `trade_receivables_mandate`, `trade_receivables_agents`
2. **New agent instances:** `tr_process_agent`, `tr_legal_agent`, `tr_credit_agent`
3. **New endpoint:** `POST /evaluate_trade_receivables`
4. **New test endpoint:** `POST /test_trade_receivables`
5. **New decision function:** `make_tr_final_decision()`

The original `/evaluate` endpoint for investment mandates remains unchanged.

---

## Testing with Live Originators

### Step 1: Validate Mandate (Optional)

If your originator has specific criteria, customize the mandate JSON and test against `/test_trade_receivables` first.

### Step 2: Submit Real Deal

```bash
curl -X POST http://localhost:8000/evaluate_trade_receivables \
  -H "Content-Type: application/json" \
  -d '{
    "mandate": {...},
    "deal": {
      "invoice_number": "YOUR_REAL_INVOICE",
      "company_name": "YOUR_SELLER",
      "buyer_name": "YOUR_BUYER",
      "invoice_amount_usd": 1000000,
      "tenor_days": 90,
      ...
    }
  }'
```

### Step 3: Review Result

- If **FUND_IT**: Execute Master Receivables Purchase Agreement, fund at 90% advance
- If **CONDITIONAL_APPROVE**: Apply pricing adjustments, then execute agreement
- If **DECLINE**: Share blocking agent feedback; address issues and resubmit

### Step 4: Monitor Payment

Track buyer payment against due date + buffer period (30 days). Log results for future deals with this buyer.

---

## Common Issues & Troubleshooting

### "Buyer is unrated"
→ This triggers Credit Agent CONDITIONAL flag. Mitigate by:
- Requesting bank references or credit report
- Reviewing 12+ months of payment history
- Reducing advance percentage (90% → 85%)
- Increasing discount rate (5.0% → 5.5%)

### "No buyer confirmation"
→ Blocker. Cannot fund without written buyer acknowledgment of invoice validity.
→ Request from seller immediately.

### "Title defect / prior pledge"
→ Hard blocker. Requires seller indemnity + title insurance.

### "Concentration already at 10%"
→ Cannot add more from this buyer without portfolio rebalancing.

### "Seller in financial distress"
→ Increases indemnity risk. May require cash collateral or reduced exposure.

---

## File Structure

```
AI2AI/
├── app.py                                  (FastAPI app - UPDATED)
├── mandate.py                              (Original investment mandate schema)
├── agents.py                               (Original agents)
├── trade_receivables_mandate.py            (NEW - Receivables schemas)
├── trade_receivables_agents.py             (NEW - 24 forcing questions + agents)
├── trade_receivables_case_study_template.md (NEW - Real example walkthrough)
├── test_trade_receivables.py               (NEW - Test script)
├── requirements.txt                        (Original deps)
├── requirements_trade_receivables.txt      (NEW - Additional deps)
├── TRADE_RECEIVABLES_README.md             (This file)
└── BUILD_FROM_SCRATCH.md                   (Original docs)
```

---

## Next Steps

1. **Test locally** with `test_trade_receivables.py` or API endpoints
2. **Customize mandate** for your fund's specific criteria
3. **Submit real deals** from your originator
4. **Iterate on questions** based on feedback (which Q's matter most?)
5. **Add Anthropic Claude integration** to generate agent reasoning (optional)
6. **Build deal dashboard** to track portfolio concentration, payment status, etc.

---

## License

Same as parent AI2AI project.

---

## Support

For issues or questions:
- Review `trade_receivables_case_study_template.md` for real example answers
- Check agent question logic in `trade_receivables_agents.py`
- Validate deal schema against `trade_receivables_mandate.py` Pydantic models

---

*Built from real LinkLogis/ChemTank trade receivables experience, anonymized to respect confidentiality.*
