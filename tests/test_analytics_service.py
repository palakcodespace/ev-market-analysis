"""
Automated Pytest Suite: EVAnalyticsService Query Operations and Business Logic.
"""
import pytest
from src.analytics import EVAnalyticsService

def test_get_executive_kpis_default():
    """Verifies default macro KPI aggregation."""
    kpis = EVAnalyticsService.get_executive_kpis()
    assert kpis["total_sales_units"] > 20000000
    assert kpis["active_manufacturers"] >= 15
    assert 400 < kpis["avg_electric_range_km"] < 700
    assert 60 < kpis["avg_battery_capacity_kwh"] < 120
    assert 3.5 <= kpis["avg_customer_rating"] <= 5.0

def test_get_executive_kpis_with_filters():
    """Verifies parameterized KPI calculation when filters are supplied."""
    kpis_2024 = EVAnalyticsService.get_executive_kpis(year=2024)
    assert kpis_2024["total_sales_units"] > 0

    kpis_tesla = EVAnalyticsService.get_executive_kpis(manufacturer="Tesla")
    assert kpis_tesla["vehicle_models_analyzed"] > 0
    assert kpis_tesla["avg_electric_range_km"] > 400

    kpis_suv = EVAnalyticsService.get_executive_kpis(category="SUV")
    assert kpis_suv["vehicle_models_analyzed"] > 0

def test_annual_sales_trend():
    """Verifies time-series sales trend calculations."""
    trend = EVAnalyticsService.get_annual_sales_trend()
    assert len(trend) >= 6
    years = [d["sales_year"] for d in trend]
    assert 2018 in years
    assert 2024 in years
    # YoY growth rate must be numeric
    for d in trend[1:]:
        assert isinstance(d["yoy_growth_pct"], (int, float))

def test_manufacturer_rankings():
    """Verifies manufacturer rankings for given year."""
    rankings_2024 = EVAnalyticsService.get_manufacturer_rankings(year=2024, limit=10)
    assert len(rankings_2024) == 10
    assert rankings_2024[0]["total_units"] >= rankings_2024[1]["total_units"]
    assert "market_share_pct" in rankings_2024[0]

def test_battery_tech_distribution():
    """Verifies battery technology distribution summary."""
    data = EVAnalyticsService.get_battery_tech_distribution()
    assert len(data) == 3
    chem_codes = {d["chemistry_code"] for d in data}
    assert chem_codes == {"LFP", "NMC", "NCA"}

def test_customer_satisfaction_summary():
    """Verifies customer ratings metrics by manufacturer."""
    ratings = EVAnalyticsService.get_customer_satisfaction_summary()
    assert len(ratings) > 0
    top = ratings[0]
    assert 3.0 <= top["avg_overall_rating"] <= 5.0
    assert "avg_reliability" in top
