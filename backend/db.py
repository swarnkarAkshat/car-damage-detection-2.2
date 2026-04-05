import mysql.connector
import os
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Database Connection Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""), 
    "database": os.getenv("DB_NAME", "car_damage_db")
}

def get_db_connection():
    """Returns a direct MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to MySQL server. Ensure MySQL is running.")
        return
        
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        prediction VARCHAR(100),
        confidence FLOAT,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL Tables checked/created successfully.")

if __name__ == "__main__":
    init_db()
