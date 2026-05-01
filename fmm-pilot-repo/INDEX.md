# Finance Mandate Matching Lab - Gstack Pilot
## Complete Repository Index

This is a reference implementation for standardizing institutional investor mandate matching using AI agents and Gstack forcing questions.

---

## 📚 Documentation (Start Here)

| Document | Purpose | Audience |
|----------|---------|----------|
| **[README.md](./README.md)** | Full overview of the system, problem, and approach | Everyone |
| **[QUICK_START.md](./QUICK_START.md)** | Get running in 30 minutes | Technical users |
| **[GSTACK_QUESTIONS.md](./GSTACK_QUESTIONS.md)** | All forcing questions for 3 agents | Domain experts, investors |
| **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** | How to build this system | Engineers |

---

## 📋 Schemas (Machine-Readable)

Investor mandates and deals are JSON—no ambiguity, no spreadsheets.

| File | Purpose | Format |
|------|---------|--------|
| **[schemas/mandate.schema.json](./schemas/mandate.schema.json)** | Investor mandate structure (JSON Schema) | JSON Schema v7 |
| **[schemas/deal_proposal.schema.json](./schemas/deal_proposal.schema.json)** | Deal submission structure (JSON Schema) | JSON Schema v7 |
| **[schemas/evaluation.schema.json](./schemas/evaluation.schema.json)** | Agent evaluation output format | JSON Schema v7 |

Use these to validate mandates and deals before submission.

---

## 👤 Agent Playbooks

Each agent asks forcing questions and returns a decision.

