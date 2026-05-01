# Implementation Guide: Finance Mandate Matching Lab

This guide explains how to build a working pilot of the three-agent evaluation system.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   INVESTOR PORTAL (UI)                           │
│  • Upload mandate JSON                                           │
│  • Review investor settings                                      │
│  • View deal pipeline                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   API LAYER (REST)                              │
│  POST /mandates          - Upload mandate                        │
│  POST /deals             - Submit deal proposal                  │
│  GET  /evaluations/{id}  - Get evaluation result               │
│  GET  /evaluations?status=approved - List pipeline            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│             EVALUATION ENGINE (Business Logic)                   │
│  • Parse mandate JSON                                            │
│  • Parse deal proposal JSON                                      │
│  • Route to three agents                                         │
│  • Aggregate results                                             │
│  • Generate evaluation report                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌─────────┐
    │PROCESS │        │ LEGAL  │        │COMPLIANCE
    │ AGENT  │        │ AGENT  │        │ AGENT   │
    └────────┘        └────────┘        └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ DATA LAYER  │
                    │ (PostgreSQL)│
                    └─────────────┘
```

---

## Tech Stack Options

### Option 1: Python (Recommended for MVP)

**Pros:**
- Easy to implement LLM agents (Claude API integration straightforward)
- Fast iteration
- Good data science tooling (pandas, numpy)
- JSON handling is native

**Pros:**
- Built-in JSON schema validation
- Can use FastAPI for REST layer
- Can deploy to any Python host (AWS Lambda, Heroku, Railway, etc.)

**Stack:**
```
Backend:        FastAPI (REST API) + Pydantic (validation)
Agents:         claude-sdk (Claude API calls) or custom logic
Data:           PostgreSQL + SQLAlchemy ORM
Deployment:     Docker + Kubernetes OR Heroku/Railway
Frontend:       React + TypeScript (optional MVP)
```

**Minimum Implementation (Flask-based):**
```python
# app.py
from flask import Flask, request, jsonify
from claude_sdk import Anthropic
import json

app = Flask(__name__)
client = Anthropic()

@app.route('/evaluate', methods=['POST'])
def evaluate_deal():
    mandate = request.json['mandate']
    deal = request.json['deal']
    
    # Call three agents
    process_result = evaluate_process_agent(mandate, deal)
    legal_result = evaluate_legal_agent(mandate, deal)
    compliance_result = evaluate_compliance_agent(mandate, deal)
    
    # Aggregate
    final_decision = aggregate_decisions([
        process_result,
        legal_result,
        compliance_result
    ])
    
    return jsonify({
        'deal_id': deal['deal_id'],
        'decision': final_decision['status'],
        'process_agent': process_result,
        'legal_agent': legal_result,
        'compliance_agent': compliance_result,
        'recommendation': final_decision['notes']
    })

def evaluate_process_agent(mandate, deal):
    # Use Claude API to evaluate
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system="""You are a Process Agent evaluating deals against investor mandates.
        
        Ask these forcing questions:
        1. Is the use of capital approved?
        2. Is the hold period within range?
        3. Is check size acceptable?
        4. Does IRR meet minimum?
        5. Are geographies allowed?
        6. Is sector approved?
        
        Return JSON: {"decision": "APPROVE|ADAPT|REJECT", "issues": [...], "reasoning": "..."}
        """,
        messages=[{
            "role": "user",
            "content": f"Mandate: {json.dumps(mandate)}\n\nDeal: {json.dumps(deal)}"
        }]
    )
    
    # Parse and return
    return json.loads(response.content[0].text)
