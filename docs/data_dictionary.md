# Data Dictionary
## Electric Vehicle Market Analysis and Intelligence System

This data dictionary provides comprehensive definitions, data types, physical units, allowable ranges, and source provenance for every field across raw, cleaned, and relational database tables.

---

### Table 1: `manufacturers` (Automotive OEMs)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `manufacturer_id` | `INT` / `INTEGER` | `PRIMARY KEY`, Auto | N/A | Unique surrogate primary key for OEM | Generated |
| `manufacturer_name` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` | Text | Standardized brand/company name (e.g., "Tesla", "BYD", "Volkswagen") | IEA / OEM Registry |
| `headquarters_country` | `VARCHAR(100)` | `NOT NULL` | Text | Country where global corporate headquarters is situated | Corporate Registry |
| `founded_year` | `INT` | Nullable | Calendar Year | Year the automotive company was established | Corporate Archive |
| `website` | `VARCHAR(255)` | Nullable | URL | Official global corporate web portal | OEM Public Domain |
| `created_at` | `TIMESTAMP` | Default Current | UTC Time | Database record insertion timestamp | System Generated |

---

### Table 2: `battery_technologies` (Cell Chemistries)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `battery_tech_id` | `INT` / `INTEGER` | `PRIMARY KEY`, Auto | N/A | Surrogate key for battery technology | Generated |
| `chemistry_code` | `VARCHAR(20)` | `NOT NULL`, `UNIQUE` | Code | Standard industrial chemistry designation (`LFP`, `NMC`, `NCA`) | Battery Council |
| `full_name` | `VARCHAR(100)` | `NOT NULL` | Text | Full scientific chemistry title | Chemical Nomenclature |
| `energy_density_wh_kg` | `INT` | `NOT NULL` | Wh/kg | Gravimetric energy density at cell level | Technical Benchmarks |
| `thermal_stability` | `VARCHAR(50)` | `NOT NULL` | Text | Relative thermal runaway resistance rating | Engineering Testing |
| `cost_tier` | `VARCHAR(30)` | `NOT NULL` | Text | Relative manufacturing raw material expense tier | Supply Chain Index |
| `description` | `TEXT` | Nullable | Text | In-depth engineering description of performance trade-offs | Technical Literature |

---

### Table 3: `geographies` (Market Regions & Assembly Nations)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `geography_id` | `INT` / `INTEGER` | `PRIMARY KEY`, Auto | N/A | Surrogate key for geographical territory | Generated |
| `market_region` | `VARCHAR(100)` | `NOT NULL` | Text | Economic reporting region (North America, Europe, Asia-Pacific, Latin America, Global) | IEA Standard |
| `country_name` | `VARCHAR(100)` | `NOT NULL` | Text | Specific sovereign nation | ISO 3166 Standard |
| `continent` | `VARCHAR(50)` | `NOT NULL` | Text | Continental landmass classification | Geographic Standard |

---

### Table 4: `vehicles` (Production Model Technical Specifications)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vehicle_id` | `VARCHAR(50)` | `PRIMARY KEY` | Code | Standardized unique model identifier (e.g. `EV-001`) | EV-Database Code |
| `manufacturer_id` | `INT` | `FOREIGN KEY` &rarr; `manufacturers` | N/A | Foreign key linking vehicle to its parent manufacturer | Relational Constraint |
| `battery_tech_id` | `INT` | `FOREIGN KEY` &rarr; `battery_technologies` | N/A | Foreign key identifying primary battery chemistry | Relational Constraint |
| `model_name` | `VARCHAR(100)` | `NOT NULL` | Text | Commercial model and trim designation (e.g., "Model 3 Long Range") | OEM Specification |
| `model_year` | `INT` | `NOT NULL`, [2010–2026] | Calendar Year | Production model release year | OEM Specification |
| `vehicle_category` | `VARCHAR(50)` | `NOT NULL` | Text | Vehicle body style (Sedan, SUV, Hatchback, Crossover, Pickup, Van, Coupe) | Automotive Classification |
| `usable_battery_capacity_kwh` | `DECIMAL(6,2)` | `NOT NULL`, &gt; 0 | kWh | Net usable electrical energy capacity of battery pack | EV-Database Tested |
| `electric_range_km` | `DECIMAL(6,2)` | `NOT NULL`, &gt; 0 | km | Real-world combined electric driving range | WLTP/EPA Certified |
| `fast_charge_power_kw` | `DECIMAL(6,2)` | `NOT NULL`, &gt; 0 | kW | Peak DC rapid-charging power acceptance | OEM Benchmark |
| `charging_time_hours` | `DECIMAL(4,2)` | `NOT NULL`, &gt; 0 | Hours | Time required for standard 10%–80% fast-charging cycle | OEM Benchmark |
| `base_msrp_usd` | `DECIMAL(10,2)` | `NOT NULL`, &gt;= 0 | USD ($) | Manufacturer's suggested retail price in baseline configuration | Market Listing |
| `manufacturing_country` | `VARCHAR(100)` | `NOT NULL` | Text | Primary assembly country where vehicle chassis is produced | OEM Assembly Registry |
| `market_region` | `VARCHAR(100)` | `NOT NULL` | Text | Primary commercial distribution target | Commercial Strategy |
| `powertrain_type` | `VARCHAR(20)` | `NOT NULL`, Default `BEV` | Text | Propulsion technology (Battery Electric Vehicle) | Standard Taxonomy |
| `co2_emissions_g_km` | `DECIMAL(5,2)` | Default `0.00` | g/km | Direct tailpipe carbon dioxide emissions (0 for BEVs) | Regulatory Mandate |

