"""
Meridian — Vessel Intelligence Engine
Handles ANY IMO/MMSI/name lookup via cascading real APIs.
Returns deep vessel intelligence: particulars, position, voyage, compliance, carbon.
"""
import requests, json, time, hashlib
from datetime import datetime, timedelta
from config.settings import (
    DEMO_MODE, CORRIDORS, VESSEL_TYPE_ICONS, NAV_STATUS,
    VESSELAPI_KEY, AIS_API_KEY, MARINETRAFFIC_KEY, VESSELFINDER_KEY,
    MYSHIPTRACKING_KEY, SEARATES_KEY, VESSEL_APIS,
)
from utils.llm_client import query_agent_json
from utils.live_data import cache_get, cache_set, get_route_weather, check_sanctions_live

# ═══════════════════════════════════════════
# DEMO FLEET (fallback when no live API / unknown IMO)
# ═══════════════════════════════════════════
DEMO_VESSELS = {
    "9839131": {"imo":"9839131","mmsi":"538008970","name":"MV LILA CONFIDENCE","type":"Bulk Carrier","flag":"Marshall Islands","dwt":81200,"gt":44200,"built":2019,"loa":229,"beam":32.3,"lat":19.42,"lon":64.81,"speed_kts":12.8,"heading":285,"draught":13.2,"origin":"Mundra, India","destination":"Salalah, Oman","eta":"2026-06-27 14:00","cargo":"Iron Ore","status":"Under way using engine","owner":"Lila Global Ltd","manager":"Lila Ship Management","class_society":"Lloyd's Register","corridor":"arabian_sea","current_route":"Mundra → Salalah","cii_rating":"C","last_port":"Mundra","callsign":"V7LC8"},
    "9745372": {"imo":"9745372","mmsi":"354991000","name":"MV FALCON MAJESTIC","type":"Crude Oil Tanker","flag":"Panama","dwt":158000,"gt":84000,"built":2017,"loa":274,"beam":48,"lat":24.12,"lon":58.45,"speed_kts":11.2,"heading":310,"draught":16.8,"origin":"Sohar, Oman","destination":"Muscat","eta":"2026-06-25 08:00","cargo":"Crude Oil (VLCC)","status":"Under way using engine","owner":"Falcon Tankers Ltd","manager":"Majestic Marine","class_society":"DNV","corridor":"strait_of_hormuz","current_route":"Sohar → Muscat","cii_rating":"D","last_port":"Sohar","callsign":"3FAB7"},
    "9456789": {"imo":"9456789","mmsi":"636019825","name":"MT GULF PIONEER","type":"Product Tanker","flag":"Liberia","dwt":49990,"gt":28000,"built":2015,"loa":183,"beam":32,"lat":26.58,"lon":56.21,"speed_kts":9.4,"heading":135,"draught":11.5,"origin":"Jebel Ali, UAE","destination":"Mumbai, India","eta":"2026-06-29 22:00","cargo":"Gasoil","status":"Under way — Transiting Hormuz","owner":"Gulf Petro Shipping","manager":"Pioneer Ship Mgmt","class_society":"Bureau Veritas","corridor":"strait_of_hormuz","current_route":"Jebel Ali → Mumbai","cii_rating":"C","last_port":"Jebel Ali","callsign":"D5PG2"},
    "9612345": {"imo":"9612345","mmsi":"563112000","name":"MV RED SEA TRADER","type":"Container Ship","flag":"Singapore","dwt":92000,"gt":96000,"built":2020,"loa":300,"beam":48.2,"lat":13.58,"lon":42.91,"speed_kts":7.1,"heading":165,"draught":14.0,"origin":"Jeddah, KSA","destination":"Colombo, Sri Lanka","eta":"2026-07-04 06:00","cargo":"Containers (TEU 8200)","status":"Under way — REDUCED SPEED (threat zone)","owner":"Eastern Container Lines","manager":"RST Marine","class_society":"ClassNK","corridor":"red_sea","current_route":"Jeddah → Colombo via Bab-el-Mandeb","cii_rating":"B","last_port":"Jeddah","callsign":"9V8821"},
    "9523871": {"imo":"9523871","mmsi":"241456000","name":"MT WEST AFRICA STAR","type":"Crude Oil Tanker","flag":"Greece","dwt":115000,"gt":63000,"built":2016,"loa":250,"beam":44,"lat":4.21,"lon":6.78,"speed_kts":10.8,"heading":220,"draught":15.2,"origin":"Bonny, Nigeria","destination":"Cape Town","eta":"2026-07-12 18:00","cargo":"Bonny Light Crude","status":"Under way — Gulf of Guinea HRA","owner":"Hellenic Tankers","manager":"WAS Maritime","class_society":"Lloyd's Register","corridor":"gulf_of_guinea","current_route":"Bonny → Cape Town → India","cii_rating":"D","last_port":"Bonny Terminal","callsign":"SVAW3"},
}

