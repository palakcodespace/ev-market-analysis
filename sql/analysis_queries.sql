-- ====================================================================
-- Electric Vehicle Market Analysis and Intelligence System
-- Comprehensive Analytical SQL Queries (15 Required Operations)
-- Target: ev_market_db (MySQL 8.0+ and SQLite 3.35+ Compatible)
-- ====================================================================

USE ev_market_db;

-- ====================================================================
-- Operation 1: SELECT, WHERE, ORDER BY, and DISTINCT
-- Business Question: Retrieve all distinct EV manufacturers producing vehicles
-- with an electric range exceeding 500 km, ordered from highest range to lowest.
-- ====================================================================
SELECT DISTINCT
    m.manufacturer_name,
    m.headquarters_country,
    v.model_name,
    v.electric_range_km,
    v.base_msrp_usd
FROM vehicles v
INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
WHERE v.electric_range_km >= 500
ORDER BY v.electric_range_km DESC, v.base_msrp_usd ASC;

-- ====================================================================
-- Operation 2: GROUP BY and Aggregate Functions (SUM, AVG, MIN, MAX, COUNT)
-- Business Question: What are the minimum, maximum, and average battery capacities,
-- average ranges, and model counts grouped across vehicle categories?
-- ====================================================================
SELECT
    v.vehicle_category,
    COUNT(v.vehicle_id) AS total_models,
    ROUND(MIN(v.usable_battery_capacity_kwh), 1) AS min_battery_kwh,
    ROUND(MAX(v.usable_battery_capacity_kwh), 1) AS max_battery_kwh,
    ROUND(AVG(v.usable_battery_capacity_kwh), 2) AS avg_battery_kwh,
    ROUND(AVG(v.electric_range_km), 2) AS avg_range_km,
    ROUND(AVG(v.base_msrp_usd), 0) AS avg_price_usd
FROM vehicles v
GROUP BY v.vehicle_category
ORDER BY avg_range_km DESC;

-- ====================================================================
-- Operation 3: INNER JOIN and LEFT JOIN
-- Business Question: Combine vehicle specifications with manufacturer details
-- (INNER JOIN) and consumer satisfaction ratings (LEFT JOIN) to evaluate
-- models that have survey scores versus those awaiting survey responses.
-- ====================================================================
SELECT
    v.vehicle_id,
    m.manufacturer_name,
    v.model_name,
    v.vehicle_category,
    v.electric_range_km,
    COALESCE(cr.overall_rating, 0.00) AS overall_customer_rating,
    COALESCE(cr.reliability_score, 0.00) AS reliability_score,
    CASE 
        WHEN cr.overall_rating IS NOT NULL THEN 'Survey Verified'
        ELSE 'Pending Benchmark'
    END AS rating_verification_status
FROM vehicles v
INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
LEFT JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id
ORDER BY overall_customer_rating DESC, v.electric_range_km DESC;

-- ====================================================================
-- Operation 4: Subqueries and Common Table Expressions (CTEs)
-- Business Question: Identify vehicles that deliver higher than average driving range
-- within their specific vehicle category and have an above-average customer rating.
-- ====================================================================
WITH category_benchmarks AS (
    SELECT
        vehicle_category,
        AVG(electric_range_km) AS cat_avg_range,
        AVG(usable_battery_capacity_kwh) AS cat_avg_battery
    FROM vehicles
    GROUP BY vehicle_category
),
rated_vehicles AS (
    SELECT
        v.vehicle_id,
        v.model_name,
        v.manufacturer_id,
        v.vehicle_category,
        v.electric_range_km,
        v.usable_battery_capacity_kwh,
        cr.overall_rating
    FROM vehicles v
    LEFT JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id
)
SELECT
    rv.vehicle_id,
    m.manufacturer_name,
    rv.model_name,
    rv.vehicle_category,
    rv.electric_range_km,
    ROUND(cb.cat_avg_range, 1) AS category_average_range_km,
    ROUND(rv.electric_range_km - cb.cat_avg_range, 1) AS range_premium_km,
    rv.overall_rating
FROM rated_vehicles rv
INNER JOIN manufacturers m ON rv.manufacturer_id = m.manufacturer_id
INNER JOIN category_benchmarks cb ON rv.vehicle_category = cb.vehicle_category
WHERE rv.electric_range_km > cb.cat_avg_range
ORDER BY range_premium_km DESC;

-- ====================================================================
-- Operation 5: CASE Statements for Categorization (Range and Battery Bins)
-- Business Question: Categorize all vehicles into standard marketing driving-range
-- buckets and battery capacity tiers, and evaluate average pricing per segment.
-- ====================================================================
SELECT
    v.model_name,
    m.manufacturer_name,
    v.electric_range_km,
    CASE
        WHEN v.electric_range_km < 350 THEN '1. Standard City (<350 km)'
        WHEN v.electric_range_km BETWEEN 350 AND 499 THEN '2. Mid-Range (350-499 km)'
        WHEN v.electric_range_km BETWEEN 500 AND 599 THEN '3. Long-Range (500-599 km)'
        ELSE '4. Ultra Long-Range (600+ km)'
    END AS driving_range_segment,
    v.usable_battery_capacity_kwh,
    CASE
        WHEN v.usable_battery_capacity_kwh < 60.0 THEN 'Compact (<60 kWh)'
        WHEN v.usable_battery_capacity_kwh BETWEEN 60.0 AND 85.0 THEN 'Standard (60-85 kWh)'
        ELSE 'Extended Pack (>85 kWh)'
    END AS battery_pack_classification,
    v.base_msrp_usd
