# GitHub Setup for FMM Pilot

Quick guide to push the Karpathy-grade refactored version to GitHub.

## Step 1: Initialize Git Repo

```bash
cd fmm-pilot-repo
git init
git add .
git commit -m "Initial commit: minimal, teachable MVP

- mandate.py: Pydantic schemas for investor mandates and deals
- agents.py: Three agents (Process, Legal, Compliance) with forcing questions
- app.py: FastAPI endpoint for /evaluate
- requirements.txt: Minimal dependencies (5 packages)
- BUILD_FROM_SCRATCH.md: Step-by-step walkthrough
- README.md: Quick start guide

~1200 lines of production code. No fluff."
```

## Step 2: Create GitHub Repo

1. Go to https://github.com/new
2. Create repo: `finance-mandate-matching-lab`
3. **Do NOT** initialize with README (we have our own)
4. Copy the HTTPS URL

## Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/finance-mandate-matching-lab.git
git branch -M main
git push -u origin main
```

## Step 4: Verify

Visit https://github.com/YOUR_USERNAME/finance-mandate-matching-lab

You should see:
```
finance-mandate-matching-lab/
├── README.md
├── BUILD_FROM_SCRATCH.md
├── mandate.py
├── agents.py
├── app.py
├── requirements.txt
└── .gitignore
```

## What to Tell Franklin

**GitHub repo:** https://github.com/YOUR_USERNAME/finance-mandate-matching-lab

**Key files to read:**
1. `README.md` - 5-minute overview
2. `BUILD_FROM_SCRATCH.md` - Step-by-step explanation
3. `mandate.py` - Understand the schemas
4. `agents.py` - Understand the forcing questions
5. `app.py` - Understand how it ties together

**To run:**
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m uvicorn app:app --reload
```

## Repository Structure

```
finance-mandate-matching-lab/
├── README.md                    # Quick start
├── BUILD_FROM_SCRATCH.md       # Deep dive explanation
├── mandate.py                  # Schemas
├── agents.py                   # Three agents
├── app.py                      # FastAPI app
├── requirements.txt            # Dependencies
└── .gitignore                  # Git ignore rules
```

**Optional additions (Phase 2):**
```
├── examples/
│   ├── example_mandate.json
│   └── example_deal.json
├── tests/
│   ├── test_schemas.py
│   └── test_agents.py
├── Dockerfile
└── docker-compose.yml
```

## Make It Fork-Friendly

Add to README (after Quick Start section):

```markdown
## For Developers

Want to fork and modify for your fund?

1. Fork this repo
2. Edit `mandate.py` to add your custom criteria
3. Edit `agents.py` to customize forcing questions per agent
4. Deploy to your infrastructure (Docker, Heroku, AWS Lambda)

See `BUILD_FROM_SCRATCH.md` for architectural decisions.
```

## GitHub Topics

Add these to your repo settings (improves discoverability):
- `venture-capital`
- `deal-evaluation`
- `ai-agents`
- `fastapi`
- `claude-api`
- `gstack`

## Next: Issues & Discussions

Create initial issues for Franklin's feedback:

**Issue 1:** "Feedback from LinkLogis pilot"
- LinkLogis team: What did you think of the forcing questions?
- Did the decisions match your manual evaluation?
- What questions should we add?

**Issue 2:** "Feature requests"
- [ ] Add batch evaluation endpoint
- [ ] Add mandate comparison API
- [ ] Add decision export (PDF report)
- [ ] Add database persistence

---

## Optional: License

Add `LICENSE` file (MIT recommended):

```
MIT License

Copyright (c) 2026 Digital Treasury

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT license text...]
```

---

**That's it!** You're ready to share with Franklin and the broader community.
