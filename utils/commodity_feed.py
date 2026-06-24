"""
Live commodity price fetcher.
Uses yfinance for Brent crude, WTI, natural gas, and shipping indices.
Falls back to realistic simulated data in demo mode.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.settings import DEMO_MODE


SYMBOLS = {
    "brent_crude": "BZ=F",
    "wti_crude": "CL=F",
    "natural_gas": "NG=F",
}


def get_live_prices() -> dict:
    """Fetch current commodity prices."""
    if DEMO_MODE:
        return _simulated_prices()
    try:
        prices = {}
        for name, symbol in SYMBOLS.items():
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            prices[name] = {
                "price": round(float(info.last_price), 2),
                "change_pct": round(float(info.regular_market_previous_close), 2),
                "currency": "USD"
            }
        return prices
    except Exception:
        return _simulated_prices()


def get_brent_history(days: int = 90) -> pd.DataFrame:
    """Fetch Brent crude price history."""
    if DEMO_MODE:
        return _simulated_brent_history(days)
    try:
        end = datetime.today()
        start = end - timedelta(days=days)
        df = yf.download("BZ=F", start=start, end=end, progress=False)
        df = df[["Close"]].rename(columns={"Close": "brent_usd"})
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return _simulated_brent_history(days)


def _simulated_prices() -> dict:
    """Realistic simulated commodity prices for demo."""
    np.random.seed(42)
    base_brent = 87.4
    shock = np.random.uniform(-2, 8)  # Simulate mild geopolitical premium
    return {
        "brent_crude": {
            "price": round(base_brent + shock, 2),
            "change_pct": round(shock / base_brent * 100, 2),
            "currency": "USD",
            "simulated": True
        },
        "wti_crude": {
            "price": round(base_brent + shock - 3.2, 2),
            "change_pct": round((shock - 0.5) / (base_brent - 3.2) * 100, 2),
            "currency": "USD",
            "simulated": True
        },
        "natural_gas": {
            "price": round(2.84 + np.random.uniform(-0.1, 0.3), 2),
            "change_pct": round(np.random.uniform(-1.5, 3.2), 2),
            "currency": "USD",
            "simulated": True
        }
    }


def _simulated_brent_history(days: int = 90) -> pd.DataFrame:
    """Generate realistic Brent crude price history with a geopolitical shock."""
    np.random.seed(7)
    dates = pd.date_range(end=datetime.today(), periods=days, freq="D")
    # Baseline around 82-88 with a shock in the last 15 days
    base = 84 + np.cumsum(np.random.randn(days) * 0.6)
    shock_start = days - 15
    base[shock_start:] += np.linspace(0, 7.8, days - shock_start)  # 2025 Hormuz scare simulation
    prices = np.clip(base, 72, 105)
    df = pd.DataFrame({"brent_usd": prices}, index=dates)
    return df


def get_tanker_rates() -> dict:
    """Baltic Dirty Tanker Index proxies (simulated)."""
    np.random.seed(99)
    return {
        "vlcc_me_india": round(35000 + np.random.uniform(-3000, 12000), 0),  # USD/day
        "suezmax_waf_india": round(28000 + np.random.uniform(-2000, 8000), 0),
        "aframax_med_india": round(22000 + np.random.uniform(-1500, 6000), 0),
        "status": "simulated"
    }
