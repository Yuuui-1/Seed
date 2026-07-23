import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.agents.question_selector import load_questions

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

async def _register(client: AsyncClient, email: str) -> str:
    res = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "password123", "nickname": "用户"
    })
    return res.json()["data"]["access_token"]

_assessment_counter = 0

async def _complete_assessment(client: AsyncClient, token: str) -> int:
    global _assessment_counter
    _assessment_counter += 1
    aid = _assessment_counter
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/assessment/start", headers=headers)
    questions = load_questions()
    for i in range(10):
        await client.post(f"/api/v1/assessment/{aid}/answer", json={
            "question_id": questions[i]["id"], "answer_value": (i % 5) + 1
        }, headers=headers)
    return aid

@pytest.mark.asyncio
async def test_generate_report(client: AsyncClient):
    token = await _register(client, "r1@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "dimensions" in data["data"]
    assert len(data["data"]["dimensions"]) == 6

@pytest.mark.asyncio
async def test_get_report(client: AsyncClient):
    token = await _register(client, "r2@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    res = await client.get(f"/api/v1/reports/{aid}", headers=headers)
    assert res.status_code == 200
    assert "summary" in res.json()["data"]

@pytest.mark.asyncio
async def test_share_report(client: AsyncClient):
    token = await _register(client, "r3@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    res = await client.post(f"/api/v1/reports/{aid}/share", headers=headers)
    assert res.status_code == 200
    assert "share_url" in res.json()["data"]
    assert "token" in res.json()["data"]

@pytest.mark.asyncio
async def test_view_shared_report(client: AsyncClient):
    token = await _register(client, "r4@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    share = await client.post(f"/api/v1/reports/{aid}/share", headers=headers)
    share_token = share.json()["data"]["token"]
    res = await client.get(f"/api/v1/reports/shared/{share_token}")
    assert res.status_code == 200
    assert "dimensions" in res.json()["data"]

@pytest.mark.asyncio
async def test_list_reports(client: AsyncClient):
    token = await _register(client, "r5@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    res = await client.get("/api/v1/reports/", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["total"] >= 1
