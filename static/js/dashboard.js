/**
 * Dashboard & Visualization Controller
 * Powered by Plotly.js and Fetch API.
 * Interactively updates charts upon filter adjustment.
 */

document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    loadDashboardVisualizations();
});

// Color Palette
const COLORS = {
    teal: "#00D2B4",
    navy: "#0F1C3F",
    blue: "#3A86FF",
    amber: "#FFB703",
    purple: "#8338EC",
    green: "#2EC4B6",
    gray: "#94A3B8",
    palette: ["#00D2B4", "#3A86FF", "#FFB703", "#8338EC", "#E63946", "#2EC4B6", "#FF006E", "#3A0CA3"]
};

// Global filter state
let currentFilters = {
    year: 2024,
    manufacturer: "All",
    category: "All"
};

function initFilters() {
    const yearSelect = document.getElementById("filter-year");
    const mfgSelect = document.getElementById("filter-mfg");
    const catSelect = document.getElementById("filter-cat");
    const resetBtn = document.getElementById("btn-reset-filters");

    if (yearSelect) {
        yearSelect.addEventListener("change", function () {
            currentFilters.year = this.value;
            applyFilters();
        });
    }

    if (mfgSelect) {
        mfgSelect.addEventListener("change", function () {
            currentFilters.manufacturer = this.value;
            applyFilters();
        });
    }

    if (catSelect) {
        catSelect.addEventListener("change", function () {
            currentFilters.category = this.value;
            applyFilters();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            if (yearSelect) yearSelect.value = "2024";
            if (mfgSelect) mfgSelect.value = "All";
            if (catSelect) catSelect.value = "All";
            currentFilters = { year: 2024, manufacturer: "All", category: "All" };
            applyFilters();
        });
    }
}

function applyFilters() {
    updateKPIs();
    renderSalesTrendChart();
    renderManufacturerRankingChart();
    renderCategoryDonutChart();
}

function updateKPIs() {
    let url = `/api/kpis?year=${currentFilters.year}`;
    if (currentFilters.manufacturer !== "All") url += `&manufacturer=${encodeURIComponent(currentFilters.manufacturer)}`;
    if (currentFilters.category !== "All") url += `&category=${encodeURIComponent(currentFilters.category)}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const elSales = document.getElementById("kpi-sales");
            const elMfgs = document.getElementById("kpi-mfgs");
            const elRange = document.getElementById("kpi-range");
            const elBattery = document.getElementById("kpi-battery");
            const elRating = document.getElementById("kpi-rating");
            const elPrice = document.getElementById("kpi-price");

            if (elSales) elSales.innerText = Number(data.total_sales_units).toLocaleString();
            if (elMfgs) elMfgs.innerText = data.active_manufacturers;
            if (elRange) elRange.innerText = `${data.avg_electric_range_km} km`;
            if (elBattery) elBattery.innerText = `${data.avg_battery_capacity_kwh} kWh`;
            if (elRating) elRating.innerText = `${data.avg_customer_rating} / 5.0`;
            if (elPrice) elPrice.innerText = `$${Number(data.avg_base_msrp_usd).toLocaleString()}`;
        })
        .catch(err => console.error("Error updating KPIs:", err));
}

function loadDashboardVisualizations() {
    updateKPIs();
    renderSalesTrendChart();
    renderManufacturerRankingChart();
    renderCategoryDonutChart();
    renderBatteryTechChart();
    renderBatteryVsRangeScatter();
    renderGeographyChart();
    renderPriceVsRangeScatter();
    renderCustomerSatisfactionChart();
}

// 1. Annual EV Sales Trend
function renderSalesTrendChart() {
    const chartDiv = document.getElementById("chart-sales-trend");
    if (!chartDiv) return;

    let url = "/api/sales-trend";
    const params = [];
    if (currentFilters.manufacturer !== "All") params.push(`manufacturer=${encodeURIComponent(currentFilters.manufacturer)}`);
    if (currentFilters.category !== "All") params.push(`category=${encodeURIComponent(currentFilters.category)}`);
    if (params.length > 0) url += `?${params.join("&")}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const years = data.map(d => d.sales_year);
            const units = data.map(d => d.annual_units);
            const yoy = data.map(d => d.yoy_growth_pct);

            const traceBars = {
                x: years,
                y: units,
                type: "bar",
                name: "Annual Sales (Units)",
                marker: { color: COLORS.navy, opacity: 0.9 },
                yaxis: "y1"
            };

            const traceLine = {
                x: years,
                y: yoy,
                type: "scatter",
                mode: "lines+markers",
                name: "YoY Growth Rate (%)",
                line: { color: COLORS.teal, width: 3 },
                marker: { size: 8, color: COLORS.teal },
                yaxis: "y2"
            };

            const layout = {
                margin: { t: 30, r: 50, l: 60, b: 40 },
                showlegend: true,
                legend: { orientation: "h", y: -0.2 },
                yaxis: { title: "Units Sold", showgrid: true, gridcolor: "#F1F5F9" },
                yaxis2: {
                    title: "YoY Growth (%)",
                    overlaying: "y",
                    side: "right",
                    showgrid: false,
                    ticksuffix: "%"
                },
                xaxis: { title: "Year", dtick: 1 },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [traceBars, traceLine], layout, { responsive: true, displayModeBar: false });
        });
}

