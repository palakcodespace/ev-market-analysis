# Tableau Calculated Fields Reference Guide
## Electric Vehicle Market Analysis and Intelligence System

This document provides the exact syntax, return types, and business purposes of all Tableau calculated fields implemented for the **EV Market Intelligence Dashboard** and **Tableau Story**.

---

### 1. Market Share Percentage (Yearly Denominator)
- **Tableau Formula:**
  ```tableau
  SUM([Annual Sales Units]) / ATTR({ FIXED [Sales Year] : SUM([Annual Sales Units]) }) * 100
  ```
- **Data Type:** Number (Decimal, Formatted as Percentage `0.0%`)
- **Purpose:** Calculates the exact market share of each manufacturer within a specific sales year, utilizing Level of Detail (LOD) expression `{ FIXED [Sales Year] : SUM([Annual Sales Units]) }` to guarantee that local visual filtering does not distort the true global denominator.

---

### 2. Year-over-Year (YoY) Sales Growth Rate
- **Tableau Formula:**
  ```tableau
  (SUM([Annual Sales Units]) - LOOKUP(SUM([Annual Sales Units]), -1)) / ABS(LOOKUP(SUM([Annual Sales Units]), -1)) * 100
  ```
- **Compute Using:** `Sales Year` (Table Across)
- **Data Type:** Number (Decimal, Formatted as `+0.0%;-0.0%`)
- **Purpose:** Computes the percentage expansion or contraction in EV sales volume relative to the immediate preceding calendar year.

---

### 3. Price-to-Range Economic Value Ratio ($/km)
- **Tableau Formula:**
  ```tableau
  [Avg Price Msrp Usd] / [Avg Electric Range Km]
  ```
- **Data Type:** Number (Decimal, Formatted as Currency `$#,##0.00`)
- **Purpose:** Quantifies consumer cost per kilometer of driving range. Lower values signify higher capital efficiency for car buyers.

---

### 4. Driving Range Bins (Segment Classification)
- **Tableau Formula:**
  ```tableau
  IF [Avg Electric Range Km] < 350 THEN "1. Standard City (<350 km)"
  ELSEIF [Avg Electric Range Km] >= 350 AND [Avg Electric Range Km] < 500 THEN "2. Mid-Range (350-499 km)"
  ELSEIF [Avg Electric Range Km] >= 500 AND [Avg Electric Range Km] < 600 THEN "3. Long-Range (500-599 km)"
  ELSE "4. Ultra Long-Range (600+ km)"
  END
  ```
- **Data Type:** String (Dimension)
- **Purpose:** Categorizes vehicle models into consumer utility tiers for color encoding and bar segmentation.

---

### 5. Battery Capacity Tier
- **Tableau Formula:**
  ```tableau
  IF [Avg Battery Capacity Kwh] < 60.0 THEN "Standard (<60 kWh)"
  ELSEIF [Avg Battery Capacity Kwh] >= 60.0 AND [Avg Battery Capacity Kwh] <= 85.0 THEN "Extended (60-85 kWh)"
  ELSE "High Capacity (>85 kWh)"
  END
  ```
- **Data Type:** String (Dimension)
- **Purpose:** Segments vehicles by physical pack size and cell raw material requirements.

---

### 6. Energy Consumption Efficiency Index (kWh/100km)
- **Tableau Formula:**
  ```tableau
  ([Avg Battery Capacity Kwh] / [Avg Electric Range Km]) * 100
  ```
- **Data Type:** Number (Decimal)
- **Purpose:** Evaluates powertrain and aerodynamic efficiency. Vehicles requiring fewer kWh per 100 km reflect superior battery management system (BMS) calibration and lower rolling resistance.

---

### 7. Fast-Charging Speed Rate (Range Added per Minute)
- **Tableau Formula:**
  ```tableau
  ([Avg Electric Range Km] * 0.70) / ([Avg Charging Time Hours] * 60)
  ```
- **Data Type:** Number (Decimal, `0.0 km/min`)
- **Purpose:** Estimates real-world highway charging convenience during a typical 10%–80% state-of-charge (SoC) DC fast-charging stop.

---

### 8. Manufacturer Volume Tier
- **Tableau Formula:**
  ```tableau
  IF { FIXED [Manufacturer], [Sales Year] : SUM([Annual Sales Units]) } >= 1000000 THEN "Tier 1 Mega-OEM (>1M units)"
  ELSEIF { FIXED [Manufacturer], [Sales Year] : SUM([Annual Sales Units]) } >= 250000 THEN "Tier 2 High-Volume (250k-1M units)"
  ELSE "Tier 3 Emerging / Niche (<250k units)"
  END
  ```
- **Data Type:** String (Dimension)
- **Purpose:** Classifies manufacturers into strategic peer groups for benchmark comparisons.

---

### 9. Top 10 Manufacturer Flag
- **Tableau Formula:**
  ```tableau
  RANK_DENSE(SUM([Annual Sales Units]), 'desc') <= 10
  ```
- **Data Type:** Boolean (Filter)
- **Purpose:** Isolates the top 10 market leaders on horizontal bar charts while preventing visual clutter.

---

### 10. Benchmark Customer Satisfaction Tier
- **Tableau Formula:**
  ```tableau
  IF [Avg Customer Rating] >= 4.50 THEN "Top Tier (4.50 - 5.00 ★)"
  ELSEIF [Avg Customer Rating] >= 4.20 THEN "Competitive (4.20 - 4.49 ★)"
  ELSE "Needs Improvement (<4.20 ★)"
  END
  ```
- **Data Type:** String (Dimension)
- **Purpose:** Groups OEM customer rating benchmarks into clear qualitative categories.
