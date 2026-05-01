"""
Three Evaluation Agents

Each agent asks forcing questions (Gstack methodology) to evaluate deals.
- Process Agent: Does the deal fit the investment thesis?
- Legal Agent: Are the contract terms acceptable?
- Compliance Agent: Are there regulatory/reputational risks?

Each returns APPROVE, ADAPT, or REJECT based on forcing question responses.
"""

import json
import anthropic
from mandate import InvestorMandate, DealProposal


class Agent:
    """Base agent class for deal evaluation."""

    def __init__(self, model: str = "claude-opus-4-6", max_tokens: int = 1024):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Claude response."""
        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")
        return json.loads(text[start:end])

    def _call_claude(self, system: str, user_prompt: str) -> str:
        """Call Claude API with system and user prompts."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    def evaluate(self, mandate: InvestorMandate, deal: DealProposal) -> dict:
        """Evaluate deal against mandate. Implement in subclasses."""
        raise NotImplementedError


class ProcessAgent(Agent):
    """
    Process Agent: Does this deal fit the investment thesis?

    Forcing Questions:
    1. Is use of capital approved?
    2. Is hold period within range?
    3. Is check size acceptable?
    4. Does projected IRR meet minimum?
    5. Are geographies allowed?
    6. Is sector approved?
    7. Are value drivers aligned?
    8. Is decision timeline feasible?
    """

    def evaluate(self, mandate: InvestorMandate, deal: DealProposal) -> dict:
        """Evaluate deal's investment fit using forcing questions."""

        system_prompt = """You are a Process Agent evaluating deals against investor mandates using Gstack forcing questions.

Your job: Ask 8 specific forcing questions. For each, answer YES/NO and explain why.
Return APPROVE (all pass), ADAPT (some fail but fixable), or REJECT (critical failures).

Return JSON: {
  "decision": "APPROVE|ADAPT|REJECT",
  "passed_questions": [list of question numbers that passed],
  "failed_questions": [list of question numbers that failed],
  "issues": ["specific issue 1", "specific issue 2"],
  "reasoning": "brief explanation of decision"
}"""

        user_prompt = f"""
MANDATE (What investor wants):
{json.dumps(mandate.model_dump(), indent=2)}

DEAL (What founder is pitching):
{json.dumps(deal.process_section.model_dump(), indent=2)}

Evaluate using 8 forcing questions:

1. Use of Capital: Is '{deal.process_section.use_of_capital.value}' in allowed list {mandate.process_criteria.primary_use_of_capital}?
2. Hold Period: Is {deal.process_section.hold_period_years} years within {mandate.process_criteria.hold_period_years}?
3. Check Size: Is ${deal.process_section.check_size_usd_millions}M within ${mandate.process_criteria.check_size_usd_millions[0]}-{mandate.process_criteria.check_size_usd_millions[1]}M?
4. IRR: Is {deal.process_section.projected_irr}% >= {mandate.process_criteria.target_irr_percent}%?
5. Geography: Are all {deal.process_section.geographies} in allowed list {mandate.process_criteria.geography}?
6. Sector: Is '{deal.process_section.primary_sector}' in {mandate.process_criteria.sectors} and not in {mandate.process_criteria.exclude_sectors}?
7. Value Drivers: Does the strategy ({deal.process_section.value_drivers}) align with investor thesis?
8. Timeline: Is {deal.process_section.decision_deadline_days} days <= {mandate.process_criteria.max_decision_days}?

Answer each question clearly. Explain your reasoning."""

        response = self._call_claude(system_prompt, user_prompt)
        result = self._extract_json(response)
        return result


class LegalAgent(Agent):
    """
    Legal Agent: Are the contract terms acceptable?

    Forcing Questions:
    1. Are required governance rights included?
    2. Is liquidation preference acceptable?
    3. Is anti-dilution protection adequate?
    4. Is non-compete duration acceptable?
    5. Are drag-along/tag-along rights included?
    6. Is founder vesting period adequate?
    7. Are required carveouts in place?
    8. Is MAC clause acceptable?
    """

    def evaluate(self, mandate: InvestorMandate, deal: DealProposal) -> dict:
        """Evaluate deal's legal terms using forcing questions."""

        system_prompt = """You are a Legal Agent evaluating deal terms against investor requirements using Gstack forcing questions.

Your job: Ask 8 specific forcing questions about contract terms. For each, answer YES/NO.
Return APPROVE (all acceptable), ADAPT (some terms need negotiation), or REJECT (unacceptable terms).

Return JSON: {
  "decision": "APPROVE|ADAPT|REJECT",
  "passed_questions": [list of question numbers that passed],
  "failed_questions": [list of question numbers that failed],
  "issues": ["specific term that needs fixing"],
  "negotiation_priority": "critical issue to raise first",
  "reasoning": "brief explanation"
}"""

        user_prompt = f"""
MANDATE (What investor requires):
{json.dumps(mandate.legal_criteria.model_dump(), indent=2)}

DEAL (What founder is proposing):
{json.dumps(deal.legal_section.model_dump(), indent=2)}

Evaluate using 8 forcing questions:

1. Governance: Does deal include all of {mandate.legal_criteria.required_governance}?
2. Liquidation Preference: Is '{deal.legal_section.liquidation_preference.value}' = '{mandate.legal_criteria.liquidation_preference.value}'?
3. Anti-Dilution: Is '{deal.legal_section.anti_dilution}' = '{mandate.legal_criteria.anti_dilution}'?
4. Non-Compete: Is {deal.legal_section.non_compete_years} years <= {mandate.legal_criteria.max_non_compete_years}?
5. Drag/Tag-Along: Included = {deal.legal_section.drag_tag_rights}, Required = {mandate.legal_criteria.require_drag_tag}?
6. Founder Vesting: Is {deal.legal_section.founder_vesting_years} years >= {mandate.legal_criteria.founder_vesting_min_years}?
7. Carveouts: Are all of {mandate.legal_criteria.required_carveouts} in cap table?
8. MAC Clause: Included = {deal.legal_section.mac_clause_included}, Required = {mandate.legal_criteria.mac_clause_required}?

Answer each question. Flag any terms that need negotiation."""

        response = self._call_claude(system_prompt, user_prompt)
        result = self._extract_json(response)
        return result


