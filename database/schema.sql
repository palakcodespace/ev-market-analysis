-- ====================================================================
-- Electric Vehicle Market Analysis and Intelligence System
-- Database Schema: ev_market_db (MySQL 8.0+ Compatible)
-- Normalized 3NF Relational Structure with Constraints and Indexes
-- ====================================================================

CREATE DATABASE IF NOT EXISTS ev_market_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ev_market_db;

-- --------------------------------------------------------------------
-- Drop Existing Tables in Reverse Dependency Order
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS customer_ratings;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS geographies;
DROP TABLE IF EXISTS battery_technologies;
DROP TABLE IF EXISTS manufacturers;

-- --------------------------------------------------------------------
-- Table 1: manufacturers
-- Holds automotive original equipment manufacturers (OEMs)
-- --------------------------------------------------------------------
CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE,
    headquarters_country VARCHAR(100) NOT NULL,
    founded_year INT NULL,
    website VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mfg_name (manufacturer_name),
    INDEX idx_mfg_country (headquarters_country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- Table 2: battery_technologies
-- Standardized battery chemistries, energy densities, and characteristics
-- --------------------------------------------------------------------
CREATE TABLE battery_technologies (
    battery_tech_id INT AUTO_INCREMENT PRIMARY KEY,
    chemistry_code VARCHAR(20) NOT NULL UNIQUE, -- LFP, NMC, NCA
    full_name VARCHAR(100) NOT NULL,
    energy_density_wh_kg INT NOT NULL,
    thermal_stability VARCHAR(50) NOT NULL,
    cost_tier VARCHAR(30) NOT NULL,
    description TEXT NULL,
    INDEX idx_battery_chemistry (chemistry_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- Table 3: geographies
-- Market regions and representative sales/manufacturing territories
-- --------------------------------------------------------------------
CREATE TABLE geographies (
    geography_id INT AUTO_INCREMENT PRIMARY KEY,
    market_region VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    continent VARCHAR(50) NOT NULL,
    CONSTRAINT uk_region_country UNIQUE (market_region, country_name),
    INDEX idx_market_region (market_region),
    INDEX idx_country_name (country_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- Table 4: vehicles
-- Technical specifications for distinct production EV models
-- --------------------------------------------------------------------
CREATE TABLE vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    battery_tech_id INT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_year INT NOT NULL,
    vehicle_category VARCHAR(50) NOT NULL, -- Sedan, SUV, Hatchback, Crossover, Pickup, Van, Coupe
    usable_battery_capacity_kwh DECIMAL(6,2) NOT NULL,
    electric_range_km DECIMAL(6,2) NOT NULL,
    fast_charge_power_kw DECIMAL(6,2) NOT NULL,
    charging_time_hours DECIMAL(4,2) NOT NULL,
    base_msrp_usd DECIMAL(10,2) NOT NULL,
    manufacturing_country VARCHAR(100) NOT NULL,
    market_region VARCHAR(100) NOT NULL DEFAULT 'Global',
    powertrain_type VARCHAR(20) NOT NULL DEFAULT 'BEV',
    co2_emissions_g_km DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_veh_manufacturer FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers(manufacturer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_veh_battery FOREIGN KEY (battery_tech_id)
        REFERENCES battery_technologies(battery_tech_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_battery_cap CHECK (usable_battery_capacity_kwh > 0),
    CONSTRAINT chk_range CHECK (electric_range_km > 0),
    CONSTRAINT chk_msrp CHECK (base_msrp_usd >= 0),
    INDEX idx_veh_mfg (manufacturer_id),
    INDEX idx_veh_battery (battery_tech_id),
    INDEX idx_veh_category (vehicle_category),
    INDEX idx_veh_mfg_country (manufacturing_country),
    INDEX idx_veh_range (electric_range_km),
    INDEX idx_veh_price (base_msrp_usd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- Table 5: customer_ratings
-- Consumer satisfaction index and reliability benchmarks
-- --------------------------------------------------------------------
CREATE TABLE customer_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    overall_rating DECIMAL(3,2) NOT NULL,
    reliability_score DECIMAL(3,2) NOT NULL,
    driving_dynamics_score DECIMAL(3,2) NOT NULL,
    infotainment_score DECIMAL(3,2) NOT NULL,
    survey_sample_size INT DEFAULT 1500,
    benchmark_source VARCHAR(100) DEFAULT 'Consumer Satisfaction Benchmark Survey',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rating_vehicle FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_overall_rating CHECK (overall_rating BETWEEN 1.0 AND 5.0),
    INDEX idx_rating_vehicle (vehicle_id),
    INDEX idx_overall_rating (overall_rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- Table 6: sales
-- Historical annual EV sales volume records (2018 - 2024)
-- --------------------------------------------------------------------
CREATE TABLE sales (
    sales_id VARCHAR(50) PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    vehicle_category VARCHAR(50) NOT NULL,
    market_region VARCHAR(100) NOT NULL,
    sales_year INT NOT NULL,
    annual_sales_units INT NOT NULL,
    data_source VARCHAR(100) DEFAULT 'IEA EV Outlook Benchmark Compilation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_manufacturer FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers(manufacturer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_sales_units CHECK (annual_sales_units >= 0),
    INDEX idx_sales_mfg (manufacturer_id),
    INDEX idx_sales_year (sales_year),
    INDEX idx_sales_category (vehicle_category),
    INDEX idx_sales_region (market_region),
    INDEX idx_sales_combo (sales_year, manufacturer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