# ═══════════════════════════════════════════
# UNIVERSAL VESSEL LOOKUP (any IMO)
# ═══════════════════════════════════════════
def lookup_vessel(query):
    """Look up vessel by IMO/MMSI/name. Cascades through live APIs → demo."""
    query = str(query).strip()
    ck = f"vessel_{query.upper()}"
    cached = cache_get(ck)
    if cached:
        return cached

    vessel = None
    if not DEMO_MODE:
        for fetcher in [_fetch_vesselapi, _fetch_myshiptracking, _fetch_datalastic, _fetch_searates]:
            try:
                vessel = fetcher(query)
                if vessel and vessel.get("name"):
                    break
            except Exception:
                continue

    if not vessel:
        vessel = _demo_lookup(query)

    if vessel:
        vessel = _enrich(vessel)
        cache_set(ck, vessel, 120)
    return vessel


def _fetch_vesselapi(query):
    """VesselAPI.com — FREE tier, 695K vessels. Primary source."""
    if not VESSELAPI_KEY:
        return None
    is_imo = query.isdigit() and len(query) == 7
    is_mmsi = query.isdigit() and len(query) == 9
    headers = {"Authorization": f"Bearer {VESSELAPI_KEY}"}
    # Get particulars
    if is_imo or is_mmsi:
        idtype = "imo" if is_imo else "mmsi"
        r = requests.get(f"{VESSEL_APIS['vesselapi']}/vessels/{query}",
                         params={"filter.idType": idtype}, headers=headers, timeout=12)
    else:
        r = requests.get(f"{VESSEL_APIS['vesselapi']}/vessels/search",
                         params={"filter.name": query}, headers=headers, timeout=12)
    if r.status_code != 200:
        return None
    d = r.json()
    if isinstance(d, dict) and d.get("data"):
        d = d["data"][0] if isinstance(d["data"], list) else d["data"]
    # Get position
    pos = {}
    try:
        pr = requests.get(f"{VESSEL_APIS['vesselapi']}/location/vessels/{query}",
                         params={"filter.idType": "imo" if is_imo else "mmsi"},
                         headers=headers, timeout=10)
        if pr.status_code == 200:
            pos = pr.json().get("data", pr.json())
    except Exception:
        pass
    return {
        "imo": str(d.get("imo", query if is_imo else "")),
        "mmsi": str(d.get("mmsi", query if is_mmsi else "")),
        "name": d.get("vesselName") or d.get("name", ""),
        "type": d.get("type") or d.get("vesselType", "Unknown"),
        "flag": d.get("flag", ""),
        "built": d.get("yearBuilt") or d.get("year_built", ""),
        "loa": d.get("length", ""), "beam": d.get("width", ""),
        "callsign": d.get("callsign") or d.get("callSign", ""),
        "lat": pos.get("latitude") or d.get("latitude", 0),
        "lon": pos.get("longitude") or d.get("longitude", 0),
        "speed_kts": pos.get("sog") or pos.get("speed", 0),
        "heading": pos.get("heading", 0),
        "status": pos.get("navStatus") or NAV_STATUS.get(pos.get("navStatus", 15), "Unknown"),
        "destination": pos.get("destination", ""),
        "_source": "VesselAPI (live AIS)",
    }


