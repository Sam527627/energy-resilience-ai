"""
Foresight Live — Vessel Intelligence Terminal
Real AIS integration + AI-powered VRA generation.
The product that fills the gap between $50K/yr Windward and nothing.
"""

import requests
import json
import time
from datetime import datetime
from config.settings import (
    DEMO_MODE, CORRIDORS, AIS_API_KEY, MARINETRAFFIC_KEY,
    VESSELFINDER_KEY, SPIRE_KEY, AIS_ENDPOINTS, VESSEL_TYPE_ICONS
)
from utils.llm_client import query_agent_json
from utils.live_data import cache_get, cache_set, get_route_weather, check_sanctions_live

# ─────────────────────────────────────────────
# DEMO VESSEL DATABASE
# ─────────────────────────────────────────────
DEMO_VESSELS = {
    "9839131": {
        "imo": "9839131", "name": "MV LILA CONFIDENCE", "type": "Bulk Carrier",
        "flag": "Marshall Islands", "dwt": 81200, "built": 2019, "loa": 229,
        "lat": 19.42, "lon": 64.81, "speed_kts": 12.8, "heading": 285, "draught": 13.2,
        "origin": "Mundra, India", "destination": "Salalah, Oman", "eta": "2026-06-27 14:00",
        "cargo": "Iron Ore", "status": "Underway Using Engine",
        "owner": "Lila Global", "manager": "Lila Ship Management",
        "corridor": "arabian_sea", "current_route": "Mundra → Salalah",
        "last_port": "Mundra", "next_port": "Salalah",
        "gt": 44200, "year_built": 2019, "class_society": "Lloyd's Register",
    },
    "9745372": {
        "imo": "9745372", "name": "MV FALCON MAJESTIC", "type": "Crude Oil Tanker",
        "flag": "Panama", "dwt": 158000, "built": 2017, "loa": 274,
        "lat": 24.12, "lon": 58.45, "speed_kts": 11.2, "heading": 310, "draught": 16.8,
        "origin": "Sohar, Oman", "destination": "Muscat", "eta": "2026-06-25 08:00",
        "cargo": "Crude Oil", "status": "Underway Using Engine",
        "owner": "Falcon Tankers Ltd", "manager": "Majestic Marine",
        "corridor": "strait_of_hormuz", "current_route": "Sohar → Muscat",
        "last_port": "Sohar", "next_port": "Muscat",
        "gt": 84000, "year_built": 2017, "class_society": "DNV",
    },
    "9456789": {
        "imo": "9456789", "name": "MT GULF PIONEER", "type": "Product Tanker",
        "flag": "Liberia", "dwt": 49990, "built": 2015, "loa": 183,
        "lat": 26.58, "lon": 56.21, "speed_kts": 9.4, "heading": 135, "draught": 11.5,
        "origin": "Jebel Ali, UAE", "destination": "Mumbai, India", "eta": "2026-06-29 22:00",
        "cargo": "Gasoil", "status": "Underway — Transiting Hormuz",
        "owner": "Gulf Petro Shipping", "manager": "Pioneer Ship Mgmt",
        "corridor": "strait_of_hormuz", "current_route": "Jebel Ali → Mumbai",
        "last_port": "Jebel Ali", "next_port": "Mumbai",
        "gt": 28000, "year_built": 2015, "class_society": "Bureau Veritas",
    },
    "9612345": {
        "imo": "9612345", "name": "MV RED SEA TRADER", "type": "Container Ship",
        "flag": "Singapore", "dwt": 92000, "built": 2020, "loa": 300,
        "lat": 13.58, "lon": 42.91, "speed_kts": 7.1, "heading": 165, "draught": 14.0,
        "origin": "Jeddah, KSA", "destination": "Colombo, Sri Lanka", "eta": "2026-07-04 06:00",
        "cargo": "Containers (TEU 8200)", "status": "Underway — REDUCED SPEED (threat zone)",
        "owner": "Eastern Container Lines", "manager": "RST Marine",
        "corridor": "red_sea", "current_route": "Jeddah → Colombo via Bab-el-Mandeb",
        "last_port": "Jeddah", "next_port": "Colombo",
        "gt": 96000, "year_built": 2020, "class_society": "ClassNK",
    },
    "9523871": {
        "imo": "9523871", "name": "MT WEST AFRICA STAR", "type": "Crude Oil Tanker",
        "flag": "Greece", "dwt": 115000, "built": 2016, "loa": 250,
        "lat": 4.21, "lon": 6.78, "speed_kts": 10.8, "heading": 220, "draught": 15.2,
        "origin": "Bonny, Nigeria", "destination": "Cape Town", "eta": "2026-07-12 18:00",
        "cargo": "Bonny Light Crude", "status": "Underway — Gulf of Guinea HRA",
        "owner": "Hellenic Tankers", "manager": "WAS Maritime",
        "corridor": "gulf_of_guinea", "current_route": "Bonny → Cape Town → India",
        "last_port": "Bonny Terminal", "next_port": "Cape Town",
        "gt": 63000, "year_built": 2016, "class_society": "Lloyd's Register",
    },
}

