"""
Database Connection and Session Management Module.
Supports MySQL 8 and SQLite seamlessly via SQLAlchemy 2.0.
"""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    """Manages database connection pool, query execution, and session lifecycle."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        """Initializes SQLAlchemy Engine with fallbacks."""
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        self.is_sqlite = db_uri.startswith("sqlite")

        try:
            if self.is_sqlite:
                # SQLite configuration
                self.engine = create_engine(
                    db_uri,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
                logger.info(f"Connected to SQLite database: {db_uri}")
            else:
                # MySQL configuration
                self.engine = create_engine(
                    db_uri,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_size=10,
                    max_overflow=20,
                    echo=False
                )
                # Test connectivity
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info(f"Connected to MySQL database at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
        except Exception as e:
            logger.warning(f"Could not connect using primary URI ({db_uri}): {e}")
            logger.info("Falling back to local SQLite engine (database/ev_market_db.sqlite)...")
            Config.SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
            fallback_uri = f"sqlite:///{Config.SQLITE_PATH.as_posix()}"
            self.engine = create_engine(
                fallback_uri,
                connect_args={"check_same_thread": False},
                echo=False
            )
            self.is_sqlite = True
            logger.info(f"Fallback SQLite database initialized: {fallback_uri}")

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_engine(self):
        """Returns active SQLAlchemy engine."""
        return self.engine

    @contextmanager
    def get_connection(self):
        """Context manager providing a safe raw DB connection."""
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self, query_str: str, params: dict = None):
        """Executes a parameterized SQL query safely."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query_str), params or {})
            if result.returns_rows:
                return result.fetchall()
            conn.commit()
            return None

    def query_to_dataframe(self, query_str: str, params: dict = None):
        """Executes a SQL query and returns results directly as a Pandas DataFrame."""
        import pandas as pd
        with self.engine.connect() as conn:
            return pd.read_sql_query(text(query_str), conn, params=params or {})

# Global singleton
db_manager = DatabaseManager()

def get_db():
    """Provides a transactional database session."""
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()