---

### Table 5: `customer_ratings` (Consumer Satisfaction Survey Benchmark)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `rating_id` | `INT` / `INTEGER` | `PRIMARY KEY`, Auto | N/A | Unique rating index | Generated |
| `vehicle_id` | `VARCHAR(50)` | `FOREIGN KEY` &rarr; `vehicles` | N/A | Foreign key linking score to specific EV model | Relational Constraint |
| `overall_rating` | `DECIMAL(3,2)` | `NOT NULL`, [1.00–5.00] | Rating (1-5) | Composite consumer satisfaction index | Survey Benchmark |
| `reliability_score` | `DECIMAL(3,2)` | `NOT NULL`, [1.00–5.00] | Rating (1-5) | Long-term mechanical and electrical reliability score | What Car? / J.D. Power |
| `driving_dynamics_score` | `DECIMAL(3,2)` | `NOT NULL`, [1.00–5.00] | Rating (1-5) | Ride comfort, acceleration, and handling rating | Consumer Reports Index |
| `infotainment_score` | `DECIMAL(3,2)` | `NOT NULL`, [1.00–5.00] | Rating (1-5) | Software responsiveness and UI intuitiveness score | Benchmark Survey |
| `survey_sample_size` | `INT` | Default `1500` | Count | Number of verified vehicle owners polled | Survey Design |
| `benchmark_source` | `VARCHAR(100)` | Text | Text | Source documentation label | Transparency Protocol |

---

### Table 6: `sales` (Annual Historical Volume Records)

| Column Name | Data Type | Constraints | Unit | Description | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `sales_id` | `VARCHAR(50)` | `PRIMARY KEY` | Code | Unique transaction/record identifier (e.g. `SALES-0001`) | Generated |
| `manufacturer_id` | `INT` | `FOREIGN KEY` &rarr; `manufacturers` | N/A | Foreign key linking sales volume to parent OEM | Relational Constraint |
| `vehicle_category` | `VARCHAR(50)` | `NOT NULL` | Text | Segment category of sold vehicles | Market Definition |
| `market_region` | `VARCHAR(100)` | `NOT NULL` | Text | Geographic region of sales delivery | Regional Audit |
| `sales_year` | `INT` | `NOT NULL`, [2018–2024] | Calendar Year | Calendar year of sales activity | Reporting Year |
| `annual_sales_units` | `INT` | `NOT NULL`, &gt;= 0 | Vehicle Units | Total number of units sold | IEA Global EV Outlook |
| `data_source` | `VARCHAR(100)` | Text | Text | Primary benchmark provenance | Reference Registry |
