import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_user_success():
    response = client.post("/users", json={"username": "testuser", "age": 25})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["age"] == 25
    assert "id" in data

def test_create_user_invalid_data():
    response = client.post("/users", json={"username": "", "age": -5})
    assert response.status_code == 422

def test_get_user_success():
    create_resp = client.post("/users", json={"username": "john", "age": 30})
    user_id = create_resp.json()["id"]
    
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "john"
    assert data["age"] == 30

def test_get_user_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_delete_user_success():
    create_resp = client.post("/users", json={"username": "delete_me", "age": 20})
    user_id = create_resp.json()["id"]
    
    delete_resp = client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 204
    
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404

def test_delete_user_not_found():
    response = client.delete("/users/99999")
    assert response.status_code == 404

def test_custom_exception_a():
    response = client.get("/trigger-a?raise_error=true")
    assert response.status_code == 400
    assert response.json()["error_code"] == "CUSTOM_A"

def test_custom_exception_b():
    response = client.get("/trigger-b/999")
    assert response.status_code == 404
    assert response.json()["error_code"] == "CUSTOM_B"

def test_user_validation_success():
    response = client.post("/users/validate", json={
        "username": "validuser",
        "age": 25,
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "validuser"

def test_user_validation_fail_age():
    response = client.post("/users/validate", json={
        "username": "younguser",
        "age": 16,
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 422