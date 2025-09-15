import time
from db import db, Tags, Documents, DocumentTags, DocumentInformationChunks

# Retry connection until DB is ready
max_retries = 10
for i in range(max_retries):
    try:
        if db.is_closed():
            db.connect()
        break
    except Exception as e:
        print(f"⏳ Attempt {i+1}/{max_retries}: Waiting for database... Error: {e}")
        time.sleep(3)
else:
    raise Exception(" Database connection failed after multiple retries.")

# Reset DB schema
db.drop_tables([DocumentInformationChunks, DocumentTags, Documents, Tags], safe=True)
db.create_tables([Tags, Documents, DocumentTags, DocumentInformationChunks], safe=True)

print("✅ Tables dropped and recreated.")
