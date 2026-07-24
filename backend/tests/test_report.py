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

async def _complete_assessment(client: AsyncClient, token: str) -> int:
    aid = await _start_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    questions = load_questions()
    for i in range(10):
        response = await client.post(f"/api/v1/assessment/{aid}/answer", json={
            "question_id": questions[i]["id"], "answer_value": (i % 5) + 1
        }, headers=headers)
        assert response.status_code == 200
    return aid

@pytest.mark.asyncio(loop_scope="module")
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

@pytest.mark.asyncio(loop_scope="module")
async def test_get_report(client: AsyncClient):
    token = await _register(client, "r2@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    generated = await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    report_id = generated.json()["data"]["id"]
    res = await client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert res.status_code == 200
    assert "summary" in res.json()["data"]

@pytest.mark.asyncio(loop_scope="module")
async def test_share_report(client: AsyncClient):
    token = await _register(client, "r3@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    generated = await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    report_id = generated.json()["data"]["id"]
    res = await client.post(f"/api/v1/reports/{report_id}/share", headers=headers)
    assert res.status_code == 200
    assert "share_url" in res.json()["data"]
    assert "token" in res.json()["data"]

@pytest.mark.asyncio(loop_scope="module")
async def test_view_shared_report(client: AsyncClient):
    token = await _register(client, "r4@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    generated = await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    report_id = generated.json()["data"]["id"]
    share = await client.post(f"/api/v1/reports/{report_id}/share", headers=headers)
    share_token = share.json()["data"]["token"]
    res = await client.get(f"/api/v1/reports/shared/{share_token}")
    assert res.status_code == 200
    assert "dimensions" in res.json()["data"]

@pytest.mark.asyncio(loop_scope="module")
async def test_list_reports(client: AsyncClient):
    token = await _register(client, "r5@test.com")
    aid = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/api/v1/reports/generate/{aid}", headers=headers)
    res = await client.get("/api/v1/reports/", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["total"] >= 1

@pytest.mark.asyncio(loop_scope="module")
async def test_cannot_generate_report_for_incomplete_assessment(client: AsyncClient):
    token = await _register(client, "incomplete@test.com")
    assessment_id = await _start_assessment(client, token)

    response = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409

@pytest.mark.asyncio(loop_scope="module")
async def test_user_cannot_generate_another_users_report(client: AsyncClient):
    owner = await _register(client, "report-owner@test.com")
    stranger = await _register(client, "report-stranger@test.com")
    assessment_id = await _complete_assessment(client, owner)

    response = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {stranger}"},
    )

    assert response.status_code == 404

@pytest.mark.asyncio(loop_scope="module")
async def test_report_generation_is_idempotent(client: AsyncClient):
    token = await _register(client, "idempotent@test.com")
    assessment_id = await _complete_assessment(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(f"/api/v1/reports/generate/{assessment_id}", headers=headers)
    second = await client.post(f"/api/v1/reports/generate/{assessment_id}", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["id"] == second.json()["data"]["id"]

@pytest.mark.asyncio(loop_scope="module")
async def test_report_detail_uses_report_id_not_assessment_id(client: AsyncClient):
    token = await _register(client, "distinct-ids@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await _start_assessment(client, token)
    await _start_assessment(client, token)
    assessment_id = await _complete_assessment(client, token)

    generated = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers=headers,
    )
    report_id = generated.json()["data"]["id"]

    assert report_id != assessment_id
    detail = await client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["assessment_id"] == assessment_id
