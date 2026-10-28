"""
Flask Web Application for Electric Vehicle Market Analysis and Intelligence System.
Serves interactive analytical dashboards, manufacturer comparisons, battery deep-dives,
geographic distributions, data narratives, and Tableau embeds.
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
from config import Config
from src.analytics import EVAnalyticsService
from database.db_connection import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.context_processor
def inject_global_metadata():
    """Injects database connection mode and Tableau config across all templates."""
    return {
        "db_mode": "SQLite (Local File DB)" if db_manager.is_sqlite else "MySQL 8.0 (Enterprise Server)",
        "tableau_dashboard_url": Config.TABLEAU_DASHBOARD_URL,
        "tableau_story_url": Config.TABLEAU_STORY_URL,
        "app_version": "2.4.0",
        "last_refresh_date": "October 2026"
    }

# --------------------------------------------------------------------
# Page Routes
# --------------------------------------------------------------------
@app.route("/")
def index():
    """Home page and executive project overview."""
    kpis = EVAnalyticsService.get_executive_kpis()
    filter_opts = EVAnalyticsService.get_filter_options()
    return render_template("index.html", kpis=kpis, filter_opts=filter_opts)

@app.route("/dashboard")
def dashboard():
    """Executive EV Market Intelligence Dashboard with interactive Plotly charts."""
    filter_opts = EVAnalyticsService.get_filter_options()
    default_kpis = EVAnalyticsService.get_executive_kpis(year=2024)
    return render_template("dashboard.html", filter_opts=filter_opts, kpis=default_kpis)

@app.route("/manufacturers")
def manufacturers():
    """Manufacturer comparison, market share ranking, and portfolio analysis."""
    filter_opts = EVAnalyticsService.get_filter_options()
    rankings = EVAnalyticsService.get_manufacturer_rankings(year=2024, limit=20)
    ratings = EVAnalyticsService.get_customer_satisfaction_summary()
    return render_template("manufacturers.html", filter_opts=filter_opts, rankings=rankings, ratings=ratings)

@app.route("/battery-analysis")
def battery_analysis():
    """Battery technology adoption, driving range, and charging speed deep-dive."""
    battery_tech = EVAnalyticsService.get_battery_tech_distribution()
    return render_template("battery_analysis.html", battery_tech=battery_tech)

@app.route("/geography")
def geography():
    """Manufacturing-country distribution and global market regional insights."""
    country_data = EVAnalyticsService.get_manufacturing_country_distribution()
    return render_template("geography.html", country_data=country_data)

@app.route("/story")
def story():
    """5-Scene Market Analysis narrative with evidence-based insights."""
    return render_template("story.html")

@app.route("/methodology")
def methodology():
    """Data sources, cleaning methodology, formulas, and limitations."""
    return render_template("methodology.html")

@app.route("/about")
def about():
    """Project architecture, technology stack, and Skill Wallet documentation."""
    return render_template("about.html")

# --------------------------------------------------------------------
# REST API Endpoints for Dynamic AJAX Charts
# --------------------------------------------------------------------
@app.route("/api/kpis", methods=["GET"])
def api_kpis():
    """Returns updated KPI metrics based on filter selections."""
    year = request.args.get("year", type=int)
    manufacturer = request.args.get("manufacturer")
    category = request.args.get("category")
    kpis = EVAnalyticsService.get_executive_kpis(year=year, manufacturer=manufacturer, category=category)
    return jsonify(kpis)

@app.route("/api/sales-trend", methods=["GET"])
def api_sales_trend():
    """Returns annual sales trends and YoY growth."""
    manufacturer = request.args.get("manufacturer")
    category = request.args.get("category")
    trend = EVAnalyticsService.get_annual_sales_trend(manufacturer=manufacturer, category=category)
    return jsonify(trend)

@app.route("/api/manufacturer-ranking", methods=["GET"])
def api_manufacturer_ranking():
    """Returns manufacturer rankings for requested year."""
    year = request.args.get("year", default=2024, type=int)
    limit = request.args.get("limit", default=10, type=int)
    data = EVAnalyticsService.get_manufacturer_rankings(year=year, limit=limit)
    return jsonify(data)

@app.route("/api/category-breakdown", methods=["GET"])
def api_category_breakdown():
    """Returns category volume breakdown."""
    year = request.args.get("year", default=2024, type=int)
    data = EVAnalyticsService.get_category_sales_breakdown(year=year)
    return jsonify(data)

@app.route("/api/battery-tech", methods=["GET"])
def api_battery_tech():
    """Returns battery chemistry distribution."""
    data = EVAnalyticsService.get_battery_tech_distribution()
    return jsonify(data)

@app.route("/api/scatter-battery-range", methods=["GET"])
def api_scatter_battery_range():
    """Returns battery capacity vs driving range data points."""
    data = EVAnalyticsService.get_battery_vs_range_scatter()
    return jsonify(data)

@app.route("/api/geography-data", methods=["GET"])
def api_geography_data():
    """Returns manufacturing country metrics."""
    data = EVAnalyticsService.get_manufacturing_country_distribution()
    return jsonify(data)

@app.route("/api/customer-ratings", methods=["GET"])
def api_customer_ratings():
    """Returns customer rating benchmarks by manufacturer."""
    data = EVAnalyticsService.get_customer_satisfaction_summary()
    return jsonify(data)

@app.route("/api/vehicles", methods=["GET"])
def api_vehicles():
    """Returns filtered vehicle inventory list."""
    cat = request.args.get("category")
    mfg = request.args.get("manufacturer")
    min_range = request.args.get("min_range", type=float)
    vehicles = EVAnalyticsService.get_all_vehicles(category=cat, manufacturer=mfg, min_range=min_range)
    return jsonify(vehicles)

# --------------------------------------------------------------------
# Error Handlers
# --------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
