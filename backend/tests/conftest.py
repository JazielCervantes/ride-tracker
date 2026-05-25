import os

# Set required env vars before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ride_tracker.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Speed up bcrypt for tests (4 rounds instead of 12)
from app.utils import security as security_module
security_module.pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4
)

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ride_tracker.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    user = User(username="testuser", password_hash=get_password_hash("TestPass123!"))
    db.add(user)
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
