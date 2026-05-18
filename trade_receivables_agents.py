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
# Agent finding logic
#
# Design principle: Agents surface facts, gaps, and flags.
# They do NOT make funding decisions — that is the investor's role.
#
# Each agent returns a list of Finding objects:
#   CONFIRMED  — question answered satisfactorily from deal data
#   MISSING    — information not provided, must be obtained before funding
#   FLAGGED    — information present but warrants investor attention
# ============================================================================

from deal_memo import Finding


class ProcessAgent:
    """
    Evaluates invoice quality, delivery proof, buyer confirmations, and deal structure.
    Surfaces what is confirmed, what is missing, and what should be reviewed.
    """

    def __init__(self):
        self.questions = PROCESS_AGENT_QUESTIONS

    def evaluate(self, deal) -> List[Finding]:
        findings = []

        # P1: Invoice tenor
        if deal.tenor_days < 90 or deal.tenor_days > 120:
            findings.append(Finding(
                question_id="P1",
                category="Invoice Eligibility",
                status="FLAGGED",
                detail=f"Tenor is {deal.tenor_days} days, outside standard 90-120 day window.",
                follow_up="Investor to confirm whether tenor exception is acceptable.",
            ))
        else:
            findings.append(Finding(
                question_id="P1",
                category="Invoice Eligibility",
                status="CONFIRMED",
                detail=f"Tenor {deal.tenor_days} days is within mandate parameters (90-120 days).",
            ))

        # P2: Buyer confirmation
        if deal.buyer_confirmation_obtained:
            findings.append(Finding(
                question_id="P2",
                category="Buyer Confirmation",
                status="CONFIRMED",
                detail="Buyer has confirmed invoice is valid, accurate, and payable.",
            ))
        else:
            findings.append(Finding(
                question_id="P2",
                category="Buyer Confirmation",
                status="MISSING",
                detail="Buyer written confirmation of invoice validity has not been obtained.",
                follow_up="Must obtain buyer confirmation before funding. This is a hard requirement.",
            ))

        # P3: Payment history
        if deal.buyer_payment_history:
            history = deal.buyer_payment_history.lower()
            if "late" in history or "overdue" in history or "default" in history:
                findings.append(Finding(
                    question_id="P3",
                    category="Buyer Payment History",
                    status="FLAGGED",
                    detail=f"Payment history notes: {deal.buyer_payment_history}",
                    follow_up="Investor to assess whether payment pattern is material to pricing.",
                ))
            else:
                findings.append(Finding(
                    question_id="P3",
                    category="Buyer Payment History",
                    status="CONFIRMED",
                    detail=f"Payment history: {deal.buyer_payment_history}",
                ))
        else:
            findings.append(Finding(
                question_id="P3",
                category="Buyer Payment History",
                status="MISSING",
                detail="No payment history provided for this buyer.",
                follow_up="Obtain at least 12 months of payment history from seller records.",
            ))

        # P4: Disputes
        disputes = deal.buyer_disputes_history or ""
        if disputes.lower() in ["none", "no disputes", "nil", ""]:
            findings.append(Finding(
                question_id="P4",
                category="Historical Disputes",
                status="CONFIRMED",
                detail="No disputes or offsets reported between seller and buyer.",
            ))
        else:
            findings.append(Finding(
                question_id="P4",
                category="Historical Disputes",
                status="FLAGGED",
                detail=f"Dispute history noted: {disputes}",
                follow_up="Investor to review dispute details and confirm they are fully resolved.",
            ))

        # P5: Delivery proof
        if deal.delivery_proof_type:
            findings.append(Finding(
                question_id="P5",
                category="Delivery Proof",
                status="CONFIRMED",
                detail=f"Delivery evidenced by: {deal.delivery_proof_type}. Delivery date: {deal.delivery_date}.",
            ))
        else:
            findings.append(Finding(
                question_id="P5",
                category="Delivery Proof",
                status="MISSING",
                detail="No proof of delivery or service completion provided.",
                follow_up="Obtain bill of lading, signed delivery receipt, or service completion certificate.",
            ))

        # P6: Relationship tenure
        months = deal.buyer_relationship_months or 0
        if months >= 12:
            findings.append(Finding(
                question_id="P6",
                category="Relationship Tenure",
                status="CONFIRMED",
                detail=f"Seller-buyer relationship is {months} months. Established trading history.",
            ))
        elif months > 0:
            findings.append(Finding(
                question_id="P6",
                category="Relationship Tenure",
                status="FLAGGED",
                detail=f"Seller-buyer relationship is only {months} months.",
                follow_up="Short relationship carries higher counterparty risk. Investor to consider additional holdback.",
            ))
        else:
            findings.append(Finding(
                question_id="P6",
                category="Relationship Tenure",
                status="MISSING",
                detail="Length of seller-buyer relationship not provided.",
                follow_up="Confirm how long seller has been trading with this buyer.",
            ))

        # P7: Title clearance — requires seller representation
        findings.append(Finding(
            question_id="P7",
            category="Title Clearance",
            status="MISSING",
            detail="Seller has not yet provided written representation that invoice is unencumbered and not previously assigned.",
            follow_up="Obtain seller title representation as part of Master Receivables Purchase Agreement execution.",
        ))

        # P8: Financing economics
        if deal.funding_requested_percentage > 92:
            findings.append(Finding(
                question_id="P8",
                category="Financing Economics",
                status="FLAGGED",
                detail=f"Seller is requesting {deal.funding_requested_percentage}% advance, above standard 90%.",
                follow_up="Investor to assess whether elevated advance is appropriate given buyer credit quality.",
            ))
        else:
            findings.append(Finding(
                question_id="P8",
                category="Financing Economics",
                status="CONFIRMED",
                detail=f"Advance requested: {deal.funding_requested_percentage}%. Within standard parameters.",
            ))

        return findings


