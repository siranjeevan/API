# Database configuration and connection
import sqlite3
from contextlib import contextmanager
from app.config import settings

# Database schema
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

class Database:
    """Database connection manager"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            # For Turso libsql connection, we would use:
            # conn = sqlite3.connect(self.db_url)
            # But since libsql-python is not available, we'll use a local SQLite file
            # This will be replaced with Turso connection when available
            
            # Use local SQLite for now (can be replaced with Turso libsql)
            local_db_path = "app.db"  # Local SQLite file
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(CREATE_USERS_TABLE)
                conn.commit()
                print("✅ Users table created or already exists")
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        try:
            # For now, use local SQLite
            # When libsql-python is available, replace with:
            # conn = sqlite3.connect(self.db_url)
            conn = sqlite3.connect("app.db")
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_non_query(self, query: str, params: tuple = None):
        """Execute a query that doesn't return results (INSERT, UPDATE, DELETE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid

# Create database instance
db = Database(settings.TURSO_DATABASE_URL)

def get_db():
    """Dependency to get database connection"""
    return db