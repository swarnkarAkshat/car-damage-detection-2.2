from database import engine
from sqlalchemy import inspect
import sys

inspector = inspect(engine)
tables = inspector.get_table_names()
output = []
for t in tables:
    output.append(f"=== {t} ===")
    for c in inspector.get_columns(t):
        output.append(f"  {c['name']}  TYPE={c['type']}  nullable={c['nullable']}")

result = "\n".join(output)
print(result)
with open("_schema_output.txt", "w") as f:
    f.write(result)
print("\nSaved to _schema_output.txt")
