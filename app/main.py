# Main application entry point
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from app.config import settings
from app.db import get_db, db
from app.models import User, UserCreate, UserUpdate

# Create FastAPI application instance
app = FastAPI(
    title="User Management API",
    description="A FastAPI application with Turso database integration for user management",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    try:
        print("🚀 Starting up User Management API...")
        print("📡 Connecting to database...")
        # Database initialization is already done in db.py
        print("✅ Database connected and tables ready!")
        print("🎯 Ready to handle requests!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint - returns a welcome message"""
    return {
        "message": "Welcome to your User Management API!",
        "version": "1.0.0",
        "database_status": "connected",
        "endpoints": {
            "users": "/users/",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute_query("SELECT 1")
        return {
            "status": "healthy", 
            "database_connected": True,
            "database_type": "SQLite (local)"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database_connected": False,
            "error": str(e)
        }

@app.get("/config")
async def get_config():
    """Display current configuration (excluding sensitive data)"""
    return {
        "port": settings.PORT,
        "host": settings.HOST,
        "debug": settings.DEBUG,
        "database_configured": bool(settings.TURSO_DATABASE_URL),
        "database_url_type": "Turso libSQL (when available)" if settings.TURSO_DATABASE_URL.startswith("libsql://") else "Local SQLite"
    }

# User CRUD Endpoints
@app.get("/users/", response_model=List[User])
async def get_users(limit: int = 10, offset: int = 0):
    """Get all users with pagination"""
    try:
        query = "SELECT id, name, email, phone FROM users LIMIT ? OFFSET ?"
        results = db.execute_query(query, (limit, offset))
        
        users = []
        for row in results:
            user_dict = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3]
            }
            users.append(user_dict)
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID"""
    try:
        query = "SELECT id, name, email, phone FROM users WHERE id = ?"
        results = db.execute_query(query, (user_id,))
        
        if not results:
            raise HTTPException(status_code=404, detail="User not found")
        
        row = results[0]
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        # Check if email already exists
        existing = db.execute_query("SELECT id FROM users WHERE email = ?", (user.email,))
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        query = "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)"
        user_id = db.execute_non_query(query, (user.name, user.email, user.phone))
        
        return {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate):
    """Update an existing user"""
    try:
        # Check if user exists
        existing = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if user_update.name is not None:
            update_fields.append("name = ?")
            params.append(user_update.name)
        
        if user_update.email is not None:
            # Check if email is taken by another user
            email_check = db.execute_query("SELECT id FROM users WHERE email = ? AND id != ?", (user_update.email, user_id))
            if email_check:
                raise HTTPException(status_code=400, detail="Email already exists")
            
            update_fields.append("email = ?")
            params.append(user_update.email)
        
        if user_update.phone is not None:
            update_fields.append("phone = ?")
            params.append(user_update.phone)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        db.execute_non_query(query, tuple(params))
        
        # Return updated user
        updated = db.execute_query("SELECT id, name, email, phone FROM users WHERE id = ?", (user_id,))[0]
        return {
            "id": updated[0],
            "name": updated[1],
            "email": updated[2],
            "phone": updated[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user"""
    try:
        # Check if user exists
        existing = db.execute_query("SELECT id FROM users WHERE id = ?", (user_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = "DELETE FROM users WHERE id = ?"
        db.execute_non_query(query, (user_id,))
        
        return {"message": f"User with ID {user_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@app.get("/users/search")
async def search_users(query: str):
    """Search users by name or email"""
    try:
        search_query = """
        SELECT id, name, email, phone FROM users 
        WHERE name LIKE ? OR email LIKE ?
        LIMIT 20
        """
        search_term = f"%{query}%"
        results = db.execute_query(search_query, (search_term, search_term))
        
        users = []
        for row in results:
            user_dict = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3]
            }
            users.append(user_dict)
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching users: {str(e)}")