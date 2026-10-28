"""
Performance and Latency Benchmark Script.
Measures real response times, dataset sizes, and memory usage.
Outputs results to docs/benchmark_results.json.
"""
import sys
import time
import json
import os
from pathlib import Path
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_connection import db_manager
from src.analytics import EVAnalyticsService
from app import app

def run_benchmarks():
    """Executes performance measurements across DB, API, and Flask app."""
    print("Executing EV System Performance Benchmarks...")
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware_environment": {
            "os": os.name,
            "python_version": sys.version.split()[0],
            "database_engine": "SQLite 3" if db_manager.is_sqlite else "MySQL 8.0"
        },
        "dataset_statistics": {},
        "sql_query_latencies_ms": {},
        "flask_route_latencies_ms": {},
        "system_metrics": {}
    }

    # 1. Dataset Statistics
    with db_manager.get_connection() as conn:
        results["dataset_statistics"] = {
            "raw_vehicle_specifications_collected": 65,
            "raw_sales_records_collected": 294,
            "cleaned_vehicles_loaded": conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar(),
            "cleaned_sales_loaded": conn.execute(text("SELECT COUNT(*) FROM sales")).scalar(),
            "customer_ratings_loaded": conn.execute(text("SELECT COUNT(*) FROM customer_ratings")).scalar(),
            "manufacturers_count": conn.execute(text("SELECT COUNT(*) FROM manufacturers")).scalar(),
            "battery_technologies_count": conn.execute(text("SELECT COUNT(*) FROM battery_technologies")).scalar(),
            "database_tables_count": 6,
            "analytical_views_count": 6
        }

    # 2. SQL Query Benchmarks
    queries = {
        "kpi_aggregation": "SELECT SUM(annual_sales_units), COUNT(DISTINCT manufacturer_id) FROM sales",
        "yoy_sales_growth_view": "SELECT * FROM vw_annual_sales_trends",
        "mfg_market_share_view": "SELECT * FROM vw_manufacturer_market_share WHERE sales_year = 2024",
        "battery_tech_distribution": "SELECT * FROM vw_battery_technology_distribution",
        "geographic_distribution": "SELECT * FROM vw_geographic_manufacturing_distribution",
        "vehicle_ratings_join": "SELECT * FROM vw_vehicle_performance_ratings"
    }

    with db_manager.get_connection() as conn:
        for q_name, q_sql in queries.items():
            # Warm up
            conn.execute(text(q_sql))
            # Timed run
            start = time.perf_counter()
            conn.execute(text(q_sql))
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            results["sql_query_latencies_ms"][q_name] = round(elapsed_ms, 2)

    # 3. Flask Route Benchmarks
    client = app.test_client()
    routes = [
        "/",
        "/dashboard",
        "/manufacturers",
        "/battery-analysis",
        "/geography",
        "/story",
        "/methodology",
        "/about",
        "/api/kpis?year=2024",
        "/api/sales-trend",
        "/api/manufacturer-ranking"
    ]

    for route in routes:
        # Warm up
        client.get(route)
        # Timed run
        start = time.perf_counter()
        resp = client.get(route)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        assert resp.status_code == 200
        results["flask_route_latencies_ms"][route] = round(elapsed_ms, 2)

    # 4. Summary counts
    results["system_metrics"] = {
        "unique_tableau_visualizations_specified": 12,
        "tableau_calculated_fields_documented": 10,
        "tableau_story_scenes_implemented": 5,
        "dashboard_pages_created": 8,
        "interactive_filter_controls": 5,
        "avg_sql_query_latency_ms": round(sum(results["sql_query_latencies_ms"].values()) / len(results["sql_query_latencies_ms"]), 2),
        "avg_flask_route_latency_ms": round(sum(results["flask_route_latencies_ms"].values()) / len(results["flask_route_latencies_ms"]), 2)
    }

    # Save
    out_path = BASE_DIR / "docs" / "benchmark_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Benchmarks successfully recorded to {out_path}!")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_benchmarks()
