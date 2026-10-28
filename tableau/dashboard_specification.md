# Tableau Executive Dashboard Specification
## Dashboard Title: "EV Market Intelligence Dashboard"

### 1. Canvas Dimensions and Layout Container Hierarchy
- **Canvas Size:** `1400px` (Width) &times; `1200px` (Height) — Fixed Desktop (1400x1200)
- **Grid Layout Strategy:** Tiled Vertical Container with nested Horizontal Sub-containers
- **Color Palette:**
  - Dark Navy Background Headers: `#081225` and `#0F1C3F`
  - Electric Teal Accents: `#00D2B4`
  - Cobalt Blue Data Marks: `#3A86FF`
  - Soft Card Backgrounds: `#FFFFFF` with `#E2E8F0` hairline borders
  - Font Hierarchy: Segoe UI / Tableau Book (Bold Headers 14–18pt, KPIs 24–32pt, Body/Labels 9–10pt)

---

### 2. Layout Structure

#### Header & Filter Band (Top 90px)
- **Left:** Dashboard Title: **EV Market Intelligence Dashboard** (20pt Bold Navy)
  - Subtitle: *Global Multi-Year Market Performance, Battery Adoption & Technical Specification Benchmark*
- **Right:** Filter Horizontal Container (Floating or Tiled in Header):
  1. `[Sales Year]` &rarr; Single Value (Dropdown) — Default: `2024`
  2. `[Manufacturer]` &rarr; Multiple Values (Dropdown) — Default: `(All)`
  3. `[Vehicle Category]` &rarr; Multiple Values (Dropdown) — Default: `(All)`
  4. `[Primary Battery Tech]` &rarr; Multiple Values (Dropdown) — Default: `(All)`
  5. `[Manufacturing Country]` &rarr; Multiple Values (Dropdown) — Default: `(All)`

---

#### Section 1: Executive KPI Cards (Height: 110px)
Six adjacent horizontal KPI cards across the grid:
1. **Total EV Sales Volume:**
   - Measure: `SUM([Annual Sales Units])`
   - Formatted: `#,##0` units
   - Subtext: *Cumulative volume in selected filters*
2. **Active Reporting Manufacturers:**
   - Measure: `COUNTD([Manufacturer])`
   - Formatted: `0` brands
3. **Average Electric Driving Range:**
   - Measure: `AVG([Avg Electric Range Km])`
   - Formatted: `#,##0 km`
   - Benchmark: *Real-world WLTP/EPA mixed cycle*
4. **Average Battery Pack Capacity:**
   - Measure: `AVG([Avg Battery Capacity Kwh])`
   - Formatted: `#,##0.0 kWh`
   - Benchmark: *Usable pack energy*
5. **Average Base MSRP:**
   - Measure: `AVG([Avg Price Msrp Usd])`
   - Formatted: `$#,##0`
6. **Consumer Satisfaction Index:**
   - Measure: `AVG([Avg Customer Rating])`
   - Formatted: `0.00 / 5.0` ★

---

#### Section 2: Macro Sales Trajectory & Competitive Hierarchy (Height: 320px)
Two columns:
- **Left (60% Width): Annual EV Sales Trend & YoY Growth**
  - **Type:** Dual-Axis Synchronized Chart (Bars + Line)
  - **Columns:** `[Sales Year]`
  - **Rows (Axis 1):** `SUM([Annual Sales Units])` (Navy Bar Marks)
  - **Rows (Axis 2):** `[YoY Sales Growth Rate]` (Teal Line Mark with Circle Data Points)
  - **Tooltip:** `Year`, `Sales Units`, `Prior Year Sales`, `Growth Rate (%)`
- **Right (40% Width): Top 10 Manufacturer Sales & Market Share Ranking**
  - **Type:** Horizontal Bar Chart
  - **Rows:** `[Manufacturer]` (Sorted Descending by `SUM([Annual Sales Units])`)
  - **Columns:** `SUM([Annual Sales Units])`
  - **Color:** Teal for Top 2, Cobalt Blue for remaining OEMs
  - **Label:** `[Market Share Percentage]` (`0.0%`)

---

#### Section 3: Segment Dynamics & Battery Chemistry Adoption (Height: 300px)
Two columns:
- **Left (45% Width): Vehicle Category Market Share**
  - **Type:** Donut / Radial Chart
  - **Color:** `[Vehicle Category]` (SUVs, Sedans, Hatchbacks, Crossovers, Pickups)
  - **Angle:** `SUM([Annual Sales Units])`
  - **Center Hole Text:** Total Market Volume
- **Right (55% Width): Battery Technology Distribution & Adoption**
  - **Type:** Grouped Bar / Line Combo
  - **Columns:** `[Primary Battery Tech]` (LFP, NMC, NCA)
  - **Rows:** `COUNTD([Vehicle Models Count])` and `AVG([Avg Electric Range Km])`
  - **Insights:** Highlights LFP cost advantage vs NMC energy density

---

#### Section 4: Engineering Trade-offs & Production Geography (Height: 320px)
Two columns:
- **Left (60% Width): Battery Capacity vs Driving Range Scatter Matrix**
  - **Type:** Interactive Scatter Plot
  - **Columns (X-Axis):** `AVG([Avg Battery Capacity Kwh])` (kWh)
  - **Rows (Y-Axis):** `AVG([Avg Electric Range Km])` (km)
  - **Detail / Marks:** `[Manufacturer]`, `[Vehicle Category]`
  - **Color:** `[Primary Battery Tech]`
  - **Size:** `AVG([Avg Price Msrp Usd])`
  - **Trendline:** Linear OLS regression line indicating efficiency slope (~6.3 km/kWh)
- **Right (40% Width): Manufacturing Country Footprint**
  - **Type:** Horizontal Bar Chart / Ranked Breakdown
  - **Rows:** `[Manufacturing Country]` (China, Germany, USA, South Korea, France, etc.)
  - **Columns:** `COUNTD([Vehicle Models Count])`
  - **Color:** Green Palette

---

#### Section 5: Value Matrix & Customer Ratings (Height: 280px)
Two columns:
- **Left (50% Width): Price-to-Range Economic Value Ratio ($/km)**
  - **Type:** Scatter Matrix (`[Avg Electric Range Km]` vs `[Avg Price Msrp Usd]`)
  - **Color:** Continuous Viridis Color Scale on `[Price-to-Range Ratio]`
  - **Interpretation:** Identifies high-value EV offerings in the lower-right quadrant
- **Right (50% Width): Customer Satisfaction & Reliability Scores**
  - **Type:** Clustered Bar Chart by Manufacturer
  - **Bars:** `[Avg Customer Rating]` alongside `[Reliability Score]`

---

#### Footer Metadata Ribbon (Bottom 40px)
- Text box: *Data Sources: IEA Global EV Outlook (CC BY 4.0), EV-Database Specifications, Automotive Consumer Survey Benchmarks. Last Refresh: October 2026. Certified Relational 3NF Pipeline.*

---

### 3. Interactive Filter Actions & Interactivity Matrix
1. **Year Selector:** Primary controller updating all sheets simultaneously.
2. **Manufacturer Click Action:** Clicking any manufacturer in Sheet 2 triggers a Filter Action across Sheets 3, 4, and 5, highlighting that OEM's specific models, range profile, and customer rating.
3. **Category Highlight Action:** Hovering over any vehicle category in the donut chart dims non-matching vehicles in the scatter plots.
4. **Tooltips:** Formatted with bold lead headers, clean units, and delta indicators.
