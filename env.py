from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)


# ✅ CORRECT
POSTGRES_DB_NAME = "backend"
POSTGRES_DB_USER = "postgres"
POSTGRES_DB_PASSWORD = "admin"
POSTGRES_DB_HOST = "localhost"
POSTGRES_DB_PORT = 5432  # this one is okay as integer


OPENAI_API_KEY="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"