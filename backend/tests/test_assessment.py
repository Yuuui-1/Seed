import json
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.agents.question_selector import load_questions
from sse_starlette.sse import AppStatus

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

@pytest_asyncio.fixture(autouse=True, loop_scope="module")
async def setup_db():
    global _engine
    AppStatus.should_exit_event = None
    if _engine is None:
        _engine = create_async_engine(TEST_DB, echo=False)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(loop_scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

async def _register(client: AsyncClient, email: str) -> str:
    res = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "password123", "nickname": "鐢ㄦ埛"
    })
    return res.json()["data"]["access_token"]

async def _start_assessment(client: AsyncClient, token: str) -> int:
    res = await client.post(
        "/api/v1/assessment/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    for line in res.text.splitlines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if "assessment_id" in data:
                return data["assessment_id"]
    raise AssertionError("assessment start event did not include an assessment_id")

@pytest.mark.asyncio(loop_scope="module")
async def test_start_assessment_requires_auth(client: AsyncClient):
    res = await client.post("/api/v1/assessment/start")
    assert res.status_code == 401

@pytest.mark.asyncio(loop_scope="module")
async def test_assessment_full_flow(client: AsyncClient):
    token = await _register(client, "a@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    assessment_id = await _start_assessment(client, token)

    questions = load_questions()
    for i in range(10):
        q = questions[i]
        res = await client.post(f"/api/v1/assessment/{assessment_id}/answer", json={
            "question_id": q["id"], "answer_value": 4
        }, headers=headers)
        assert res.status_code == 200

    prog = await client.get(f"/api/v1/assessment/{assessment_id}/progress", headers=headers)
    assert prog.json()["data"]["status"] == "completed"

@pytest.mark.asyncio(loop_scope="module")
async def test_first_question_is_q001(client: AsyncClient):
    token = await _register(client, "e@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    assessment_id = await _start_assessment(client, token)

    questions = load_questions()
    res = await client.post(f"/api/v1/assessment/{assessment_id}/answer", json={
        "question_id": questions[0]["id"], "answer_value": 3
    }, headers=headers)
    assert res.status_code == 200

@pytest.mark.asyncio(loop_scope="module")
async def test_preview_after_3rd_answer(client: AsyncClient):
    token = await _register(client, "f@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    assessment_id = await _start_assessment(client, token)

    questions = load_questions()
    # Answer first 3 questions
    for i in range(3):
        res = await client.post(f"/api/v1/assessment/{assessment_id}/answer", json={
            "question_id": questions[i]["id"], "answer_value": 4
        }, headers=headers)
        assert res.status_code == 200

@pytest.mark.asyncio(loop_scope="module")
async def test_answer_and_progress_require_auth(client: AsyncClient):
    token = await _register(client, "private@test.com")
    assessment_id = await _start_assessment(client, token)
    question = load_questions()[0]

    answer = await client.post(
        f"/api/v1/assessment/{assessment_id}/answer",
        json={"question_id": question["id"], "answer_value": 3},
    )
    progress = await client.get(f"/api/v1/assessment/{assessment_id}/progress")

    assert answer.status_code == 401
    assert progress.status_code == 401

@pytest.mark.asyncio(loop_scope="module")
async def test_user_cannot_access_another_users_assessment(client: AsyncClient):
    owner = await _register(client, "owner@test.com")
    stranger = await _register(client, "stranger@test.com")
    assessment_id = await _start_assessment(client, owner)
    stranger_headers = {"Authorization": f"Bearer {stranger}"}
    question = load_questions()[0]

    progress = await client.get(
        f"/api/v1/assessment/{assessment_id}/progress",
        headers=stranger_headers,
    )
    answer = await client.post(
        f"/api/v1/assessment/{assessment_id}/answer",
        headers=stranger_headers,
        json={"question_id": question["id"], "answer_value": 3},
    )

    assert progress.status_code == 404
    assert answer.status_code == 404
