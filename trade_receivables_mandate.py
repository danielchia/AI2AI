"""
Trade Receivables Financing Mandate Schema
Extracted from LinkLogis/ChemTank Master Receivables Purchase Agreement experience
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from enum import Enum


class ReceiverQuality(BaseModel):
    """Buyer credit quality assessment"""
    credit_rating: Optional[str] = Field(None, description="Moody's/S&P rating or equivalent")
    years_in_business: Optional[int] = Field(None, description="Years of operational history")
    payment_history_score: Optional[int] = Field(None, description="0-100 scale, payment timeliness")
    regulatory_status: str = Field(description="e.g., 'regulated', 'compliant', 'under review'")
    jurisdiction: str = Field(description="Country/jurisdiction of buyer")
    no_active_disputes: bool = Field(True, description="No material litigation with suppliers")
    financial_stability: Literal["strong", "stable", "at_risk", "distressed"] = Field(description="Buyer solvency assessment")


class SellerQuality(BaseModel):
    """Seller (originator) quality assessment"""
    years_in_business: Optional[int] = Field(None, description="Seller operational history")
    good_standing: bool = Field(True, description="Registered/licensed in home jurisdiction")
    not_in_insolvency: bool = Field(True, description="Seller not in bankruptcy/liquidation")
    no_material_litigation: bool = Field(True, description="No material legal claims")
    regulatory_compliance: Literal["fully_compliant", "substantially_compliant", "at_risk"] = Field(description="Compliance status")


class InvoiceCharacteristics(BaseModel):
    """Eligible receivable invoice criteria"""
    tenor_days_min: int = Field(90, description="Minimum invoice tenor in days")
    tenor_days_max: int = Field(120, description="Maximum invoice tenor in days")
    invoice_amount_min_usd: Optional[float] = Field(None, description="Minimum transaction size")
    invoice_amount_max_usd: Optional[float] = Field(None, description="Maximum transaction size")
    goods_services_delivered: bool = Field(True, description="Proof of delivery/performance required")
    buyer_confirmation_required: bool = Field(True, description="Buyer must confirm invoice validity")
    no_prior_payment: bool = Field(True, description="Invoice not previously paid/canceled")


class CollateralDocumentation(BaseModel):
    """Supporting documents and collateral"""
    invoice_copy: bool = Field(True, description="Copy of invoice required")
    proof_of_delivery: bool = Field(True, description="BoL, delivery receipt, or service completion")
    buyer_confirmation: bool = Field(True, description="Written buyer confirmation of validity")
    seller_kyc_aml: bool = Field(True, description="Seller KYC/AML documentation")
    buyer_kyc_aml: bool = Field(True, description="Buyer KYC/AML documentation")
    additional_docs: Optional[List[str]] = Field(None, description="Additional required docs (e.g., LoI, contract)")


class FinancingTerms(BaseModel):
    """Financing structure and economics"""
    advance_percentage: float = Field(90.0, description="Advance as % of invoice (typically 85-95%)")
    holdback_percentage: float = Field(10.0, description="Holdback as % of invoice (released post-payment)")
    discount_rate_percent_pa: float = Field(5.0, description="Annual discount rate for time value of money")
    buffer_period_days: int = Field(30, description="Grace period after due date before default")
    max_overdue_days_allowed: Optional[int] = Field(None, description="Max days overdue before repurchase/indemnification")
    recourse_type: Literal["non_recourse", "limited_recourse", "full_recourse"] = Field(
        "non_recourse",
        description="Seller liability if buyer doesn't pay"
    )


class TradeReceivablesMandate(BaseModel):
    """Trade Receivables Financing Mandate"""
    mandate_name: str = Field(description="Fund or program name")
    fund_manager: str = Field(description="Asset manager name")
    investor_jurisdiction: str = Field(description="Fund registration jurisdiction")

    # Credit quality thresholds
    buyer_quality: ReceiverQuality = Field(description="Buyer credit requirements")
    seller_quality: SellerQuality = Field(description="Seller/originator quality requirements")

    # Invoice eligibility
    invoice_criteria: InvoiceCharacteristics = Field(description="Eligible invoice specifications")

    # Documentation
    required_documentation: CollateralDocumentation = Field(description="Supporting documents required")

    # Financing economics
    financing_terms: FinancingTerms = Field(description="Advance, holdback, discount rates")

    # Portfolio constraints
    max_concentration_single_buyer_pct: Optional[float] = Field(None, description="Max % of portfolio from one buyer")
    max_concentration_single_seller_pct: Optional[float] = Field(None, description="Max % of portfolio from one originator")
    allowed_industries: Optional[List[str]] = Field(None, description="Sector restrictions (e.g., 'chemicals', 'commodities')")
    excluded_jurisdictions: Optional[List[str]] = Field(None, description="Geographic restrictions")

    # Additional criteria
    min_buyer_experience_months: Optional[int] = Field(None, description="Buyer track record with seller")
    max_aggregate_exposure_usd: Optional[float] = Field(None, description="Maximum total exposure")


class Deal(BaseModel):
    """Trade receivable deal submission for evaluation"""
    company_name: str = Field(description="Seller name")
    seller_incorporation: str = Field(description="Seller jurisdiction and company type")

    buyer_name: str = Field(description="Account debtor / buyer name")
    buyer_jurisdiction: str = Field(description="Buyer jurisdiction")
    buyer_credit_score: Optional[int] = Field(None, description="Credit score if available")
    buyer_relationship_months: Optional[int] = Field(None, description="How long seller has been working with buyer")
    buyer_payment_history: Optional[str] = Field(None, description="Payment performance (e.g., 'on-time', '5 days late average')")

    invoice_number: str = Field(description="Invoice identifier")
    invoice_date: str = Field(description="Date invoice issued (YYYY-MM-DD)")
    invoice_amount_usd: float = Field(description="Invoice face amount in USD")
    due_date: str = Field(description="Invoice due date (YYYY-MM-DD)")
    tenor_days: int = Field(description="Days from invoice date to due date")

    goods_services_description: str = Field(description="What was delivered/performed")
    delivery_date: str = Field(description="Date goods delivered or services completed")
    delivery_proof_type: str = Field(description="Type of proof (BoL, receipt, signed contract, etc.)")

    buyer_confirmation_obtained: bool = Field(True, description="Has buyer confirmed invoice validity")
    buyer_disputes_history: Optional[str] = Field(None, description="Any known disputes or claims")

    seller_financials_summary: Optional[Dict] = Field(None, description="Seller revenue, EBITDA, liquidity")

    funding_requested_percentage: float = Field(90.0, description="Advance % requested (typically 85-95%)")
    purpose: str = Field(description="Why seller needs financing (working capital, growth, etc.)")
