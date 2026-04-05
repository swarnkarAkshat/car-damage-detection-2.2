import sqlalchemy
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:@localhost/car_damage_db"

def run_migration():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Checking for image_data column in history table...")
        try:
            # 1. Check if column already exists
            result = connection.execute(text("SHOW COLUMNS FROM history LIKE 'image_data'"))
            if result.fetchone():
                print("✅ Column 'image_data' already exists.")
            else:
                # 2. Add column
                print("Adding 'image_data' column to 'history' table...")
                connection.execute(text("ALTER TABLE history ADD COLUMN image_data LONGTEXT AFTER explanation"))
                connection.commit()
                print("✅ Column 'image_data' added successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
