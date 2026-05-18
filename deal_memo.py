"""
Deal Memo Generator

Produces a structured investor memo from trade receivables evaluation results.
The AI surfaces findings, flags, and options — the investor makes the decision.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Finding:
    """A single finding from agent evaluation"""
    question_id: str
    category: str
    status: str  # "CONFIRMED", "MISSING", "FLAGGED"
    detail: str
    follow_up: Optional[str] = None


@dataclass
class PricingScenario:
    """One pricing option for investor to consider"""
    label: str                  # e.g. "Standard", "Conservative", "Aggressive"
    advance_pct: float
    discount_rate_pa: float
    rationale: str

    @property
    def net_cost_to_seller(self) -> str:
        return f"{self.discount_rate_pa:.1f}% p.a. on {self.advance_pct:.0f}% advance"


@dataclass
class DealMemoInput:
    """Everything needed to generate the investor memo"""
    deal: object                            # Deal schema object
    mandate: object                         # TradeReceivablesMandate object
    process_findings: List[Finding]
    legal_findings: List[Finding]
    credit_findings: List[Finding]
    memo_id: Optional[str] = None
    generated_at: Optional[str] = None

    def __post_init__(self):
        if not self.memo_id:
            self.memo_id = f"MEMO-{self.deal.invoice_number}-{datetime.now().strftime('%Y%m%d')}"
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%B %d, %Y at %H:%M UTC")


class DealMemoGenerator:
    """
    Generates a structured investor memo from evaluation findings.

    Design principle: The AI never says fund or don't fund.
    It surfaces what is known, what is missing, what is risky,
    and what the economics look like at different terms.
    The investor decides.
    """

    def generate(self, memo_input: DealMemoInput) -> Dict:
        """
        Returns both a structured dict (for AI parsing) and
        a formatted text memo (for email / human review).
        """
        deal = memo_input.deal
        mandate = memo_input.mandate

        confirmed = self._filter(memo_input, "CONFIRMED")
        missing = self._filter(memo_input, "MISSING")
        flagged = self._filter(memo_input, "FLAGGED")

        pricing_scenarios = self._build_pricing_scenarios(deal, mandate, flagged, missing)
        open_items = self._build_open_items(missing)
        risk_summary = self._build_risk_summary(flagged)

        structured = {
            "memo_id": memo_input.memo_id,
            "generated_at": memo_input.generated_at,
            "deal": {
                "invoice_number": deal.invoice_number,
                "seller": deal.company_name,
                "buyer": deal.buyer_name,
                "amount_usd": deal.invoice_amount_usd,
                "tenor_days": deal.tenor_days,
                "due_date": deal.due_date,
                "goods": deal.goods_services_description,
            },
            "findings_summary": {
                "confirmed_count": len(confirmed),
                "missing_count": len(missing),
                "flagged_count": len(flagged),
            },
            "confirmed_facts": [{"id": f.question_id, "category": f.category, "detail": f.detail} for f in confirmed],
            "open_items": open_items,
            "risk_flags": risk_summary,
            "pricing_scenarios": [
                {
                    "label": s.label,
                    "advance_pct": s.advance_pct,
                    "discount_rate_pa": s.discount_rate_pa,
                    "amount_advanced_usd": round(deal.invoice_amount_usd * s.advance_pct / 100, 2),
                    "rationale": s.rationale,
                }
                for s in pricing_scenarios
            ],
            "next_steps": self._build_next_steps(missing, flagged),
            "full_memo_text": self._format_memo_text(memo_input, confirmed, missing, flagged, pricing_scenarios),
        }

        return structured

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _filter(self, memo_input: DealMemoInput, status: str) -> List[Finding]:
        all_findings = (
            memo_input.process_findings
            + memo_input.legal_findings
            + memo_input.credit_findings
        )
        return [f for f in all_findings if f.status == status]

    def _build_pricing_scenarios(
        self,
        deal,
        mandate,
        flagged: List[Finding],
        missing: List[Finding],
    ) -> List[PricingScenario]:
        base_advance = mandate.financing_terms.advance_percentage
        base_rate = mandate.financing_terms.discount_rate_percent_pa

        scenarios = []

        # Standard — no issues
        scenarios.append(PricingScenario(
            label="Standard (Mandate Terms)",
            advance_pct=base_advance,
            discount_rate_pa=base_rate,
            rationale="All criteria met at mandate standard terms.",
        ))

        # Conservative — for flagged/missing items
        if flagged or missing:
            conservative_advance = max(base_advance - 10, 75.0)
            conservative_rate = base_rate + 1.0
            scenarios.append(PricingScenario(
                label="Conservative (Risk-Adjusted)",
                advance_pct=conservative_advance,
                discount_rate_pa=conservative_rate,
                rationale=(
                    f"Reduced advance and higher discount to reflect "
                    f"{len(flagged)} risk flag(s) and {len(missing)} open item(s). "
                    "Holdback released once open items resolved."
                ),
            ))

        # Aggressive — for investor who wants to move fast
        if not missing:
            aggressive_advance = min(base_advance + 2, 95.0)
            aggressive_rate = max(base_rate - 0.5, 3.0)
            scenarios.append(PricingScenario(
                label="Aggressive (Relationship Pricing)",
                advance_pct=aggressive_advance,
                discount_rate_pa=aggressive_rate,
                rationale="No missing documentation. Buyer payment history strong. "
                          "Offered as relationship pricing for repeat sellers.",
            ))

        return scenarios

    def _build_open_items(self, missing: List[Finding]) -> List[Dict]:
        return [
            {
                "id": f.question_id,
                "category": f.category,
                "what_is_missing": f.detail,
                "action_required": f.follow_up or "Obtain from seller/buyer before funding.",
            }
            for f in missing
        ]

    def _build_risk_summary(self, flagged: List[Finding]) -> List[Dict]:
        return [
            {
                "id": f.question_id,
                "category": f.category,
                "flag": f.detail,
                "investor_consideration": f.follow_up or "Investor to assess materiality.",
            }
            for f in flagged
        ]

    def _build_next_steps(self, missing: List[Finding], flagged: List[Finding]) -> List[str]:
        steps = []
        if missing:
            steps.append(f"Resolve {len(missing)} open item(s) — see Open Items section.")
        if flagged:
            steps.append(f"Investor to review {len(flagged)} risk flag(s) and determine materiality.")
        if not missing and not flagged:
            steps.append("All items confirmed. Investor to select pricing scenario and proceed if desired.")
        steps.append("Execute Master Receivables Purchase Agreement upon investor approval.")
        steps.append("Advance funds per agreed pricing scenario within 2 business days of execution.")
        return steps

    def _format_memo_text(
        self,
        memo_input: DealMemoInput,
        confirmed: List[Finding],
        missing: List[Finding],
        flagged: List[Finding],
        scenarios: List[PricingScenario],
    ) -> str:
        deal = memo_input.deal
        mandate = memo_input.mandate

        lines = []

        lines += [
            f"DEAL MEMO — FOR INVESTOR REVIEW",
            f"{'=' * 50}",
            f"Memo ID:   {memo_input.memo_id}",
            f"Prepared:  {memo_input.generated_at}",
            f"Mandate:   {mandate.mandate_name} ({mandate.fund_manager})",
            "",
            "DEAL SUMMARY",
            f"{'-' * 30}",
            f"Seller:        {deal.company_name} ({deal.seller_incorporation})",
            f"Buyer:         {deal.buyer_name} ({deal.buyer_jurisdiction})",
            f"Invoice:       {deal.invoice_number}",
            f"Amount:        USD {deal.invoice_amount_usd:,.2f}",
            f"Tenor:         {deal.tenor_days} days",
            f"Due Date:      {deal.due_date}",
            f"Goods:         {deal.goods_services_description}",
            f"Purpose:       {deal.purpose}",
            "",
            "EVALUATION SUMMARY",
            f"{'-' * 30}",
            f"  Confirmed facts:   {len(confirmed)} of 24 questions answered satisfactorily",
            f"  Open items:        {len(missing)} items require further information",
            f"  Risk flags:        {len(flagged)} items flagged for investor attention",
            "",
        ]

        # Confirmed facts
        lines += ["WHAT WE KNOW (CONFIRMED)", f"{'-' * 30}"]
        if confirmed:
            for f in confirmed:
                lines.append(f"  [{f.question_id}] {f.category}: {f.detail}")
        else:
            lines.append("  No items fully confirmed yet.")
        lines.append("")

        # Open items
        lines += ["WHAT IS MISSING (OPEN ITEMS)", f"{'-' * 30}"]
        if missing:
            for f in missing:
                lines.append(f"  [{f.question_id}] {f.category}")
                lines.append(f"    Missing:  {f.detail}")
                if f.follow_up:
                    lines.append(f"    Action:   {f.follow_up}")
        else:
            lines.append("  No missing items. All documentation accounted for.")
        lines.append("")

        # Risk flags
        lines += ["RISK FLAGS (INVESTOR TO ASSESS)", f"{'-' * 30}"]
        if flagged:
            for f in flagged:
                lines.append(f"  [{f.question_id}] {f.category}")
                lines.append(f"    Flag:     {f.detail}")
                if f.follow_up:
                    lines.append(f"    Consider: {f.follow_up}")
        else:
            lines.append("  No risk flags identified.")
        lines.append("")

        # Pricing scenarios
        lines += ["PRICING SCENARIOS (INVESTOR TO SELECT)", f"{'-' * 30}"]
        for s in scenarios:
            amount_advanced = deal.invoice_amount_usd * s.advance_pct / 100
            lines += [
                f"  {s.label}",
                f"    Advance:       {s.advance_pct:.0f}% = USD {amount_advanced:,.2f}",
                f"    Discount Rate: {s.discount_rate_pa:.1f}% p.a.",
                f"    Rationale:     {s.rationale}",
                "",
            ]

        # Next steps
        lines += ["NEXT STEPS", f"{'-' * 30}"]
        for step in self._build_next_steps(missing, flagged):
            lines.append(f"  - {step}")
        lines.append("")

        lines += [
            f"{'=' * 50}",
            "This memo was prepared by AI2AI's automated evaluation system.",
            "All funding decisions remain with the investor.",
            f"{'=' * 50}",
        ]

        return "\n".join(lines)
