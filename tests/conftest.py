import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Use a dedicated test database and reset it for each test session
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")
Path("test.db").unlink(missing_ok=True)

# Provide a TestClient that ensures FastAPI startup/shutdown events run
@pytest.fixture(scope="session")
def client():
	from app.main import app
	with TestClient(app) as c:
		yield c