# ─────────────────────────────────────────────
# LIVE AIS LOOKUP — tries all configured providers
# ─────────────────────────────────────────────
def lookup_vessel(query: str):
    """
    Look up vessel by IMO or name.
    Priority: Datalastic → MarineTraffic → VesselFinder → demo DB
    Cache: 2 minutes per IMO
    """
    query = query.strip()
    cache_key = f"vessel_{query.upper()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    vessel = None

    if not DEMO_MODE:
        # Try Datalastic (most affordable live AIS)
        if AIS_API_KEY:
            vessel = _fetch_datalastic(query)

        # Try MarineTraffic
        if not vessel and MARINETRAFFIC_KEY:
            vessel = _fetch_marinetraffic(query)

        # Try VesselFinder
        if not vessel and VESSELFINDER_KEY:
            vessel = _fetch_vesselfinder(query)

    # Demo database fallback
    if not vessel:
        vessel = _demo_lookup(query)

    if vessel:
        # Enrich with computed fields
        vessel["_risk"] = quick_risk_score(vessel)
        vessel["_icon"] = VESSEL_TYPE_ICONS.get(vessel.get("type", ""), "🚢")
        vessel["_fetched_at"] = datetime.utcnow().isoformat()
        cache_set(cache_key, vessel, ttl=120)

    return vessel


def _fetch_datalastic(query: str):
    try:
        params = {"api-key": AIS_API_KEY}
        if query.isdigit() and len(query) == 7:
            params["imo"] = query
        else:
            params["name"] = query
        resp = requests.get(AIS_ENDPOINTS["datalastic"], params=params, timeout=10)
        d = resp.json().get("data", {})
        if not d:
            return None
        return _normalise_vessel(d, "Datalastic")
    except Exception:
        return None


def _fetch_marinetraffic(query: str):
    try:
        params = {"v": 3, "apikey": MARINETRAFFIC_KEY,
                  "imo": query if query.isdigit() else None,
                  "vesselname": None if query.isdigit() else query}
        resp = requests.get(
            "https://services.marinetraffic.com/api/getvessel/v:3",
            params={k: v for k, v in params.items() if v}, timeout=10
        )
        data = resp.json()
        if not data:
            return None
        d = data[0] if isinstance(data, list) and data else data
        return {
            "imo": str(d.get("IMO", query)), "name": d.get("SHIPNAME", ""),
            "type": d.get("TYPENAME", "Unknown"), "flag": d.get("FLAG", ""),
            "dwt": d.get("SUMMER_DWT", 0), "lat": float(d.get("LAT", 0)),
            "lon": float(d.get("LON", 0)), "speed_kts": float(d.get("SPEED", 0)) / 10,
            "heading": d.get("HEADING", 0), "draught": float(d.get("DRAUGHT", 0)) / 10,
            "destination": d.get("DESTINATION", ""), "status": d.get("NAVIGATIONAL_STATUS", ""),
            "_source": "MarineTraffic",
        }
    except Exception:
        return None


def _fetch_vesselfinder(query: str):
    try:
        params = {"userkey": VESSELFINDER_KEY,
                  "imo": query if query.isdigit() else None,
                  "name": None if query.isdigit() else query}
        resp = requests.get(AIS_ENDPOINTS["vesselfinder"], params={k: v for k, v in params.items() if v}, timeout=10)
        d = resp.json()
        if not d or d.get("error"):
            return None
        return _normalise_vessel(d, "VesselFinder")
    except Exception:
        return None