```

### Option 2: JavaScript/Node.js

**Pros:**
- Full-stack JS (frontend + backend same language)
- npm ecosystem
- Easy deployment to Vercel/Netlify/Railway

**Stack:**
```
Backend:        Express.js + TypeScript
Agents:         claude-sdk-js
Validation:     Zod or Joi (JSON schema validation)
Data:           MongoDB or PostgreSQL + Prisma ORM
Deployment:     Vercel/Railway/Netlify
Frontend:       Next.js + React
```

### Option 3: No-Code/Low-Code

**Airtable-based approach:**
- Create Airtable base with two tables: "Mandates" and "Deals"
- Use Zapier + Make.com to trigger Anthropic API calls
- Store evaluation results in Airtable
- Use Airtable views/filters for dashboard

**Pros:** Deploy in 1 hour, no coding
**Cons:** Limited customization, slower processing

---

## Detailed Implementation: Python MVP

### 1. Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic anthropic python-dotenv sqlalchemy psycopg2-binary

# Create .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo "DATABASE_URL=postgresql://user:password@localhost/fmm" >> .env
```

### 2. Core Application Structure

```
fmm-pilot/
├── backend/
│   ├── app.py                 # FastAPI app
│   ├── agents/
│   │   ├── process_agent.py
│   │   ├── legal_agent.py
│   │   └── compliance_agent.py
│   ├── models/
│   │   ├── mandate.py         # SQLAlchemy models
│   │   ├── deal.py
│   │   └── evaluation.py
│   ├── schemas/
│   │   ├── mandate_schema.py  # Pydantic validation
│   │   └── deal_schema.py
│   ├── utils/
│   │   ├── validators.py      # JSON schema validation
│   │   └── decision_engine.py # Final decision logic
│   └── requirements.txt
├── frontend/                  # React (optional)
├── examples/
│   ├── mandates/
│   └── deals/
└── docs/
```

### 3. Minimal Working Example

**backend/app.py:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import anthropic

app = FastAPI(title="Finance Mandate Matching Lab")
client = anthropic.Anthropic()

class MandateInput(BaseModel):
    mandate: dict
    deal: dict

