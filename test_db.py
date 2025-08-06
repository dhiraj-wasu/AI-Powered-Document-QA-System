from db import db

try:
    db.connect()
    print("✅ Connected to database successfully.")
except Exception as e:
    print("❌ Failed to connect:", e)
finally:
    if not db.is_closed():
        db.close()