def _normalise_vessel(d: dict, source: str) -> dict:
    """Normalise different API responses into standard vessel dict."""
    return {
        "imo":       str(d.get("imo") or d.get("IMO") or ""),
        "name":      d.get("name") or d.get("SHIPNAME") or d.get("vessel_name") or "",
        "type":      d.get("type") or d.get("TYPENAME") or d.get("vessel_type") or "Unknown",
        "flag":      d.get("flag") or d.get("FLAG") or d.get("country_iso") or "",
        "dwt":       int(d.get("summer_dwt") or d.get("SUMMER_DWT") or d.get("deadweight") or 0),
        "lat":       float(d.get("lat") or d.get("LAT") or 0),
        "lon":       float(d.get("lon") or d.get("LON") or 0),
        "speed_kts": float(d.get("speed") or d.get("SPEED") or 0),
        "heading":   int(d.get("heading") or d.get("HEADING") or 0),
        "draught":   float(d.get("draught") or d.get("DRAUGHT") or 0),
        "destination": d.get("destination") or d.get("DESTINATION") or "",
        "status":    d.get("navigation_status") or d.get("NAVIGATIONAL_STATUS") or "Unknown",
        "_source":   source,
        "corridor":  _infer_corridor(
            float(d.get("lat") or 0),
            float(d.get("lon") or 0)
        ),
    }


def _infer_corridor(lat: float, lon: float) -> str:
    """Infer which threat corridor a vessel is in from its position."""
    if 24 < lat < 27 and 54 < lon < 59:
        return "strait_of_hormuz"
    if 10 < lat < 20 and 40 < lon < 48:
        return "red_sea"
    if -5 < lat < 10 and -5 < lon < 15:
        return "gulf_of_guinea"
    if 10 < lat < 25 and 55 < lon < 75:
        return "arabian_sea"
    return "open_ocean"


def _demo_lookup(query: str):
    query = query.upper().strip()
    # By IMO
    if query in DEMO_VESSELS:
        return DEMO_VESSELS[query].copy()
    # By name
    for imo, v in DEMO_VESSELS.items():
        if query in v["name"].upper():
            return v.copy()
    # By partial IMO
    for imo, v in DEMO_VESSELS.items():
        if query in imo:
            return v.copy()
    return None


def get_demo_fleet() -> list[dict]:
    """Return all demo vessels."""
    return [v.copy() for v in DEMO_VESSELS.values()]


# ─────────────────────────────────────────────
# RISK SCORING
# ─────────────────────────────────────────────
def quick_risk_score(vessel: dict) -> dict:
    """Instant deterministic risk score (no LLM, <1ms)."""
    corridor = vessel.get("corridor", "open_ocean")
    base_scores = {
        "red_sea": 85, "strait_of_hormuz": 75,
        "gulf_of_guinea": 68, "arabian_sea": 35,
        "cape_of_good_hope": 22, "open_ocean": 30,
    }
    score = base_scores.get(corridor, 40)

    status = vessel.get("status", "").lower()
    if any(x in status for x in ["reduced speed", "threat", "alert"]):
        score += 8
    if any(x in status for x in ["anchored", "awaiting", "delayed"]):
        score += 5

    # Cargo risk modifier
    cargo = vessel.get("cargo", "").lower()
    if any(x in cargo for x in ["crude", "lng", "chemicals", "fuel"]):
        score += 4

    # Flag risk
    foc_flags = ["panama", "liberia", "belize", "cambodia", "sierra leone"]
    if vessel.get("flag", "").lower() in foc_flags:
        score += 3

    score = min(score, 100)
    if score >= 80:   level = "HIGH"
    elif score >= 65: level = "ELEVATED"
    elif score >= 45: level = "MODERATE"
    else:             level = "LOW"

    return {"score": score, "level": level, "corridor": corridor}


def check_sanctions(vessel: dict) -> dict:
    """Run sanctions screening — tries live OFAC check, falls back to structured result."""
    return check_sanctions_live(vessel.get("imo", ""), vessel.get("name", ""))


