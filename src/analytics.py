"""
Analytics Service Module.
Executes parameterized SQL queries against ev_market_db to provide
data payloads for Flask routes, Plotly visualizations, and API endpoints.
"""
import logging
from sqlalchemy import text
from database.db_connection import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class EVAnalyticsService:
    """Encapsulates business intelligence queries and metric calculations."""

    @staticmethod
    def get_filter_options() -> dict:
        """Retrieves distinct values for frontend filter dropdowns."""
        with db_manager.get_connection() as conn:
            years = [r[0] for r in conn.execute(text("SELECT DISTINCT sales_year FROM sales ORDER BY sales_year DESC")).fetchall()]
            manufacturers = [r[0] for r in conn.execute(text("SELECT DISTINCT manufacturer_name FROM manufacturers ORDER BY manufacturer_name ASC")).fetchall()]
            categories = [r[0] for r in conn.execute(text("SELECT DISTINCT vehicle_category FROM vehicles ORDER BY vehicle_category ASC")).fetchall()]
            battery_techs = [r[0] for r in conn.execute(text("SELECT DISTINCT chemistry_code FROM battery_technologies ORDER BY chemistry_code ASC")).fetchall()]
            countries = [r[0] for r in conn.execute(text("SELECT DISTINCT manufacturing_country FROM vehicles ORDER BY manufacturing_country ASC")).fetchall()]
            regions = [r[0] for r in conn.execute(text("SELECT DISTINCT market_region FROM sales ORDER BY market_region ASC")).fetchall()]

        return {
            "years": years,
            "manufacturers": manufacturers,
            "categories": categories,
            "battery_techs": battery_techs,
            "countries": countries,
            "regions": regions
        }

    @staticmethod
    def get_executive_kpis(year: int = None, manufacturer: str = None, category: str = None) -> dict:
        """Computes top-level KPI summary cards from SQL."""
        # 1. Sales metrics
        sales_where = []
        sales_params = {}
        if year:
            sales_where.append("s.sales_year = :year")
            sales_params["year"] = int(year)
        if manufacturer and manufacturer != "All":
            sales_where.append("m.manufacturer_name = :mfg")
            sales_params["mfg"] = manufacturer
        if category and category != "All":
            sales_where.append("s.vehicle_category = :cat")
            sales_params["cat"] = category

        where_clause_sales = ("WHERE " + " AND ".join(sales_where)) if sales_where else ""

        sql_sales = f"""
        SELECT
            COALESCE(SUM(s.annual_sales_units), 0) AS total_sales,
            COUNT(DISTINCT s.manufacturer_id) AS active_mfgs
        FROM sales s
        INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
        {where_clause_sales}
        """

        # 2. Vehicle specifications metrics
        veh_where = []
        veh_params = {}
        if manufacturer and manufacturer != "All":
            veh_where.append("m.manufacturer_name = :mfg")
            veh_params["mfg"] = manufacturer
        if category and category != "All":
            veh_where.append("v.vehicle_category = :cat")
            veh_params["cat"] = category

        where_clause_veh = ("WHERE " + " AND ".join(veh_where)) if veh_where else ""

        sql_veh = f"""
        SELECT
            COUNT(v.vehicle_id) AS model_count,
            COALESCE(ROUND(AVG(v.electric_range_km), 1), 0.0) AS avg_range_km,
            COALESCE(ROUND(AVG(v.usable_battery_capacity_kwh), 1), 0.0) AS avg_battery_kwh,
            COALESCE(ROUND(AVG(v.base_msrp_usd), 0), 0) AS avg_price_usd,
            COALESCE(ROUND(AVG(cr.overall_rating), 2), 0.0) AS avg_rating
        FROM vehicles v
        INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
        LEFT JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id
        {where_clause_veh}
        """

        with db_manager.get_connection() as conn:
            sales_row = conn.execute(text(sql_sales), sales_params).mappings().fetchone()
            veh_row = conn.execute(text(sql_veh), veh_params).mappings().fetchone()

        return {
            "total_sales_units": int(sales_row["total_sales"]) if sales_row else 0,
            "active_manufacturers": int(sales_row["active_mfgs"]) if sales_row else 0,
            "vehicle_models_analyzed": int(veh_row["model_count"]) if veh_row else 0,
            "avg_electric_range_km": float(veh_row["avg_range_km"]) if veh_row else 0.0,
            "avg_battery_capacity_kwh": float(veh_row["avg_battery_kwh"]) if veh_row else 0.0,
            "avg_base_msrp_usd": float(veh_row["avg_price_usd"]) if veh_row else 0.0,
            "avg_customer_rating": float(veh_row["avg_rating"]) if veh_row else 0.0
        }

    @staticmethod
    def get_annual_sales_trend(manufacturer: str = None, category: str = None) -> list:
        """Returns annual sales and YoY growth for charting."""
        conditions = []
        params = {}
        if manufacturer and manufacturer != "All":
            conditions.append("m.manufacturer_name = :mfg")
            params["mfg"] = manufacturer
        if category and category != "All":
            conditions.append("s.vehicle_category = :cat")
            params["cat"] = category

        where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        sql = f"""
        WITH yearly_sales AS (
            SELECT
                s.sales_year,
                SUM(s.annual_sales_units) AS annual_units
            FROM sales s
            INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
            {where_clause}
            GROUP BY s.sales_year
        )
        SELECT
            curr.sales_year,
            curr.annual_units,
            prev.annual_units AS prior_units,
            ROUND(
                CASE
                    WHEN prev.annual_units IS NULL OR prev.annual_units = 0 THEN 0.0
                    ELSE ((curr.annual_units - prev.annual_units) * 100.0) / prev.annual_units
                END, 2
            ) AS yoy_growth_pct
        FROM yearly_sales curr
        LEFT JOIN yearly_sales prev ON curr.sales_year = prev.sales_year + 1
        ORDER BY curr.sales_year ASC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql), params).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_manufacturer_rankings(year: int = 2024, limit: int = 10) -> list:
        """Returns top manufacturers by volume and market share for a given year."""
        sql = """
        WITH yearly_market AS (
            SELECT SUM(annual_sales_units) AS market_total
            FROM sales
            WHERE sales_year = :year
        )
        SELECT
            m.manufacturer_name,
            m.headquarters_country,
            SUM(s.annual_sales_units) AS total_units,
            ROUND((SUM(s.annual_sales_units) * 100.0) / ym.market_total, 2) AS market_share_pct
        FROM sales s
        INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
        CROSS JOIN yearly_market ym
        WHERE s.sales_year = :year
        GROUP BY m.manufacturer_name, m.headquarters_country, ym.market_total
        ORDER BY total_units DESC
        LIMIT :limit
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql), {"year": int(year), "limit": int(limit)}).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_category_sales_breakdown(year: int = 2024) -> list:
        """Returns vehicle category share of sales for a given year."""
        sql = """
        WITH cat_market AS (
            SELECT SUM(annual_sales_units) AS total_units
            FROM sales
            WHERE sales_year = :year
        )
        SELECT
            s.vehicle_category,
            SUM(s.annual_sales_units) AS category_units,
            ROUND((SUM(s.annual_sales_units) * 100.0) / cm.total_units, 2) AS share_pct
        FROM sales s
        CROSS JOIN cat_market cm
        WHERE s.sales_year = :year
        GROUP BY s.vehicle_category, cm.total_units
        ORDER BY category_units DESC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql), {"year": int(year)}).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_battery_tech_distribution() -> list:
        """Returns vehicle model count and technical attributes by battery chemistry."""
        sql = """
        SELECT
            bt.chemistry_code,
            bt.full_name,
            bt.energy_density_wh_kg,
            bt.thermal_stability,
            bt.cost_tier,
            COUNT(v.vehicle_id) AS model_count,
            ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_kwh,
            ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
            ROUND(AVG(v.fast_charge_power_kw), 1) AS avg_charging_power_kw
        FROM battery_technologies bt
        LEFT JOIN vehicles v ON bt.battery_tech_id = v.battery_tech_id
        GROUP BY bt.battery_tech_id, bt.chemistry_code, bt.full_name, bt.energy_density_wh_kg, bt.thermal_stability, bt.cost_tier
        ORDER BY model_count DESC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql)).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_battery_vs_range_scatter() -> list:
        """Returns vehicle data points for battery capacity vs range scatter plot."""
        sql = """
        SELECT
            v.vehicle_id,
            m.manufacturer_name,
            v.model_name,
            v.vehicle_category,
            bt.chemistry_code AS battery_chemistry,
            v.usable_battery_capacity_kwh,
            v.electric_range_km,
            v.base_msrp_usd,
            ROUND(v.base_msrp_usd / v.electric_range_km, 2) AS price_to_range_ratio
        FROM vehicles v
        INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
        INNER JOIN battery_technologies bt ON v.battery_tech_id = bt.battery_tech_id
        ORDER BY v.usable_battery_capacity_kwh ASC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql)).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_manufacturing_country_distribution() -> list:
        """Returns vehicle models and specifications grouped by manufacturing country."""
        sql = """
        SELECT
            v.manufacturing_country,
            COUNT(v.vehicle_id) AS model_count,
            COUNT(DISTINCT v.manufacturer_id) AS manufacturer_count,
            ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
            ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_kwh,
            ROUND(AVG(v.base_msrp_usd), 0) AS avg_price_usd
        FROM vehicles v
        GROUP BY v.manufacturing_country
        ORDER BY model_count DESC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql)).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_customer_satisfaction_summary() -> list:
        """Returns customer rating benchmarks grouped by manufacturer."""
        sql = """
        SELECT
            m.manufacturer_name,
            m.headquarters_country,
            COUNT(cr.rating_id) AS rated_models,
            ROUND(AVG(cr.overall_rating), 2) AS avg_overall_rating,
            ROUND(AVG(cr.reliability_score), 2) AS avg_reliability,
            ROUND(AVG(cr.driving_dynamics_score), 2) AS avg_dynamics,
            ROUND(AVG(cr.infotainment_score), 2) AS avg_infotainment
        FROM customer_ratings cr
        INNER JOIN vehicles v ON cr.vehicle_id = v.vehicle_id
        INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
        GROUP BY m.manufacturer_id, m.manufacturer_name, m.headquarters_country
        ORDER BY avg_overall_rating DESC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql)).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_all_vehicles(category: str = None, manufacturer: str = None, min_range: float = None) -> list:
        """Retrieves vehicle specifications inventory with optional filters."""
        conditions = []
        params = {}
        if category and category != "All":
            conditions.append("v.vehicle_category = :cat")
            params["cat"] = category
        if manufacturer and manufacturer != "All":
            conditions.append("m.manufacturer_name = :mfg")
            params["mfg"] = manufacturer
        if min_range:
            conditions.append("v.electric_range_km >= :min_r")
            params["min_r"] = float(min_range)

        where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        sql = f"""
        SELECT
            v.vehicle_id,
            m.manufacturer_name,
            v.model_name,
            v.model_year,
            v.vehicle_category,
            bt.chemistry_code AS battery_chemistry,
            v.usable_battery_capacity_kwh,
            v.electric_range_km,
            v.fast_charge_power_kw,
            v.charging_time_hours,
            v.base_msrp_usd,
            ROUND(v.base_msrp_usd / v.electric_range_km, 2) AS price_to_range_ratio,
            v.manufacturing_country,
            cr.overall_rating
        FROM vehicles v
        INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
        INNER JOIN battery_technologies bt ON v.battery_tech_id = bt.battery_tech_id
        LEFT JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id
        {where_clause}
        ORDER BY v.electric_range_km DESC
        """
        with db_manager.get_connection() as conn:
            rows = conn.execute(text(sql), params).mappings().fetchall()
            return [dict(r) for r in rows]
