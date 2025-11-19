# Configuration settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Turso Database Configuration
    TURSO_DATABASE_URL: str = os.getenv("TURSO_DATABASE_URL", "libsql://localhost:8080")
    TURSO_AUTH_TOKEN: str = os.getenv("TURSO_AUTH_TOKEN", "")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Development mode
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Create a global instance of settings
settings = Settings()