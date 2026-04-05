import pymysql
from database import SQLALCHEMY_DATABASE_URL

# Parse the URL (mysql+pymysql://root:@localhost/car_damage_db)
# Rough parsing for this specific script
conn_str = SQLALCHEMY_DATABASE_URL.replace("mysql+pymysql://", "")
user_pass, host_db = conn_str.split("@")
user, password = (user_pass.split(":") + [""])[:2]
host, db = host_db.split("/")

print(f"Connecting to {host}/{db} as {user}...")

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db
    )
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("SHOW COLUMNS FROM history LIKE 'report_path'")
        result = cursor.fetchone()
        if not result:
            print("Adding report_path column to history table...")
            cursor.execute("ALTER TABLE history ADD COLUMN report_path VARCHAR(255) NULL AFTER explanation")
            connection.commit()
            print("Column added successfully!")
        else:
            print("Column report_path already exists.")
    connection.close()
except Exception as e:
    print(f"Error: {e}")
