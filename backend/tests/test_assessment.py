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

@pytest.mark.asyncio
async def test_start_assessment_anonymous(client: AsyncClient):
    res = await client.post("/api/v1/assessment/start")
    assert res.status_code == 200
    assert "text/event-stream" in res.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_assessment_full_flow(client: AsyncClient):
    token = await _register(client, "a@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    start = await client.post("/api/v1/assessment/start", headers=headers)
    assert start.status_code == 200

    questions = load_questions()
    for i in range(10):
        q = questions[i]
        res = await client.post("/api/v1/assessment/1/answer", json={
            "question_id": q["id"], "answer_value": 4
        }, headers=headers)
        assert res.status_code == 200

    prog = await client.get("/api/v1/assessment/1/progress", headers=headers)
    assert prog.json()["data"]["status"] == "completed"

@pytest.mark.asyncio
async def test_first_question_is_q001(client: AsyncClient):
    token = await _register(client, "e@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/assessment/start", headers=headers)

    questions = load_questions()
    res = await client.post("/api/v1/assessment/1/answer", json={
        "question_id": questions[0]["id"], "answer_value": 3
    }, headers=headers)
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_preview_after_3rd_answer(client: AsyncClient):
    token = await _register(client, "f@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/assessment/start", headers=headers)

    questions = load_questions()
    # Answer first 3 questions
    for i in range(3):
        res = await client.post("/api/v1/assessment/1/answer", json={
            "question_id": questions[i]["id"], "answer_value": 4
        }, headers=headers)
        assert res.status_code == 200
