from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql

# Database configuration for XAMPP MySQL
# root is the default user, no password by default
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/car_damage_db"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Error connecting to MySQL database: {e}")
    raise e

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- DATABASE CONNECTION TEST ---
# Run this file directly (python database.py) to verify your XAMPP setup
if __name__ == "__main__":
    import sqlalchemy
    print(f"Testing connection to: {SQLALCHEMY_DATABASE_URL}")
    try:
        with engine.connect() as connection:
            print("✅ Database connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTIP: Ensure MySQL is 'Running' in your XAMPP Control Panel.")
        print("TIP: If your MySQL uses port 3307, change localhost to localhost:3307 in the URL above.")