class LegalAgent:
    """
    Evaluates enforceability, authority, security interest, and regulatory compliance.
    Surfaces what is confirmed, what is missing, and what should be reviewed.
    """

    def __init__(self):
        self.questions = LEGAL_AGENT_QUESTIONS

    def evaluate(self, deal) -> List[Finding]:
        findings = []

        # L1: Invoice enforceability — always requires legal confirmation
        findings.append(Finding(
            question_id="L1",
            category="Invoice Enforceability",
            status="MISSING",
            detail="Legal review of invoice and underlying contract enforceability not yet completed.",
            follow_up="Confirm invoice and purchase order are legally compliant and obligations are clear.",
        ))

        # L2: Seller authority to assign
        findings.append(Finding(
            question_id="L2",
            category="Seller Authority",
            status="MISSING",
            detail="Seller written representation of authority to assign receivable not yet obtained.",
            follow_up="Obtain board resolution or officer certification confirming seller's right to assign.",
        ))

        # L3: Security interest perfection
        findings.append(Finding(
            question_id="L3",
            category="Security Interest Perfection",
            status="MISSING",
            detail="Security interest perfection steps (UCC filing, PPSA, or equivalent) not yet confirmed.",
            follow_up=f"Identify applicable jurisdiction ({deal.buyer_jurisdiction}) and complete required filings before funding.",
        ))

        # L4: Payment restrictions — flag for legal review
        findings.append(Finding(
            question_id="L4",
            category="Payment Restrictions",
            status="MISSING",
            detail="Underlying contract has not been reviewed for anti-assignment or payment restriction clauses.",
            follow_up="Review purchase order / supply agreement for any clause restricting payment to third parties.",
        ))

        # L5: Governing law
        buyer_jx = deal.buyer_jurisdiction
        if buyer_jx.lower() in ["singapore", "sg", "united kingdom", "uk", "united states", "us", "australia"]:
            findings.append(Finding(
                question_id="L5",
                category="Governing Law",
                status="CONFIRMED",
                detail=f"Buyer jurisdiction ({buyer_jx}) is a common law jurisdiction with strong receivables enforcement.",
            ))
        else:
            findings.append(Finding(
                question_id="L5",
                category="Governing Law",
                status="FLAGGED",
                detail=f"Buyer jurisdiction is {buyer_jx}. Enforceability of receivables in this jurisdiction should be verified.",
                follow_up="Obtain local counsel confirmation that receivable is enforceable and Purchaser's interest can be perfected.",
            ))

        # L6: KYC/AML
        findings.append(Finding(
            question_id="L6",
            category="KYC/AML Compliance",
            status="MISSING",
            detail="KYC/AML documentation for seller and buyer not yet confirmed as complete and clear.",
            follow_up="Confirm KYC/AML packs received, screened against OFAC/EU/UN sanctions lists, and cleared.",
        ))

        # L7: Litigation
        findings.append(Finding(
            question_id="L7",
            category="Litigation Risk",
            status="MISSING",
            detail="No confirmation obtained that seller and buyer are free of material pending litigation.",
            follow_up="Obtain seller and buyer litigation representations. Run public court record searches.",
        ))

        # L8: Collection rights
        findings.append(Finding(
            question_id="L8",
            category="Collection Rights",
            status="MISSING",
            detail="Payment and remedies mechanisms upon buyer default have not been documented.",
            follow_up="Confirm Purchaser's collection rights, including ability to enforce judgment in buyer's jurisdiction.",
        ))

        return findings


