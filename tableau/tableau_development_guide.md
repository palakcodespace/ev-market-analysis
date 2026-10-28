# Tableau Development & Publishing Guide
## Electric Vehicle Market Analysis and Intelligence System

This guide provides end-to-end instructions for building, validating, and publishing the **EV Market Intelligence Dashboard** and **Tableau Story** using Tableau Desktop or Tableau Public.

---

### Table of Contents
1. Data Source Connection
2. 12 Detailed Visualization Specifications
3. Executive Dashboard Assembly & Layout
4. 5-Scene Story Assembly
5. Publishing to Tableau Public / Tableau Cloud
6. Web Embedding Configuration in Flask

---

### 1. Data Source Connection

#### Method A: Direct CSV Extract (Recommended for Tableau Public)
1. Launch **Tableau Desktop** or **Tableau Public**.
2. Under **Connect &rarr; To a File**, select **Text file**.
3. Navigate to your project directory and select:
   `data/processed/tableau_ev_market_data.csv`
4. Verify the schema in the Data Source canvas:
   - `sales_year`: Number (whole) &rarr; Drag to Dimension or convert to Discrete.
   - `annual_sales_units`: Number (whole) &rarr; Measure.
   - `avg_electric_range_km`: Number (decimal) &rarr; Measure.
   - `avg_battery_capacity_kwh`: Number (decimal) &rarr; Measure.
   - `avg_price_msrp_usd`: Number (decimal) &rarr; Measure.
   - `avg_customer_rating`: Number (decimal) &rarr; Measure.
   - `manufacturer`, `vehicle_category`, `primary_battery_tech`, `manufacturing_country`: String &rarr; Dimension.

#### Method B: Live MySQL 8 Connection (Tableau Desktop)
1. Under **Connect &rarr; To a Server**, select **MySQL**.
2. Enter Server: `localhost`, Port: `3306`, Database: `ev_market_db`.
3. Provide your MySQL credentials and click **Sign In**.
4. Drag the analytical view `vw_vehicle_performance_ratings` and `vw_manufacturer_market_share` onto the canvas.

---

### 2. Twelve Distinct Visualization Specifications

#### Visualization 1: Executive KPI Cards
- **Business Question:** What are the top-level macroeconomic and engineering metrics of the EV market?
- **Dimensions:** None (Global or Filtered scope).
- **Measures:**
  - `SUM([Annual Sales Units])`
  - `COUNTD([Manufacturer])`
  - `AVG([Avg Electric Range Km])`
  - `AVG([Avg Battery Capacity Kwh])`
  - `AVG([Avg Price Msrp Usd])`
  - `AVG([Avg Customer Rating])`
- **Mark Type:** Text / Square KPI card.
- **Interpretation:** Provides immediate context on overall scale, range parity with ICE vehicles, and consumer sentiment.

#### Visualization 2: Annual EV Sales Trend & YoY Growth Rate
- **Business Question:** How has global electric vehicle sales volume grown from 2018 to 2024, and what were the year-over-year acceleration rates?
- **Dimensions:** `Sales Year` on Columns.
- **Measures:**
  - Axis 1: `SUM([Annual Sales Units])` &rarr; Bar Mark (Color: Dark Navy `#0F1C3F`).
  - Axis 2: `[YoY Sales Growth Rate]` &rarr; Line Mark (Color: Electric Teal `#00D2B4`, with Circle Data Points).
- **Tableau Operations:** Right-click second axis &rarr; **Dual Axis** &rarr; **Synchronize Axis** &rarr; Format as percentage.
- **Interpretation:** Highlights the massive 2021 post-pandemic inflection (+94% YoY) and steady multi-million unit expansion through 2024.

#### Visualization 3: Manufacturer Sales Ranking & Market Share
- **Business Question:** Which automotive manufacturers dominate global volume, and what is their relative market share?
- **Dimensions:** `Manufacturer` on Rows (Sorted descending by `SUM([Annual Sales Units])`).
- **Measures:** `SUM([Annual Sales Units])` on Columns.
- **Calculated Field:** `[Market Share Percentage]` placed on Label.
- **Filters:** Top 10 by Sales Volume; `Sales Year = 2024`.
- **Mark Type:** Horizontal Bar. Color top 2 (BYD & Tesla) in Teal, others in Cobalt Blue.
- **Interpretation:** Visualizes the volume duopoly at the top while demonstrating the tight contest between European and Korean legacy OEMs.

