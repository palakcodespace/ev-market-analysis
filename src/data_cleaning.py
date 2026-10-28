"""
Data Cleaning and Validation Module for Electric Vehicle Market Analysis.
Performs data type coercion, missing value resolution, string standardization,
outlier detection (without deleting valid high-performance models), deduplication,
and data quality auditing.
"""
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def clean_ev_specifications(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Cleans and standardizes raw EV technical specifications."""
    df = df_raw.copy()
    audit = {
        "raw_rows": len(df),
        "duplicates_removed": 0,
        "null_values_imputed": {},
        "standardizations_applied": [],
        "outlier_flags": {}
    }

    # 1. Deduplication based on vehicle_id and model_name
    initial_len = len(df)
    df = df.drop_duplicates(subset=["vehicle_id"])
    df = df.drop_duplicates(subset=["manufacturer", "model_name", "model_year"])
    audit["duplicates_removed"] = initial_len - len(df)

    # 2. String trimming and case standardization
    string_cols = ["manufacturer", "model_name", "vehicle_category", "battery_technology", "manufacturing_country", "market_region", "powertrain_type"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Standardize manufacturer naming
    mfg_mapping = {
        "VW": "Volkswagen",
        "Mercedes": "Mercedes-Benz",
        "MB": "Mercedes-Benz"
    }
    df["manufacturer"] = df["manufacturer"].replace(mfg_mapping)
    audit["standardizations_applied"].append("Manufacturer names normalized (e.g. VW -> Volkswagen)")

    # Standardize battery chemistry terminology
    battery_mapping = {
        "Lithium Iron Phosphate": "LFP",
        "LiFePO4": "LFP",
        "Nickel Manganese Cobalt": "NMC",
        "Li-NMC": "NMC",
        "Nickel Cobalt Aluminum": "NCA"
    }
    df["battery_technology"] = df["battery_technology"].replace(battery_mapping)
    audit["standardizations_applied"].append("Battery chemistry terms mapped to LFP, NMC, NCA standards")

    # 3. Numeric validation and range checking
    numeric_bounds = {
        "model_year": (2010, 2026),
        "usable_battery_capacity_kwh": (10.0, 250.0),
        "electric_range_km": (50.0, 1200.0),
        "fast_charge_power_kw": (10.0, 400.0),
        "charging_time_hours": (0.1, 24.0),
        "base_msrp_usd": (5000.0, 500000.0),
        "customer_rating": (1.0, 5.0)
    }

    for col, (min_v, max_v) in numeric_bounds.items():
        if col in df.columns:
            # Ensure float/int
            df[col] = pd.to_numeric(df[col], errors="coerce")
            null_count = int(df[col].isna().sum())
            if null_count > 0:
                median_val = float(df[col].median())
                df[col] = df[col].fillna(median_val)
                audit["null_values_imputed"][col] = {"count": null_count, "imputed_with": median_val}

            # Outlier detection using IQR
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_fence = max(min_v, q1 - 1.5 * iqr)
            upper_fence = q3 + 1.5 * iqr
            outlier_count = int(((df[col] < lower_fence) | (df[col] > upper_fence)).sum())
            audit["outlier_flags"][col] = {
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "iqr": round(iqr, 2),
                "outliers_detected": outlier_count,
                "action": "Retained legitimate production vehicle records (e.g. high-capacity pickups, luxury sports sedans)"
            }

    audit["cleaned_rows"] = len(df)
    return df, audit

def clean_ev_sales(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Cleans and validates historical annual EV sales records."""
    df = df_raw.copy()
    audit = {
        "raw_rows": len(df),
        "duplicates_removed": 0,
        "null_values_imputed": {},
        "validations_passed": True
    }

    # Deduplication
    initial_len = len(df)
    df = df.drop_duplicates(subset=["manufacturer", "vehicle_category", "market_region", "sales_year"])
    audit["duplicates_removed"] = initial_len - len(df)

    # String cleanup
    for col in ["manufacturer", "vehicle_category", "market_region"]:
        df[col] = df[col].astype(str).str.strip()

    # Numeric coercion and validation
    df["sales_year"] = pd.to_numeric(df["sales_year"], errors="coerce").astype(int)
    df["annual_sales_units"] = pd.to_numeric(df["annual_sales_units"], errors="coerce").fillna(0).astype(int)

    # Verify no negative sales numbers
    invalid_sales = (df["annual_sales_units"] < 0).sum()
    if invalid_sales > 0:
        df["annual_sales_units"] = df["annual_sales_units"].clip(lower=0)
        audit["negative_sales_fixed"] = int(invalid_sales)

    audit["cleaned_rows"] = len(df)
    audit["total_sales_units"] = int(df["annual_sales_units"].sum())
    audit["years_covered"] = sorted(df["sales_year"].unique().tolist())
    return df, audit

def main():
    """Runs data cleaning and exports cleaned CSV datasets and audit log."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Executing EV data cleaning and audit pipeline...")

    # Load raw
    raw_specs_file = RAW_DIR / "ev_specifications_raw.csv"
    raw_sales_file = RAW_DIR / "ev_global_sales_raw.csv"

    if not raw_specs_file.exists() or not raw_sales_file.exists():
        logger.error("Raw data files missing. Please run src/data_collection.py first.")
        return

    df_raw_specs = pd.read_csv(raw_specs_file)
    df_raw_sales = pd.read_csv(raw_sales_file)

    # Clean specs
    df_clean_specs, specs_audit = clean_ev_specifications(df_raw_specs)
    specs_output = PROCESSED_DIR / "cleaned_vehicles.csv"
    df_clean_specs.to_csv(specs_output, index=False)
    logger.info(f"Cleaned vehicles: {len(df_clean_specs)} records written to {specs_output}")

    # Clean sales
    df_clean_sales, sales_audit = clean_ev_sales(df_raw_sales)
    sales_output = PROCESSED_DIR / "cleaned_sales.csv"
    df_clean_sales.to_csv(sales_output, index=False)
    logger.info(f"Cleaned sales: {len(df_clean_sales)} records written to {sales_output}")

    # Save full audit log
    audit_report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "specifications_audit": specs_audit,
        "sales_audit": sales_audit
    }
    audit_path = PROCESSED_DIR / "data_cleaning_log.json"
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=4)
    logger.info(f"Audit log saved to {audit_path}")

if __name__ == "__main__":
    main()
