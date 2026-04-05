"""Direct register test bypassing HTTP to see exact error."""
import sys
sys.path.insert(0, r'c:\Users\91798\Desktop\saved_model\backend')

from database import SessionLocal
import models as db_models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

try:
    existing = db.query(db_models.User).filter(
        (db_models.User.email == "debug_test@test.com") |
        (db_models.User.username == "debug_test")
    ).first()
    if existing:
        print(f"User already exists: id={existing.id} username={existing.username}")
        # Test verify
        ok = pwd_context.verify("debug1234", existing.hashed_password)
        print(f"Password verify with bcrypt: {ok}")
        # Show hash
        print(f"Stored hash: {existing.hashed_password[:30]}...")
    else:
        new_user = db_models.User(
            username="debug_test",
            email="debug_test@test.com",
            name="debug_test",
            hashed_password=pwd_context.hash("debug1234"),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Created user: id={new_user.id}")
        
        # Now test login query
        found = db.query(db_models.User).filter(
            (db_models.User.email == "debug_test") |
            (db_models.User.username == "debug_test")
        ).first()
        if found:
            ok = pwd_context.verify("debug1234", found.hashed_password)
            print(f"Login test passed: {ok}")
        else:
            print("ERROR: Could not find just-created user")
except Exception as e:
    import traceback
    print("EXCEPTION:")
    traceback.print_exc()
finally:
    db.close()
