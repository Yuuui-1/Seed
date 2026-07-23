import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.session import get_session
from app.main import app

TEST_DB = "sqlite+aiosqlite:///:memory:"
_engine = None

async def _get_test_session():
    global _engine
    if _engine is None:
        _engine = create_async_engine(TEST_DB, echo=False)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    global _engine
    if _engine is None:
        _engine = create_async_engine(TEST_DB, echo=False)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com", "password": "password123", "nickname": "测试用户"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com", "password": "password123", "nickname": "测试"
    })
    res = await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com", "password": "password123", "nickname": "测试2"
    })
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com", "password": "password123", "nickname": "用户"
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com", "password": "password123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com", "password": "password123", "nickname": "用户"
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com", "password": "wrongpassword"
    })
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_me_with_token(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@example.com", "password": "password123", "nickname": "用户"
    })
    token = reg.json()["data"]["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "me@example.com"

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refresh@example.com", "password": "password123", "nickname": "用户"
    })
    refresh_token = reg.json()["data"]["refresh_token"]
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()["data"]
