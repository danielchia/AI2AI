"""
Finance Mandate Matching Lab - FastAPI Application

Minimal, teachable MVP of the FMM system.
Evaluates deals against investor mandates using 3 agents (Process, Legal, Compliance).
Each agent asks forcing questions (Gstack methodology).
Final decision aggregates all three.

To run:
    pip install fastapi uvicorn pydantic anthropic python-dotenv
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m uvicorn app:app --reload

Then visit http://localhost:8000/docs for interactive API docs.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import logging

from mandate import (
    InvestorMandate,
    DealProposal,
    EvaluationRequest,
    validate_evaluation_request,
)
from agents import ProcessAgent, LegalAgent, ComplianceAgent


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Finance Mandate Matching Lab",
    description="Evaluate deals against investor mandates using AI agents + forcing questions",
    version="1.0.0",
)

# Initialize agents
process_agent = ProcessAgent()
legal_agent = LegalAgent()
compliance_agent = ComplianceAgent()


def make_final_decision(process_result: dict, legal_result: dict, compliance_result: dict) -> dict:
    """
    Aggregate agent results into final decision.

    Decision logic:
    - If any agent REJECTs → PASS (don't fund)
    - If any agent says ADAPT and others don't REJECT → FLAG_FOR_NEGOTIATION
    - If all APPROVE (or legal/compliance APPROVE_WITH_MONITORING) → FUND_IT

    This keeps the decision logic transparent and force-checkable.
    """

    # Extract decisions
    process_decision = process_result.get("decision", "UNKNOWN")
    legal_decision = legal_result.get("decision", "UNKNOWN")
    compliance_decision = compliance_result.get("decision", "UNKNOWN")

    # Hard blockers: any REJECT means pass
    if process_decision == "REJECT" or legal_decision == "REJECT" or compliance_decision == "REJECT":
        return {
            "status": "PASS",
            "reason": "Hard blocker detected",
            "blocking_agent": [
                "process" if process_decision == "REJECT" else None,
                "legal" if legal_decision == "REJECT" else None,
                "compliance" if compliance_decision == "REJECT" else None,
            ],
            "next_steps": ["Review blocking agent feedback", "Pass on deal or address before resubmitting"],
        }

    # Negotiable issues: ADAPT means flag for negotiation
    if process_decision == "ADAPT" or legal_decision == "ADAPT":
        return {
            "status": "FLAG_FOR_NEGOTIATION",
            "reason": "Adaptable issues detected (terms fixable via negotiation)",
            "negotiation_focus": [
                "process" if process_decision == "ADAPT" else None,
                "legal" if legal_decision == "ADAPT" else None,
            ],
            "next_steps": [
                "Review required changes",
                "Work with legal/founders on term sheet modifications",
                "Resubmit after negotiation",
            ],
        }

    # Compliance with monitoring
    if compliance_decision == "APPROVE_WITH_MONITORING":
        return {
            "status": "FUND_IT",
            "reason": "All agents approve (compliance requires monitoring)",
            "conditions": ["Implement compliance monitoring plan"],
            "next_steps": ["Schedule investment committee", "Finalize docs", "Implement monitoring"],
        }

    # All clear
    return {
        "status": "FUND_IT",
        "reason": "All agents approved",
        "next_steps": ["Schedule investment committee", "Finalize docs"],
    }


@app.post("/evaluate")
async def evaluate_deal(request: EvaluationRequest) -> JSONResponse:
    """
    Evaluate a deal against an investor mandate.

    Input: mandate (investor criteria) + deal (founder pitch)
    Process:
      1. Process Agent: Does it fit the thesis?
      2. Legal Agent: Are terms acceptable?
      3. Compliance Agent: Any regulatory/reputational risk?
    Output: Final decision (FUND_IT / FLAG_FOR_NEGOTIATION / PASS)

    This is the core of the system.
    """

    mandate = request.mandate
    deal = request.deal

    logger.info(f"Evaluating deal {deal.deal_id} against mandate {mandate.mandate_id}")

    try:
        # Run all three agents in parallel (conceptually; actually sequential for simplicity)
        logger.info("Running Process Agent...")
        process_result = process_agent.evaluate(mandate, deal)

        logger.info("Running Legal Agent...")
        legal_result = legal_agent.evaluate(mandate, deal)

        logger.info("Running Compliance Agent...")
        compliance_result = compliance_agent.evaluate(mandate, deal)

        # Aggregate results
        logger.info("Aggregating results...")
        final_decision = make_final_decision(process_result, legal_result, compliance_result)

        # Build response
        response = {
            "deal_id": deal.deal_id,
            "company_name": deal.company_name,
            "mandate_id": mandate.mandate_id,
            "final_decision": final_decision["status"],
            "final_reasoning": final_decision.get("reason", ""),
            "agents": {
                "process": process_result,
                "legal": legal_result,
                "compliance": compliance_result,
            },
            "conditions": final_decision.get("conditions", []),
            "next_steps": final_decision.get("next_steps", []),
        }

        logger.info(f"Evaluation complete: {final_decision['status']}")
        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Evaluation failed: {str(e)}")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Finance Mandate Matching Lab",
        "version": "1.0.0",
    }


@app.post("/test")
async def test_evaluation() -> JSONResponse:
    """
    Quick test endpoint with example mandate + deal.
    Useful for testing without creating full request bodies.
    """

    # Example mandate (TechVest Partners IV)
    example_mandate = {
        "investor_name": "TechVest Partners IV",
        "mandate_id": "tvp4-2026",
        "process_criteria": {
            "primary_use_of_capital": ["acquisition", "growth"],
            "hold_period_years": [3, 7],
            "check_size_usd_millions": [5, 30],
            "target_irr_percent": 25,
            "geography": ["US", "CA", "GB", "SG", "AU"],
            "sectors": ["software", "saas", "fintech", "payments"],
            "exclude_sectors": ["defense", "gambling", "tobacco"],
            "max_decision_days": 60,
        },
        "legal_criteria": {
            "required_governance": ["board_seat", "information_rights", "veto_rights"],
            "liquidation_preference": "non_participating",
            "anti_dilution": "broad_based_weighted_average",
            "max_non_compete_years": 2,
            "require_drag_tag": True,
            "founder_vesting_min_years": 4,
            "required_carveouts": ["equity_pool", "founder_friendly"],
            "mac_clause_required": True,
        },
        "compliance_criteria": {
            "allowed_jurisdictions": ["US", "CA", "GB", "DE", "SG", "AU"],
            "aml_kyc_required": True,
            "sanctions_screening_required": True,
            "blocked_sectors": ["weapons", "gambling", "fossil_fuels", "tobacco"],
            "min_esg_rating": "yellow",
            "data_privacy_required": True,
            "export_control_risk_acceptable": False,
        },
    }

    # Example deal (LinkLogis)
    example_deal = {
        "deal_id": "DEAL-2026-LINKLOGIS",
        "company_name": "LinkLogis Pte Ltd",
        "founder_names": ["Franklin", "Team"],
        "process_section": {
            "use_of_capital": "acquisition",
            "hold_period_years": 4,
            "check_size_usd_millions": 20,
            "projected_irr": 28,
            "geographies": ["SG", "MY", "TH"],
            "primary_sector": "fintech",
            "value_drivers": "Bolt-on M&A strategy, 40% YoY growth, multiple expansion",
            "decision_deadline_days": 45,
        },
        "legal_section": {
            "governance_rights": ["board_seat", "information_rights", "veto_rights"],
            "liquidation_preference": "participating",
            "anti_dilution": "broad_based_weighted_average",
            "non_compete_years": 2,
            "drag_tag_rights": True,
            "founder_vesting_years": 4,
            "founder_vesting_cliff_months": 12,
            "cap_table_summary": "Founders 60%, Series A 30%, Options 10%",
            "mac_clause_included": True,
        },
        "compliance_section": {
            "jurisdictions": [
                {"country": "SG", "risk_level": "low"},
                {"country": "MY", "risk_level": "low"},
                {"country": "TH", "risk_level": "low"},
            ],
            "aml_kyc_status": "complete",
            "sanctions_screening_result": "clean",
            "pep_screening_result": "clean",
            "primary_sector": "fintech",
            "esg_rating": "green",
            "data_privacy_status": "compliant",
            "export_control_relevant": False,
            "reputational_concerns": None,
        },
        "company_description": "Trade receivables financing platform for APAC SMEs",
        "financial_highlights": {
            "annual_revenue": 5000000,
            "revenue_growth_percent": 40,
            "monthly_burn": 200000,
            "runway_months": 18,
        },
    }

    # Build request and evaluate
    request = EvaluationRequest(mandate=example_mandate, deal=example_deal)
    return await evaluate_deal(request)


if __name__ == "__main__":
    import uvicorn

    # Run with: python app.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
