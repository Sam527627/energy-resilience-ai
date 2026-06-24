"""
Live geopolitical news ingestion for energy supply chain risk monitoring.
Uses NewsAPI with fallback to curated demo headlines.
"""

import requests
from datetime import datetime, timedelta
from config.settings import NEWS_API_KEY, DEMO_MODE


RISK_KEYWORDS = [
    "Strait of Hormuz", "Iran oil", "Houthi attack", "Red Sea shipping",
    "OPEC", "Saudi Arabia oil", "Iraq oil exports", "Persian Gulf tanker",
    "crude oil sanctions", "energy supply disruption", "India oil imports",
    "Bab-el-Mandeb", "Gulf of Oman", "Yemen attack", "oil embargo"
]


def fetch_geopolitical_news(max_articles: int = 10) -> list[dict]:
    """Fetch latest geopolitical energy risk news."""
    if DEMO_MODE or not NEWS_API_KEY:
        return _demo_headlines()

    query = " OR ".join(RISK_KEYWORDS[:5])
    from_date = (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d")

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": max_articles,
            "apiKey": NEWS_API_KEY
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "published": a.get("publishedAt", "")[:10],
                "url": a.get("url", ""),
                "description": a.get("description", "")
            })
        return articles
    except Exception:
        return _demo_headlines()


def _demo_headlines() -> list[dict]:
    """Curated realistic headlines reflecting the current threat environment (June 2026)."""
    return [
        {
            "title": "Houthi forces claim drone strike on VLCC transiting Bab-el-Mandeb southbound",
            "source": "Reuters",
            "published": "2026-06-21",
            "url": "#",
            "description": "A Yemeni Houthi spokesperson announced a drone strike on a very large crude carrier transiting the Bab-el-Mandeb strait, raising alarm among Indian refinery operators reliant on Red Sea routing.",
            "risk_score": 85,
            "corridor": "red_sea"
        },
        {
            "title": "US Treasury expands Iran oil sanctions; targets three additional shipping entities",
            "source": "Bloomberg",
            "published": "2026-06-20",
            "url": "#",
            "description": "The US Treasury's OFAC designated three additional entities facilitating Iranian crude exports, tightening enforcement and potentially reducing supply available to secondary market buyers.",
            "risk_score": 72,
            "corridor": "strait_of_hormuz"
        },
        {
            "title": "IRGC conducts naval exercises in Strait of Hormuz; shipping warned of delays",
            "source": "Al Jazeera",
            "published": "2026-06-19",
            "url": "#",
            "description": "Iran's Islamic Revolutionary Guard Corps announced a three-day maritime exercise in the Strait of Hormuz, with maritime advisories issued for transiting vessels on both inbound and outbound lanes.",
            "risk_score": 78,
            "corridor": "strait_of_hormuz"
        },
        {
            "title": "OPEC+ emergency meeting called amid price volatility; output cut extension discussed",
            "source": "Financial Times",
            "published": "2026-06-18",
            "url": "#",
            "description": "OPEC+ members are convening an emergency virtual session to discuss extending production cuts through Q4 2026 as Brent crude slides below the group's preferred $85/bbl threshold.",
            "risk_score": 65,
            "corridor": "global"
        },
        {
            "title": "Indian refiners scramble for spot cargoes as Saudi OSPs rise 3.2% for July",
            "source": "Platts",
            "published": "2026-06-17",
            "url": "#",
            "description": "Saudi Aramco has raised its official selling prices for Arab Light crude to Asia by $3.20/bbl for July loadings, prompting Indian refiners to evaluate alternative procurement corridors.",
            "risk_score": 58,
            "corridor": "strait_of_hormuz"
        },
        {
            "title": "Russia-India crude trade at record high; Urals discount narrows to $4/bbl",
            "source": "Energy Intelligence",
            "published": "2026-06-16",
            "url": "#",
            "description": "Russia supplied a record 2.1 million barrels per day to Indian refiners in May 2026, but the Urals discount to Brent has narrowed significantly as Western buyers reduce exposure.",
            "risk_score": 35,
            "corridor": "alternative"
        },
        {
            "title": "Pentagon confirms naval escort operations expanded for tankers in Gulf of Oman",
            "source": "Defense News",
            "published": "2026-06-15",
            "url": "#",
            "description": "US Fifth Fleet announced an expansion of escort operations for commercial tankers in the Gulf of Oman corridor following three incidents in the preceding 30 days.",
            "risk_score": 70,
            "corridor": "strait_of_hormuz"
        },
    ]