# ─────────────────────────────────────────────
# AI-POWERED VRA GENERATION
# ─────────────────────────────────────────────
VRA_SYSTEM_PROMPT = """You are a senior maritime security analyst at HR Maritime Consultants, under the direction of Capt. Ritesh Kapoor, Director of Operations.

You produce professional Foresight Intelligence Voyage Risk Assessments — the kind that shipowners, P&I clubs, charterers, and war risk underwriters actually rely on.

Return ONLY valid JSON with this structure:
{
  "vessel_name": "<string>",
  "imo": "<string>",
  "assessment_date": "<YYYY-MM-DD>",
  "route": "<origin → destination>",
  "overall_risk_rating": "LOW|MODERATE|ELEVATED|HIGH|CRITICAL",
  "risk_score": <0-100>,
  "executive_summary": "<3-4 sentences — bottom line for the shipowner>",
  "threat_assessment": {
    "piracy_armed_robbery": {"level": "LOW|MODERATE|HIGH|CRITICAL", "detail": "<specific to this route>"},
    "geopolitical_military": {"level": "...", "detail": "..."},
    "drone_missile_threat": {"level": "...", "detail": "..."},
    "gps_spoofing_jamming": {"level": "...", "detail": "..."},
    "sea_state_weather": {"level": "...", "detail": "..."}
  },
  "chokepoints": [
    {"name": "<chokepoint>", "risk": "LOW|MODERATE|HIGH|CRITICAL", "advisory": "<specific actionable transit advice>"}
  ],
  "recommendations": ["<specific actionable recommendation>"],
  "hardening_measures": ["<BMP5-aligned measure>"],
  "reporting_requirements": ["<UKMTO/MSCHOA/EUNAVFOR reporting obligation>"],
  "insurance_note": "<JWC listed areas, war risk breach areas relevant to this voyage>",
  "analyst_note": "<closing professional note from Capt. Ritesh Kapoor's desk>"
}

Use: BMP5, UKMTO, MSCHOA, JWC listed areas, IMO MSC guidance. Be route-specific and quantitative. This is a professional paid deliverable."""


def generate_vra(vessel: dict, corridor_risk: dict = None) -> dict:
    """Generate full AI-powered VRA for a vessel. Uses Claude Sonnet."""
    corridor_key = vessel.get("corridor", "")
    corridor_info = CORRIDORS.get(corridor_key, {})
    weather = get_route_weather(vessel.get("lat", 15), vessel.get("lon", 60))

    context = f"""
VESSEL:
  Name: {vessel.get('name')}
  IMO: {vessel.get('imo')}
  Type: {vessel.get('type')}
  Flag: {vessel.get('flag')}
  DWT: {vessel.get('dwt', 'N/A')} | Built: {vessel.get('built') or vessel.get('year_built', 'N/A')}
  Position: {vessel.get('lat'):.2f}°N, {vessel.get('lon'):.2f}°E
  Speed: {vessel.get('speed_kts')} kts | Heading: {vessel.get('heading')}°
  Draught: {vessel.get('draught', 'N/A')} m
  Cargo: {vessel.get('cargo', 'N/A')}
  Route: {vessel.get('current_route', str(vessel.get('origin','')) + ' → ' + str(vessel.get('destination','')))}
  Status: {vessel.get('status')}
  ETA: {vessel.get('eta', 'N/A')}

CORRIDOR: {corridor_info.get('name', corridor_key)}
  India dependency: {corridor_info.get('india_dependency_pct', 'N/A')}%
  High Risk Area: {corridor_info.get('hra', False)}
  BMP5 applicable: {corridor_info.get('bmp5_applicable', False)}
  UKMTO area: {corridor_info.get('ukmto_area', False)}

WEATHER AT POSITION:
  Wave height: {weather.get('wave_height_m')} m | Sea state: {weather.get('sea_state')}
  Wind: {weather.get('wind_speed_kts')} kts from {weather.get('wind_direction_deg')}°
  Source: {weather.get('source')}

CURRENT THREAT ENVIRONMENT (June 2026):
  - Red Sea/Bab-el-Mandeb: Active Houthi drone and anti-ship missile threat. Multiple vessels struck.
    Many operators diverting via Cape of Good Hope (+10-15 days transit). UKMTO operating.
  - Strait of Hormuz: IRGC naval exercise. GPS jamming reported (11,600+ vessels affected Q1 2026).
    Expanded US sanctions on Iranian exports. Tensions elevated.
  - Gulf of Guinea: Persistent piracy, kidnap-for-ransom. IMB/ICC HRA in effect.
  - Arabian Sea: Generally moderate. Residual Somali piracy risk in approaches to Gulf of Aden.

Generate a complete, authoritative Foresight Voyage Risk Assessment for this specific vessel.
"""
    result = query_agent_json(VRA_SYSTEM_PROMPT, context, max_tokens=2800)
    result["_vessel"] = vessel
    result["_weather"] = weather
    return result
