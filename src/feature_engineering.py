"""
Feature Engineering and Tableau Dataset Preparation Module.
Computes domain metrics:
- Price-to-range ratio ($/km)
- Energy consumption efficiency (kWh/100km)
- Charging speed index (km range added per min)
- Range, battery, and price categorization bins
- Year-over-year sales growth (%)
- Annual manufacturer market share (%)
- Unified Tableau-ready analytical extract
"""
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def engineer_vehicle_features(df_vehicles: pd.DataFrame) -> pd.DataFrame:
    """Calculates engineering and economic metrics for vehicle models."""
    df = df_vehicles.copy()

    # 1. Price-to-range ratio ($ / km)
    # Lower is better value for consumers
    df["price_to_range_ratio"] = np.where(
        df["electric_range_km"] > 0,
        (df["base_msrp_usd"] / df["electric_range_km"]).round(2),
        np.nan
    )

    # 2. Energy efficiency (kWh per 100 km)
    # Lower is more energy-efficient
    df["efficiency_kwh_per_100km"] = np.where(
        df["electric_range_km"] > 0,
        ((df["usable_battery_capacity_kwh"] / df["electric_range_km"]) * 100).round(2),
        np.nan
    )

    # 3. Charging rate metric: range added per minute during 10-80% fast charging
    # 70% of total range divided by fast charging time in minutes
    df["fast_charge_km_per_min"] = np.where(
        df["charging_time_hours"] > 0,
        ((df["electric_range_km"] * 0.70) / (df["charging_time_hours"] * 60)).round(2),
        np.nan
    )

    # 4. Driving Range Bins
    range_conditions = [
        (df["electric_range_km"] < 350),
        (df["electric_range_km"] >= 350) & (df["electric_range_km"] < 500),
        (df["electric_range_km"] >= 500) & (df["electric_range_km"] < 600),
        (df["electric_range_km"] >= 600)
    ]
    range_labels = ["Standard City (<350 km)", "Mid-Range (350-499 km)", "Long-Range (500-599 km)", "Ultra Long-Range (600+ km)"]
    df["range_tier"] = np.select(range_conditions, range_labels, default="Unclassified")

    # 5. Battery Capacity Bins
    cap_conditions = [
        (df["usable_battery_capacity_kwh"] < 60),
        (df["usable_battery_capacity_kwh"] >= 60) & (df["usable_battery_capacity_kwh"] <= 85),
        (df["usable_battery_capacity_kwh"] > 85)
    ]
    cap_labels = ["Standard (<60 kWh)", "Extended (60-85 kWh)", "High Capacity (>85 kWh)"]
    df["battery_tier"] = np.select(cap_conditions, cap_labels, default="Standard (<60 kWh)")

    # 6. Price Tier
    price_conditions = [
        (df["base_msrp_usd"] < 35000),
        (df["base_msrp_usd"] >= 35000) & (df["base_msrp_usd"] <= 65000),
        (df["base_msrp_usd"] > 65000)
    ]
    price_labels = ["Entry/Budget (<$35k)", "Mass Market ($35k-$65k)", "Premium/Luxury (>$65k)"]
    df["price_tier"] = np.select(price_conditions, price_labels, default="Mass Market ($35k-$65k)")

    return df

def engineer_sales_features(df_sales: pd.DataFrame) -> pd.DataFrame:
    """Calculates market share and YoY growth rates."""
    df = df_sales.copy()

    # Annual total sales denominator
    annual_totals = df.groupby("sales_year")["annual_sales_units"].transform("sum")
    df["annual_market_total_units"] = annual_totals
    df["market_share_pct"] = np.where(
        annual_totals > 0,
        ((df["annual_sales_units"] / annual_totals) * 100).round(2),
        0.0
    )

    # Manufacturer annual aggregated sales and YoY
    mfg_annual = df.groupby(["manufacturer", "sales_year"])["annual_sales_units"].sum().reset_index()
    mfg_annual = mfg_annual.sort_values(by=["manufacturer", "sales_year"])
    mfg_annual["prior_year_sales"] = mfg_annual.groupby("manufacturer")["annual_sales_units"].shift(1)
    mfg_annual["mfg_yoy_growth_pct"] = np.where(
        (mfg_annual["prior_year_sales"].notna()) & (mfg_annual["prior_year_sales"] > 0),
        (((mfg_annual["annual_sales_units"] - mfg_annual["prior_year_sales"]) / mfg_annual["prior_year_sales"]) * 100).round(2),
        np.nan
    )

    # Merge back YoY growth
    df = df.merge(
        mfg_annual[["manufacturer", "sales_year", "mfg_yoy_growth_pct"]],
        on=["manufacturer", "sales_year"],
        how="left"
    )

    return df

