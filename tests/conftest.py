import os

# Use a dedicated test database
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")

# Ensure models are imported so Base.metadata is populated
from app import models  # noqa: F401,E402
from app.db.database import Base, engine  # noqa: E402

# Create tables before tests
Base.metadata.create_all(bind=engine)
