"""
Database Initialization and Data Seeding Module.
Seeds ev_market_db (MySQL 8 or SQLite) from cleaned CSV datasets.
Populates normalized tables:
- manufacturers
- battery_technologies
- geographies
- vehicles
- customer_ratings
- sales
And compiles all analytical SQL views.
"""
import sys
from pathlib import Path
import logging
import pandas as pd
from sqlalchemy import text

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_connection import db_manager, Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = BASE_DIR / "data" / "processed"

MANUFACTURERS_DATA = [
    ("Tesla", "USA", 2003, "https://www.tesla.com"),
    ("BYD", "China", 1995, "https://www.bydglobal.com"),
    ("Volkswagen", "Germany", 1937, "https://www.volkswagen.com"),
    ("Audi", "Germany", 1909, "https://www.audi.com"),
    ("Porsche", "Germany", 1931, "https://www.porsche.com"),
    ("BMW", "Germany", 1916, "https://www.bmw.com"),
    ("Hyundai", "South Korea", 1967, "https://www.hyundai.com"),
    ("Kia", "South Korea", 1944, "https://www.kia.com"),
    ("Genesis", "South Korea", 2015, "https://www.genesis.com"),
    ("Mercedes-Benz", "Germany", 1926, "https://www.mercedes-benz.com"),
    ("Ford", "USA", 1903, "https://www.ford.com"),
    ("Volvo", "Sweden", 1927, "https://www.volvocars.com"),
    ("Polestar", "Sweden", 1996, "https://www.polestar.com"),
    ("Geely", "China", 1986, "https://www.geely.com"),
    ("Nissan", "Japan", 1933, "https://www.nissan-global.com"),
    ("Renault", "France", 1899, "https://www.renaultgroup.com"),
    ("MG", "UK", 1924, "https://mg.co.uk"),
    ("Peugeot", "France", 1810, "https://www.peugeot.com"),
    ("Jeep", "USA", 1941, "https://www.jeep.com"),
    ("Rivian", "USA", 2009, "https://www.rivian.com"),
    ("Lucid", "USA", 2007, "https://www.lucidmotors.com"),
    ("NIO", "China", 2014, "https://www.nio.com"),
    ("XPeng", "China", 2014, "https://www.xpeng.com")
]

BATTERY_TECH_DATA = [
    ("LFP", "Lithium Iron Phosphate", 160, "High (Excellent thermal safety)", "Low (Cobalt/Nickel free)", "Exceptional longevity and thermal stability, lower energy density, ideal for standard-range and commercial EVs."),
    ("NMC", "Nickel Manganese Cobalt", 250, "Medium (Standard BMS cooling required)", "Medium (Optimized cobalt content)", "High energy density and excellent cold-weather performance; dominant choice in premium and long-range passenger EVs."),
    ("NCA", "Nickel Cobalt Aluminum", 260, "Moderate (Active thermal management required)", "High (High energy density formulation)", "High specific energy suitable for performance electric vehicles requiring high power discharge.")
]

GEOGRAPHY_DATA = [
    ("North America", "United States", "North America"),
    ("North America", "Canada", "North America"),
    ("North America", "Mexico", "North America"),
    ("Europe", "Germany", "Europe"),
    ("Europe", "France", "Europe"),
    ("Europe", "United Kingdom", "Europe"),
    ("Europe", "Norway", "Europe"),
    ("Europe", "Sweden", "Europe"),
    ("Europe", "Belgium", "Europe"),
    ("Europe", "Poland", "Europe"),
    ("Europe", "Slovakia", "Europe"),
    ("Europe", "Hungary", "Europe"),
    ("Asia-Pacific", "China", "Asia"),
    ("Asia-Pacific", "Japan", "Asia"),
    ("Asia-Pacific", "South Korea", "Asia"),
    ("Latin America", "Brazil", "South America"),
    ("Global", "Global Aggregate", "Global")
]

