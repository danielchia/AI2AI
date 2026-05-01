# Finance Mandate Matching Lab - Gstack Pilot

A reference implementation for standardizing how institutional investor mandates are matched to deal proposals using three specialized evaluation agents.

## The Problem

Institutional investors (PE firms, family offices, foundations, pension funds) struggle with:
- **Deal flow quality**: 90% of inbound opportunities don't fit their mandate
- **Screening velocity**: Manual review takes 2-4 weeks per deal
- **Mandate clarity**: Investors' own mandates are vague or incomplete
- **Feedback loops**: Dealmakers get rejected without understanding why

This pilot proves that **AI agents asking forcing questions can standardize mandate definition and automate deal evaluation**.

---

## The Gstack Approach

This repo adapts [Garry Tan's Y Combinator standardization model](https://www.linkedin.com/feed/update/urn:li:activity:7012345678/) to investor mandates.

Instead of vague criteria ("we like fintech"), the **Process, Legal, and Compliance agents ask forcing questions** that:
1. **Clarify what the investor actually wants** (mandate definition)
2. **Evaluate whether a deal fits** (deal screening)
3. **Identify adaptation paths** (what needs to change for a "maybe" to become a "yes")

---

## Three Agents

### 1. Process Agent
**Questions:** Does the deal structure match our investment thesis and timeline?

- **Forcing Questions:**
  - What is the primary use of capital? (acquisition, growth, dividend, debt paydown, etc.)
  - How long until exit? Must align with fund lifecycle
  - What are the key value drivers? Do they match our expertise?
  - What is the decision timeline? Does it fit our closing velocity?

**Output:** APPROVE, ADAPT, or REJECT with specific reasoning

### 2. Legal Agent
**Questions:** Are the contractual terms acceptable within our risk tolerance?

- **Forcing Questions:**
  - What are governance rights? (board seats, information rights, veto rights)
  - What are liquidation preferences? (non-participating, 1x, participating, capped)
  - What anti-dilution protections exist?
  - What are the deal exclusions? (non-competes, non-solicits, survival periods)

**Output:** APPROVE, ADAPT, or REJECT with required changes

### 3. Compliance Agent
**Questions:** Are there regulatory, AML, or reputational risks?

- **Forcing Questions:**
  - What jurisdictions are involved? Any high-risk countries?
  - What is the beneficial ownership structure? AML/KYC pass?
  - Are there sanctioned parties or PEPs involved?
  - What reputational risks exist in the sector/geography?

**Output:** APPROVE, APPROVE_WITH_MONITORING, or REJECT

---

## Machine-Readable Mandates

Mandates are JSON schemas that remove ambiguity.

```json
{
  "investor": "Example PE Fund IV",
  "mandate_id": "pef4-2024",
  "version": "1.0",
  "created_at": "2026-04-30",
  
  "process_criteria": {
    "primary_use_of_capital": ["acquisition", "growth"],
    "hold_period_years": [3, 7],
    "target_irr_percent": 25,
    "check_size_usd_millions": [5, 50],
    "geography": ["US", "EU"],
    "sectors": ["software", "fintech", "saas"],
    "exclude_sectors": ["defense", "fossil_fuels"]
  },
  
  "legal_criteria": {
    "required_governance": ["board_seat", "information_rights"],
    "liquidation_preference": "non_participating",
    "max_anti_dilution": "broad_based_weighted_average",
    "max_non_compete_years": 2,
    "required_carveouts": ["founder_friendly"]
  },
  
  "compliance_criteria": {
    "allowed_jurisdictions": ["US", "CA", "GB", "DE", "SG", "AU"],
    "aml_kyc_required": true,
    "blocked_sectors": ["gambling", "weapons"],
    "reputational_review": true,
    "sanctions_check": true
  }
}
```

---

## Deal Evaluation Flow

```
Deal Proposal (JSON)
    ↓
[Process Agent] → APPROVE / ADAPT / REJECT
    ↓
[Legal Agent] → APPROVE / ADAPT / REJECT
    ↓
[Compliance Agent] → APPROVE / APPROVE_WITH_MONITORING / REJECT
    ↓
Decision Engine:
  - All APPROVE → FUND IT
  - Any REJECT → PASS (unless ADAPT path exists)
  - Mix of APPROVE/ADAPT → FLAG FOR NEGOTIATION
```

---

## Example: Deal Proposal Evaluation

**Input:** Trade receivables financing deal from LinkLogis (Asia-Pacific)

**Process Agent:**
- Use of capital: Acquisition of competitor → ✓ Matches mandate
- Hold period: 4 years → ✓ Within 3-7 range
- Geography: Singapore → ✓ Approved
- **Decision: APPROVE**

**Legal Agent:**
- Governance: Board seat requested → ✓ Required
- Liquidation preference: Participating → ✗ Mandate allows non-participating only
- **Decision: ADAPT** (need to change liquidation preference)

**Compliance Agent:**
- Jurisdiction: Singapore → ✓ Approved
- AML/KYC: Completed → ✓ Pass
- Sanctions check: Clean → ✓ Pass
- **Decision: APPROVE**

**Final Decision:** ADAPT (legal structure change required)
**Action:** Flag for negotiation; send back specific change requests

---

## Repository Structure

```
fmm-pilot/
├── README.md                          (this file)
├── GSTACK_QUESTIONS.md               (forcing questions for each agent)
├── schemas/
│   ├── mandate.schema.json           (mandate definition spec)
│   ├── deal_proposal.schema.json     (deal submission spec)
│   └── evaluation.schema.json        (agent output format)
├── agents/
│   ├── process_agent.md              (Process agent playbook)
│   ├── legal_agent.md                (Legal agent playbook)
│   └── compliance_agent.md           (Compliance agent playbook)
├── examples/
│   ├── mandates/
│   │   ├── example_pe_fund.json
│   │   └── example_foundation.json
│   ├── deals/
│   │   ├── deal_01_trade_receivables.json
│   │   └── deal_02_saas_acquisition.json
│   └── evaluations/
│       ├── eval_01_approved.json
│       └── eval_02_adapt.json
├── decision_engine.md                (logic for final decisions)
├── IMPLEMENTATION.md                 (how to build this)
└── LICENSE
```

---

## Getting Started

### For Mandate Creators
1. Start with `examples/mandates/example_pe_fund.json`
2. Fill in your own criteria (use `schemas/mandate.schema.json` as reference)
3. Share JSON with your deal team

### For Deal Submitters
1. Review the investor's mandate JSON
2. Prepare your deal proposal using `schemas/deal_proposal.schema.json`
3. Submit and get structured feedback

### For Implementers
1. Read `GSTACK_QUESTIONS.md` to understand the forcing questions
2. Review agent playbooks in `agents/` directory
3. Follow `IMPLEMENTATION.md` for tech stack guidance
4. Use example evaluations in `examples/evaluations/` as test cases

---

## Why This Works

**Standardization**: Mandates aren't documents anymore—they're queryable schemas
**Speed**: Agents answer forcing questions in seconds, not weeks
**Feedback**: Deals get specific, actionable rejection reasons instead of "doesn't fit"
**Transparency**: Both sides know the exact criteria upfront

---

## Next Steps

### Phase 1: Pilot (4 weeks)
- [ ] Define 3-5 investor mandates in JSON
- [ ] Generate 10-15 deal proposals
- [ ] Run agents, measure accuracy vs. human decisions
- [ ] Iterate on forcing questions

### Phase 2: Integration (8 weeks)
- [ ] Build API layer for deal submission
- [ ] Connect to Noxlabs smart contracts (optional)
- [ ] Create investor dashboard showing deal pipeline
- [ ] Automate mandate updates

### Phase 3: Network (12+ weeks)
- [ ] Add institutional investors to network
- [ ] Build deal syndication (multiple investors)
- [ ] Add learning loop (agents improve from past decisions)

---

## References

- [Garry Tan on Standardization](https://twitter.com/garrytan/status/...)
- [Gstack Format](https://www.ycombinator.com/gstack)
- [AI2AI Matching Concept](./docs/ai2ai_matching.md)

---

**Created:** April 30, 2026  
**Status:** Pilot Reference Implementation  
**Target Users:** PE firms, institutional investors, deal platforms
