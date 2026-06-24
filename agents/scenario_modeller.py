"""
Scenario Modeller Agent
Simulates specific disruption events and computes cascading economic impact
on India's refinery sector, fuel prices, and GDP trajectory.
"""

from utils.llm_client import query_agent_json
from config.settings import CORRIDORS, ALT_CRUDE_SOURCES, SPR_CAPACITY_DAYS, INDIA_DAILY_CONSUMPTION_MBPD
import json


SCENARIOS = {
    "hormuz_partial_closure": {
        "name": "Strait of Hormuz — 40% Capacity Reduction",
        "description": "IRGC mine-laying or naval blockade reduces tanker throughput by 40% for 30 days",
        "corridor": "strait_of_hormuz",
        "supply_reduction_pct": 40,
        "duration_days": 30,
        "icon": "🚨"
    },
    "red_sea_suspension": {
        "name": "Red Sea — Full Suspension (Houthi Escalation)",
        "description": "Houthi missile threat forces complete diversion of tankers via Cape of Good Hope",
        "corridor": "red_sea",
        "supply_reduction_pct": 100,
        "duration_days": 60,
        "icon": "⚠️"
    },
    "opec_emergency_cut": {
        "name": "OPEC+ Emergency Output Cut — 2 MBPD",
        "description": "OPEC+ announces emergency cut of 2 million barrels per day effective 30 days",
        "corridor": "global",
        "supply_reduction_pct": 8,
        "duration_days": 90,
        "icon": "📉"
    },
    "iran_sanctions_full": {
        "name": "Full Iran Oil Export Embargo",
        "description": "Comprehensive US/EU sanctions eliminate Iranian exports entirely from market",
        "corridor": "strait_of_hormuz",
        "supply_reduction_pct": 25,
        "duration_days": 180,
        "icon": "🛑"
    },
    "dual_corridor_crisis": {
        "name": "Dual Corridor Crisis — Hormuz + Red Sea",
        "description": "Simultaneous Hormuz tension and Red Sea suspension forces full rerouting",
        "corridor": "multiple",
        "supply_reduction_pct": 55,
        "duration_days": 45,
        "icon": "🆘"
    }
}


SYSTEM_PROMPT = """You are a quantitative energy supply chain analyst specialising in India's crude oil import economics.

Given a disruption scenario, you must compute precise economic impacts and return a JSON object with this structure:
{
  "scenario_name": "<string>",
  "severity": "MODERATE|SEVERE|CRITICAL|CATASTROPHIC",
  "india_supply_gap_mbpd": <float — how many MBPD India loses>,
  "spr_cover_days": <float — how long SPR bridges the gap>,
  "spr_exhaustion_date_days_from_now": <integer or null if not exhausted>,
  "refinery_run_rate_impact_pct": <negative float — reduction in refinery utilisation>,
  "brent_price_spike_estimate_pct": <float — estimated % Brent price increase>,
  "india_import_bill_increase_usd_bn_monthly": <float>,
  "petrol_price_impact_inr_per_litre": <float>,
  "diesel_price_impact_inr_per_litre": <float>,
  "gdp_impact_annualised_pct": <negative float>,
  "power_sector_stress_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "alternative_sources_available_mbpd": <float — how much alt supply India can realistically access>,
  "supply_gap_after_rerouting_mbpd": <float>,
  "rerouting_cost_premium_usd_per_barrel": <float>,
  "response_timeline": [
    {"day": <int>, "action": "<string>", "impact": "<string>"},
    ...
  ],
  "key_vulnerabilities": ["vulnerability1", "vulnerability2", "vulnerability3"],
  "mitigation_recommendations": ["rec1", "rec2", "rec3"],
  "scenario_narrative": "<3-4 sentence summary for the Ministry of Petroleum>"
}

Use real-world data: India consumes ~5.1 MBPD, SPR capacity is 9.5 days, Jamnagar refinery alone is 1.24 MBPD. Brent was approximately $87/bbl baseline. Indian petrol retail at ~Rs 95/litre, diesel ~Rs 88/litre. Be quantitatively precise."""


def run(scenario_key: str) -> dict:
    """Run scenario modeller for a given scenario key."""
    
    if scenario_key not in SCENARIOS:
        return {"error": f"Unknown scenario: {scenario_key}"}
    
    scenario = SCENARIOS[scenario_key]
    
    context = f"""
SCENARIO TO MODEL:
{json.dumps(scenario, indent=2)}

INDIA SUPPLY CHAIN BASELINE:
- Total daily imports: {INDIA_DAILY_CONSUMPTION_MBPD} MBPD
- SPR cover: {SPR_CAPACITY_DAYS} days
- Corridor dependencies: {json.dumps({k: v['india_dependency_pct'] for k, v in CORRIDORS.items()}, indent=2)}

ALTERNATIVE SOURCES AVAILABLE:
{json.dumps(ALT_CRUDE_SOURCES, indent=2)}

KEY CONSTRAINTS:
- Rerouting via Cape adds 8-15 transit days
- Spot market premiums when buying emergency cargoes: +$4-12/bbl
- Jamnagar (1.24 MBPD) can process most grades; Haldia and Chennai are more grade-sensitive
- India has diplomatic channels with Russia, USA, Nigeria, UAE for emergency supply

Please model this scenario comprehensively for the Ministry of Petroleum & Natural Gas.
"""
    
    result = query_agent_json(SYSTEM_PROMPT, context, max_tokens=2000)
    result["scenario_meta"] = scenario
    return result


def get_all_scenarios() -> dict:
    """Return scenario definitions for UI display."""
    return SCENARIOS