def _fetch_myshiptracking(query):
    if not MYSHIPTRACKING_KEY:
        return None
    is_imo = query.isdigit() and len(query) == 7
    params = {"imo": query} if is_imo else ({"mmsi": query} if query.isdigit() else {"name": query})
    params["response"] = "extended"
    r = requests.get(f"{VESSEL_APIS['myshiptracking']}", params=params,
                     headers={"Authorization": f"Bearer {MYSHIPTRACKING_KEY}"}, timeout=12)
    if r.status_code != 200:
        return None
    data = r.json().get("data", [])
    if not data:
        return None
    d = data[0] if isinstance(data, list) else data
    return {
        "imo": str(d.get("imo", "")), "mmsi": str(d.get("mmsi", "")),
        "name": d.get("vessel_name", ""), "type": d.get("vtype", "Unknown"),
        "flag": d.get("flag", ""), "lat": d.get("lat", 0), "lon": d.get("lng", 0),
        "speed_kts": d.get("speed", 0), "heading": d.get("course", 0),
        "status": NAV_STATUS.get(d.get("nav_status", 15), "Unknown"),
        "destination": d.get("destination", ""), "_source": "MyShipTracking (live AIS)",
    }


def _fetch_datalastic(query):
    if not AIS_API_KEY:
        return None
    params = {"api-key": AIS_API_KEY}
    if query.isdigit() and len(query) == 7: params["imo"] = query
    elif query.isdigit(): params["mmsi"] = query
    else: params["name"] = query
    r = requests.get(VESSEL_APIS["datalastic"], params=params, timeout=12)
    d = r.json().get("data", {})
    if not d:
        return None
    return {
        "imo": str(d.get("imo", "")), "mmsi": str(d.get("mmsi", "")),
        "name": d.get("name", ""), "type": d.get("type", "Unknown"),
        "flag": d.get("country_iso", ""), "lat": d.get("lat", 0), "lon": d.get("lon", 0),
        "speed_kts": d.get("speed", 0), "heading": d.get("heading", 0),
        "destination": d.get("destination", ""), "status": d.get("navigation_status", "Unknown"),
        "_source": "Datalastic (live AIS)",
    }


def _fetch_searates(query):
    if not SEARATES_KEY:
        return None
    r = requests.get(VESSEL_APIS["searates"], params={"api_key": SEARATES_KEY, "number": query, "type": "VL"}, timeout=12)
    if r.status_code != 200:
        return None
    d = r.json().get("data", {}).get("vessels", [{}])
    d = d[0] if d else {}
    if not d.get("name"):
        return None
    ais = d.get("ais", {})
    return {
        "imo": str(d.get("imo", "")), "mmsi": str(d.get("mmsi", "")),
        "name": d.get("name", ""), "type": d.get("type", "Unknown"),
        "flag": d.get("flag", ""), "built": d.get("year_built", ""),
        "loa": d.get("length", ""), "beam": d.get("width", ""),
        "callsign": d.get("call_sign", ""),
        "lat": ais.get("latitude", 0), "lon": ais.get("longitude", 0),
        "speed_kts": ais.get("speed", 0), "heading": ais.get("course", 0),
        "draught": ais.get("draught", 0), "status": ais.get("navigational_status", "Unknown"),
        "_source": "SeaRates (live AIS)",
    }


def _demo_lookup(query):
    q = query.upper().strip()
    if q in DEMO_VESSELS:
        return DEMO_VESSELS[q].copy()
    for imo, v in DEMO_VESSELS.items():
        if q in v["name"].upper() or q == v.get("mmsi", ""):
            return v.copy()
    for imo, v in DEMO_VESSELS.items():
        if q in imo:
            return v.copy()
    # Unknown IMO → synthesise a plausible vessel so demo still works for ANY input
    if q.isdigit() and len(q) == 7:
        return _synthesise_vessel(q)
    return None


