"""
Trade Receivables Evaluation Agents
Process, Legal, and Credit Risk agents for receivables financing
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class ForcingQuestion:
    """A forcing question that must be answered to approve a trade receivable deal"""

    def __init__(self, question_id: str, question: str, agent: str, category: str, follow_up: str = None):
        self.question_id = question_id
        self.question = question
        self.agent = agent  # 'process', 'legal', 'credit'
        self.category = category
        self.follow_up = follow_up  # Optional follow-up if answer is concerning


# ============================================================================
# PROCESS AGENT: Investment fit, deal structure, receivables quality
# ============================================================================

PROCESS_AGENT_QUESTIONS = [
    ForcingQuestion(
        "P1",
        "Is the invoice tenor (90-120 days) within mandate parameters, and if outside, has it been explicitly approved? What is the actual tenor and why does it matter for working capital?",
        "process",
        "Invoice Eligibility",
        follow_up="If tenor exceeds 120 days, requires exception waiver. If under 90 days, reduces advance period benefit."
    ),

    ForcingQuestion(
        "P2",
        "Has the buyer explicitly confirmed in writing that the invoice is valid, accurate, and payable in full? What date was this confirmation received?",
        "process",
        "Buyer Confirmation",
        follow_up="Without buyer confirmation, receivable cannot be purchased. Must obtain before funding."
    ),

    ForcingQuestion(
        "P3",
        "What is the buyer's payment history with this seller over the past 12-24 months? Are they consistently on-time, early, or have there been delays?",
        "process",
        "Buyer Credit Quality",
        follow_up="Material payment delays or disputes indicate elevated default risk. May require higher holdback or reduced advance."
    ),

    ForcingQuestion(
        "P4",
        "Has the buyer or any related party ever disputed, deferred, or offset payment against invoices from this seller? If yes, what was the resolution and is it now resolved?",
        "process",
        "Historical Disputes",
        follow_up="Unresolved disputes create payment uncertainty. Requires seller indemnification or deal restructure."
    ),

    ForcingQuestion(
        "P5",
        "What goods or services were provided under this invoice? When were they delivered/completed and by whom? Is there independent proof of delivery (BoL, receipt, signature)?",
        "process",
        "Delivery/Performance Proof",
        follow_up="If goods are still in transit or services incomplete, receivable is not yet earned. Cannot purchase until delivery confirmed."
    ),

    ForcingQuestion(
        "P6",
        "What is the seller's relationship with this buyer? How long have they been trading? What is the historical transaction volume and frequency?",
        "process",
        "Relationship Tenure",
        follow_up="New or sporadic trading relationships carry higher default risk. May require additional collateral or reduced advance."
    ),

    ForcingQuestion(
        "P7",
        "Has the seller previously assigned, pledged, or created any security interest in this or similar invoices with other lenders or parties? Is the title clear and unencumbered?",
        "process",
        "Title Clearance",
        follow_up="Double sales or prior pledges make the receivable uncollectable. Requires seller indemnity and title insurance if available."
    ),

    ForcingQuestion(
        "P8",
        "What is the advance-to-invoice ratio and effective discount rate? Is the 90% advance and 5% annual discount appropriate given buyer credit quality and market conditions?",
        "process",
        "Financing Economics",
        follow_up="Underpriced financing (advance too high, discount too low) increases loss given default. May require repricing."
    ),
]


# ============================================================================
# LEGAL AGENT: Contract, documentation, regulatory compliance
# ============================================================================

LEGAL_AGENT_QUESTIONS = [
    ForcingQuestion(
        "L1",
        "Are the invoice and supporting contract (purchase order, service agreement) legally compliant with applicable law? Are the parties' obligations clear and enforceable?",
        "legal",
        "Invoice Enforceability",
        follow_up="Ambiguous or unlawful contracts may be unenforceable. Requires legal counsel review in buyer's jurisdiction."
    ),

    ForcingQuestion(
        "L2",
        "Does the seller have the legal right and authority to assign this receivable to the purchaser? Has the seller represented this in writing?",
        "legal",
        "Seller Authority",
        follow_up="Unauthorized assignments are void. Requires board resolution and officer certification from seller."
    ),

    ForcingQuestion(
        "L3",
        "In the buyer's jurisdiction, what is the procedure to perfect Purchaser's security interest in the receivable? Has all required notice, filing, or registration been completed?",
        "legal",
        "Security Interest Perfection",
        follow_up="Unperfected interests are subordinate to other creditors. Requires UCC filing (US), PPSA registration (Canada), or equivalent."
    ),

    ForcingQuestion(
        "L4",
        "Are there any statutory or contractual restrictions on the buyer's ability to pay a third party (the Purchaser)? For example, are there anti-assignment clauses in the underlying contract?",
        "legal",
        "Payment Restrictions",
        follow_up="Anti-assignment provisions may make payment to Purchaser unlawful. Requires seller consent or court waiver."
    ),

    ForcingQuestion(
        "L5",
        "What governing law applies to the invoice and the receivables purchase agreement? Is Singapore law (or the chosen forum) the most favorable jurisdiction for enforcing the receivable?",
        "legal",
        "Governing Law & Jurisdiction",
        follow_up="Unfavorable jurisdictions increase collection costs and legal risk. May require buyer guarantees or credit insurance."
    ),

    ForcingQuestion(
        "L6",
        "Has the seller provided complete KYC/AML documentation for itself and the buyer? Are there any sanctions, PEP, or adverse media flags in either party?",
        "legal",
        "KYC/AML Compliance",
        follow_up="Failure to complete KYC creates regulatory risk. Cannot proceed without clean AML clearance."
    ),

    ForcingQuestion(
        "L7",
        "Are there any pending or threatened litigations, arbitrations, or regulatory inquiries involving the seller, buyer, or underlying goods/services? If yes, what is the status and exposure?",
        "legal",
        "Litigation Risk",
        follow_up="Material litigation creates payment uncertainty. Requires escrow holdback or credit enhancement."
    ),

    ForcingQuestion(
        "L8",
        "What are the payment and remedies mechanisms if the buyer defaults? Can Purchaser seize collateral, set-off other payables, or enforce a judgment quickly in the buyer's jurisdiction?",
        "legal",
        "Collection Rights",
        follow_up="Weak enforcement rights reduce recoverable amount. May require guarantees or pre-authorized wire access."
    ),
]


# ============================================================================
# CREDIT RISK AGENT: Buyer & seller financial strength, portfolio risk
# ============================================================================

CREDIT_RISK_AGENT_QUESTIONS = [
    ForcingQuestion(
        "C1",
        "What is the buyer's credit rating (if rated), bank references, or internal credit score? What is their debt level, liquidity, and financial stability trend?",
        "credit",
        "Buyer Financial Strength",
        follow_up="Unrated or financially weak buyers pose high default risk. May require personal guarantee, collateral, or reduced advance."
    ),

    ForcingQuestion(
        "C2",
        "What is the buyer's industry and market position? Are they a market leader, mid-tier, or struggling? What is their market share and competitive risk?",
        "credit",
        "Buyer Business Risk",
        follow_up="High-risk sectors (e.g., retail, shipping in downturn) require larger holdbacks or credit insurance."
    ),

    ForcingQuestion(
        "C3",
        "What is the seller's revenue, EBITDA, and cash position? Are they profitable and growing, or declining? What is their debt-to-equity ratio?",
        "credit",
        "Seller Financial Health",
        follow_up="Weak sellers cannot indemnify if buyer defaults. Requires cash collateral or reduced advance."
    ),

    ForcingQuestion(
        "C4",
        "What is the seller's credit rating or bank references? Have they defaulted on trade credit or loans in the past 3-5 years?",
        "credit",
        "Seller Credit History",
        follow_up="Prior defaults indicate elevated insolvency risk. Requires personal guarantee from owner or cash reserve."
    ),

    ForcingQuestion(
        "C5",
        "What is the concentration risk? What % of Purchaser's portfolio is already exposed to this buyer or seller? What is the aggregate exposure limit?",
        "credit",
        "Portfolio Concentration",
        follow_up="Concentration above 5-10% per buyer/seller increases correlated default risk. May require portfolio rebalancing."
    ),

    ForcingQuestion(
        "C6",
        "In the event of seller insolvency, would purchased receivables be protected from Seller's creditors? Are they perfected and segregated from Seller's estate?",
        "credit",
        "Bankruptcy Protection",
        follow_up="Unperfected interests are lost in seller bankruptcy. Requires UCC filings, asset-level perfection, and non-recourse structure."
    ),

    ForcingQuestion(
        "C7",
        "What is the historical or estimated loss-given-default (LGD) for similar receivables in this buyer/seller combination? What is the recovery rate if buyer defaults?",
        "credit",
        "Expected Loss Modeling",
        follow_up="High LGD (low recovery) requires lower advance or credit insurance. May require 80% advance instead of 90%."
    ),

    ForcingQuestion(
        "C8",
        "Are there macroeconomic or sector-wide headwinds that could materially impact the buyer's ability to pay? For example, commodity price collapse, regulatory changes, or recession?",
        "credit",
        "Macro Risk Factors",
        follow_up="Elevated macro risk requires stress testing of deal assumptions and may require higher discount rates or reduced advance."
    ),
]


# ============================================================================
# Agent decision logic
# ============================================================================

class ProcessAgent:
    """Evaluates invoice quality, delivery proof, buyer confirmations, and deal structure"""

    def __init__(self):
        self.questions = PROCESS_AGENT_QUESTIONS

    def evaluate(self, deal) -> Dict:
        """
        Ask all process questions and aggregate pass/fail.
        Returns: {'decision': 'APPROVE'|'REJECT'|'CONDITIONAL', 'passed': [1,2,3...], 'failed': [...], 'conditions': [...]}
        """
        return {
            "decision": "PENDING",
            "agent": "process",
            "questions": [q.question_id for q in self.questions],
        }


class LegalAgent:
    """Evaluates enforceability, authority, perfection, and compliance"""

    def __init__(self):
        self.questions = LEGAL_AGENT_QUESTIONS

    def evaluate(self, deal) -> Dict:
        return {
            "decision": "PENDING",
            "agent": "legal",
            "questions": [q.question_id for q in self.questions],
        }


class CreditRiskAgent:
    """Evaluates buyer creditworthiness, seller strength, and portfolio concentration"""

    def __init__(self):
        self.questions = CREDIT_RISK_AGENT_QUESTIONS

    def evaluate(self, deal) -> Dict:
        return {
            "decision": "PENDING",
            "agent": "credit",
            "questions": [q.question_id for q in self.questions],
        }


def get_all_questions() -> List[ForcingQuestion]:
    """Return all forcing questions across all agents"""
    return PROCESS_AGENT_QUESTIONS + LEGAL_AGENT_QUESTIONS + CREDIT_RISK_AGENT_QUESTIONS
