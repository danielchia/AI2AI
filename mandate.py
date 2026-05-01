"""
Mandate Schema Definitions

This module defines the Pydantic models for investor mandates and deal proposals.
Mandates describe what an investor wants. Deals describe what a founder is pitching.
Validators ensure both are well-formed before evaluation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class UseOfCapital(str, Enum):
    """Valid uses of capital that investors can require."""
    ACQUISITION = "acquisition"
    GROWTH = "growth"
    INFRASTRUCTURE = "infrastructure"
    WORKING_CAPITAL = "working_capital"
    DEBT_PAYDOWN = "debt_paydown"


class LiquidationPreference(str, Enum):
    """Types of liquidation preferences investors can require."""
    NON_PARTICIPATING = "non_participating"
    PARTICIPATING = "participating"
    CAPPED = "capped"


class GovernanceRight(str, Enum):
    """Governance rights investors can require."""
    BOARD_SEAT = "board_seat"
    BOARD_OBSERVER = "board_observer"
    INFORMATION_RIGHTS = "information_rights"
    VETO_RIGHTS = "veto_rights"
    PRO_RATA = "pro_rata"


class ProcessCriteria(BaseModel):
    """Process Agent criteria: Does this deal fit the investment thesis?"""

    primary_use_of_capital: List[UseOfCapital] = Field(
        description="Approved uses of capital (acquisition, growth, etc)"
    )
    hold_period_years: tuple = Field(
        description="Acceptable hold period as (min, max)"
    )
    check_size_usd_millions: tuple = Field(
        description="Acceptable check size as (min, max)"
    )
    target_irr_percent: float = Field(
        description="Minimum IRR required"
    )
    geography: List[str] = Field(
        description="Approved countries/regions (e.g., US, SG, UK)"
    )
    sectors: List[str] = Field(
        description="Approved sectors (e.g., fintech, software, healthcare)"
    )
    exclude_sectors: List[str] = Field(
        default=[], description="Explicitly excluded sectors"
    )
    max_decision_days: int = Field(
        default=60, description="Maximum days investor can take to decide"
    )


class LegalCriteria(BaseModel):
    """Legal Agent criteria: Are contract terms acceptable?"""

    required_governance: List[GovernanceRight] = Field(
        description="Required governance rights (board seat, veto, etc)"
    )
    liquidation_preference: LiquidationPreference = Field(
        description="Required liquidation preference"
    )
    anti_dilution: str = Field(
        default="broad_based_weighted_average",
        description="Anti-dilution protection required"
    )
    max_non_compete_years: int = Field(
        default=2, description="Maximum non-compete duration acceptable"
    )
    require_drag_tag: bool = Field(
        default=True, description="Require drag-along and tag-along rights"
    )
    founder_vesting_min_years: int = Field(
        default=4, description="Minimum founder vesting period required"
    )
    required_carveouts: List[str] = Field(
        default=["equity_pool", "founder_friendly"],
        description="Required carveouts in cap table"
    )
    mac_clause_required: bool = Field(
        default=True, description="Material Adverse Change clause required"
    )


class ComplianceCriteria(BaseModel):
    """Compliance Agent criteria: Are there regulatory/reputational risks?"""

    allowed_jurisdictions: List[str] = Field(
        description="Approved countries for operations"
    )
    aml_kyc_required: bool = Field(
        default=True, description="AML/KYC verification required"
    )
    sanctions_screening_required: bool = Field(
        default=True, description="Sanctions and PEP screening required"
    )
    blocked_sectors: List[str] = Field(
        default=["weapons", "gambling", "fossil_fuels", "tobacco"],
        description="Sectors investor will not fund"
    )
    min_esg_rating: str = Field(
        default="yellow", description="Minimum ESG rating (green, yellow, red)"
    )
    data_privacy_required: bool = Field(
        default=True, description="Data privacy compliance required"
    )
    export_control_risk_acceptable: bool = Field(
        default=False, description="Accept export control risk"
    )


class InvestorMandate(BaseModel):
    """Complete investor mandate definition."""

    investor_name: str = Field(description="Name of investor/fund")
    mandate_id: str = Field(description="Unique mandate identifier")
    process_criteria: ProcessCriteria
    legal_criteria: LegalCriteria
    compliance_criteria: ComplianceCriteria
    notes: Optional[str] = Field(default=None, description="Additional notes")


class DealProcess(BaseModel):
    """Deal's process information (answered by founder)."""

    use_of_capital: UseOfCapital
    hold_period_years: int
    check_size_usd_millions: float
    projected_irr: float
    geographies: List[str]
    primary_sector: str
    value_drivers: str = Field(
        description="How will value be created (acquisition, organic growth, etc)"
    )
    decision_deadline_days: int = Field(
        default=30, description="Days until founder needs decision"
    )


class DealLegal(BaseModel):
    """Deal's legal structure (proposed by founder)."""

    governance_rights: List[GovernanceRight]
    liquidation_preference: LiquidationPreference
    anti_dilution: str
    non_compete_years: int
    drag_tag_rights: bool
    founder_vesting_years: int
    founder_vesting_cliff_months: int
    cap_table_summary: str = Field(
        description="Brief description of cap table structure"
    )
    mac_clause_included: bool


class ComplianceInfo(BaseModel):
    """Deal's compliance information (facts about company)."""

    jurisdictions: List[Dict[str, str]] = Field(
        description="List of {country, risk_level} where company operates"
    )
    aml_kyc_status: str = Field(
        description="Status of AML/KYC verification (complete, pending, failed)"
    )
    sanctions_screening_result: str = Field(
        description="Sanctions screening result (clean, flagged, pending)"
    )
    pep_screening_result: str = Field(
        description="PEP (Politically Exposed Person) screening result"
    )
    primary_sector: str = Field(
        description="Industry sector"
    )
    esg_rating: str = Field(
        description="ESG rating if available (green, yellow, red)"
    )
    data_privacy_status: str = Field(
        description="Data privacy compliance status (compliant, non-compliant, pending)"
    )
    export_control_relevant: bool = Field(
        default=False, description="Does deal involve export control items"
    )
    reputational_concerns: Optional[str] = Field(
        default=None, description="Any known reputational risks"
    )


class DealProposal(BaseModel):
    """Complete deal proposal submitted by founder."""

    deal_id: str = Field(description="Unique deal identifier")
    company_name: str = Field(description="Name of company")
    founder_names: List[str] = Field(description="Founder/CEO names")
    process_section: DealProcess
    legal_section: DealLegal
    compliance_section: ComplianceInfo
    company_description: Optional[str] = Field(
        default=None, description="Brief company description"
    )
    financial_highlights: Optional[Dict[str, Any]] = Field(
        default=None, description="Revenue, growth rate, runway, etc"
    )


class EvaluationRequest(BaseModel):
    """Request to evaluate a deal against a mandate."""

    mandate: InvestorMandate
    deal: DealProposal


# Validation helpers
def validate_mandate(mandate_dict: dict) -> InvestorMandate:
    """Parse and validate investor mandate from dict."""
    return InvestorMandate(**mandate_dict)


def validate_deal(deal_dict: dict) -> DealProposal:
    """Parse and validate deal proposal from dict."""
    return DealProposal(**deal_dict)


def validate_evaluation_request(
    mandate_dict: dict, deal_dict: dict
) -> EvaluationRequest:
    """Parse and validate complete evaluation request."""
    mandate = validate_mandate(mandate_dict)
    deal = validate_deal(deal_dict)
    return EvaluationRequest(mandate=mandate, deal=deal)