| Agent | Role | Questions | File |
|-------|------|-----------|------|
| **Process** | Does deal fit investment thesis? | 8 questions (use of capital, hold period, check size, IRR, geography, sector, drivers, timeline) | [GSTACK_QUESTIONS.md](./GSTACK_QUESTIONS.md#process-agent) |
| **Legal** | Are contract terms acceptable? | 8 questions (governance, liquidation, anti-dilution, non-compete, MAC, carveouts, drag/tag, vesting) | [GSTACK_QUESTIONS.md](./GSTACK_QUESTIONS.md#legal-agent) |
| **Compliance** | Are there regulatory/reputational risks? | 8 questions (jurisdiction, AML/KYC, sanctions, PEP, sector, export control, ESG, privacy) | [GSTACK_QUESTIONS.md](./GSTACK_QUESTIONS.md#compliance-agent) |

---

## 💼 Examples

Real-world examples to understand how the system works.

### Mandates (What Investors Want)

```
examples/mandates/
├── example_pe_fund_iv.json       (Mid-market PE fund, $5-30M checks, 25%+ IRR)
└── [Add your own...]
```

**Example:** TechVest Partners IV
- Invests in fintech, software, SaaS
- $5-30M per deal
- 3-7 year hold
- Non-participating liquidation preference
- Requires board seat + veto rights

### Deals (What Founders Pitch)

```
examples/deals/
├── deal_linklogis_trade_receivables.json   (Trade finance platform, Singapore)
└── [Add your own...]
```

**Example:** LinkLogis Pte Ltd
- $20M capital request
- 4-year hold, 28% projected IRR
- Expanding across APAC via acquisition
- Clean AML/KYC, strong team

### Evaluations (What the System Outputs)

```
examples/evaluations/
├── example_evaluation_approved.md          (FUND IT decision)
└── [Add your own...]
```

**Shows:**
- Process Agent: ✓ APPROVE (hits all forcing questions)
- Legal Agent: ✓ APPROVE (minor note on liquidation preference)
- Compliance Agent: ✓ APPROVE (all jurisdictions clear)
- **Final: FUND IT**

---

## 🛠️ Implementation

Code to actually build this system.

### For MVP (Python, 4 weeks)

```
backend/
├── app.py                   (FastAPI entry point)
├── agents/
│   ├── process_agent.py    (Process Agent logic)
│   ├── legal_agent.py      (Legal Agent logic)
│   └── compliance_agent.py (Compliance Agent logic)
├── models/                 (Database models, optional)
└── utils/
    ├── validators.py       (JSON schema validation)
    └── decision_engine.py  (Final decision logic)
```

See **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** for:
- Complete code samples
- FastAPI + Anthropic integration
- Deployment to Heroku/Railway/AWS
- Cost estimates ($0.08 per deal)

### For Production (Phase 2)

- Authentication / API keys
- Investor dashboard
- Deal pipeline views
- Email notifications
- Analytics/reporting
- Optional: Noxlabs integration

---

## 🚀 Getting Started

### 1. Understand the Concept (15 minutes)
- Read **README.md** to understand the problem and solution
- Skim **GSTACK_QUESTIONS.md** to see the forcing questions
- Review example files in `examples/`

### 2. Run Locally (30 minutes)
- Follow **QUICK_START.md**
- Set up Python environment
- Start FastAPI server
- Test with example mandate + deal

### 3. Customize for Your Use Case
- Copy `examples/mandates/example_pe_fund_iv.json`
- Edit for your investor criteria
- Create deal proposals for your pipeline
- Test evaluations

### 4. Deploy to Production
- See **IMPLEMENTATION.md** for Heroku/Railway/AWS setup
- Add authentication
- Connect to your deal platform

---

## 📊 Decision Flow

```
Investor Mandate (JSON)
    ↓
Deal Proposal (JSON)
    ↓
┌─────────────────────────────────────────┐
│  EVALUATION ENGINE (FastAPI)            │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Process Agent (forcing Q1-8)      │  │
│  │ → APPROVE / ADAPT / REJECT       │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Legal Agent (forcing Q1-8)        │  │
│  │ → APPROVE / ADAPT / REJECT       │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Compliance Agent (forcing Q1-8)   │  │
│  │ → APPROVE / APPROVE_WITH_MONITORING / REJECT  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Decision Engine                   │  │
│  │ Aggregate → Final Decision        │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
    ↓
Final Decision:
  • FUND_IT (all approved)
  • FLAG_FOR_NEGOTIATION (adaptable issues)
  • PASS (hard blockers)
    ↓
Evaluation Report (JSON + Markdown)
```

---

## 📞 Key Concepts

### Gstack Forcing Questions
- Remove ambiguity by asking specific, checkable questions
- Standardization framework from Y Combinator (Garry Tan)
- Applied to investor mandates instead of startup pitches

### Machine-Readable Mandates
- JSON schemas replace vague documents
- Computer-queryable criteria
- Version control friendly
- Easy to compare across funds

### Three-Agent Architecture
- **Process:** Investment thesis alignment
- **Legal:** Contract fairness and structure
- **Compliance:** Regulatory, AML, reputational risk

### Forced Decisions
- APPROVE: Hits all criteria
- ADAPT: Negotiable issues (term sheet changes)
- REJECT: Hard blockers (doesn't fit mandate)

---

## 📈 Use Cases

### For Investors
- Standardize mandate across team
- Accelerate deal screening (weeks → minutes)
- Get consistent feedback reasons
- Track deal pipeline programmatically

### For Founders/Dealmakers
- Understand why you're rejected (specifically, not vaguely)
- Know exact term changes needed for "maybe" → "yes"
- Submit once, get evaluated by all agents
- Faster feedback loops

### For Platforms
- Build deal syndication (multiple investors)
- Rank deals by investor fit
- Auto-route to matching investors
- Measure deal quality over time

---

## 🔧 Configuration

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@localhost/fmm  # optional
DEBUG=false
```

### Database (Optional)
- Store mandates, deals, evaluations in PostgreSQL
- Query past decisions to improve agents
- Build dashboard views

### Deployment
- Docker image provided
- Heroku/Railway templates in IMPLEMENTATION.md
- AWS Lambda serverless option

---

## 🎯 Roadmap

**Phase 1: MVP (4 weeks)**
- ✅ Schemas and forcing questions
- ⏳ FastAPI + Claude agent integration
- ⏳ Example mandates and deals
- ⏳ Deploy to Heroku

**Phase 2: Production (8 weeks)**
- ⏳ Authentication / API keys
- ⏳ Investor dashboard
- ⏳ Deal pipeline views
- ⏳ Email notifications

**Phase 3: Network (12+ weeks)**
- ⏳ Multi-investor syndication
- ⏳ Deal routing optimization
- ⏳ Agent learning from past decisions
- ⏳ Noxlabs smart contract integration (optional)

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Contributing

This is a reference implementation. Feel free to:
- Fork and customize for your fund
- Add more forcing questions
- Extend agents for new use cases
- Share improvements back

---

## 📞 Questions?

- **How do I customize mandates?** → See `examples/mandates/` and GSTACK_QUESTIONS.md
- **How do I deploy this?** → See IMPLEMENTATION.md
- **Can I use my own LLM?** → Yes, replace Claude API calls
- **What's the cost?** → ~$0.08 per deal evaluation
- **Can agents learn?** → Future feature; design for it now

---

**Last Updated:** April 30, 2026  
**Status:** Pilot Reference Implementation  
**Target Users:** PE firms, institutional investors, deal platforms
