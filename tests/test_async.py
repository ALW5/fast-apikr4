import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app import app

fake = Faker()

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
def fake_user_data():
    return {
        "username": fake.user_name(),
        "age": fake.random_int(min=18, max=99)
    }

@pytest.mark.asyncio
async def test_async_create_user(async_client, fake_user_data):
    response = await async_client.post("/users", json=fake_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == fake_user_data["username"]
    assert data["age"] == fake_user_data["age"]
    assert "id" in data

@pytest.mark.asyncio
async def test_async_create_user_edge_age(async_client):
    response = await async_client.post("/users", json={"username": "olduser", "age": 120})
    assert response.status_code == 201
    data = response.json()
    assert data["age"] == 120

@pytest.mark.asyncio
async def test_async_get_user_success(async_client, fake_user_data):
    create_resp = await async_client.post("/users", json=fake_user_data)
    user_id = create_resp.json()["id"]
    
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == fake_user_data["username"]
    assert data["age"] == fake_user_data["age"]

@pytest.mark.asyncio
async def test_async_get_user_not_found(async_client):
    response = await async_client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_async_delete_user_success(async_client, fake_user_data):
    create_resp = await async_client.post("/users", json=fake_user_data)
    user_id = create_resp.json()["id"]
    
    delete_resp = await async_client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 204
    
    get_resp = await async_client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_async_delete_user_not_found(async_client):
    response = await async_client.delete("/users/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_async_delete_twice(async_client, fake_user_data):
    create_resp = await async_client.post("/users", json=fake_user_data)
    user_id = create_resp.json()["id"]
    
    first_delete = await async_client.delete(f"/users/{user_id}")
    assert first_delete.status_code == 204
    
    second_delete = await async_client.delete(f"/users/{user_id}")
    assert second_delete.status_code == 404