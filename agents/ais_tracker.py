"""
AIS Maritime Tracker Agent
Monitors vessel movements across India's critical supply corridors.
Uses simulated AIS data representing the current threat environment.
In production: integrate AISHub, MarineTraffic, or Spire Maritime APIs.
"""

import numpy as np
import random
from datetime import datetime, timedelta


VESSELS_DATABASE = [
    # Strait of Hormuz transiting tankers
    {"mmsi": "477123456", "name": "GULF TITAN", "type": "VLCC", "flag": "Marshall Islands",
     "lat": 26.58, "lon": 56.23, "speed_kts": 12.4, "heading": 135, "cargo": "Arabian Light Crude",
     "destination": "Jamnagar", "eta_days": 4, "corridor": "strait_of_hormuz", "status": "TRANSITING"},
    {"mmsi": "566234567", "name": "INDIA SPIRIT", "type": "VLCC", "flag": "India",
     "lat": 25.42, "lon": 57.88, "speed_kts": 14.1, "heading": 110, "cargo": "Arab Heavy Crude",
     "destination": "Mundra", "eta_days": 5, "corridor": "strait_of_hormuz", "status": "TRANSITING"},
    {"mmsi": "310345678", "name": "HORMUZ STAR", "type": "Suezmax", "flag": "Greece",
     "lat": 26.91, "lon": 55.67, "speed_kts": 0.3, "heading": 0, "cargo": "Iraqi Basrah Light",
     "destination": "Paradip", "eta_days": None, "corridor": "strait_of_hormuz", "status": "ANCHORED — AWAITING CLEARANCE"},
    {"mmsi": "229456789", "name": "KAIROS VENTURE", "type": "VLCC", "flag": "Cyprus",
     "lat": 24.85, "lon": 59.12, "speed_kts": 13.7, "heading": 125, "cargo": "Kuwait Export Crude",
     "destination": "Kochi", "eta_days": 6, "corridor": "strait_of_hormuz", "status": "TRANSITING"},

    # Red Sea corridor
    {"mmsi": "538567890", "name": "ATLAS MARINER", "type": "Suezmax", "flag": "Marshall Islands",
     "lat": 13.22, "lon": 43.77, "speed_kts": 16.2, "heading": 155, "cargo": "Libyan Es Sider",
     "destination": "Chennai", "eta_days": 12, "corridor": "red_sea", "status": "DIVERTING — CAPE ROUTE"},
    {"mmsi": "255678901", "name": "OCEAN PROVIDER", "type": "Aframax", "flag": "Malta",
     "lat": 14.83, "lon": 42.58, "speed_kts": 8.1, "heading": 180, "cargo": "Yemeni Crude",
     "destination": "Haldia", "eta_days": None, "corridor": "red_sea", "status": "DELAYED — RISK ASSESSMENT"},

    # Cape of Good Hope alternative route
    {"mmsi": "636789012", "name": "CAPE PIONEER", "type": "VLCC", "flag": "Liberia",
     "lat": -28.54, "lon": 32.14, "speed_kts": 15.3, "heading": 45, "cargo": "Nigerian Bonny Light",
     "destination": "Jamnagar", "eta_days": 14, "corridor": "cape_of_good_hope", "status": "TRANSITING — ALT ROUTE"},
    {"mmsi": "372890123", "name": "RESILIENCE MAX", "type": "Suezmax", "flag": "Panama",
     "lat": -33.91, "lon": 18.52, "speed_kts": 14.8, "heading": 70, "cargo": "Angolan Girassol",
     "destination": "Kochi", "eta_days": 16, "corridor": "cape_of_good_hope", "status": "TRANSITING — ALT ROUTE"},

    # Arabian Sea approach
    {"mmsi": "419901234", "name": "MUMBAI STAR", "type": "VLCC", "flag": "India",
     "lat": 20.12, "lon": 68.43, "speed_kts": 11.8, "heading": 70, "cargo": "Saudi Arab Light",
     "destination": "Jamnagar", "eta_days": 1, "corridor": "arabian_sea", "status": "APPROACHING PORT"},
    {"mmsi": "503012345", "name": "EASTERN GRACE", "type": "Aframax", "flag": "Singapore",
     "lat": 18.77, "lon": 66.91, "speed_kts": 13.2, "heading": 85, "cargo": "Russian Urals",
     "destination": "Mundra", "eta_days": 2, "corridor": "arabian_sea", "status": "APPROACHING PORT"},
]

STATUS_COLORS = {
    "TRANSITING": "#44BB44",
    "TRANSITING — ALT ROUTE": "#88DDAA",
    "ANCHORED — AWAITING CLEARANCE": "#FF8C00",
    "DELAYED — RISK ASSESSMENT": "#FF4444",
    "DIVERTING — CAPE ROUTE": "#FFA500",
    "APPROACHING PORT": "#4488FF",
}

VESSEL_ICONS = {
    "VLCC": "🛢️",
    "Suezmax": "🚢",
    "Aframax": "⛴️",
}


def get_live_vessels() -> list[dict]:
    """Return current vessel positions with minor random drift to simulate live data."""
    np.random.seed(int(datetime.now().strftime("%H%M")))
    vessels = []
    for v in VESSELS_DATABASE:
        vessel = v.copy()
        # Simulate position drift
        if vessel["status"] not in ["ANCHORED — AWAITING CLEARANCE"]:
            drift = 0.05
            vessel["lat"] = round(vessel["lat"] + np.random.uniform(-drift, drift), 4)
            vessel["lon"] = round(vessel["lon"] + np.random.uniform(-drift, drift), 4)
        vessel["color"] = STATUS_COLORS.get(vessel["status"], "#888888")
        vessel["icon"] = VESSEL_ICONS.get(vessel["type"], "🚢")
        vessel["last_update"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        vessels.append(vessel)
    return vessels


def get_corridor_summary() -> dict:
    """Summarise vessel activity by corridor."""
    vessels = get_live_vessels()
    summary = {}
    for v in vessels:
        c = v["corridor"]
        if c not in summary:
            summary[c] = {"total": 0, "delayed": 0, "transiting": 0, "vessels": []}
        summary[c]["total"] += 1
        if "DELAYED" in v["status"] or "ANCHORED" in v["status"]:
            summary[c]["delayed"] += 1
        elif "TRANSITING" in v["status"] or "APPROACHING" in v["status"]:
            summary[c]["transiting"] += 1
        summary[c]["vessels"].append(v["name"])
    return summary


def get_at_risk_vessels() -> list[dict]:
    """Return vessels with delayed or uncertain status."""
    return [v for v in get_live_vessels()
            if any(s in v["status"] for s in ["DELAYED", "ANCHORED", "DIVERTING"])]
