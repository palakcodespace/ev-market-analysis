"""
Automated Pytest Suite: Data Ingestion, Cleaning, and Feature Engineering Pipeline.
"""
from pathlib import Path
import pandas as pd
import pytest
from src.data_collection import generate_ev_specifications_raw, generate_ev_sales_raw
from src.data_cleaning import clean_ev_specifications, clean_ev_sales
from src.feature_engineering import engineer_vehicle_features, engineer_sales_features

def test_raw_dataset_generation():
    """Tests that raw data collection generates expected row counts and required fields."""
    df_specs = generate_ev_specifications_raw()
    df_sales = generate_ev_sales_raw()

    assert len(df_specs) >= 50
    assert len(df_sales) >= 200
    assert "vehicle_id" in df_specs.columns
    assert "usable_battery_capacity_kwh" in df_specs.columns
    assert "annual_sales_units" in df_sales.columns

def test_data_cleaning_specifications():
    """Tests deduplication, normalization, and outlier detection in vehicle specs."""
    df_raw = generate_ev_specifications_raw()
    df_clean, audit = clean_ev_specifications(df_raw)

    assert len(df_clean) == audit["cleaned_rows"]
    assert df_clean["vehicle_id"].is_unique
    # Verify battery chemistry normalization
    assert set(df_clean["battery_technology"].unique()).issubset({"LFP", "NMC", "NCA"})
    # Verify positive numeric values
    assert (df_clean["electric_range_km"] > 0).all()
    assert (df_clean["usable_battery_capacity_kwh"] > 0).all()

def test_data_cleaning_sales():
    """Tests sales data integrity, positive units, and year ranges."""
    df_raw = generate_ev_sales_raw()
    df_clean, audit = clean_ev_sales(df_raw)

    assert len(df_clean) == audit["cleaned_rows"]
    assert audit["total_sales_units"] > 10000000
    assert (df_clean["annual_sales_units"] >= 0).all()
    assert 2018 in audit["years_covered"]
    assert 2024 in audit["years_covered"]

def test_feature_engineering():
    """Tests calculated metrics: $/km ratio, efficiency, and market share."""
    df_clean_v, _ = clean_ev_specifications(generate_ev_specifications_raw())
    df_clean_s, _ = clean_ev_sales(generate_ev_sales_raw())

    df_veh_feat = engineer_vehicle_features(df_clean_v)
    df_sales_feat = engineer_sales_features(df_clean_s)

    # Check vehicle derived features
    assert "price_to_range_ratio" in df_veh_feat.columns
    assert "efficiency_kwh_per_100km" in df_veh_feat.columns
    assert "range_tier" in df_veh_feat.columns
    assert (df_veh_feat["price_to_range_ratio"] > 0).all()

    # Check sales derived features
    assert "market_share_pct" in df_sales_feat.columns
    assert "mfg_yoy_growth_pct" in df_sales_feat.columns
    assert (df_sales_feat["market_share_pct"] >= 0).all()