def _synthesise_vessel(imo):
    """For an unknown but valid IMO, build a deterministic plausible profile."""
    import random
    seed = int(hashlib.md5(imo.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    types = ["Bulk Carrier","Crude Oil Tanker","Container Ship","Product Tanker","LNG Tanker","Chemical Tanker"]
    flags = ["Panama","Liberia","Marshall Islands","Singapore","Greece","Malta","Hong Kong","Cyprus"]
    corridors = ["strait_of_hormuz","red_sea","arabian_sea","gulf_of_guinea","malacca_strait"]
    ck = rng.choice(corridors)
    corr = CORRIDORS[ck]
    vtype = rng.choice(types)
    return {
        "imo": imo, "mmsi": str(200000000+seed%99999999),
        "name": f"MV VESSEL {imo[-4:]}", "type": vtype,
        "flag": rng.choice(flags), "dwt": rng.randint(20000,320000),
        "gt": rng.randint(15000,180000), "built": rng.randint(2005,2023),
        "loa": rng.randint(150,360), "beam": rng.randint(25,60),
        "lat": round(corr["lat"]+rng.uniform(-2,2),4), "lon": round(corr["lon"]+rng.uniform(-2,2),4),
        "speed_kts": round(rng.uniform(8,16),1), "heading": rng.randint(0,359),
        "draught": round(rng.uniform(8,18),1), "status": "Under way using engine",
        "destination": rng.choice(["Mumbai","Jamnagar","Singapore","Rotterdam","Fujairah","Colombo"]),
        "cargo": "Cargo (estimated)", "corridor": ck,
        "current_route": f"At sea — {corr['name']}",
        "owner": "Registered owner (lookup pending)", "manager": "Ship manager (lookup pending)",
        "class_society": rng.choice(["Lloyd's Register","DNV","ABS","Bureau Veritas","ClassNK"]),
        "cii_rating": rng.choice(["A","B","C","D","E"]),
        "callsign": f"{rng.choice('ABCD9')}{imo[-4:]}",
        "_source": "Synthesised profile (no live AIS key — add VESSELAPI_KEY for real data)",
        "_synthesised": True,
    }


def _enrich(v):
    """Add computed intelligence fields."""
    if not v.get("_source"):
        v["_source"] = "Meridian demo fleet"
    if not v.get("corridor"):
        v["corridor"] = _infer_corridor(float(v.get("lat") or 0), float(v.get("lon") or 0))
    v["_risk"] = quick_risk_score(v)
    v["_icon"] = VESSEL_TYPE_ICONS.get(v.get("type", ""), "🚢")
    v["_fetched_at"] = datetime.utcnow().isoformat()
    return v


def _infer_corridor(lat, lon):
    if 24<lat<27 and 54<lon<59: return "strait_of_hormuz"
    if 10<lat<20 and 40<lon<48: return "red_sea"
    if -5<lat<10 and -5<lon<15: return "gulf_of_guinea"
    if -2<lat<8 and 98<lon<104: return "malacca_strait"
    if 10<lat<25 and 55<lon<75: return "arabian_sea"
    return "open_ocean"


def get_demo_fleet():
    return [v.copy() for v in DEMO_VESSELS.values()]


# ═══════════════════════════════════════════
# RISK SCORING
# ═══════════════════════════════════════════
def quick_risk_score(vessel):
    corridor = vessel.get("corridor","open_ocean")
    base = {"red_sea":85,"strait_of_hormuz":75,"gulf_of_guinea":68,"malacca_strait":40,"arabian_sea":35,"cape_of_good_hope":22,"open_ocean":30}.get(corridor,40)
    status = str(vessel.get("status","")).lower()
    if any(x in status for x in ["reduced speed","threat","alert"]): base += 8
    if any(x in status for x in ["anchor","awaiting","aground","not under command"]): base += 5
    cargo = str(vessel.get("cargo","")).lower()
    if any(x in cargo for x in ["crude","lng","lpg","chemical","fuel","gasoil"]): base += 4
    if str(vessel.get("flag","")).lower() in ["panama","liberia","belize","cambodia","sierra leone","comoros"]: base += 3
    score = min(base, 100)
    level = "HIGH" if score>=80 else "ELEVATED" if score>=65 else "MODERATE" if score>=45 else "LOW"
    return {"score":score,"level":level,"corridor":corridor}


def check_sanctions(vessel):
    return check_sanctions_live(vessel.get("imo",""), vessel.get("name",""))


# ═══════════════════════════════════════════
# AI VRA GENERATION
# ═══════════════════════════════════════════
VRA_SYSTEM_PROMPT = """You are the lead maritime security analyst at Meridian Maritime Intelligence, producing a Meridian Voyage Risk Assessment (VRA) — a professional deliverable relied upon by shipowners, charterers, P&I clubs, and war-risk underwriters.

Return ONLY valid JSON:
{
  "vessel_name":"...", "imo":"...", "assessment_date":"YYYY-MM-DD", "route":"origin → destination",
  "overall_risk_rating":"LOW|MODERATE|ELEVATED|HIGH|CRITICAL", "risk_score":<0-100>,
  "executive_summary":"3-4 sentences for the shipowner",
  "threat_assessment":{
    "piracy_armed_robbery":{"level":"...","detail":"route-specific"},
    "geopolitical_military":{"level":"...","detail":"..."},
    "drone_missile_threat":{"level":"...","detail":"..."},
    "gps_spoofing_jamming":{"level":"...","detail":"..."},
    "sea_state_weather":{"level":"...","detail":"..."}
  },
  "chokepoints":[{"name":"...","risk":"...","advisory":"specific transit advice"}],
  "recommendations":["actionable rec"],
  "hardening_measures":["BMP5-aligned measure"],
  "reporting_requirements":["UKMTO/MSCHOA/EUNAVFOR obligation"],
  "insurance_note":"JWC listed area / war-risk breach considerations",
  "analyst_note":"closing professional note from Meridian's desk"
}
Use BMP5, UKMTO, MSCHOA, JWC listed areas, IMO MSC guidance. Be route-specific, quantitative, authoritative."""


def generate_vra(vessel, corridor_risk=None):
    ckey = vessel.get("corridor","")
    corr = CORRIDORS.get(ckey,{})
    wx = get_route_weather(float(vessel.get("lat") or 15), float(vessel.get("lon") or 60))
    ctx = f"""VESSEL: {vessel.get('name')} (IMO {vessel.get('imo')})
Type: {vessel.get('type')} | Flag: {vessel.get('flag')} | DWT: {vessel.get('dwt','N/A')} | Built: {vessel.get('built','N/A')}
Position: {vessel.get('lat')}, {vessel.get('lon')} | Speed: {vessel.get('speed_kts')} kts | Status: {vessel.get('status')}
Route: {vessel.get('current_route', str(vessel.get('origin',''))+' → '+str(vessel.get('destination','')))}
Cargo: {vessel.get('cargo','N/A')} | ETA: {vessel.get('eta','N/A')}

CORRIDOR: {corr.get('name', ckey)} | HRA: {corr.get('hra',False)} | BMP5: {corr.get('bmp5_applicable',False)} | UKMTO: {corr.get('ukmto_area',False)}
WEATHER: Wave {wx.get('wave_height_m')}m, {wx.get('sea_state')}, Wind {wx.get('wind_speed_kts')}kts

THREAT ENVIRONMENT (June 2026):
- Red Sea/Bab-el-Mandeb: Active Houthi drone/AShM strikes. Many divert via Cape (+10-15 days).
- Strait of Hormuz: IRGC exercises, GPS jamming (11,600+ vessels affected Q1 2026), US sanctions pressure.
- Gulf of Guinea: Piracy, kidnap-for-ransom. IMB HRA in effect.
- Malacca: Petty theft at anchorages, generally secure transit.
- Arabian Sea: Moderate; residual Somali piracy in GoA approaches.

Generate the complete Meridian VRA for this specific vessel."""
    result = query_agent_json(VRA_SYSTEM_PROMPT, ctx, max_tokens=2800)
    result["_vessel"] = vessel
    result["_weather"] = wx
    return result
