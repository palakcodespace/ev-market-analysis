"""
Automated Pytest Suite: Database Connectivity, Schema Integrity, and Views.
"""
import pytest
from sqlalchemy import text
from database.db_connection import db_manager

def test_database_connection():
    """Verifies active database connection and engine initialization."""
    with db_manager.get_connection() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1

def test_tables_exist_and_populated():
    """Verifies that all 6 normalized relational tables are created and contain data."""
    required_tables = [
        "manufacturers",
        "battery_technologies",
        "geographies",
        "vehicles",
        "customer_ratings",
        "sales"
    ]
    with db_manager.get_connection() as conn:
        for tbl in required_tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            assert count > 0, f"Table {tbl} must be populated"

def test_foreign_key_integrity():
    """Ensures no orphan records exist across vehicles, ratings, and sales."""
    with db_manager.get_connection() as conn:
        # Vehicles with invalid manufacturer FK
        orphan_veh_mfg = conn.execute(text("""
            SELECT COUNT(*) FROM vehicles v
            LEFT JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
            WHERE m.manufacturer_id IS NULL
        """)).scalar()
        assert orphan_veh_mfg == 0

        # Ratings with invalid vehicle FK
        orphan_rating = conn.execute(text("""
            SELECT COUNT(*) FROM customer_ratings cr
            LEFT JOIN vehicles v ON cr.vehicle_id = v.vehicle_id
            WHERE v.vehicle_id IS NULL
        """)).scalar()
        assert orphan_rating == 0

        # Sales with invalid manufacturer FK
        orphan_sales = conn.execute(text("""
            SELECT COUNT(*) FROM sales s
            LEFT JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
            WHERE m.manufacturer_id IS NULL
        """)).scalar()
        assert orphan_sales == 0

def test_analytical_views_queryable():
    """Ensures all 6 analytical SQL views return valid summary records."""
    views = [
        "vw_annual_sales_trends",
        "vw_manufacturer_market_share",
        "vw_category_performance",
        "vw_battery_technology_distribution",
        "vw_geographic_manufacturing_distribution",
        "vw_vehicle_performance_ratings"
    ]
    with db_manager.get_connection() as conn:
        for vw in views:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {vw}")).scalar()
            assert res > 0, f"View {vw} must return records"