// 2. Top Manufacturer Rankings
function renderManufacturerRankingChart() {
    const chartDiv = document.getElementById("chart-manufacturer-ranking");
    if (!chartDiv) return;

    fetch(`/api/manufacturer-ranking?year=${currentFilters.year}&limit=10`)
        .then(res => res.json())
        .then(data => {
            // Sort ascending for horizontal bar chart
            const sorted = [...data].reverse();
            const names = sorted.map(d => d.manufacturer_name);
            const units = sorted.map(d => d.total_units);
            const shares = sorted.map(d => d.market_share_pct);

            const trace = {
                x: units,
                y: names,
                type: "bar",
                orientation: "h",
                marker: {
                    color: units.map((u, i) => i === sorted.length - 1 ? COLORS.teal : COLORS.blue)
                },
                text: shares.map(s => `${s}% share`),
                textposition: "auto",
                hoverinfo: "x+y+text"
            };

            const layout = {
                margin: { t: 20, r: 30, l: 110, b: 40 },
                xaxis: { title: "Volume (Units Sold)", showgrid: true, gridcolor: "#F1F5F9" },
                yaxis: { automargin: true },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [trace], layout, { responsive: true, displayModeBar: false });
        });
}

// 3. Category Market Breakdown (Donut)
function renderCategoryDonutChart() {
    const chartDiv = document.getElementById("chart-category-breakdown");
    if (!chartDiv) return;

    fetch(`/api/category-breakdown?year=${currentFilters.year}`)
        .then(res => res.json())
        .then(data => {
            const labels = data.map(d => d.vehicle_category);
            const values = data.map(d => d.category_units);

            const trace = {
                labels: labels,
                values: values,
                type: "pie",
                hole: 0.55,
                marker: { colors: COLORS.palette },
                textinfo: "label+percent",
                hoverinfo: "label+value+percent"
            };

            const layout = {
                margin: { t: 20, r: 20, l: 20, b: 20 },
                showlegend: true,
                legend: { orientation: "h", y: -0.1 },
                paper_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [trace], layout, { responsive: true, displayModeBar: false });
        });
}

// 4. Battery Technology Distribution
function renderBatteryTechChart() {
    const chartDiv = document.getElementById("chart-battery-tech");
    if (!chartDiv) return;

    fetch("/api/battery-tech")
        .then(res => res.json())
        .then(data => {
            const chemistries = data.map(d => d.chemistry_code);
            const models = data.map(d => d.model_count);
            const ranges = data.map(d => d.avg_range_km);

            const traceCount = {
                x: chemistries,
                y: models,
                type: "bar",
                name: "Models Produced",
                marker: { color: COLORS.blue },
                yaxis: "y1"
            };

            const traceRange = {
                x: chemistries,
                y: ranges,
                type: "scatter",
                mode: "lines+markers",
                name: "Avg Range (km)",
                marker: { size: 10, color: COLORS.amber },
                line: { width: 3, dash: "dot" },
                yaxis: "y2"
            };

            const layout = {
                margin: { t: 30, r: 50, l: 50, b: 40 },
                showlegend: true,
                legend: { orientation: "h", y: -0.2 },
                yaxis: { title: "Vehicle Models Count" },
                yaxis2: { title: "Avg Range (km)", overlaying: "y", side: "right", showgrid: false },
                xaxis: { title: "Battery Chemistry" },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [traceCount, traceRange], layout, { responsive: true, displayModeBar: false });
        });
}

