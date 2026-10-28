-- ====================================================================
-- Electric Vehicle Market Analysis and Intelligence System
-- Dashboard-Ready SQL Views
-- Provides high-performance, pre-computed analytical views for Flask and Tableau
-- ====================================================================

USE ev_market_db;

-- --------------------------------------------------------------------
-- View 1: vw_annual_sales_trends
-- Aggregates global sales by year with YoY growth calculations
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_annual_sales_trends;
CREATE VIEW vw_annual_sales_trends AS
WITH annual_totals AS (
    SELECT
        sales_year,
        SUM(annual_sales_units) AS total_sales_units,
        COUNT(DISTINCT manufacturer_id) AS active_manufacturers_count
    FROM sales
    GROUP BY sales_year
)
SELECT
    curr.sales_year,
    curr.total_sales_units,
    curr.active_manufacturers_count,
    prev.total_sales_units AS prior_year_sales_units,
    ROUND(
        CASE
            WHEN prev.total_sales_units IS NULL OR prev.total_sales_units = 0 THEN 0.00
            ELSE ((curr.total_sales_units - prev.total_sales_units) * 100.0) / prev.total_sales_units
        END,
        2
    ) AS yoy_growth_percentage
FROM annual_totals curr
LEFT JOIN annual_totals prev ON curr.sales_year = prev.sales_year + 1;

-- --------------------------------------------------------------------
-- View 2: vw_manufacturer_market_share
-- Ranks manufacturers by annual sales and calculates true market share (%)
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_manufacturer_market_share;
CREATE VIEW vw_manufacturer_market_share AS
WITH mfg_sales AS (
    SELECT
        s.sales_year,
        m.manufacturer_name,
        m.headquarters_country,
        SUM(s.annual_sales_units) AS annual_sales_units
    FROM sales s
    INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
    GROUP BY s.sales_year, m.manufacturer_name, m.headquarters_country
),
market_totals AS (
    SELECT
        sales_year,
        SUM(annual_sales_units) AS total_market_units
    FROM sales
    GROUP BY sales_year
)
SELECT
    ms.sales_year,
    ms.manufacturer_name,
    ms.headquarters_country,
    ms.annual_sales_units,
    mt.total_market_units,
    ROUND((ms.annual_sales_units * 100.0) / mt.total_market_units, 2) AS market_share_percentage,
    DENSE_RANK() OVER (PARTITION BY ms.sales_year ORDER BY ms.annual_sales_units DESC) AS annual_rank
FROM mfg_sales ms
INNER JOIN market_totals mt ON ms.sales_year = mt.sales_year;

-- --------------------------------------------------------------------
-- View 3: vw_category_performance
-- Analyzes sales and vehicle attributes across categories (Sedan, SUV, etc.)
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_category_performance;
CREATE VIEW vw_category_performance AS
SELECT
    s.vehicle_category,
    s.sales_year,
    SUM(s.annual_sales_units) AS total_sales_units,
    ROUND(AVG(v.electric_range_km), 1) AS avg_driving_range_km,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_capacity_kwh,
    ROUND(AVG(v.base_msrp_usd), 0) AS avg_msrp_usd,
    COUNT(DISTINCT v.vehicle_id) AS available_models_count
FROM sales s
LEFT JOIN vehicles v ON s.vehicle_category = v.vehicle_category
GROUP BY s.vehicle_category, s.sales_year;

-- --------------------------------------------------------------------
-- View 4: vw_battery_technology_distribution
-- Summarizes adoption, range, and capacity by battery chemistry (LFP, NMC, NCA)
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_battery_technology_distribution;
CREATE VIEW vw_battery_technology_distribution AS
SELECT
    bt.chemistry_code,
    bt.full_name AS battery_full_name,
    bt.thermal_stability,
    bt.cost_tier,
    COUNT(v.vehicle_id) AS total_vehicle_models,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_capacity_kwh,
    ROUND(MIN(v.usable_battery_capacity_kwh), 1) AS min_battery_capacity_kwh,
    ROUND(MAX(v.usable_battery_capacity_kwh), 1) AS max_battery_capacity_kwh,
    ROUND(AVG(v.electric_range_km), 1) AS avg_driving_range_km,
    ROUND(AVG(v.fast_charge_power_kw), 1) AS avg_fast_charge_power_kw,
    ROUND(AVG(v.base_msrp_usd), 0) AS avg_msrp_usd
FROM battery_technologies bt
LEFT JOIN vehicles v ON bt.battery_tech_id = v.battery_tech_id
GROUP BY bt.battery_tech_id, bt.chemistry_code, bt.full_name, bt.thermal_stability, bt.cost_tier;

-- --------------------------------------------------------------------
-- View 5: vw_geographic_manufacturing_distribution
-- Details vehicle assembly counts and characteristics by country
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_geographic_manufacturing_distribution;
CREATE VIEW vw_geographic_manufacturing_distribution AS
SELECT
    v.manufacturing_country,
    COUNT(DISTINCT v.manufacturer_id) AS manufacturers_count,
    COUNT(v.vehicle_id) AS vehicle_models_produced,
    ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_kwh,
    ROUND(AVG(v.base_msrp_usd), 0) AS avg_msrp_usd
FROM vehicles v
GROUP BY v.manufacturing_country;

-- --------------------------------------------------------------------
-- View 6: vw_vehicle_performance_ratings
-- Denormalized view joining vehicles, manufacturers, battery specs, and ratings
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS vw_vehicle_performance_ratings;
CREATE VIEW vw_vehicle_performance_ratings AS
SELECT
    v.vehicle_id,
    m.manufacturer_name,
    m.headquarters_country,
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
    v.powertrain_type,
    cr.overall_rating,
    cr.reliability_score,
    cr.driving_dynamics_score,
    cr.infotainment_score,
    CASE
        WHEN v.electric_range_km < 350 THEN 'Standard City (<350 km)'
        WHEN v.electric_range_km BETWEEN 350 AND 499 THEN 'Mid-Range (350-499 km)'
        WHEN v.electric_range_km BETWEEN 500 AND 599 THEN 'Long-Range (500-599 km)'
        ELSE 'Ultra Long-Range (600+ km)'
    END AS range_classification,
    CASE
        WHEN v.base_msrp_usd < 35000 THEN 'Budget EV (<$35k)'
        WHEN v.base_msrp_usd BETWEEN 35000 AND 65000 THEN 'Mass Market ($35k-$65k)'
        ELSE 'Luxury EV (>$65k)'
    END AS price_tier
FROM vehicles v
INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
INNER JOIN battery_technologies bt ON v.battery_tech_id = bt.battery_tech_id
LEFT JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id;
