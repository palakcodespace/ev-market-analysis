"""
Configuration Module for Electric Vehicle Market Analysis and Intelligence System.
Supports MySQL 8 with automatic SQLite fallback for zero-dependency execution.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base Configuration Class."""
    SECRET_KEY = os.getenv("SECRET_KEY", "ev-market-intelligence-secret-key-2026")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))

    # MySQL Database Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ev_market_db")

    # SQLite Database File Path
    SQLITE_PATH = BASE_DIR / "database" / "ev_market_db.sqlite"

    # Database URL determination:
    # 1. Custom DATABASE_URL if explicitly supplied
    # 2. Or MySQL URI if MYSQL_PASSWORD / explicit flag is configured
    # 3. Default fallback to local SQLite for smooth standalone execution
    CUSTOM_DB_URL = os.getenv("DATABASE_URL")
    if CUSTOM_DB_URL:
        SQLALCHEMY_DATABASE_URI = CUSTOM_DB_URL
    elif os.getenv("USE_MYSQL", "False").lower() in ("true", "1", "yes"):
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
    else:
        # Check if MySQL is requested or fallback to SQLite
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tableau Integration URLs (Tableau Public / Tableau Cloud)
    TABLEAU_DASHBOARD_URL = os.getenv(
        "TABLEAU_DASHBOARD_URL",
        ""
    )
    TABLEAU_STORY_URL = os.getenv(
        "TABLEAU_STORY_URL",
        ""
    )

    # Data file paths
    RAW_DATA_DIR = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
    SQL_DIR = BASE_DIR / "sql"
