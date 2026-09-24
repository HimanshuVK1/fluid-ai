import os
import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import pymysql

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="FastAPI MySQL Backend")

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")
DB_NAME = os.getenv("DB_NAME", "sampledb")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.on_event("startup")
def startup_event():
    """Initializes the database schema on startup."""
    logger.info("Initializing database schema...")
    try:
        # First, establish a connection to create database if not exists
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
        conn.close()

        # Now connect to the database and create the table
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guestbook (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

class NamePayload(BaseModel):
    name: str

@app.get("/health")
def health_check():
    """Verifies database connectivity."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

@app.post("/name", status_code=status.HTTP_201_CREATED)
def add_name(payload: NamePayload):
    """Inserts a new name entry into the database."""
    name = payload.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO guestbook (name) VALUES (%s)", (name,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Name '{name}' added successfully!"}
    except Exception as e:
        logger.error(f"Failed to add name: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/names")
def get_names():
    """Retrieves all name entries from the database."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, created_at FROM guestbook ORDER BY id ASC")
            rows = cursor.fetchall()
        conn.close()
        # Standardize datetime objects to strings for clean JSON serialization
        for row in rows:
            if "created_at" in row and row["created_at"] is not None:
                row["created_at"] = row["created_at"].isoformat()
        return rows
    except Exception as e:
        logger.error(f"Failed to retrieve names: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
