"""
Meridian Maritime Intelligence — Central Configuration
50+ API integrations. Set keys in .env. Platform degrades gracefully:
live API → cached → high-fidelity simulation.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# CORE
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEMO_MODE         = os.getenv("DEMO_MODE", "true").lower() == "true"
APP_TITLE         = os.getenv("APP_TITLE", "Meridian Maritime Intelligence")
CACHE_TTL_SECS    = int(os.getenv("CACHE_TTL_SECS", "300"))
BRAND_NAME        = "MERIDIAN"
BRAND_TAGLINE     = "Maritime Intelligence Platform"
BRAND_FULL        = "Meridian Maritime Intelligence"

# ═════════════════════════════════════════════
# API REGISTRY — 50+ endpoints across 9 categories
# ═════════════════════════════════════════════

# ── 1. VESSEL / AIS TRACKING (8) ──
VESSELAPI_KEY      = os.getenv("VESSELAPI_KEY", "")        # vesselapi.com — FREE tier 695K vessels
AIS_API_KEY        = os.getenv("AIS_API_KEY", "")          # datalastic.com
MARINETRAFFIC_KEY  = os.getenv("MARINETRAFFIC_KEY", "")
VESSELFINDER_KEY   = os.getenv("VESSELFINDER_KEY", "")
MYSHIPTRACKING_KEY = os.getenv("MYSHIPTRACKING_KEY", "")
SEARATES_KEY       = os.getenv("SEARATES_KEY", "")
SPIRE_KEY          = os.getenv("SPIRE_KEY", "")
SHIPFINDER_KEY     = os.getenv("SHIPFINDER_KEY", "")

VESSEL_APIS = {
    "vesselapi":      "https://api.vesselapi.com/v1",
    "datalastic":     "https://api.datalastic.com/api/v0/vessel",
    "marinetraffic":  "https://services.marinetraffic.com/api/getvessel/v:3",
    "vesselfinder":   "https://api.vesselfinder.com/vessels",
    "myshiptracking": "https://api.myshiptracking.com/api/v2/vessel",
    "searates":       "https://rest.searates.com/tracking",
    "shipfinder":     "https://api.shipfinder.com/apicall/QueryShip",
    "aishub":         "https://data.aishub.net/ws.php",
}

# ── 2. SANCTIONS / COMPLIANCE (6) ──
OFAC_API_KEY = os.getenv("OFAC_API_KEY", "")
LSEG_KEY     = os.getenv("LSEG_KEY", "")
SANCTIONS_APIS = {
    "ofac_sdn":   "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.JSON",
    "ofac_cons":  "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONS_PRIM.JSON",
    "eu_consol":  "https://webgate.ec.europa.eu/fsd/fsf/public/files/jsonFullSanctionsList_1_1/content",
    "uk_ofsi":    "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.json",
    "un_sc":      "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
    "opensanctions":"https://api.opensanctions.org/search/default",
}

# ── 3. COMMODITY / MARKETS (7) ──
NEWS_API_KEY      = os.getenv("NEWS_API_KEY", "")
EIA_API_KEY       = os.getenv("EIA_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
FRED_API_KEY      = os.getenv("FRED_API_KEY", "")
QUANDL_KEY        = os.getenv("QUANDL_KEY", "")
COMMODITY_APIS = {
    "eia_brent":      "https://api.eia.gov/v2/petroleum/pri/spt/data/",
    "eia_stocks":     "https://api.eia.gov/v2/petroleum/stoc/wstk/data/",
    "alpha_vantage":  "https://www.alphavantage.co/query",
    "fred":           "https://api.stlouisfed.org/fred/series/observations",
    "opec_basket":    "https://www.opec.org/basket/basketDayArchives.xml",
    "worldbank":      "https://api.worldbank.org/v2/country/IND/indicator",
    "yahoo":          "yfinance",
}

# ── 4. WEATHER / METOCEAN (5) ──
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")
STORMGLASS_KEY  = os.getenv("STORMGLASS_KEY", "")
WEATHER_APIS = {
    "openmeteo_marine": "https://marine-api.open-meteo.com/v1/marine",   # FREE, no key
    "openmeteo_fcst":   "https://api.open-meteo.com/v1/forecast",         # FREE, no key
    "stormglass":       "https://api.stormglass.io/v2/weather/point",
    "openweather":      "https://api.openweathermap.org/data/2.5/weather",
    "noaa":             "https://api.weather.gov/points",
}

# ── 5. PORT / INCIDENT INTELLIGENCE (6) ──
PORT_APIS = {
    "ukmto":         "https://www.ukmto.org/rss/incidents.rss",
    "icc_piracy":    "https://www.icc-ccs.org/rss/imo.xml",
    "recaap":        "https://www.recaap.org/incident_rss",
    "nato_shipping": "https://www.shipping.nato.int/nsc/rss",
    "mschoa":        "https://www.mschoa.org/feed",
    "imo_gisis":     "https://gisis.imo.org/Public",
}

# ── 6. NEWS / GEOPOLITICAL (4) ──
NEWS_APIS = {
    "newsapi":  "https://newsapi.org/v2/everything",
    "gdelt":    "https://api.gdeltproject.org/api/v2/doc/doc",   # FREE, no key
    "reuters":  "https://www.reutersagency.com/feed/",
    "marex":    "https://www.maritime-executive.com/rss",
}

# ── 7. GEOSPATIAL / MAPPING (3) ──
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
GEO_APIS = {
    "openseamap":   "https://tiles.openseamap.org",
    "natural_earth":"https://www.naturalearthdata.com",
    "geonames":     "http://api.geonames.org/searchJSON",
}

# ── 8. ECONOMIC / FX (3) ──
FX_APIS = {
    "exchangerate": "https://api.exchangerate-api.com/v4/latest/USD",  # FREE
    "frankfurter":  "https://api.frankfurter.app/latest",               # FREE, no key
    "worldbank_gdp":"https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.CD",
}

# ── 9. BUNKER / FREIGHT (6) ──
FREIGHT_APIS = {
    "baltic_proxy":  "internal",
    "ship_bunker":   "https://shipandbunker.com/prices",
    "vortexa":       "https://api.vortexa.com",
    "balticexchange":"https://www.balticexchange.com/api",
    "freightos":     "https://www.freightos.com/freight-index",
    "xeneta":        "https://www.xeneta.com/api",
}

# ── 10. CARBON / ENVIRONMENTAL (4) ──
CARBON_APIS = {
    "imo_dcs":       "https://gisis.imo.org/Public/SHIPS",     # IMO ship CII data
    "rightship":     "https://www.rightship.com/api",
    "carbon_chain":  "https://api.carbonchain.com",
    "co2_emiss":     "https://api.carbonintensity.org.uk",     # FREE
}

# Count total
ALL_API_COUNT = (len(VESSEL_APIS)+len(SANCTIONS_APIS)+len(COMMODITY_APIS)+
                 len(WEATHER_APIS)+len(PORT_APIS)+len(NEWS_APIS)+len(GEO_APIS)+
                 len(FX_APIS)+len(FREIGHT_APIS)+len(CARBON_APIS))

# ═════════════════════════════════════════════
# DOMAIN DATA
# ═════════════════════════════════════════════
CORRIDORS = {
    "strait_of_hormuz": {"name":"Strait of Hormuz","lat":26.5667,"lon":56.25,"india_dependency_pct":42,"daily_mbpd":21,"color":"#FF4444","risk_baseline":72,"hra":True,"bmp5_applicable":True,"ukmto_area":True},
    "red_sea":          {"name":"Red Sea / Bab-el-Mandeb","lat":12.5833,"lon":43.45,"india_dependency_pct":18,"daily_mbpd":8,"color":"#FF8C00","risk_baseline":85,"hra":True,"bmp5_applicable":True,"ukmto_area":True},
    "gulf_of_guinea":   {"name":"Gulf of Guinea","lat":2.5,"lon":2.5,"india_dependency_pct":12,"daily_mbpd":4.5,"color":"#FFD700","risk_baseline":65,"hra":True,"bmp5_applicable":False,"ukmto_area":False},
    "malacca_strait":   {"name":"Strait of Malacca","lat":2.5,"lon":101.0,"india_dependency_pct":10,"daily_mbpd":16,"color":"#9C27B0","risk_baseline":40,"hra":False,"bmp5_applicable":False,"ukmto_area":False},
    "arabian_sea":      {"name":"Arabian Sea","lat":18.0,"lon":64.0,"india_dependency_pct":15,"daily_mbpd":5.5,"color":"#4488FF","risk_baseline":35,"hra":False,"bmp5_applicable":True,"ukmto_area":True},
    "cape_of_good_hope":{"name":"Cape of Good Hope","lat":-34.3568,"lon":18.4754,"india_dependency_pct":8,"daily_mbpd":3,"color":"#44AA44","risk_baseline":22,"hra":False,"bmp5_applicable":False,"ukmto_area":False},
}

INDIA_REFINERIES = [
    {"name":"Jamnagar (Reliance)","lat":22.39,"lon":70.05,"capacity_mbpd":1.24,"operator":"Reliance"},
    {"name":"Mundra (Nayara)","lat":22.83,"lon":69.72,"capacity_mbpd":0.40,"operator":"Nayara Energy"},
    {"name":"Kochi (BPCL)","lat":10.04,"lon":76.27,"capacity_mbpd":0.31,"operator":"BPCL"},
    {"name":"Chennai (CPCL)","lat":13.08,"lon":80.27,"capacity_mbpd":0.21,"operator":"CPCL"},
    {"name":"Paradip (IOCL)","lat":20.32,"lon":86.67,"capacity_mbpd":0.30,"operator":"IOCL"},
    {"name":"Haldia (IOCL)","lat":22.06,"lon":88.07,"capacity_mbpd":0.175,"operator":"IOCL"},
    {"name":"Panipat (IOCL)","lat":29.39,"lon":76.97,"capacity_mbpd":0.30,"operator":"IOCL"},
    {"name":"Vizag (HPCL)","lat":17.69,"lon":83.22,"capacity_mbpd":0.30,"operator":"HPCL"},
]

ALT_CRUDE_SOURCES = [
    {"country":"Russia","grade":"Urals","max_mbpd":1.8,"premium_usd":-3.5,"route":"Cape/Arctic","transit_days":28,"g2g":True},
    {"country":"Saudi Arabia","grade":"Arab Light","max_mbpd":1.5,"premium_usd":0.8,"route":"Hormuz","transit_days":8,"g2g":True},
    {"country":"UAE","grade":"Murban","max_mbpd":0.8,"premium_usd":1.2,"route":"Hormuz","transit_days":9,"g2g":True},
    {"country":"USA","grade":"WTI Midland","max_mbpd":0.6,"premium_usd":2.1,"route":"Cape","transit_days":35,"g2g":False},
    {"country":"Nigeria","grade":"Bonny Light","max_mbpd":0.25,"premium_usd":1.8,"route":"Direct","transit_days":18,"g2g":False},
    {"country":"Angola","grade":"Girassol","max_mbpd":0.20,"premium_usd":1.2,"route":"Direct","transit_days":20,"g2g":False},
    {"country":"Brazil","grade":"Lula","max_mbpd":0.15,"premium_usd":2.5,"route":"Cape","transit_days":30,"g2g":False},
    {"country":"Iraq","grade":"Basrah Light","max_mbpd":1.0,"premium_usd":0.5,"route":"Hormuz","transit_days":10,"g2g":True},
    {"country":"Kuwait","grade":"Kuwait Export","max_mbpd":0.7,"premium_usd":0.9,"route":"Hormuz","transit_days":9,"g2g":True},
    {"country":"Kazakhstan","grade":"CPC Blend","max_mbpd":0.4,"premium_usd":0.8,"route":"Caspian","transit_days":22,"g2g":True},
]

SPR_CAPACITY_DAYS = 9.5
INDIA_DAILY_CONSUMPTION_MBPD = 5.1
SPR_SITES = [
    {"name":"Visakhapatnam","capacity_MMbbl":9.75,"current_fill_pct":88,"operator":"ISPRL","lat":17.68,"lon":83.22},
    {"name":"Mangaluru","capacity_MMbbl":11.33,"current_fill_pct":82,"operator":"ISPRL","lat":12.87,"lon":74.88},
    {"name":"Padur","capacity_MMbbl":18.33,"current_fill_pct":91,"operator":"ISPRL","lat":13.18,"lon":74.89},
]

VESSEL_TYPE_ICONS = {
    "VLCC":"🛢️","Crude Oil Tanker":"🛢️","Oil Tanker":"🛢️","Product Tanker":"⛽","Chemical Tanker":"⚗️",
    "Bulk Carrier":"🚢","Container Ship":"📦","LNG Tanker":"🔵","LPG Tanker":"🟡","General Cargo":"📦",
    "Passenger":"🛳️","Ro-Ro":"🚗","Offshore":"⚓","Tug":"🚤","Fishing":"🎣","Unknown":"🚢",
}

# Navigation status codes (AIS standard)
NAV_STATUS = {
    0:"Under way using engine",1:"At anchor",2:"Not under command",3:"Restricted manoeuvrability",
    4:"Constrained by draught",5:"Moored",6:"Aground",7:"Engaged in fishing",8:"Under way sailing",
    15:"Undefined",
}