// 5. Battery Capacity vs Driving Range Scatter
function renderBatteryVsRangeScatter() {
    const chartDiv = document.getElementById("chart-scatter-battery-range");
    if (!chartDiv) return;

    fetch("/api/scatter-battery-range")
        .then(res => res.json())
        .then(data => {
            const chemistries = [...new Set(data.map(d => d.battery_chemistry))];
            const traces = chemistries.map((chem, idx) => {
                const subset = data.filter(d => d.battery_chemistry === chem);
                return {
                    x: subset.map(d => d.usable_battery_capacity_kwh),
                    y: subset.map(d => d.electric_range_km),
                    mode: "markers",
                    name: chem,
                    text: subset.map(d => `${d.manufacturer_name} ${d.model_name}<br>Price: $${d.base_msrp_usd.toLocaleString()}<br>Rating: $${d.price_to_range_ratio}/km`),
                    marker: {
                        size: 11,
                        color: COLORS.palette[idx % COLORS.palette.length],
                        opacity: 0.85
                    }
                };
            });

            const layout = {
                margin: { t: 30, r: 30, l: 60, b: 50 },
                xaxis: { title: "Usable Battery Capacity (kWh)", showgrid: true, gridcolor: "#F1F5F9" },
                yaxis: { title: "Electric Driving Range (km)", showgrid: true, gridcolor: "#F1F5F9" },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, traces, layout, { responsive: true, displayModeBar: false });
        });
}

// 6. Geographic Distribution
function renderGeographyChart() {
    const chartDiv = document.getElementById("chart-geography");
    if (!chartDiv) return;

    fetch("/api/geography-data")
        .then(res => res.json())
        .then(data => {
            const sorted = [...data].reverse();
            const countries = sorted.map(d => d.manufacturing_country);
            const models = sorted.map(d => d.model_count);

            const trace = {
                x: models,
                y: countries,
                type: "bar",
                orientation: "h",
                marker: { color: COLORS.green },
                text: models.map(m => `${m} models`),
                textposition: "auto"
            };

            const layout = {
                margin: { t: 20, r: 30, l: 90, b: 40 },
                xaxis: { title: "Models Manufactured" },
                yaxis: { automargin: true },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [trace], layout, { responsive: true, displayModeBar: false });
        });
}

// 7. Price vs Range Matrix
function renderPriceVsRangeScatter() {
    const chartDiv = document.getElementById("chart-scatter-price-range");
    if (!chartDiv) return;

    fetch("/api/scatter-battery-range")
        .then(res => res.json())
        .then(data => {
            const trace = {
                x: data.map(d => d.electric_range_km),
                y: data.map(d => d.base_msrp_usd),
                mode: "markers",
                text: data.map(d => `${d.manufacturer_name} ${d.model_name}<br>Value: $${d.price_to_range_ratio}/km`),
                marker: {
                    size: 10,
                    color: data.map(d => d.price_to_range_ratio),
                    colorscale: "Viridis",
                    showscale: true,
                    colorbar: { title: "$/km Ratio", len: 0.8 }
                }
            };

            const layout = {
                margin: { t: 30, r: 30, l: 70, b: 50 },
                xaxis: { title: "Electric Driving Range (km)", showgrid: true, gridcolor: "#F1F5F9" },
                yaxis: { title: "Base MSRP (USD)", showgrid: true, gridcolor: "#F1F5F9" },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [trace], layout, { responsive: true, displayModeBar: false });
        });
}

// 8. Customer Satisfaction by Manufacturer
function renderCustomerSatisfactionChart() {
    const chartDiv = document.getElementById("chart-customer-ratings");
    if (!chartDiv) return;

    fetch("/api/customer-ratings")
        .then(res => res.json())
        .then(data => {
            const top = data.slice(0, 10);
            const mfgs = top.map(d => d.manufacturer_name);
            const overall = top.map(d => d.avg_overall_rating);
            const reliability = top.map(d => d.avg_reliability);

            const traceOverall = {
                x: mfgs,
                y: overall,
                type: "bar",
                name: "Overall Rating",
                marker: { color: COLORS.teal }
            };

            const traceReliability = {
                x: mfgs,
                y: reliability,
                type: "bar",
                name: "Reliability Score",
                marker: { color: COLORS.navy }
            };

            const layout = {
                barmode: "group",
                margin: { t: 30, r: 30, l: 50, b: 70 },
                yaxis: { title: "Score (1 - 5 Scale)", range: [3.5, 5.0] },
                xaxis: { tickangle: -30 },
                legend: { orientation: "h", y: -0.3 },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent"
            };

            Plotly.newPlot(chartDiv, [traceOverall, traceReliability], layout, { responsive: true, displayModeBar: false });
        });
}