FROM vehicles v
INNER JOIN manufacturers m ON v.manufacturer_id = m.manufacturer_id
ORDER BY v.electric_range_km DESC;

-- ====================================================================
-- Operation 6: Window Functions (RANK, DENSE_RANK, and Market Share Partitioning)
-- Business Question: Compute manufacturer rankings by sales volume within each
-- sales year, along with percentage contribution to total annual volume.
-- ====================================================================
WITH yearly_mfg_sales AS (
    SELECT
        s.sales_year,
        m.manufacturer_name,
        SUM(s.annual_sales_units) AS total_units
    FROM sales s
    INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
    GROUP BY s.sales_year, m.manufacturer_name
)
SELECT
    sales_year,
    manufacturer_name,
    total_units,
    DENSE_RANK() OVER (PARTITION BY sales_year ORDER BY total_units DESC) AS sales_rank,
    ROUND(
        (total_units * 100.0) / SUM(total_units) OVER (PARTITION BY sales_year),
        2
    ) AS yearly_market_share_pct
FROM yearly_mfg_sales
ORDER BY sales_year DESC, sales_rank ASC;

-- ====================================================================
-- Operation 7: Year-Wise Sales Analysis & YoY Growth
-- Business Question: What is the total global EV sales volume for each year (2018-2024),
-- and what was the year-over-year percentage growth rate?
-- ====================================================================
WITH yearly_totals AS (
    SELECT
        sales_year,
        SUM(annual_sales_units) AS total_sales
    FROM sales
    GROUP BY sales_year
)
SELECT
    curr.sales_year,
    curr.total_sales AS annual_sales_units,
    LAG(curr.total_sales, 1) OVER (ORDER BY curr.sales_year) AS prior_year_sales,
    ROUND(
        ((curr.total_sales - LAG(curr.total_sales, 1) OVER (ORDER BY curr.sales_year)) * 100.0) /
        NULLIF(LAG(curr.total_sales, 1) OVER (ORDER BY curr.sales_year), 0),
        2
    ) AS yoy_sales_growth_pct
FROM yearly_totals curr
ORDER BY curr.sales_year ASC;

-- ====================================================================
-- Operation 8: Manufacturer Ranking and Performance
-- Business Question: Determine cumulative sales and market share across all years
-- for every manufacturer, sorted by total volume.
-- ====================================================================
SELECT
    m.manufacturer_name,
    m.headquarters_country,
    SUM(s.annual_sales_units) AS cumulative_sales_units,
    ROUND(
        (SUM(s.annual_sales_units) * 100.0) / (SELECT SUM(annual_sales_units) FROM sales),
        2
    ) AS overall_market_share_pct,
    COUNT(DISTINCT s.sales_year) AS active_years_count
FROM manufacturers m
INNER JOIN sales s ON m.manufacturer_id = s.manufacturer_id
GROUP BY m.manufacturer_id, m.manufacturer_name, m.headquarters_country
ORDER BY cumulative_sales_units DESC;

-- ====================================================================
-- Operation 9: Vehicle-Category Comparison
-- Business Question: Compare total volume, average range, and price across categories.
-- ====================================================================
SELECT
    s.vehicle_category,
    SUM(s.annual_sales_units) AS total_units_sold,
    ROUND((SUM(s.annual_sales_units) * 100.0) / (SELECT SUM(annual_sales_units) FROM sales), 2) AS category_share_pct,
    ROUND(AVG(v.electric_range_km), 1) AS category_avg_range_km,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS category_avg_battery_kwh,
    ROUND(AVG(v.base_msrp_usd), 0) AS category_avg_price_usd
FROM sales s
LEFT JOIN vehicles v ON s.vehicle_category = v.vehicle_category
GROUP BY s.vehicle_category
ORDER BY total_units_sold DESC;

-- ====================================================================
-- Operation 10: Battery Technology Distribution
-- Business Question: How are vehicle models distributed across battery chemistries,
-- and what are the average technical attributes of each chemistry?
-- ====================================================================
SELECT
    bt.chemistry_code,
    bt.full_name AS battery_technology_name,
    bt.cost_tier,
    COUNT(v.vehicle_id) AS vehicle_count,
    ROUND((COUNT(v.vehicle_id) * 100.0) / (SELECT COUNT(*) FROM vehicles), 2) AS vehicle_model_share_pct,
    ROUND(AVG(v.usable_battery_capacity_kwh), 2) AS avg_capacity_kwh,
    ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
    ROUND(AVG(v.fast_charge_power_kw), 1) AS avg_charging_power_kw
