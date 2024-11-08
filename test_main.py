import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base, User as DBUser, Item as DBItem, Category
from database import DATABASE_URL

# Use the existing database for testing
SQLALCHEMY_DATABASE_URL = DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the existing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    # Create the database schema
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database schema
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_register_user(setup_database, db):
    response = client.post("/register", json={
        "username": "usertest",
        "email": "usertest@example.com",
        "full_name": "User Test",
        "password": "password123"
    })
    print(response.json()) 
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "usertest"
    assert data["email"] == "usertest@example.com"

def test_login_user(setup_database):
    response = client.post("/token", data={
        "username": "usertest",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_add_item(setup_database, db):
    token = test_login_user(setup_database)
    response = client.post("/", json={
        "name": "Hammer",
        "description": "A useful tool",
        "price": 10.0,
        "category": "TOOLS"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["added"]["name"] == "Hammer"
    assert data["added"]["description"] == "A useful tool"
    assert data["added"]["price"] == 10.0
    assert data["added"]["category"] == "TOOLS"

# def test_get_items(setup_database):
#     response = client.get("/")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data["items"]) > 0

# def test_get_item_by_id(setup_database):
#     response = client.get("/items/1")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Hammer"

# def test_update_item(setup_database):
#     token = test_login_user(setup_database)
#     response = client.put("/update/1", json={
#         "name": "Hammer",
#         "description": "A very useful tool",
#         "price": 12.0,
#         "category": "TOOLS"
#     }, headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["updated"]["description"] == "A very useful tool"
#     assert data["updated"]["price"] == 12.0

# def test_delete_item(setup_database):
#     token = test_login_user(setup_database)
#     response = client.delete("/delete/1", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["deleted"]["name"] == "Hammer"