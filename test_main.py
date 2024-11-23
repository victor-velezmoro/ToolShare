import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base, User as DBUser, Item as DBItem, Category
from database import DATABASE_URL
import os


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

    
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

# @pytest.fixture(scope="module")
# def setup_database():
#     # Ensure we're using the test database
#     if "test" not in SQLALCHEMY_DATABASE_URL:
#         raise RuntimeError("Tests should not run on the production database!")

#     # Create the test database if it does not exist
#     engine = create_engine("postgresql://myuser:password@db:5432/postgres")
#     conn = engine.connect()
#     conn.execute("commit")  # We need to be outside a transaction to create databases.
#     result = conn.execute(
#         "SELECT 1 FROM pg_database WHERE datname = 'test_fastapi_database'"
#     )
#     if result.rowcount == 0:
#         conn.execute("CREATE DATABASE test_fastapi_database")
#     conn.close()

    # # Create the tables in the test database
    # engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Base.metadata.create_all(bind=engine)
    # yield  # Run the tests
    # # Drop the tables after tests complete
    # Base.metadata.drop_all(bind=engine)

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
    return data["access_token"]

def test_add_item(setup_database, db):
    # Obtain the token first
    token = test_login_user(setup_database)

    # Add the item
    response = client.post("/", json={
        "name": "Hammer",
        "description": "A useful tool",
        "price": 10.0,
        "category": "tools"
    }, headers={"Authorization": f"Bearer {token}"})

    # Assertions to validate the response
    assert response.status_code == 200
    data = response.json()

    # Ensure the item was added correctly
    assert "added" in data
    assert data["added"]["name"] == "Hammer"
    assert data["added"]["description"] == "A useful tool"
    assert data["added"]["price"] == 10.0
    assert data["added"]["category"] == "tools"



def test_get_item_by_id(setup_database):
    # Obtain the token first
    token = test_login_user(setup_database)

    # Retrieve item by ID
    response = client.get("/items/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Hammer"

def test_update_item(setup_database):
    # Obtain the token first
    token = test_login_user(setup_database)

    # Update the item
    response = client.put("/update/1", json={
        "name": "Hammer",
        "description": "A very useful tool",
        "price": 12.0,
        "category": "tools"
    }, headers={"Authorization": f"Bearer {token}"})

    # Assertions to validate the response
    assert response.status_code == 200
    data = response.json()
    assert data["updated"]["description"] == "A very useful tool"
    assert data["updated"]["price"] == 12.0

def test_delete_item(setup_database):
    # Obtain the token first
    token = test_login_user(setup_database)

    # Delete the item
    response = client.delete("/delete/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"]["name"] == "Hammer"
