import sqlalchemy
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:@localhost/car_damage_db"

def run_migration():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Checking for damage_percentage column in history table...")
        try:
            # 1. Check if column already exists
            result = connection.execute(text("SHOW COLUMNS FROM history LIKE 'damage_percentage'"))
            if result.fetchone():
                print("✅ Column 'damage_percentage' already exists.")
            else:
                # 2. Add column
                print("Adding 'damage_percentage' column to 'history' table...")
                connection.execute(text("ALTER TABLE history ADD COLUMN damage_percentage INT AFTER confidence"))
                connection.commit()
                print("✅ Column 'damage_percentage' added successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
