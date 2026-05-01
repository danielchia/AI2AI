# Gstack Forcing Questions: Finance Mandate Matching

These are the **forcing questions** each agent asks to standardize deal evaluation. Unlike vague criteria ("good fit"), forcing questions have **specific, checkable answers**.

---

## Process Agent: Investment Thesis & Timeline

**Mission:** Does this deal align with our investment thesis and operational capability?

### Forcing Questions

#### 1. Primary Use of Capital
**Q:** What will the investor's capital be used for?

**Valid answers:**
- `acquisition` - Buying another company
- `growth` - Organic scaling / market expansion
- `debt_paydown` - Refinancing existing debt
- `dividend` - Cash distribution to shareholders
- `infrastructure` - Platform / systems investment
- `working_capital` - Day-to-day operations

**Why it matters:** Investors specialize. A growth-stage PE fund doesn't want acquisition-focused deals; a venture fund doesn't want dividend recaps.

**Agent checks:** `deal.use_of_capital IN mandate.process_criteria.primary_use_of_capital`

---

#### 2. Hold Period / Time to Exit
**Q:** How many years until exit (IPO, secondary, or strategic sale)?

**Valid range:** `[min_years, max_years]` e.g., `[3, 7]`

**Why it matters:** Fund lifecycle. A 5-year fund can't wait 10 years for exit.

**Agent checks:** `deal.hold_period_years WITHIN mandate.process_criteria.hold_period_years`

---

#### 3. Check Size (Capital Deployment)
**Q:** How much capital is the investor deploying?

**Valid range:** `[$min_millions, $max_millions]` e.g., `[$5M, $50M]`

**Why it matters:** 
- Too small: inefficient deployment, not enough upside to justify work
- Too large: concentration risk, portfolio management burden

**Agent checks:** `deal.check_size_usd_millions WITHIN mandate.process_criteria.check_size_usd_millions`

---

#### 4. Expected Internal Rate of Return (IRR)
**Q:** What return is the investor targeting?

**Valid range:** `[min_percent, max_percent]` e.g., `[20%, 30%]`

**Why it matters:** Risk tolerance. A conservative family office targets 12% IRR; a venture fund targets 40%+.

**Agent checks:** `deal.projected_irr >= mandate.process_criteria.target_irr_percent`

---

#### 5. Geography / Jurisdiction
**Q:** Which countries/regions is the company operating in?

**Valid list:** `["US", "EU", "APAC", "LATAM", "MENA"]` or specific countries `["US", "CA", "GB"]`

**Why it matters:** 
- Regulatory expertise (investor has legal teams in certain jurisdictions)
- Tax efficiency
- Currency exposure
- Political risk

**Agent checks:** `ALL deal.geographies IN mandate.process_criteria.geography`

---

#### 6. Industry / Sector
**Q:** What industry is the company in?

**Valid list:** `["software", "fintech", "saas", "healthcare", "manufacturing", ...]`

**Why it matters:** Investors build expertise. They know software economics; they don't know deep manufacturing.

**Agent checks:** `deal.primary_sector IN mandate.process_criteria.sectors` AND `deal.primary_sector NOT IN mandate.process_criteria.exclude_sectors`

---

#### 7. Key Value Drivers
**Q:** What are the 2-3 ways value will be created?

**Valid answers:**
- `organic_growth` - Revenue growth from existing business
- `multiple_expansion` - Increasing valuation multiple (e.g., 10x → 12x EBITDA)
- `bolt_on_acquisition` - Buying smaller companies to add scale
- `operational_improvement` - Cost reduction, margin expansion
- `market_consolidation` - Roll-up strategy

**Why it matters:** Tells you if the investor has the right skillset to help.

**Agent checks:** `deal.value_drivers INTERSECT mandate.process_criteria.target_value_drivers` (if specified)

---

#### 8. Decision Timeline
**Q:** When does the investor need to decide (due diligence complete)?