#### Visualization 4: Vehicle Category Sales Comparison
- **Business Question:** What is the breakdown of EV sales across vehicle body styles (SUVs, Sedans, Hatchbacks, Pickups)?
- **Dimensions:** `Vehicle Category` on Color.
- **Measures:** `SUM([Annual Sales Units])` on Angle and Label.
- **Mark Type:** Pie / Donut Chart (created using dual-axis dummy measure `MIN(1)` with white center circle).
- **Interpretation:** Demonstrates clear SUV preference (&gt;52% market share), illustrating consumer demand for family utility and elevated ride height.

#### Visualization 5: Manufacturer Market Share Trajectory (100% Stacked Bar)
- **Business Question:** How has OEM market share shifted over time (2018 vs 2024)?
- **Dimensions:** `Sales Year` on Columns, `Manufacturer` on Color.
- **Measures:** `SUM([Annual Sales Units])` on Rows &rarr; Quick Table Calculation &rarr; **Percent of Total** &rarr; Compute using `Manufacturer`.
- **Mark Type:** Bar (100% Stacked).
- **Interpretation:** Reveals the dramatic market-share growth of Chinese manufacturers (BYD, MG, NIO) relative to early North American and European shares.

#### Visualization 6: Battery Technology Distribution (LFP vs NMC vs NCA)
- **Business Question:** What proportion of EV models employ LFP vs NMC chemistry, and how do their average ranges compare?
- **Dimensions:** `Primary Battery Tech` on Columns.
- **Measures:**
  - Bar Axis: `COUNTD([Vehicle Models Count])` (Model count).
  - Line Axis: `AVG([Avg Electric Range Km])` (km Range).
- **Mark Type:** Dual-Axis Combo Chart.
- **Interpretation:** Explains why LFP is the volume choice for affordable mass-market vehicles, while NMC commands the luxury/long-range sector.

#### Visualization 7: Driving Range Comparison by Vehicle Category
- **Business Question:** How does real-world driving range vary between luxury sedans, family SUVs, and urban hatchbacks?
- **Dimensions:** `Vehicle Category` on Rows.
- **Measures:** `AVG([Avg Electric Range Km])` on Columns.
- **Detail:** Reference Line showing the global fleet average (517 km).
- **Mark Type:** Bar or Box-and-Whisker plot showing min, median, and max range within each category.
- **Interpretation:** Sedans achieve superior top-end range (exceeding 600 km) due to reduced aerodynamic drag, while hatchbacks optimize for city efficiency (300–420 km).

#### Visualization 8: Battery Capacity vs Driving Range Scatter Matrix
- **Business Question:** What is the empirical correlation between usable battery pack size (kWh) and electric driving range (km)?
- **Columns (X-Axis):** `AVG([Avg Battery Capacity Kwh])`.
- **Rows (Y-Axis):** `AVG([Avg Electric Range Km])`.
- **Detail:** `Manufacturer`, `Vehicle Category`.
- **Color:** `Primary Battery Tech`.
- **Analytics Pane:** Add **Linear Trend Line**.
- **Calculated Metric:** Slope indicates ~6.3 km of driving range per usable kWh.
- **Interpretation:** Validates that while larger packs increase range, diminishing returns occur above 100 kWh due to curb weight penalties.

#### Visualization 9: Manufacturing Country Distribution
- **Business Question:** Which countries assemble the highest number of electric vehicle models?
- **Dimensions:** `Manufacturing Country` on Rows (Sorted descending).
- **Measures:** `COUNTD([Vehicle Models Count])` on Columns.
- **Color:** `AVG([Avg Price Msrp Usd])`.
- **Mark Type:** Horizontal Bar Chart.
- **Interpretation:** Underscores China’s manufacturing leadership (23 models across all price tiers) followed by Germany's focus on premium EVs.

#### Visualization 10: Customer Satisfaction Benchmarks by Manufacturer
- **Business Question:** Which automotive brands achieve the highest customer satisfaction and reliability scores?
- **Dimensions:** `Manufacturer` on Columns (Sorted descending by rating).
- **Measures:** `AVG([Avg Customer Rating])` on Rows.
- **Detail / Tooltip:** `Reliability Score`, `Driving Dynamics Score`.
- **Mark Type:** Ranked Bar Chart.
- **Interpretation:** Porsche, Hyundai, and Tesla lead in overall customer satisfaction, reflecting driver appreciation for rapid acceleration, infotainment, and charging networks.