def generate_tableau_dataset(df_vehicles_feat: pd.DataFrame, df_sales_feat: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a denormalized, comprehensive dataset tailored for Tableau Desktop / Public.
    Merges vehicle specifications with annual sales metrics.
    """
    # Average specs by manufacturer and category to match sales grain
    mfg_cat_specs = df_vehicles_feat.groupby(["manufacturer", "vehicle_category"]).agg(
        avg_battery_capacity_kwh=("usable_battery_capacity_kwh", "mean"),
        avg_electric_range_km=("electric_range_km", "mean"),
        avg_charging_time_hours=("charging_time_hours", "mean"),
        avg_price_msrp_usd=("base_msrp_usd", "mean"),
        avg_customer_rating=("customer_rating", "mean"),
        primary_battery_tech=("battery_technology", lambda x: x.mode()[0] if not x.empty else "NMC"),
        manufacturing_country=("manufacturing_country", lambda x: x.mode()[0] if not x.empty else "Global"),
        vehicle_models_count=("model_name", "count")
    ).reset_index()

    # Round aggregated numbers
    mfg_cat_specs["avg_battery_capacity_kwh"] = mfg_cat_specs["avg_battery_capacity_kwh"].round(1)
    mfg_cat_specs["avg_electric_range_km"] = mfg_cat_specs["avg_electric_range_km"].round(1)
    mfg_cat_specs["avg_charging_time_hours"] = mfg_cat_specs["avg_charging_time_hours"].round(2)
    mfg_cat_specs["avg_price_msrp_usd"] = mfg_cat_specs["avg_price_msrp_usd"].round(0)
    mfg_cat_specs["avg_customer_rating"] = mfg_cat_specs["avg_customer_rating"].round(2)

    # Merge with sales records
    df_tableau = df_sales_feat.merge(
        mfg_cat_specs,
        on=["manufacturer", "vehicle_category"],
        how="left"
    )

    # Fill defaults for manufacturers/categories that only exist in sales or specs
    df_tableau["avg_battery_capacity_kwh"] = df_tableau["avg_battery_capacity_kwh"].fillna(75.0)
    df_tableau["avg_electric_range_km"] = df_tableau["avg_electric_range_km"].fillna(480.0)
    df_tableau["avg_charging_time_hours"] = df_tableau["avg_charging_time_hours"].fillna(0.50)
    df_tableau["avg_price_msrp_usd"] = df_tableau["avg_price_msrp_usd"].fillna(52000.0)
    df_tableau["avg_customer_rating"] = df_tableau["avg_customer_rating"].fillna(4.30)
    df_tableau["primary_battery_tech"] = df_tableau["primary_battery_tech"].fillna("NMC")
    df_tableau["manufacturing_country"] = df_tableau["manufacturing_country"].fillna("Germany")
    df_tableau["vehicle_models_count"] = df_tableau["vehicle_models_count"].fillna(1).astype(int)

    # Derived price-to-range for tableau
    df_tableau["tableau_price_to_range_ratio"] = (
        df_tableau["avg_price_msrp_usd"] / df_tableau["avg_electric_range_km"]
    ).round(2)

    return df_tableau

def main():
    """Executes feature engineering and outputs enriched data files."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Starting Feature Engineering pipeline...")

    # Load cleaned datasets
    vehicles_path = PROCESSED_DIR / "cleaned_vehicles.csv"
    sales_path = PROCESSED_DIR / "cleaned_sales.csv"

    if not vehicles_path.exists() or not sales_path.exists():
        logger.error("Cleaned data files missing. Please run src/data_cleaning.py first.")
        return

    df_vehicles = pd.read_csv(vehicles_path)
    df_sales = pd.read_csv(sales_path)

    # 1. Feature Engineering
    df_vehicles_feat = engineer_vehicle_features(df_vehicles)
    df_sales_feat = engineer_sales_features(df_sales)

    # Save enriched datasets
    enriched_veh_path = PROCESSED_DIR / "engineered_vehicles.csv"
    enriched_sales_path = PROCESSED_DIR / "engineered_sales.csv"
    df_vehicles_feat.to_csv(enriched_veh_path, index=False)
    df_sales_feat.to_csv(enriched_sales_path, index=False)
    logger.info(f"Saved engineered vehicles ({len(df_vehicles_feat)} rows) to {enriched_veh_path}")
    logger.info(f"Saved engineered sales ({len(df_sales_feat)} rows) to {enriched_sales_path}")

    # 2. Unified Tableau Dataset
    df_tableau = generate_tableau_dataset(df_vehicles_feat, df_sales_feat)
    tableau_path = PROCESSED_DIR / "tableau_ev_market_data.csv"
    df_tableau.to_csv(tableau_path, index=False)
    logger.info(f"Saved Tableau analytical dataset ({len(df_tableau)} rows) to {tableau_path}")

if __name__ == "__main__":
    main()