FROM battery_technologies bt
LEFT JOIN vehicles v ON bt.battery_tech_id = v.battery_tech_id
GROUP BY bt.battery_tech_id, bt.chemistry_code, bt.full_name, bt.cost_tier
ORDER BY vehicle_count DESC;

-- ====================================================================
-- Operation 11: Manufacturing-Country Analysis
-- Business Question: Which countries manufacture the highest number of EV models,
-- and what is the average driving range and price of vehicles built in each country?
-- ====================================================================
SELECT
    v.manufacturing_country,
    COUNT(DISTINCT v.manufacturer_id) AS total_manufacturers,
    COUNT(v.vehicle_id) AS models_produced_count,
    ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_battery_kwh,
    ROUND(AVG(v.base_msrp_usd), 0) AS avg_msrp_usd
FROM vehicles v
GROUP BY v.manufacturing_country
ORDER BY models_produced_count DESC;

-- ====================================================================
-- Operation 12: Driving-Range and Battery-Capacity Relationship
-- Business Question: Calculate range-to-capacity efficiency (km per kWh)
-- and group by battery chemistry and category to analyze powertrain efficiency.
-- ====================================================================
SELECT
    bt.chemistry_code,
    v.vehicle_category,
    COUNT(v.vehicle_id) AS sample_size,
    ROUND(AVG(v.usable_battery_capacity_kwh), 1) AS avg_capacity_kwh,
    ROUND(AVG(v.electric_range_km), 1) AS avg_range_km,
    ROUND(AVG(v.electric_range_km / v.usable_battery_capacity_kwh), 2) AS range_per_kwh_efficiency
FROM vehicles v
INNER JOIN battery_technologies bt ON v.battery_tech_id = bt.battery_tech_id
GROUP BY bt.chemistry_code, v.vehicle_category
ORDER BY range_per_kwh_efficiency DESC;

-- ====================================================================
-- Operation 13: Customer Rating Analysis
-- Business Question: Evaluate customer satisfaction benchmarks by manufacturer,
-- including overall rating, reliability, and driving dynamics.
-- ====================================================================
SELECT
    m.manufacturer_name,
    COUNT(cr.rating_id) AS rated_models_count,
    ROUND(AVG(cr.overall_rating), 2) AS avg_overall_rating,
    ROUND(AVG(cr.reliability_score), 2) AS avg_reliability_score,
    ROUND(AVG(cr.driving_dynamics_score), 2) AS avg_dynamics_score,
    ROUND(AVG(cr.infotainment_score), 2) AS avg_infotainment_score
FROM manufacturers m
INNER JOIN vehicles v ON m.manufacturer_id = v.manufacturer_id
INNER JOIN customer_ratings cr ON v.vehicle_id = cr.vehicle_id
GROUP BY m.manufacturer_id, m.manufacturer_name
ORDER BY avg_overall_rating DESC;

-- ====================================================================
-- Operation 14: Market Share with Explicitly Defined Denominators
-- Business Question: Calculate 2024 regional market share by manufacturer,
-- showing explicit numerator (mfg regional sales) and denominator (regional total).
-- ====================================================================
WITH regional_totals_2024 AS (
    SELECT
        market_region,
        SUM(annual_sales_units) AS region_total_units
    FROM sales
    WHERE sales_year = 2024
    GROUP BY market_region
),
mfg_regional_2024 AS (
    SELECT
        s.market_region,
        m.manufacturer_name,
        SUM(s.annual_sales_units) AS mfg_region_units
    FROM sales s
    INNER JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
    WHERE s.sales_year = 2024
    GROUP BY s.market_region, m.manufacturer_name
)
SELECT
    mr.market_region,
    mr.manufacturer_name,
    mr.mfg_region_units AS numerator_mfg_sales,
    rt.region_total_units AS denominator_region_total,
    ROUND((mr.mfg_region_units * 100.0) / rt.region_total_units, 2) AS market_share_percentage
FROM mfg_regional_2024 mr
INNER JOIN regional_totals_2024 rt ON mr.market_region = rt.market_region
ORDER BY mr.market_region, market_share_percentage DESC;

-- ====================================================================
-- Operation 15: Missing-Value and Duplicate-Record Checks
-- Business Question: Perform database integrity audit checking for null foreign keys,
-- missing ranges/prices, duplicate vehicle IDs, or unlinked sales records.
-- ====================================================================
SELECT
    'Missing Battery Tech FK' AS integrity_check,
    COUNT(*) AS issue_count
FROM vehicles
WHERE battery_tech_id IS NULL
UNION ALL
SELECT
    'Vehicles with Zero or Negative Range',
    COUNT(*)
FROM vehicles
WHERE electric_range_km <= 0
UNION ALL
SELECT
    'Vehicles with Zero or Negative Battery Capacity',
    COUNT(*)
FROM vehicles
WHERE usable_battery_capacity_kwh <= 0
UNION ALL
SELECT
    'Duplicate Vehicle IDs in Specifications',
    COUNT(*) - COUNT(DISTINCT vehicle_id)
FROM vehicles
UNION ALL
SELECT
    'Sales Records with Non-Existent Manufacturer',
    COUNT(*)
FROM sales s
LEFT JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
WHERE m.manufacturer_id IS NULL;