**Valid format:** `days_from_now` e.g., `30` (decide in 30 days)

**Why it matters:** Investor velocity. Some funds close in 60 days; others take 6 months.

**Agent checks:** `deal.decision_timeline <= mandate.process_criteria.max_decision_days`

---

### Process Agent Decision Logic

```
IF all forcing questions are satisfied:
  RETURN APPROVE

ELSE IF some forcing questions are out of spec but negotiable:
  RETURN ADAPT {
    "issues": [...],
    "possible_changes": [...]
  }

ELSE:
  RETURN REJECT {
    "reason": "Outside mandate scope",
    "hard_blockers": [...]
  }
```

---

## Legal Agent: Contract Terms & Risk

**Mission:** Are the contractual terms acceptable and fair?

### Forcing Questions

#### 1. Governance Rights
**Q:** What control/influence will the investor have post-investment?

**Valid answers:**
- `observer` - Attend board meetings, no voting
- `board_seat` - One seat on board, voting rights
- `board_majority` - Majority of board seats
- `veto_rights` - Can veto certain decisions (e.g., major spend, new debt)
- `information_rights` - Monthly/quarterly financial reports

**Mandate requirement:** `investor.required_governance = ["board_seat", "information_rights"]`

**Agent checks:** `deal.governance_rights INCLUDES ALL investor.required_governance`

---

#### 2. Liquidation Preferences
**Q:** In event of sale/failure, how much do investors get back and in what order?

**Valid answers:**
- `non_participating` - Get preference amount, no upside after
- `participating` - Get preference + pro-rata share of remaining
- `capped_participating` - Preference + shares up to 2x or 3x
- `multiple_X` - 1x, 2x, 3x return of invested capital

**Mandate requirement:** `investor.liquidation_preference = "non_participating"`

**Agent checks:** `deal.liquidation_preference == mandate.legal_criteria.liquidation_preference`

---

#### 3. Anti-Dilution Protection
**Q:** If company raises more money at lower valuation, what happens to investor's shares?

**Valid answers:**
- `none` - Nothing (shares get diluted)
- `full_ratchet` - Shares repriced to lowest future price (harsh)
- `broad_based_weighted_average` - Fair adjustment based on capital raised (standard)
- `narrow_based_weighted_average` - Adjustment based on preferred shares only

**Mandate requirement:** `investor.max_anti_dilution = "broad_based_weighted_average"`

**Agent checks:** `deal.anti_dilution IN mandate.legal_criteria.allowed_anti_dilution_types`

---

#### 4. Non-Compete & Non-Solicit
**Q:** After founder/employee leaves, what restrictions apply?

**Valid format:** `years_of_restriction` e.g., `2` (2-year non-compete)

**Mandate requirement:** `investor.max_non_compete_years = 2`

**Agent checks:** `deal.non_compete_years <= mandate.legal_criteria.max_non_compete_years`

---

#### 5. Material Adverse Change (MAC) Clause
**Q:** What conditions allow the investor to walk away post-signature?

**Valid answers:**
- `standard` - 50%+ drop in EBITDA, key customer loss, regulatory approval failure
- `narrow` - Only legal/regulatory blockers
- `broad` - Any material business change

**Mandate requirement:** `investor.max_mac_scope = "standard"`

**Agent checks:** `deal.mac_scope <= mandate.legal_criteria.max_mac_scope`

---

#### 6. Required Carveouts
**Q:** What exceptions must be carved out (e.g., founder-friendly)?

**Valid answers:**
- `founder_friendly` - Non-competes don't apply to founders
- `equity_pool` - Employee option pool not affected
- `charitable_exceptions` - Charitable work not restricted
- `family_management` - Family members can work elsewhere

**Mandate requirement:** `investor.required_carveouts = ["founder_friendly"]`

**Agent checks:** `deal.carveouts INCLUDES ALL mandate.legal_criteria.required_carveouts`

---

#### 7. Drag-Along / Tag-Along Rights
**Q:** In a sale, can the investor force other shareholders to sell (drag-along), or follow along (tag-along)?