@app.post("/evaluate")
async def evaluate_deal(input_data: MandateInput):
    try:
        # Step 1: Process Agent
        process_evaluation = await run_process_agent(
            input_data.mandate,
            input_data.deal
        )
        
        # Step 2: Legal Agent
        legal_evaluation = await run_legal_agent(
            input_data.mandate,
            input_data.deal
        )
        
        # Step 3: Compliance Agent
        compliance_evaluation = await run_compliance_agent(
            input_data.mandate,
            input_data.deal
        )
        
        # Step 4: Decision Engine
        final_decision = make_final_decision(
            process_evaluation,
            legal_evaluation,
            compliance_evaluation
        )
        
        return {
            "deal_id": input_data.deal['deal_id'],
            "mandate_id": input_data.mandate['mandate_id'],
            "final_decision": final_decision['status'],
            "agents": {
                "process": process_evaluation,
                "legal": legal_evaluation,
                "compliance": compliance_evaluation
            },
            "next_steps": final_decision['next_steps'],
            "evaluation_id": f"EVAL-{input_data.deal['deal_id']}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def run_process_agent(mandate, deal):
    prompt = f"""You are a Process Agent evaluating deals against investor mandates using Gstack forcing questions.

MANDATE:
{json.dumps(mandate, indent=2)}

DEAL PROPOSAL:
{json.dumps(deal['process_section'], indent=2)}

Evaluate the deal against these forcing questions:
1. Is use_of_capital in the allowed list? ({mandate['process_criteria']['primary_use_of_capital']})
2. Is hold_period_years within range? ({mandate['process_criteria']['hold_period_years']})
3. Is check_size_usd_millions acceptable? ({mandate['process_criteria']['check_size_usd_millions']})
4. Is projected_irr >= target? ({mandate['process_criteria']['target_irr_percent']}%)
5. Are all geographies in allowed list? ({mandate['process_criteria']['geography']})
6. Is primary_sector approved? ({mandate['process_criteria']['sectors']})
7. Is sector NOT in exclude list? ({mandate['process_criteria'].get('exclude_sectors', [])})
8. Does decision_deadline fit max_decision_days? ({mandate['process_criteria']['max_decision_days']} days)

Return a JSON object with:
{{
  "decision": "APPROVE|ADAPT|REJECT",
  "passed_questions": [...],
  "failed_questions": [...],
  "issues": [...],
  "reasoning": "..."
}}"""
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract JSON from response
    text = message.content[0].text
    # Simple extraction (production code should use regex)
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    return json.loads(text[json_start:json_end])

# Similar implementations for legal_agent and compliance_agent...

def make_final_decision(process_result, legal_result, compliance_result):
    # Decision logic
    if (legal_result['decision'] == 'REJECT' or 
        compliance_result['decision'] == 'REJECT'):
        return {
            'status': 'PASS',
            'reason': 'Hard blockers in legal or compliance',
            'next_steps': ['Revise term sheet or pass on deal']
        }
    
    elif (process_result['decision'] == 'ADAPT' or 
          legal_result['decision'] == 'ADAPT'):
        return {
            'status': 'FLAG_FOR_NEGOTIATION',
            'reason': 'Adaptable issues detected',
            'next_steps': ['Review required changes', 'Negotiate with founders']
        }
    
    else:
        return {
            'status': 'FUND_IT',
            'reason': 'All agents approved',
            'next_steps': ['Schedule investment committee', 'Finalize docs']
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Running the MVP

```bash
# Start server
python -m uvicorn backend.app:app --reload

# Test endpoint
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d @examples/test_payload.json
```

---

## Deployment Options

### Option 1: Heroku (Simplest)

```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create fmm-pilot
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Option 2: Docker + Railway/Render

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Deploy to Railway
railway up
```

### Option 3: AWS Lambda (Serverless)

Use Zappa or AWS SAM to deploy FastAPI as serverless function.

---

## Phase 1: MVP (4 weeks)

**Week 1-2:** Setup
- [ ] FastAPI app skeleton
- [ ] Claude API integration for one agent (Process)
- [ ] Basic JSON validation
- [ ] Deploy to local/Heroku

**Week 2-3:** Expand
- [ ] Add Legal and Compliance agents
- [ ] Implement decision engine
- [ ] Add database for storing evaluations
- [ ] Create simple frontend (React or just API docs)

**Week 3-4:** Test & Iterate
- [ ] Run 5-10 deals against example mandates
- [ ] Gather feedback on agent decisions
- [ ] Refine forcing questions based on feedback
- [ ] Deploy to production

---

## Phase 2: Production (8 weeks)

- [ ] Authentication/authorization (API keys for investors)
- [ ] Mandate management dashboard
- [ ] Deal pipeline view
- [ ] Email notifications
- [ ] Reporting/analytics
- [ ] Integration with Noxlabs (optional)

---

## Integration with Claude API

The agents use the Claude API with this pattern:

```python
# System prompt defines the agent role and forcing questions
# User prompt contains the specific mandate + deal
# Model responds with JSON evaluation

response = client.messages.create(
    model="claude-opus-4-6",  # or claude-sonnet-4-6 for faster/cheaper
    max_tokens=2000,
    system="You are a [Process|Legal|Compliance] Agent...",
    messages=[
        {"role": "user", "content": f"Mandate: {mandate}\nDeal: {deal}"}
    ]
)
```

**Cost estimate (per deal evaluation):**
- 3 agent calls × ~1500 tokens each = ~4500 tokens
- At $0.003/1K input tokens + $0.015/1K output tokens = ~$0.08 per deal

**For 100 deals/month:** ~$8 in API costs

---

## Open Questions for Production

1. **Agent Learning:** Should agents learn from past decisions? (Fine-tuning, RAG, etc.)
2. **Speed:** Current implementation: ~3-5 seconds per evaluation. Can optimize with parallel agent calls or caching.
3. **Accuracy:** How do we validate agent decisions against human evaluators?
4. **Customization:** Should investors be able to customize forcing questions per fund?
5. **API Rate Limits:** How to handle high-volume deal submissions?

---

## Getting Started

1. Fork/clone this repo
2. Follow MVP implementation above
3. Run: `python backend/app.py`
4. Test with examples in `examples/deals/`
5. Deploy to production when ready

---

**Next:** See README.md for conceptual overview, or GSTACK_QUESTIONS.md for the full forcing questions framework.
