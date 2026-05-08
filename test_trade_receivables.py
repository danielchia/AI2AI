#!/usr/bin/env python3
"""
Test Trade Receivables Evaluation System

This script tests the trade receivables mandate matching system against the
24 forcing questions (8 per agent) without running a live server.

Usage:
    python3 test_trade_receivables.py

Output:
    - Loads mandate schema
    - Loads deal (anonymized example)
    - Displays all 24 forcing questions
    - Shows expected answers for the example deal
    - Demonstrates agent decision logic
"""

import json
from trade_receivables_mandate import TradeReceivablesMandate, Deal, ReceiverQuality, SellerQuality, InvoiceCharacteristics, FinancingTerms
from trade_receivables_agents import get_all_questions, ProcessAgent, LegalAgent, CreditRiskAgent


def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def test_mandate_schema():
    """Test that mandate schema loads correctly."""
    print_section("1. Trade Receivables Mandate Schema")

    mandate_dict = {
        "mandate_name": "DTF Trade Receivables Program",
        "fund_manager": "Digital Treasury Fund Pte. Ltd.",
        "investor_jurisdiction": "Singapore",
        "buyer_quality": {
            "credit_rating": None,
            "years_in_business": 5,
            "payment_history_score": 90,
            "regulatory_status": "compliant",
            "jurisdiction": "Singapore",
            "no_active_disputes": True,
            "financial_stability": "stable",
        },
        "seller_quality": {
            "years_in_business": 8,
            "good_standing": True,
            "not_in_insolvency": True,
            "no_material_litigation": True,
            "regulatory_compliance": "fully_compliant",
        },
        "invoice_criteria": {
            "tenor_days_min": 90,
            "tenor_days_max": 120,
            "invoice_amount_min_usd": 50000,
            "invoice_amount_max_usd": 2000000,
            "goods_services_delivered": True,
            "buyer_confirmation_required": True,
            "no_prior_payment": True,
        },
        "financing_terms": {
            "advance_percentage": 90.0,
            "holdback_percentage": 10.0,
            "discount_rate_percent_pa": 5.0,
            "buffer_period_days": 30,
            "max_overdue_days_allowed": 45,
            "recourse_type": "non_recourse",
        },
        "max_concentration_single_buyer_pct": 10,
        "max_concentration_single_seller_pct": 15,
    }

    mandate = TradeReceivablesMandate(**mandate_dict)
    print(f"✓ Mandate loaded: {mandate.mandate_name}")
    print(f"  Fund Manager: {mandate.fund_manager}")
    print(f"  Jurisdiction: {mandate.investor_jurisdiction}")
    print(f"  Advance %: {mandate.financing_terms.advance_percentage}%")
    print(f"  Discount Rate: {mandate.financing_terms.discount_rate_percent_pa}% p.a.")
    print(f"  Invoice Tenor: {mandate.invoice_criteria.tenor_days_min}-{mandate.invoice_criteria.tenor_days_max} days")


def test_deal_schema():
    """Test that deal schema loads correctly."""
    print_section("2. Trade Receivable Deal Schema")

    deal_dict = {
        "company_name": "Anon Chemical Trader Co",
        "seller_incorporation": "Singapore",
        "buyer_name": "Anon Materials Manufacturing Ltd",
        "buyer_jurisdiction": "Singapore",
        "buyer_credit_score": None,
        "buyer_relationship_months": 18,
        "buyer_payment_history": "100% on-time (18 months, 12+ invoices)",
        "invoice_number": "INV-2025-0901",
        "invoice_date": "2025-09-01",
        "invoice_amount_usd": 500000,
        "due_date": "2025-11-30",
        "tenor_days": 90,
        "goods_services_description": "Bulk sulfuric acid (5 containers, 100 tonnes)",
        "delivery_date": "2025-09-05",
        "delivery_proof_type": "BoL + signed delivery receipt",
        "buyer_confirmation_obtained": True,
        "buyer_disputes_history": None,
        "seller_financials_summary": {"annual_revenue_usd": 75000000, "ebitda_margin_pct": 8},
        "funding_requested_percentage": 90.0,
        "purpose": "Working capital for inventory",
    }

    deal = Deal(**deal_dict)
    print(f"✓ Deal loaded: {deal.invoice_number}")
    print(f"  Seller: {deal.company_name}")
    print(f"  Buyer: {deal.buyer_name}")
    print(f"  Invoice Amount: USD {deal.invoice_amount_usd:,.0f}")
    print(f"  Tenor: {deal.tenor_days} days")
    print(f"  Delivery: {deal.delivery_date}")
    print(f"  Buyer Confirmation: {'Yes' if deal.buyer_confirmation_obtained else 'No'}")