#### Visualization 11: Vehicle Price vs Driving Range Economic Value Matrix ($/km)
- **Business Question:** Which vehicles deliver the greatest driving range per dollar of retail MSRP?
- **Columns (X-Axis):** `AVG([Avg Electric Range Km])`.
- **Rows (Y-Axis):** `AVG([Avg Price Msrp Usd])`.
- **Color:** Continuous color scale on `[Price-to-Range Ratio]`.
- **Reference Bands:** Quadrant lines at median price ($52k) and median range (500 km).
- **Interpretation:** The lower-right quadrant highlights consumer "value champions" (e.g. BYD Seal, Tesla Model 3 RWD, Volvo EX30).

#### Visualization 12: Year-wise Battery Technology Adoption Trends
- **Business Question:** How has the market share of LFP chemistry expanded between 2018 and 2024?
- **Dimensions:** `Sales Year` on Columns, `Primary Battery Tech` on Color.
- **Measures:** `SUM([Annual Sales Units])` on Rows (Percent of Total).
- **Mark Type:** Area Chart.
- **Interpretation:** Documents the rapid escalation of LFP adoption from &lt;10% in 2018 to &gt;35% in 2024 as cobalt prices rose.

---

### 3. Executive Dashboard Assembly & Layout
1. In Tableau, click **New Dashboard** (Bottom tab).
2. Set Size to **Fixed Size: 1400 x 1200 pixels**.
3. Drag a **Vertical Layout Container** onto the canvas.
4. Drag a **Horizontal Layout Container** to the top for the Title and Filters:
   - Add Text Box: "EV Market Intelligence Dashboard".
   - Drag Filters: `Sales Year`, `Manufacturer`, `Vehicle Category`. Set all filters to **Apply to All Worksheets using this Data Source**.
5. Drag a Horizontal Container for the **KPI Cards** (Sheet 1).
6. Drag a 2-column Horizontal Container for **Sales Trend** (Sheet 2) and **Top 10 Rankings** (Sheet 3).
7. Drag a 2-column Container for **Category Share** (Sheet 4) and **Battery Chemistry** (Sheet 6).
8. Drag a 2-column Container for **Scatter Plot** (Sheet 8) and **Geography** (Sheet 9).
9. Add **Dashboard Actions**:
   - Go to **Dashboard &rarr; Actions &rarr; Add Action &rarr; Filter**.
   - Source Sheet: Sheet 3 (Top 10 Manufacturers).
   - Target Sheets: All other sheets.
   - Run Action On: **Select** (Click). Clearing the selection shows all values.

---

### 4. Five-Scene Story Assembly
1. Click **New Story** (Bottom tab).
2. Set Story Size to **1366 x 768 pixels**.
3. **Scene 1:** Drag Dashboard / Sales Trend sheet into the first story navigator block.
   - Heading: `EV Market Overview: Global Electric Inflection (2018-2024)`.
   - Text Callout: Add narrative from `story_specification.md`.
4. Click **Blank** to create Scene 2:
   - Drag Top 10 Manufacturers sheet.
   - Heading: `Manufacturer Competition: BYD vs Tesla Duopoly`.
5. Create Scene 3 (Category Hegemony: SUVs vs Sedans).
6. Create Scene 4 (Battery Chemistry Revolution: Rise of Cobalt-Free LFP).
7. Create Scene 5 (Geographic Supply Chains & Strategic Roadmap).

---

### 5. Publishing to Tableau Public / Tableau Cloud
1. In Tableau, navigate to **Data &rarr; [Data Source] &rarr; Extract Data...** and click **Extract**.
2. Go to **Server &rarr; Tableau Public &rarr; Save to Tableau Public As...**.
3. Enter your Tableau Public login credentials.
4. Name the workbook: `Electric Vehicle Market Analysis and Intelligence System`.
5. Once published, your browser opens the interactive visualization.
6. Click the **Share** icon on the published page and copy the **Link URL** (e.g. `https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Dashboard`).

---

### 6. Web Embedding Configuration in Flask
1. Open the project root `.env` file (or copy from `.env.example`).
2. Paste the copied Tableau Public URLs:
   ```env
   TABLEAU_DASHBOARD_URL=https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Dashboard
   TABLEAU_STORY_URL=https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Story
   ```
3. Restart or refresh the Flask application.
4. The dashboard page (`/dashboard`) and story page (`/story`) will now automatically render your live Tableau workbook in high-definition responsive iframes with interactive Tableau toolbars!
