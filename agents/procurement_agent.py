"""
Procurement Orchestrator Agent
Ranks alternative crude sources and logistics routes under disruption,
factoring price, tanker availability, transit time, and refinery grade compatibility.
"""

from utils.llm_client import query_agent_json
from utils.commodity_feed import get_live_prices, get_tanker_rates
from config.settings import ALT_CRUDE_SOURCES, INDIA_REFINERIES
import json


SYSTEM_PROMPT = """You are India's Chief Procurement Intelligence Agent for crude oil, operating for the Petroleum Planning and Analysis Cell (PPAC) of India.

Given a supply disruption scenario and current market conditions, generate executable procurement recommendations that Indian refinery operators can act on within 48 hours.

Return a JSON object with this structure:
{
  "procurement_window": "<string — urgency level>",
  "supply_gap_to_fill_mbpd": <float>,
  "ranked_alternatives": [
    {
      "rank": <int>,
      "country": "<string>",
      "grade": "<string>",
      "recommended_volume_mbpd": <float>,
      "procurement_mechanism": "SPOT|TERM|GOVERNMENT_TO_GOVERNMENT",
      "estimated_price_vs_brent": "<string e.g. Brent -$3.5>",
      "total_cost_usd_per_barrel": <float>,
      "tanker_type_required": "<VLCC|Suezmax|Aframax>",
      "transit_days_to_india": <int>,
      "grade_compatible_refineries": ["refinery1", "refinery2"],
      "confidence_score": <0-100>,
      "risks": ["risk1", "risk2"],
      "action_required": "<specific, actionable step — who calls whom, what contract mechanism>"
    }
  ],
  "immediate_actions_48h": [
    {"priority": <int>, "action": "<string>", "owner": "<PPAC|IOC|Reliance|BPCL|etc>", "deadline": "<string>"}
  ],
  "spr_drawdown_recommendation": {
    "initiate": <boolean>,
    "daily_drawdown_mbpd": <float or null>,
    "rationale": "<string>"
  },
  "total_gap_covered_mbpd": <float>,
  "residual_gap_mbpd": <float>,
  "executive_summary": "<3 sentences — bottom line for Minister of Petroleum>"
}

Be specific and actionable. Name real refineries, real shipping companies (VLCC fleet operators), real grade specifications. This is a decision-support tool for real procurement teams."""


def run(supply_gap_mbpd: float, scenario_name: str, brent_baseline: float = 87.0) -> dict:
    """Run procurement agent for a given supply gap."""
    
    prices = get_live_prices()
    tanker_rates = get_tanker_rates()
    brent_live = prices.get("brent_crude", {}).get("price", brent_baseline)
    
    context = f"""
DISRUPTION CONTEXT: {scenario_name}
SUPPLY GAP TO FILL: {supply_gap_mbpd:.2f} MBPD
CURRENT BRENT PRICE: ${brent_live}/bbl

AVAILABLE ALTERNATIVE SOURCES (assessed pre-crisis):
{json.dumps(ALT_CRUDE_SOURCES, indent=2)}

INDIA REFINERY NETWORK:
{json.dumps(INDIA_REFINERIES, indent=2)}

CURRENT TANKER MARKET:
- VLCC (ME→India): ${tanker_rates.get('vlcc_me_india', 0):,.0f}/day
- Suezmax (WAF→India): ${tanker_rates.get('suezmax_waf_india', 0):,.0f}/day
- Aframax (Med→India): ${tanker_rates.get('aframax_med_india', 0):,.0f}/day

CONSTRAINTS:
- Indian refineries need 15–30 days minimum to switch primary crude grade
- G2G mechanisms can be activated within 72 hours (Russia, UAE, Saudi)
- Spot market volumes above 0.3 MBPD require tanker pre-positioning
- SPR drawdown requires Cabinet Committee on Economic Affairs approval
- Jamnagar (Reliance) can process virtually any grade; public sector refineries are more constrained

Generate the full procurement rerouting plan.
"""
    
    result = query_agent_json(SYSTEM_PROMPT, context, max_tokens=2500)
    result["_meta"] = {
        "supply_gap_mbpd": supply_gap_mbpd,
        "scenario": scenario_name,
        "brent_price": brent_live
    }
    return result
