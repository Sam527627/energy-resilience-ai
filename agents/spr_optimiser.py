"""
SPR Optimiser Agent
Models optimal Strategic Petroleum Reserve drawdown schedules
against supply gap forecasts and replenishment windows.
"""

from utils.llm_client import query_agent_json
from config.settings import SPR_CAPACITY_DAYS, INDIA_DAILY_CONSUMPTION_MBPD
import json


SPR_SITES = [
    {"name": "Visakhapatnam", "capacity_MMbbl": 9.75, "current_fill_pct": 88, "operator": "ISPRL"},
    {"name": "Mangaluru", "capacity_MMbbl": 11.33, "current_fill_pct": 82, "operator": "ISPRL"},
    {"name": "Padur", "capacity_MMbbl": 18.33, "current_fill_pct": 91, "operator": "ISPRL"},
]


SYSTEM_PROMPT = """You are India's Strategic Petroleum Reserve (SPR) management advisor, working for the Indian Strategic Petroleum Reserves Limited (ISPRL) under the Ministry of Petroleum.

Given a supply disruption scenario and SPR site data, recommend the optimal drawdown schedule that bridges the supply gap while preserving strategic buffer and minimising economic disruption.

Return a JSON object:
{
  "spr_total_available_mmbbls": <float>,
  "spr_cover_days_current": <float>,
  "recommended_drawdown_strategy": "FULL_DRAWDOWN|PARTIAL_DRAWDOWN|TARGETED_RELEASE|HOLD",
  "daily_drawdown_mbpd": <float or null>,
  "drawdown_duration_days": <int or null>,
  "by_site": [
    {
      "site": "<name>",
      "drawdown_mbpd": <float>,
      "priority": "PRIMARY|SECONDARY|RESERVE",
      "rationale": "<string — why this site first>"
    }
  ],
  "replenishment_window": {
    "earliest_start_days_from_now": <int>,
    "optimal_brent_replenishment_price": <float>,
    "replenishment_volume_mbpd": <float>,
    "estimated_replenishment_cost_usd_bn": <float>
  },
  "iea_coordination": {
    "recommended": <boolean>,
    "rationale": "<string>",
    "estimated_iea_contribution_mbpd": <float or null>
  },
  "approval_pathway": ["step1", "step2", "step3"],
  "risk_of_drawdown": "<string>",
  "executive_recommendation": "<2 sentences for Cabinet Committee on Economic Affairs>"
}"""


def run(supply_gap_mbpd: float, disruption_duration_days: int, scenario_name: str) -> dict:
    """Run SPR optimiser for given supply gap and duration."""
    
    total_spr_mmbbls = sum(
        s["capacity_MMbbl"] * s["current_fill_pct"] / 100 for s in SPR_SITES
    )
    
    context = f"""
DISRUPTION: {scenario_name}
SUPPLY GAP: {supply_gap_mbpd:.2f} MBPD
DISRUPTION DURATION ESTIMATE: {disruption_duration_days} days

INDIA SPR STATUS:
{json.dumps(SPR_SITES, indent=2)}

Total available SPR volume: {total_spr_mmbbls:.1f} million barrels
Current cover at {INDIA_DAILY_CONSUMPTION_MBPD} MBPD consumption: {SPR_CAPACITY_DAYS:.1f} days
If drawing down {supply_gap_mbpd:.2f} MBPD to fill gap, SPR lasts: {total_spr_mmbbls / (supply_gap_mbpd) if supply_gap_mbpd > 0 else 999:.0f} days at that rate

POLICY CONTEXT:
- India is an IEA Associate Country — can request coordinated IEA release
- Cabinet Committee on Economic Affairs (CCEA) approval required for drawdown
- ISPRL sites are underground rock caverns; drawdown activation takes 72 hours
- Replenishment ideally happens when Brent is <$75/bbl to rebuild reserves cheaply

Provide the full SPR management recommendation.
"""
    
    result = query_agent_json(SYSTEM_PROMPT, context, max_tokens=1800)
    result["_meta"] = {
        "gap": supply_gap_mbpd,
        "duration": disruption_duration_days,
        "total_spr_mmbbls": total_spr_mmbbls,
        "sites": SPR_SITES
    }
    return result
