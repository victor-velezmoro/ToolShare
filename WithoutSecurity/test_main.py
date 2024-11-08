# test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from WithoutSecurity.main import app, get_db
from models import Base, User as DBUser, Item as DBItem, Category


#SQLALCHEMY_DATABASE_URL = "postgresql://myuser:password@localhost:5432/test_fastapi_database"
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:password@localhost:5432/test_fastapi_database"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the test client
client = TestClient(app)

# Setup and teardown for the test database
@pytest.fixture(scope="module")
def setup_database():
    # Ensure we're using the test database
    if "test" not in SQLALCHEMY_DATABASE_URL:
        raise RuntimeError("Tests should not run on the production database!")

    # Create the test tables
    Base.metadata.create_all(bind=engine)
    yield  # Run the tests
    # Drop the tables after tests complete
    Base.metadata.drop_all(bind=engine)

# Test functions using the setup_database fixture
def test_register_user(setup_database):
    response = client.post("/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login_user(setup_database):
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_add_item(setup_database):
    response = client.post("/", json={
        "name": "Hammer",
        "description": "A tool for hammering nails",
        "price": 10.0,
        "category": "tools"
    })
    assert response.status_code == 200
    assert response.json()["added"]["name"] == "Hammer"
    


def test_get_item_by_id(setup_database):
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Hammer"

def test_update_item(setup_database):
    response = client.put("/update/1", json={
        "name": "Updated Hammer",
        "description": "An updated tool for hammering nails",
        "price": 12.0,
        "category": "tools"
    })
    assert response.status_code == 200
    assert response.json()["updated"]["name"] == "Updated Hammer"

def test_delete_item(setup_database):
    response = client.delete("/delete/1")
    assert response.status_code == 200
    assert response.json()["deleted"]["name"] == "Updated Hammer"
