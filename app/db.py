# Database configuration and connection
import libsql_client
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
    """Turso Database connection manager"""
    
    def __init__(self, db_url: str, auth_token: str):
        self.client = libsql_client.create_client(
            url=db_url,
            auth_token=auth_token
        )
    
    async def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            await self.client.execute(CREATE_USERS_TABLE)
            print("✅ Users table created or already exists in Turso")
        except Exception as e:
            print(f"❌ Error initializing Turso database: {e}")
            raise
    
    async def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        try:
            if params:
                result = await self.client.execute(query, list(params))
            else:
                result = await self.client.execute(query)
            return result.rows
        except Exception as e:
            print(f"Query error: {e}")
            raise
    
    async def execute_non_query(self, query: str, params: tuple = None):
        """Execute a query that doesn't return results (INSERT, UPDATE, DELETE)"""
        try:
            if params:
                result = await self.client.execute(query, list(params))
            else:
                result = await self.client.execute(query)
            return result.last_insert_rowid
        except Exception as e:
            print(f"Non-query error: {e}")
            raise

# Create database instance
db = Database(settings.TURSO_DATABASE_URL, settings.TURSO_AUTH_TOKEN)

def get_db():
    """Dependency to get database connection"""
    return db