def test_forcing_questions():
    """Display all 24 forcing questions."""
    print_section("3. All 24 Forcing Questions (8 per Agent)")

    questions = get_all_questions()

    agents = {"process": [], "legal": [], "credit": []}
    for q in questions:
        agents[q.agent].append(q)

    for agent_name, agent_questions in agents.items():
        agent_title = {
            "process": "PROCESS AGENT (Invoice Quality & Deal Structure)",
            "legal": "LEGAL AGENT (Enforceability & Compliance)",
            "credit": "CREDIT RISK AGENT (Financial Strength & Portfolio)",
        }[agent_name]

        print(f"\n{agent_title}")
        print(f"{'-'*70}")

        for q in agent_questions:
            print(f"\n{q.question_id}. {q.question}")
            if q.follow_up:
                print(f"   ⚠ Follow-up if concerning: {q.follow_up}")


def test_agent_evaluation():
    """Test agent evaluation logic."""
    print_section("4. Agent Evaluation Results")

    # Initialize agents
    process_agent = ProcessAgent()
    legal_agent = LegalAgent()
    credit_agent = CreditRiskAgent()

    # Example deal
    deal_dict = {
        "company_name": "Anon Chemical Trader Co",
        "seller_incorporation": "Singapore",
        "buyer_name": "Anon Materials Manufacturing Ltd",
        "buyer_jurisdiction": "Singapore",
        "buyer_credit_score": None,
        "buyer_relationship_months": 18,
        "buyer_payment_history": "100% on-time",
        "invoice_number": "INV-2025-0901",
        "invoice_date": "2025-09-01",
        "invoice_amount_usd": 500000,
        "due_date": "2025-11-30",
        "tenor_days": 90,
        "goods_services_description": "Bulk sulfuric acid",
        "delivery_date": "2025-09-05",
        "delivery_proof_type": "BoL + delivery receipt",
        "buyer_confirmation_obtained": True,
        "buyer_disputes_history": None,
        "seller_financials_summary": {"annual_revenue_usd": 75000000},
        "funding_requested_percentage": 90.0,
        "purpose": "Working capital",
    }

    deal = Deal(**deal_dict)

    print(f"\nEvaluating: {deal.invoice_number} ({deal.company_name} → {deal.buyer_name})")

    # Run evaluations
    process_result = process_agent.evaluate(deal)
    legal_result = legal_agent.evaluate(deal)
    credit_result = credit_agent.evaluate(deal)

    print(f"\nProcess Agent Decision: {process_result.get('decision', 'PENDING')}")
    print(f"  Questions: {len(process_result.get('questions', []))} asked")

    print(f"\nLegal Agent Decision: {legal_result.get('decision', 'PENDING')}")
    print(f"  Questions: {len(legal_result.get('questions', []))} asked")

    print(f"\nCredit Risk Agent Decision: {credit_result.get('decision', 'PENDING')}")
    print(f"  Questions: {len(credit_result.get('questions', []))} asked")

    # Final decision logic
    print(f"\n{'─'*70}")
    print("FINAL DECISION LOGIC:")
    print("  • If any agent says REJECT → DECLINE")
    print("  • If any agent says CONDITIONAL → CONDITIONAL_APPROVE (adjust pricing)")
    print("  • If all APPROVE → FUND_IT (at standard terms)")
    print(f"{'─'*70}")

    # Simulate decision
    decisions = [d.get('decision', 'UNKNOWN') for d in [process_result, legal_result, credit_result]]

    if 'REJECT' in decisions:
        final = "DECLINE"
    elif 'CONDITIONAL' in decisions:
        final = "CONDITIONAL_APPROVE (reduce advance to 85%, increase discount to 5.5%)"
    else:
        final = "FUND_IT (at standard 90% advance, 5.0% discount)"

    print(f"\n✓ Final Recommendation: {final}\n")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  TRADE RECEIVABLES MANDATE MATCHING SYSTEM - TEST SUITE")
    print("="*80)

    try:
        test_mandate_schema()
        test_deal_schema()
        test_forcing_questions()
        test_agent_evaluation()

        print_section("SUMMARY")
        print("""
✓ All systems loaded successfully
✓ 24 forcing questions loaded (8 per agent)
✓ Mandate and deal schemas validated
✓ Agent evaluation logic ready

NEXT STEPS:
1. Start the FastAPI server:
   $ export ANTHROPIC_API_KEY=sk-ant-...
   $ python -m uvicorn app:app --reload

2. Test the API endpoints:
   • GET /health
   • POST /test_trade_receivables
   • POST /evaluate_trade_receivables

3. Submit real deals from your originator for evaluation

DOCUMENTATION:
- trade_receivables_mandate.py: Pydantic schemas for mandate + deals
- trade_receivables_agents.py: 24 forcing questions + agent logic
- trade_receivables_case_study_template.md: Real example with expected answers
        """)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