**Valid answers:**
- `drag_along_required` - Investor can force sale
- `tag_along_required` - Investor can follow any sale
- `standard` - Pro-rata rights only

**Mandate requirement:** `investor.requires = ["drag_along"]`

**Agent checks:** `deal.drag_along == true` (if required)

---

#### 8. Founder Vesting / Key Person Clause
**Q:** Is founder equity subject to vesting? What happens if they leave?

**Valid format:** `years` e.g., `4` (4-year vest with 1-year cliff)

**Mandate requirement:** `investor.min_founder_vest_years = 4`

**Agent checks:** `deal.founder_vest_schedule.years >= mandate.legal_criteria.min_founder_vest_years`

---

### Legal Agent Decision Logic

```
issues = []

FOR EACH legal forcing question:
  IF deal violates mandate:
    IF condition is negotiable:
      issues.append({ "category": "adaptable", "change_needed": ... })
    ELSE:
      issues.append({ "category": "hard_blocker", "change_needed": ... })

IF hard_blockers.length > 0:
  RETURN REJECT { "blockers": hard_blockers }

ELSE IF issues.length > 0:
  RETURN ADAPT { "required_changes": issues }

ELSE:
  RETURN APPROVE
```

---

## Compliance Agent: Regulatory & Reputational Risk

**Mission:** Are there legal/regulatory/reputational risks that block the investment?

### Forcing Questions

#### 1. Jurisdiction Risk Assessment
**Q:** Which jurisdictions are involved, and what is the risk level?

**Valid answers:**
```json
{
  "jurisdiction": "US",
  "risk_level": "low"  // "low", "medium", "high", "blocked"
}
```

**Mandate requirement:** `investor.allowed_jurisdictions = ["US", "CA", "GB", "DE"]`

**Blocked jurisdictions:** OFAC list, high-corruption countries, etc.

**Agent checks:** `all(deal.jurisdictions.risk_level != "blocked")`

---

#### 2. AML/KYC (Anti-Money Laundering / Know Your Customer)
**Q:** Have beneficial owners been verified against sanctions/PEP lists?

**Valid answers:**
- `complete` - Full KYC done, all beneficial owners verified
- `pending` - In progress
- `failed` - Sanctions hit or PEP identified

**Mandate requirement:** `investor.aml_kyc_required = true`

**Agent checks:** `deal.aml_kyc_status == "complete"`

---

#### 3. Sanctioned Parties & PEPs
**Q:** Are any founders, board members, or beneficial owners on sanctions lists or politically exposed persons?

**Valid answers:**
- `clean` - No hits
- `review` - Hit on screening, but false positive likely
- `blocked` - Confirmed hit on OFAC or other list

**Mandate requirement:** Mandate may exclude certain lists

**Agent checks:** `deal.sanctions_screening.result == "clean"`

---

#### 4. Sector Restrictions
**Q:** Is the company in a blocked sector?

**Valid answers:**
```json
{
  "sectors": ["defense", "weapons", "gambling", "tobacco", "fossil_fuels"],
  "status": "allowed" // or "blocked"
}
```

**Mandate requirement:** `investor.blocked_sectors = ["weapons", "gambling"]`

**Agent checks:** `deal.primary_sector NOT IN mandate.compliance_criteria.blocked_sectors`

---

#### 5. Environmental / Social / Governance (ESG) Compliance
**Q:** Are there significant ESG violations or controversies?

**Valid answers:**
- `green` - Aligned with ESG
- `yellow` - Minor issues, manageable
- `red` - Major ESG violations

**Mandate requirement:** `investor.min_esg_rating = "yellow"`

**Agent checks:** `deal.esg_rating >= mandate.compliance_criteria.min_esg_rating`

---

#### 6. Export Control / Sanctions Goods
**Q:** Does the company use or export controlled technology/goods?