class CreditRiskAgent:
    """
    Evaluates buyer creditworthiness, seller financial health, and portfolio concentration.
    Surfaces what is confirmed, what is missing, and what should be reviewed.
    """

    def __init__(self):
        self.questions = CREDIT_RISK_AGENT_QUESTIONS

    def evaluate(self, deal) -> List[Finding]:
        findings = []

        # C1: Buyer financial strength
        if deal.buyer_credit_score:
            if deal.buyer_credit_score >= 700:
                findings.append(Finding(
                    question_id="C1",
                    category="Buyer Financial Strength",
                    status="CONFIRMED",
                    detail=f"Buyer credit score: {deal.buyer_credit_score}. Indicates strong creditworthiness.",
                ))
            else:
                findings.append(Finding(
                    question_id="C1",
                    category="Buyer Financial Strength",
                    status="FLAGGED",
                    detail=f"Buyer credit score: {deal.buyer_credit_score}. Below strong threshold.",
                    follow_up="Investor to assess whether credit score reflects current financial position and whether additional collateral is warranted.",
                ))
        else:
            findings.append(Finding(
                question_id="C1",
                category="Buyer Financial Strength",
                status="FLAGGED",
                detail="Buyer is unrated. No formal credit score or rating agency assessment available.",
                follow_up="Investor to consider requesting buyer bank references, management accounts, or trade credit report.",
            ))

        # C2: Buyer business risk
        goods = deal.goods_services_description.lower()
        high_risk_keywords = ["oil", "gas", "coal", "shipping", "retail", "crypto", "real estate"]
        flagged_sector = next((k for k in high_risk_keywords if k in goods), None)
        if flagged_sector:
            findings.append(Finding(
                question_id="C2",
                category="Buyer Business Risk",
                status="FLAGGED",
                detail=f"Goods/services ({deal.goods_services_description}) may relate to a cyclical or higher-risk sector ({flagged_sector}).",
                follow_up="Investor to assess whether sector headwinds materially affect buyer's ability to pay.",
            ))
        else:
            findings.append(Finding(
                question_id="C2",
                category="Buyer Business Risk",
                status="CONFIRMED",
                detail=f"Goods/services ({deal.goods_services_description}) do not appear to indicate elevated sector risk.",
            ))

        # C3: Seller financial health
        financials = deal.seller_financials_summary or {}
        if financials:
            revenue = financials.get("annual_revenue_usd", 0)
            ebitda = financials.get("ebitda_margin_pct", 0)
            liquidity = financials.get("liquidity_months", 0)
            if ebitda > 5 and liquidity >= 3:
                findings.append(Finding(
                    question_id="C3",
                    category="Seller Financial Health",
                    status="CONFIRMED",
                    detail=f"Seller revenue USD {revenue:,.0f}, EBITDA margin {ebitda}%, liquidity {liquidity} months. Financially stable.",
                ))
            else:
                findings.append(Finding(
                    question_id="C3",
                    category="Seller Financial Health",
                    status="FLAGGED",
                    detail=f"Seller financials show EBITDA margin {ebitda}% and {liquidity} months liquidity. May be thin.",
                    follow_up="Investor to assess whether seller can cover indemnification obligations if buyer defaults.",
                ))
        else:
            findings.append(Finding(
                question_id="C3",
                category="Seller Financial Health",
                status="MISSING",
                detail="Seller financial summary (revenue, EBITDA, liquidity) not provided.",
                follow_up="Request seller management accounts or audited financials to assess indemnification capacity.",
            ))

        # C4: Seller credit history
        findings.append(Finding(
            question_id="C4",
            category="Seller Credit History",
            status="MISSING",
            detail="Seller's credit history and any prior loan defaults have not been confirmed.",
            follow_up="Obtain seller bank references or credit bureau report for the past 3 years.",
        ))

        # C5: Portfolio concentration
        findings.append(Finding(
            question_id="C5",
            category="Portfolio Concentration",
            status="MISSING",
            detail="Current portfolio concentration for this buyer and seller has not been checked against mandate limits.",
            follow_up=f"Confirm this deal does not breach single-buyer or single-seller concentration limits before funding.",
        ))

        # C6: Bankruptcy protection
        findings.append(Finding(
            question_id="C6",
            category="Bankruptcy Protection",
            status="MISSING",
            detail="Confirmation that purchased receivables are bankruptcy-remote from seller's estate not yet obtained.",
            follow_up="Confirm perfection of security interest and non-recourse structure protects Purchaser in seller insolvency.",
        ))

        # C7: Expected loss modeling
        findings.append(Finding(
            question_id="C7",
            category="Expected Loss Modeling",
            status="MISSING",
            detail="Loss-given-default estimate for this buyer/seller combination not provided.",
            follow_up="Investor to assess recovery rate assumptions and whether advance percentage reflects expected LGD.",
        ))

        # C8: Macro risk
        findings.append(Finding(
            question_id="C8",
            category="Macro Risk Factors",
            status="MISSING",
            detail="No macro or sector stress assessment has been completed for this deal.",
            follow_up="Investor to consider current macro environment (rates, trade policy, currency) as it relates to buyer's payment capacity.",
        ))

        return findings


def get_all_questions() -> List[ForcingQuestion]:
    """Return all forcing questions across all agents"""
    return PROCESS_AGENT_QUESTIONS + LEGAL_AGENT_QUESTIONS + CREDIT_RISK_AGENT_QUESTIONS
