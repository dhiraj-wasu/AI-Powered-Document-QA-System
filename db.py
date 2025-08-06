from dotenv import load_dotenv
from os import getenv
from pgvector.peewee import VectorField
from peewee import PostgresqlDatabase, Model, TextField, ForeignKeyField

load_dotenv(override=True)

POSTGRES_DB_NAME = getenv("POSTGRES_DB_NAME")
POSTGRES_DB_USER = getenv("POSTGRES_DB_USER")
POSTGRES_DB_PASSWORD = getenv("POSTGRES_DB_PASSWORD") or None
POSTGRES_DB_HOST = getenv("POSTGRES_DB_HOST")
POSTGRES_DB_PORT = int(getenv("POSTGRES_DB_PORT", 5432))
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

print("📦 Connecting to DB with settings:")
print(f"  DB Name    : {POSTGRES_DB_NAME}")
print(f"  DB User    : {POSTGRES_DB_USER}")
print(f"  DB Host    : {POSTGRES_DB_HOST}")
print(f"  DB Port    : {POSTGRES_DB_PORT}")
print(f"  DB Password: {'(provided)' if POSTGRES_DB_PASSWORD else '(empty)'}")

if not all([POSTGRES_DB_NAME, POSTGRES_DB_USER, POSTGRES_DB_HOST, POSTGRES_DB_PORT]):
    raise ValueError("❌ Missing one or more PostgreSQL environment variables.")

db = PostgresqlDatabase(
    POSTGRES_DB_NAME,
    host=POSTGRES_DB_HOST,
    port=POSTGRES_DB_PORT,
    user=POSTGRES_DB_USER,
    password=POSTGRES_DB_PASSWORD,
)

class Documents(Model):
    name = TextField()
    class Meta:
        database = db
        db_table = 'documents'

class Tags(Model):
    name = TextField()
    class Meta:
        database = db
        db_table = 'tags'

class DocumentTags(Model):
    document_id = ForeignKeyField(Documents, backref="document_tags", on_delete='CASCADE')
    tag_id = ForeignKeyField(Tags, backref="document_tags", on_delete='CASCADE')
    class Meta:
        database = db
        db_table = 'document_tags'

class DocumentInformationChunks(Model):
    document_id = ForeignKeyField(Documents, backref="document_information_chunks", on_delete='CASCADE')
    chunk = TextField()
    embedding = VectorField(dimensions=1536)
    class Meta:
        database = db
        db_table = 'document_information_chunks'

def set_diskann_query_rescore(query_rescore: int):
    db.execute_sql("SET diskann.query_rescore = %s", (query_rescore,))

def set_openai_api_key():
    db.execute_sql(
        "SET ai.openai_api_key = %s;\n"
        "SELECT pg_catalog.current_setting('ai.openai_api_key', true) as api_key",
        (OPENAI_API_KEY,)
    )
