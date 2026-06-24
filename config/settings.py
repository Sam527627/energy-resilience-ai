"""
EnergyShield AI / Foresight Live — Central Configuration
All API integrations documented here. Set keys in .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CORE AI
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────
# APP SETTINGS
# ─────────────────────────────────────────────
APP_TITLE       = os.getenv("APP_TITLE", "EnergyShield AI × Foresight Live")
DEMO_MODE       = os.getenv("DEMO_MODE", "true").lower() == "true"
CACHE_TTL_SECS  = int(os.getenv("CACHE_TTL_SECS", "300"))   # 5 min default cache

# ─────────────────────────────────────────────
# AIS / VESSEL TRACKING APIs
# Plug in whichever you subscribe to — platform supports all
# ─────────────────────────────────────────────
AIS_API_KEY          = os.getenv("AIS_API_KEY", "")          # Datalastic / AISHub
MARINETRAFFIC_KEY    = os.getenv("MARINETRAFFIC_KEY", "")    # MarineTraffic (industry standard)
VESSELFINDER_KEY     = os.getenv("VESSELFINDER_KEY", "")     # VesselFinder
MYSHIPTRACKING_KEY   = os.getenv("MYSHIPTRACKING_KEY", "")   # MyShipTracking
SPIRE_KEY            = os.getenv("SPIRE_KEY", "")            # Spire Maritime (satellite AIS)
EXACTEARTH_KEY       = os.getenv("EXACTEARTH_KEY", "")       # exactEarth (satellite AIS)

# AIS endpoint map
AIS_ENDPOINTS = {
    "datalastic":     "https://api.datalastic.com/api/v0/vessel",
    "marinetraffic":  "https://services.marinetraffic.com/api/getvessel/v:3",
    "vesselfinder":   "https://api.vesselfinder.com/vessels",
    "myshiptracking": "https://api.myshiptracking.com/api/v2/ais/vessel",
    "spire":          "https://api.spire.com/graphql",
    "aishub":         "https://data.aishub.net/ws.php",
}

# ─────────────────────────────────────────────
# COMMODITY / MARKET DATA APIs
# ─────────────────────────────────────────────
NEWS_API_KEY         = os.getenv("NEWS_API_KEY", "")
ALPHA_VANTAGE_KEY    = os.getenv("ALPHA_VANTAGE_KEY", "")    # Commodity prices
EIA_API_KEY          = os.getenv("EIA_API_KEY", "")          # US Energy Info Admin (free)
QUANDL_KEY           = os.getenv("QUANDL_KEY", "")           # OPEC / crude data
FRED_API_KEY         = os.getenv("FRED_API_KEY", "")         # Federal Reserve (free)

# Commodity endpoints
COMMODITY_ENDPOINTS = {
    "eia_petroleum":    "https://api.eia.gov/v2/petroleum/pri/spt/data/",
    "alpha_vantage":    "https://www.alphavantage.co/query",
    "fred_oil":         "https://api.stlouisfed.org/fred/series/observations",
    "opec_basket":      "https://www.opec.org/opec_web/static/project/member/data/OPEC_basket.json",
}

# ─────────────────────────────────────────────
# SANCTIONS / COMPLIANCE APIs
# ─────────────────────────────────────────────
OFAC_API_KEY     = os.getenv("OFAC_API_KEY", "")    # OFAC SDN list
LSEG_KEY         = os.getenv("LSEG_KEY", "")         # LSEG World-Check (used by Windward)
REFINITIV_KEY    = os.getenv("REFINITIV_KEY", "")    # Refinitiv screening

SANCTIONS_ENDPOINTS = {
    "ofac_sdn":    "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.JSON",
    "eu_consol":   "https://webgate.ec.europa.eu/fsd/fsf/public/files/jsonFullSanctionsList_1_1/content",
    "uk_ofsi":     "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.json",
    "un_sc":       "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
    "swiss_seco":  "https://www.seco.admin.ch/dam/seco/de/dokumente/Aussenwirtschaft/Wirtschaftliche_Landesversorgung/Embargo_Massnahmen/sanktionen_aktuell.xlsx.download.xlsx",
}

# ─────────────────────────────────────────────
# WEATHER / METOCEAN APIs
# ─────────────────────────────────────────────
OPENWEATHER_KEY      = os.getenv("OPENWEATHER_KEY", "")    # Free tier available
STORMGLASS_KEY       = os.getenv("STORMGLASS_KEY", "")     # Marine weather / wave height
WINDY_KEY            = os.getenv("WINDY_KEY", "")           # Windy.com API

WEATHER_ENDPOINTS = {
    "openweather":  "https://api.openweathermap.org/data/2.5/weather",
    "stormglass":   "https://api.stormglass.io/v2/weather/point",
    "openmeteo":    "https://marine-api.open-meteo.com/v1/marine",   # FREE, no key
}

# ─────────────────────────────────────────────
# PORT / MARITIME AUTHORITY APIs
# ─────────────────────────────────────────────
PORT_ENDPOINTS = {
    "ukmto":        "https://www.ukmto.org/rss/incidents.rss",       # UKMTO incident feed (free RSS)
    "icc_piracy":   "https://www.icc-ccs.org/rss/imo.xml",           # ICC piracy reports
    "mschoa":       "https://www.mschoa.org/",                        # EU NAVFOR
    "nato_shipping":"https://mc.nato.int/rss.aspx",                  # NATO shipping advisories
    "imo_gisis":    "https://gisis.imo.org/Public/",                  # IMO GISIS vessel registry
}

# ─────────────────────────────────────────────
# GEOSPATIAL / MAPPING APIs
# ─────────────────────────────────────────────
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

# ─────────────────────────────────────────────
# DOMAIN DATA
# ─────────────────────────────────────────────
CORRIDORS = {
    "strait_of_hormuz": {
        "name": "Strait of Hormuz",
        "lat": 26.5667, "lon": 56.25,
        "india_dependency_pct": 42,
        "daily_mbpd": 21,
        "color": "#FF4444",
        "risk_baseline": 72,
        "hra": True,
        "bmp5_applicable": True,
        "ukmto_area": True,
    },
    "red_sea": {
        "name": "Red Sea / Bab-el-Mandeb",
        "lat": 12.5833, "lon": 43.45,
        "india_dependency_pct": 18,
        "daily_mbpd": 8,
        "color": "#FF8C00",
        "risk_baseline": 85,
        "hra": True,
        "bmp5_applicable": True,
        "ukmto_area": True,
    },
    "gulf_of_guinea": {
        "name": "Gulf of Guinea",
        "lat": 2.5, "lon": 2.5,
        "india_dependency_pct": 12,
        "daily_mbpd": 4.5,
        "color": "#FFD700",
        "risk_baseline": 65,
        "hra": True,
        "bmp5_applicable": False,
        "ukmto_area": False,
    },
    "arabian_sea": {
        "name": "Arabian Sea",
        "lat": 18.0, "lon": 64.0,
        "india_dependency_pct": 15,
        "daily_mbpd": 5.5,
        "color": "#4488FF",
        "risk_baseline": 35,
        "hra": False,
        "bmp5_applicable": True,
        "ukmto_area": True,
    },
    "cape_of_good_hope": {
        "name": "Cape of Good Hope (Alternate)",
        "lat": -34.3568, "lon": 18.4754,
        "india_dependency_pct": 8,
        "daily_mbpd": 3,
        "color": "#44AA44",
        "risk_baseline": 22,
        "hra": False,
        "bmp5_applicable": False,
        "ukmto_area": False,
    }
}

INDIA_REFINERIES = [
    {"name": "Jamnagar (Reliance)", "lat": 22.39, "lon": 70.05, "capacity_mbpd": 1.24, "operator": "Reliance"},
    {"name": "Mundra (Nayara)", "lat": 22.83, "lon": 69.72, "capacity_mbpd": 0.40, "operator": "Nayara Energy"},
    {"name": "Kochi (BPCL)", "lat": 10.04, "lon": 76.27, "capacity_mbpd": 0.31, "operator": "BPCL"},
    {"name": "Chennai (CPCL)", "lat": 13.08, "lon": 80.27, "capacity_mbpd": 0.21, "operator": "CPCL"},
    {"name": "Paradip (IOCL)", "lat": 20.32, "lon": 86.67, "capacity_mbpd": 0.30, "operator": "IOCL"},
    {"name": "Haldia (IOCL)", "lat": 22.06, "lon": 88.07, "capacity_mbpd": 0.175, "operator": "IOCL"},
    {"name": "Panipat (IOCL)", "lat": 29.39, "lon": 76.97, "capacity_mbpd": 0.30, "operator": "IOCL"},
    {"name": "Bina (BPCL-Oman)", "lat": 24.17, "lon": 78.14, "capacity_mbpd": 0.156, "operator": "BPCL"},
]

ALT_CRUDE_SOURCES = [
    {"country": "Russia", "grade": "Urals", "max_mbpd": 1.8, "premium_usd": -3.5, "route": "Cape/Arctic", "transit_days": 28, "g2g": True},
    {"country": "Saudi Arabia", "grade": "Arab Light", "max_mbpd": 1.5, "premium_usd": 0.8, "route": "Hormuz", "transit_days": 8, "g2g": True},
    {"country": "UAE", "grade": "Murban", "max_mbpd": 0.8, "premium_usd": 1.2, "route": "Hormuz", "transit_days": 9, "g2g": True},
    {"country": "USA", "grade": "WTI Midland", "max_mbpd": 0.6, "premium_usd": 2.1, "route": "Cape of Good Hope", "transit_days": 35, "g2g": False},
    {"country": "Nigeria", "grade": "Bonny Light", "max_mbpd": 0.25, "premium_usd": 1.8, "route": "Direct", "transit_days": 18, "g2g": False},
    {"country": "Angola", "grade": "Girassol", "max_mbpd": 0.20, "premium_usd": 1.2, "route": "Direct", "transit_days": 20, "g2g": False},
    {"country": "Brazil", "grade": "Lula", "max_mbpd": 0.15, "premium_usd": 2.5, "route": "Cape of Good Hope", "transit_days": 30, "g2g": False},
    {"country": "Kazakhstan", "grade": "CPC Blend", "max_mbpd": 0.4, "premium_usd": 0.8, "route": "Pipeline/Caspian", "transit_days": 22, "g2g": True},
    {"country": "Iraq", "grade": "Basrah Light", "max_mbpd": 1.0, "premium_usd": 0.5, "route": "Hormuz", "transit_days": 10, "g2g": True},
    {"country": "Kuwait", "grade": "Kuwait Export", "max_mbpd": 0.7, "premium_usd": 0.9, "route": "Hormuz", "transit_days": 9, "g2g": True},
]

SPR_CAPACITY_DAYS          = 9.5
INDIA_DAILY_CONSUMPTION_MBPD = 5.1

SPR_SITES = [
    {"name": "Visakhapatnam", "capacity_MMbbl": 9.75,  "current_fill_pct": 88, "operator": "ISPRL", "lat": 17.68, "lon": 83.22},
    {"name": "Mangaluru",     "capacity_MMbbl": 11.33, "current_fill_pct": 82, "operator": "ISPRL", "lat": 12.87, "lon": 74.88},
    {"name": "Padur",         "capacity_MMbbl": 18.33, "current_fill_pct": 91, "operator": "ISPRL", "lat": 13.18, "lon": 74.89},
]

# ─────────────────────────────────────────────
# VESSEL TYPE ICONS
# ─────────────────────────────────────────────
VESSEL_TYPE_ICONS = {
    "VLCC": "🛢️", "Crude Oil Tanker": "🛢️", "Product Tanker": "⛽",
    "Bulk Carrier": "🚢", "Container Ship": "📦", "LNG Tanker": "🔵",
    "LPG Tanker": "🟡", "Chemical Tanker": "⚗️", "General Cargo": "🚢",
    "Offshore Supply": "⚓", "Tug": "🛥️", "Unknown": "🚢"
}