class ComplianceAgent(Agent):
    """
    Compliance Agent: Are there regulatory/reputational risks?

    Forcing Questions:
    1. Are all jurisdictions approved?
    2. Is AML/KYC verification complete?
    3. Are sanctions/PEP screenings clean?
    4. Is sector in blocked list?
    5. Is ESG rating acceptable?
    6. Is data privacy compliant?
    7. Is export control relevant?
    8. Are there reputational concerns?
    """

    def evaluate(self, mandate: InvestorMandate, deal: DealProposal) -> dict:
        """Evaluate deal's compliance risk using forcing questions."""

        system_prompt = """You are a Compliance Agent evaluating regulatory and reputational risks using Gstack forcing questions.

Your job: Ask 8 specific forcing questions. For each, answer YES/NO.
Return APPROVE (low risk), APPROVE_WITH_MONITORING (manageable risk), or REJECT (unacceptable risk).

Return JSON: {
  "decision": "APPROVE|APPROVE_WITH_MONITORING|REJECT",
  "passed_questions": [list of question numbers that passed],
  "failed_questions": [list of question numbers that failed],
  "risk_level": "low|medium|high",
  "monitoring_requirements": ["requirement 1 if needed"],
  "issues": ["specific risk identified"],
  "reasoning": "brief explanation"
}"""

        jurisdictions_str = ", ".join(
            [f"{j['country']} ({j['risk_level']})" for j in deal.compliance_section.jurisdictions]
        )

        user_prompt = f"""
MANDATE (What investor accepts):
{json.dumps(mandate.compliance_criteria.model_dump(), indent=2)}

DEAL (Company facts):
Company: {deal.company_name}
Jurisdictions: {jurisdictions_str}
Sector: {deal.compliance_section.primary_sector}
AML/KYC Status: {deal.compliance_section.aml_kyc_status}
Sanctions: {deal.compliance_section.sanctions_screening_result}
PEP: {deal.compliance_section.pep_screening_result}
ESG Rating: {deal.compliance_section.esg_rating}
Data Privacy: {deal.compliance_section.data_privacy_status}
Export Control Relevant: {deal.compliance_section.export_control_relevant}
Reputational Concerns: {deal.compliance_section.reputational_concerns or 'None known'}

Evaluate using 8 forcing questions:

1. Jurisdiction Risk: Are all of {jurisdictions_str} in approved list {mandate.compliance_criteria.allowed_jurisdictions}?
2. AML/KYC: Is status '{deal.compliance_section.aml_kyc_status}' = 'complete'? (Required: {mandate.compliance_criteria.aml_kyc_required})
3. Sanctions: Is result '{deal.compliance_section.sanctions_screening_result}' = 'clean'? (Required: {mandate.compliance_criteria.sanctions_screening_required})
4. PEP: Is '{deal.compliance_section.pep_screening_result}' = 'clean'?
5. Sector: Is '{deal.compliance_section.primary_sector}' NOT in blocked list {mandate.compliance_criteria.blocked_sectors}?
6. ESG Rating: Is '{deal.compliance_section.esg_rating}' >= '{mandate.compliance_criteria.min_esg_rating}'?
7. Data Privacy: Is status '{deal.compliance_section.data_privacy_status}' acceptable? (Required: {mandate.compliance_criteria.data_privacy_required})
8. Export Control: Export control relevant = {deal.compliance_section.export_control_relevant}, acceptable = {mandate.compliance_criteria.export_control_risk_acceptable}?

For each question, explain the risk level and any monitoring needed."""

        response = self._call_claude(system_prompt, user_prompt)
        result = self._extract_json(response)
        return result
