import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

from ..dependencies.auth_dependency import verify_active_user

from .. import schemas

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def override_verify_active_user():
    mock_user = schemas.User(
        id=999,
        email="test-auth-user@example.com",
        is_active=True,
        items=[]
    )
    return mock_user


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    # テストに、dbセッションが必要なため追加
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    app.dependency_overrides[verify_active_user] = override_verify_active_user
    client = TestClient(app)
    return client
