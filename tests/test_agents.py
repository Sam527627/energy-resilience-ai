"""
Unit tests for EnergyShield AI agents.
Run: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.commodity_feed import get_live_prices, get_brent_history, get_tanker_rates
from utils.news_fetcher import fetch_geopolitical_news
from agents.ais_tracker import get_live_vessels, get_at_risk_vessels, get_corridor_summary
from agents.scenario_modeller import get_all_scenarios


class TestCommodityFeed:
    def test_live_prices_returns_dict(self):
        prices = get_live_prices()
        assert isinstance(prices, dict)
        assert "brent_crude" in prices
        assert "wti_crude" in prices

    def test_brent_price_in_realistic_range(self):
        prices = get_live_prices()
        brent = prices["brent_crude"]["price"]
        assert 40 < brent < 150, f"Brent price {brent} outside realistic range"

    def test_brent_history_returns_dataframe(self):
        df = get_brent_history(30)
        assert len(df) > 0
        assert "brent_usd" in df.columns

    def test_tanker_rates_positive(self):
        rates = get_tanker_rates()
        assert rates["vlcc_me_india"] > 10000


class TestNewsFetcher:
    def test_returns_list(self):
        headlines = fetch_geopolitical_news(5)
        assert isinstance(headlines, list)
        assert len(headlines) > 0

    def test_headlines_have_required_fields(self):
        headlines = fetch_geopolitical_news(3)
        for h in headlines:
            assert "title" in h
            assert "source" in h
            assert "published" in h


class TestAISTracker:
    def test_vessels_returned(self):
        vessels = get_live_vessels()
        assert len(vessels) > 0

    def test_vessel_has_coordinates(self):
        vessels = get_live_vessels()
        for v in vessels:
            assert -90 <= v["lat"] <= 90
            assert -180 <= v["lon"] <= 180

    def test_at_risk_vessels_subset(self):
        all_vessels = get_live_vessels()
        at_risk = get_at_risk_vessels()
        assert len(at_risk) <= len(all_vessels)

    def test_corridor_summary_structure(self):
        summary = get_corridor_summary()
        assert isinstance(summary, dict)
        for key, val in summary.items():
            assert "total" in val
            assert "delayed" in val


class TestScenarioModeller:
    def test_all_scenarios_returned(self):
        scenarios = get_all_scenarios()
        assert len(scenarios) >= 5

    def test_scenario_has_required_fields(self):
        scenarios = get_all_scenarios()
        for key, s in scenarios.items():
            assert "name" in s
            assert "supply_reduction_pct" in s
            assert "duration_days" in s
            assert s["supply_reduction_pct"] > 0