**Valid answers:**
- `not_applicable` - No export controls apply
- `compliant` - All licenses/approvals in place
- `pending` - Awaiting export control approval
- `blocked` - Cannot obtain licenses

**Mandate requirement:** `investor.allows_export_control_risk = false`

**Agent checks:** `deal.export_control_status != "blocked"`

---

#### 7. Data Privacy / GDPR Compliance
**Q:** Does the company process personal data? Is it GDPR/privacy compliant?

**Valid answers:**
- `not_applicable` - No personal data processing
- `compliant` - Full GDPR/privacy compliance
- `in_progress` - Working toward compliance
- `at_risk` - Known violations

**Mandate requirement:** `investor.requires_privacy_compliance = true`

**Agent checks:** `deal.data_privacy_status IN ["not_applicable", "compliant"]`

---

#### 8. Reputational Risk
**Q:** Is the company or its leadership subject to public controversy?

**Valid answers:**
- `clear` - No public controversies
- `minor` - Contained controversy, not material
- `elevated` - Ongoing controversy or litigation
- `blocked` - Severe reputational risk

**Mandate requirement:** Investors may decline elevated/blocked risk

**Agent checks:** `deal.reputational_risk <= "minor"`

---

### Compliance Agent Decision Logic

```
blockers = []
warnings = []

FOR EACH compliance question:
  IF answer == "blocked":
    blockers.append(question)
  ELSE IF answer == "review" OR "at_risk":
    warnings.append(question)

IF blockers.length > 0:
  RETURN REJECT { "blockers": blockers }

ELSE IF warnings.length > 0:
  RETURN APPROVE_WITH_MONITORING { 
    "conditions": warnings,
    "monitoring_required": true 
  }

ELSE:
  RETURN APPROVE
```

---

## Final Decision Engine

```
RESULTS = {
  process_agent: APPROVE|ADAPT|REJECT,
  legal_agent: APPROVE|ADAPT|REJECT,
  compliance_agent: APPROVE|APPROVE_WITH_MONITORING|REJECT
}

IF ANY agent returns REJECT:
  final_decision = PASS
  reason = "Failed hard blockers: [...]"

ELSE IF ANY agent returns ADAPT:
  final_decision = FLAG_FOR_NEGOTIATION
  required_changes = [
    {agent: "legal", changes: [...]},
    {agent: "process", changes: [...]}
  ]
  negotiation_priority = HIGH if compliance APPROVE else MEDIUM

ELSE IF compliance returns APPROVE_WITH_MONITORING:
  final_decision = APPROVE_WITH_CONDITIONS
  conditions = [...]

ELSE IF ALL return APPROVE:
  final_decision = FUND_IT

RETURN final_decision
```

---

## Example: Complete Evaluation

**Deal:** LinkLogis Trade Receivables Financing, Singapore

**Process Agent:**
- Use of capital: Growth ✓
- Hold period: 4 years ✓
- Check size: $20M ✓
- IRR target: 28% ✓
- Geography: Singapore ✓
- Sector: Fintech/Trade ✓
- Decision timeline: 45 days ✓
- **Result: APPROVE**

**Legal Agent:**
- Governance: Board seat ✓
- Liquidation: Participating (mandate requires non-participating) ✗
- Anti-dilution: Broad-based ✓
- Non-compete: 2 years ✓
- MAC clause: Standard ✓
- **Result: ADAPT** (liquidation preference negotiation needed)

**Compliance Agent:**
- Jurisdiction: Singapore (low risk) ✓
- AML/KYC: Complete ✓
- Sanctions: Clean ✓
- Sectors: Fintech (not blocked) ✓
- ESG: Green ✓
- Privacy: Compliant ✓
- Reputational: Clear ✓
- **Result: APPROVE**

**Final Decision:** `FLAG_FOR_NEGOTIATION`
**Next Step:** Legal team addresses liquidation preference; if changed, → `FUND_IT`

---

**These forcing questions make mandate matching **transparent, repeatable, and defensible**.**