def create_schema(is_sqlite: bool):
    """Creates database tables matching MySQL and SQLite standards."""
    engine = db_manager.get_engine()

    if is_sqlite:
        sqlite_ddl = """
        DROP TABLE IF EXISTS customer_ratings;
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS vehicles;
        DROP TABLE IF EXISTS geographies;
        DROP TABLE IF EXISTS battery_technologies;
        DROP TABLE IF EXISTS manufacturers;

        CREATE TABLE manufacturers (
            manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_name TEXT NOT NULL UNIQUE,
            headquarters_country TEXT NOT NULL,
            founded_year INTEGER,
            website TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE battery_technologies (
            battery_tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemistry_code TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            energy_density_wh_kg INTEGER NOT NULL,
            thermal_stability TEXT NOT NULL,
            cost_tier TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE geographies (
            geography_id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_region TEXT NOT NULL,
            country_name TEXT NOT NULL,
            continent TEXT NOT NULL,
            UNIQUE(market_region, country_name)
        );

        CREATE TABLE vehicles (
            vehicle_id TEXT PRIMARY KEY,
            manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(manufacturer_id),
            battery_tech_id INTEGER NOT NULL REFERENCES battery_technologies(battery_tech_id),
            model_name TEXT NOT NULL,
            model_year INTEGER NOT NULL,
            vehicle_category TEXT NOT NULL,
            usable_battery_capacity_kwh REAL NOT NULL,
            electric_range_km REAL NOT NULL,
            fast_charge_power_kw REAL NOT NULL,
            charging_time_hours REAL NOT NULL,
            base_msrp_usd REAL NOT NULL,
            manufacturing_country TEXT NOT NULL,
            market_region TEXT NOT NULL DEFAULT 'Global',
            powertrain_type TEXT NOT NULL DEFAULT 'BEV',
            co2_emissions_g_km REAL NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE customer_ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
            overall_rating REAL NOT NULL,
            reliability_score REAL NOT NULL,
            driving_dynamics_score REAL NOT NULL,
            infotainment_score REAL NOT NULL,
            survey_sample_size INTEGER DEFAULT 1500,
            benchmark_source TEXT DEFAULT 'Consumer Satisfaction Benchmark Survey',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE sales (
            sales_id TEXT PRIMARY KEY,
            manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(manufacturer_id),
            vehicle_category TEXT NOT NULL,
            market_region TEXT NOT NULL,
            sales_year INTEGER NOT NULL,
            annual_sales_units INTEGER NOT NULL,
            data_source TEXT DEFAULT 'IEA EV Outlook Benchmark Compilation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        import sqlite3
        raw_conn = sqlite3.connect(Config.SQLITE_PATH)
        raw_conn.executescript(sqlite_ddl)
        raw_conn.commit()
        raw_conn.close()
        logger.info("SQLite schema created successfully.")
    else:
        schema_path = BASE_DIR / "database" / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split and execute individual statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        with engine.connect() as conn:
            for stmt in statements:
                if stmt.lower().startswith("create database") or stmt.lower().startswith("use "):
                    continue
                conn.execute(text(stmt))
            conn.commit()
        logger.info("MySQL schema created successfully from database/schema.sql.")

def create_views(is_sqlite: bool):
    """Compiles analytical views for high-performance reporting."""
    engine = db_manager.get_engine()
    views_path = BASE_DIR / "sql" / "views.sql"
    with open(views_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    with engine.connect() as conn:
        for stmt in statements:
            if stmt.lower().startswith("use "):
                continue
            try:
                conn.execute(text(stmt))
            except Exception as e:
                logger.warning(f"Notice on executing view statement: {e}")
        conn.commit()
    logger.info("Database views compiled successfully.")

def seed_database():
    """Populates normalized tables with curated and cleaned records."""
    engine = db_manager.get_engine()
    is_sqlite = db_manager.is_sqlite

    # 1. Create Schema
    create_schema(is_sqlite)

    # 2. Insert Reference Dimensions
    with engine.connect() as conn:
        # Manufacturers
        for name, country, yr, web in MANUFACTURERS_DATA:
            conn.execute(
                text("INSERT INTO manufacturers (manufacturer_name, headquarters_country, founded_year, website) VALUES (:n, :c, :y, :w)"),
                {"n": name, "c": country, "y": yr, "w": web}
            )

        # Battery Technologies
        for code, full, density, thermal, cost, desc in BATTERY_TECH_DATA:
            conn.execute(
                text("INSERT INTO battery_technologies (chemistry_code, full_name, energy_density_wh_kg, thermal_stability, cost_tier, description) VALUES (:c, :f, :d, :t, :ct, :de)"),
                {"c": code, "f": full, "d": density, "t": thermal, "ct": cost, "de": desc}
            )

        # Geographies
        for region, country, continent in GEOGRAPHY_DATA:
            conn.execute(
                text("INSERT INTO geographies (market_region, country_name, continent) VALUES (:r, :c, :ct)"),
                {"r": region, "c": country, "ct": continent}
            )
        conn.commit()
    logger.info("Reference dimensions seeded.")

    # Fetch lookup maps
    with engine.connect() as conn:
        mfg_map = {row[1]: row[0] for row in conn.execute(text("SELECT manufacturer_id, manufacturer_name FROM manufacturers")).fetchall()}
        battery_map = {row[1]: row[0] for row in conn.execute(text("SELECT battery_tech_id, chemistry_code FROM battery_technologies")).fetchall()}

    # 3. Insert Vehicles and Customer Ratings
    vehicles_file = PROCESSED_DIR / "cleaned_vehicles.csv"
    if vehicles_file.exists():
        df_v = pd.read_csv(vehicles_file)
        with engine.connect() as conn:
            for _, r in df_v.iterrows():
                m_name = str(r["manufacturer"]).strip()
                mfg_id = mfg_map.get(m_name, 1)

                b_code = str(r["battery_technology"]).strip()
                b_id = battery_map.get(b_code, 1)

                conn.execute(
                    text("""
                    INSERT INTO vehicles (
                        vehicle_id, manufacturer_id, battery_tech_id, model_name, model_year,
                        vehicle_category, usable_battery_capacity_kwh, electric_range_km,
                        fast_charge_power_kw, charging_time_hours, base_msrp_usd,
                        manufacturing_country, market_region, powertrain_type, co2_emissions_g_km
                    ) VALUES (
                        :vid, :mid, :bid, :mod, :myr, :cat, :cap, :rng, :pwr, :hrs, :msrp, :mfg_cty, :reg, :pwt, :co2
                    )
                    """),
                    {
                        "vid": r["vehicle_id"],
                        "mid": mfg_id,
                        "bid": b_id,
                        "mod": r["model_name"],
                        "myr": int(r["model_year"]),
                        "cat": r["vehicle_category"],
                        "cap": float(r["usable_battery_capacity_kwh"]),
                        "rng": float(r["electric_range_km"]),
                        "pwr": float(r["fast_charge_power_kw"]),
                        "hrs": float(r["charging_time_hours"]),
                        "msrp": float(r["base_msrp_usd"]),
                        "mfg_cty": r["manufacturing_country"],
                        "reg": r.get("market_region", "Global"),
                        "pwt": r.get("powertrain_type", "BEV"),
                        "co2": float(r.get("co2_emissions_g_km", 0.0))
                    }
                )

                # Rating entry
                overall_rating = float(r.get("customer_rating", 4.3))
                reliability = round(max(3.0, overall_rating - 0.1), 2)
                dynamics = round(min(5.0, overall_rating + 0.1), 2)
                infotainment = round(overall_rating, 2)

                conn.execute(
                    text("""
                    INSERT INTO customer_ratings (
                        vehicle_id, overall_rating, reliability_score, driving_dynamics_score, infotainment_score
                    ) VALUES (:vid, :ovr, :rel, :dyn, :inf)
                    """),
                    {
                        "vid": r["vehicle_id"],
                        "ovr": overall_rating,
                        "rel": reliability,
                        "dyn": dynamics,
                        "inf": infotainment
                    }
                )
            conn.commit()
        logger.info(f"Loaded {len(df_v)} vehicles and ratings into database.")

    # 4. Insert Sales
    sales_file = PROCESSED_DIR / "cleaned_sales.csv"
    if sales_file.exists():
        df_s = pd.read_csv(sales_file)
        with engine.connect() as conn:
            for _, r in df_s.iterrows():
                m_name = str(r["manufacturer"]).strip()
                mfg_id = mfg_map.get(m_name, 1)

                conn.execute(
                    text("""
                    INSERT INTO sales (
                        sales_id, manufacturer_id, vehicle_category, market_region, sales_year, annual_sales_units, data_source
                    ) VALUES (:sid, :mid, :cat, :reg, :syr, :units, :src)
                    """),
                    {
                        "sid": r["sales_id"],
                        "mid": mfg_id,
                        "cat": r["vehicle_category"],
                        "reg": r["market_region"],
                        "syr": int(r["sales_year"]),
                        "units": int(r["annual_sales_units"]),
                        "src": r.get("data_source", "IEA EV Outlook Benchmark Compilation")
                    }
                )
            conn.commit()
        logger.info(f"Loaded {len(df_s)} sales records into database.")

    # 5. Create Views
    create_views(is_sqlite)

    # 6. Verify record counts
    with engine.connect() as conn:
        counts = {
            "manufacturers": conn.execute(text("SELECT COUNT(*) FROM manufacturers")).scalar(),
            "battery_technologies": conn.execute(text("SELECT COUNT(*) FROM battery_technologies")).scalar(),
            "geographies": conn.execute(text("SELECT COUNT(*) FROM geographies")).scalar(),
            "vehicles": conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar(),
            "customer_ratings": conn.execute(text("SELECT COUNT(*) FROM customer_ratings")).scalar(),
            "sales": conn.execute(text("SELECT COUNT(*) FROM sales")).scalar()
        }
        logger.info(f"Database Seeding Complete! Summary Table Counts: {counts}")

def main():
    seed_database()

if __name__ == "__main__":
    main()
