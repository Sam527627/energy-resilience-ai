"""
GeoSentinel Agent — Geopolitical Risk Intelligence
Ingests news, commodity signals, and sanctions data to produce
live corridor disruption probability scores.
"""

from utils.llm_client import query_agent_json
from utils.news_fetcher import fetch_geopolitical_news
from utils.commodity_feed import get_live_prices, get_tanker_rates
from config.settings import CORRIDORS
import json


SYSTEM_PROMPT = """You are GeoSentinel, an expert geopolitical energy risk intelligence agent specialising in India's crude oil supply corridors. 

Your role is to analyse news headlines, commodity price signals, and tanker market data, then produce a structured risk assessment for each supply corridor.

You must return a JSON object with this exact structure:
{
  "assessment_timestamp": "ISO datetime string",
  "overall_risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "overall_risk_score": <0-100 integer>,
  "corridors": {
    "strait_of_hormuz": {
      "risk_score": <0-100>,
      "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "primary_threat": "<one sentence>",
      "disruption_probability_30d": <0-100 percentage>,
      "india_supply_at_risk_mbpd": <float>,
      "key_signals": ["signal1", "signal2", "signal3"]
    },
    "red_sea": { <same structure> },
    "gulf_of_guinea": { <same structure> },
    "cape_of_good_hope": { <same structure> }
  },
  "top_3_risks": [
    {"rank": 1, "risk": "<description>", "impact": "<impact statement>", "probability": <0-100>},
    {"rank": 2, ...},
    {"rank": 3, ...}
  ],
  "analyst_summary": "<2-3 sentence executive summary for Indian energy policymakers>"
}

Base your analysis on the data provided. Be specific and quantitative. Indian context is critical — always frame impacts in terms of India's refinery operations, SPR adequacy, and fuel price implications."""


def run(news_limit: int = 7) -> dict:
    """Run the GeoSentinel agent and return structured risk assessment."""
    
    # Gather inputs
    headlines = fetch_geopolitical_news(news_limit)
    prices = get_live_prices()
    tanker_rates = get_tanker_rates()
    
    # Build context for the agent
    context = f"""
CORRIDOR DEPENDENCY DATA:
{json.dumps(CORRIDORS, indent=2)}

LIVE COMMODITY PRICES:
- Brent Crude: ${prices.get('brent_crude', {}).get('price', 'N/A')}/bbl (change: {prices.get('brent_crude', {}).get('change_pct', 'N/A')}%)
- WTI Crude: ${prices.get('wti_crude', {}).get('price', 'N/A')}/bbl
- Natural Gas: ${prices.get('natural_gas', {}).get('price', 'N/A')}/MMBtu

TANKER MARKET (USD/day):
- VLCC (Middle East → India): ${tanker_rates.get('vlcc_me_india', 'N/A'):,.0f}
- Suezmax (West Africa → India): ${tanker_rates.get('suezmax_waf_india', 'N/A'):,.0f}

LATEST GEOPOLITICAL HEADLINES:
{chr(10).join([f"[{i+1}] ({h['published']}) {h['title']} — {h.get('description','')[:150]}" for i, h in enumerate(headlines)])}

India imports 5.1 million barrels per day total. Strategic Petroleum Reserves cover 9.5 days of consumption.
"""

    result = query_agent_json(SYSTEM_PROMPT, context, max_tokens=2000)
    
    # Attach raw inputs for UI display
    result["_inputs"] = {
        "headlines": headlines,
        "prices": prices,
        "tanker_rates": tanker_rates
    }
    
    return result
