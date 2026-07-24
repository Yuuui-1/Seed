import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from app.db.session import get_session
from app.core.deps import require_auth
from app.schemas.assessment import AnswerRequest
from app.services import assessment_service
from app.agents.orchestrator import OPTIONS, TOTAL_ROUNDS

router = APIRouter()

async def _start_stream(assessment_id: int, question: dict):
    yield {"event": "start", "data": json.dumps({"assessment_id": assessment_id, "total_rounds": TOTAL_ROUNDS})}
    await asyncio.sleep(0.05)
    yield {"event": "question", "data": json.dumps(question)}

@router.post("/start")
async def start_assessment(
    user_id: int = Depends(require_auth),
    db: AsyncSession = Depends(get_session),
):
    assessment, question = await assessment_service.start_assessment_flow(db, user_id, None)
    return EventSourceResponse(_start_stream(assessment.id, question))

@router.post("/{assessment_id}/answer")
async def submit_answer(
    assessment_id: int,
    req: AnswerRequest,
    user_id: int = Depends(require_auth),
    db: AsyncSession = Depends(get_session),
):
    assessment, result = await assessment_service.submit_answer(
        db, assessment_id, user_id, req.question_id, req.answer_value
    )
    if not assessment:
        raise HTTPException(404, detail={"code": 1003, "msg": "测评不存在"})

    async def stream():
        yield {"event": "answered", "data": json.dumps({"round": assessment.current_round})}
        await asyncio.sleep(0.05)
        if result is None:
            yield {"event": "error", "data": json.dumps({"msg": "题目不存在或测评已完成"})}
            return
        if result["type"] == "complete":
            yield {"event": "complete", "data": json.dumps({"assessment_id": assessment_id})}
            return
        if "preview" in result:
            yield {"event": "preview", "data": json.dumps(result["preview"])}
            await asyncio.sleep(0.05)
        yield {"event": "question", "data": json.dumps({
            "question_id": result["question_id"],
            "round": result["round"],
            "agent_message": result["agent_message"],
            "question_text": result["question_text"],
            "options": OPTIONS,
            "target_dimension": result["target_dimension"],
        })}

    return EventSourceResponse(stream())

@router.get("/{assessment_id}/progress")
async def get_progress(
    assessment_id: int,
    user_id: int = Depends(require_auth),
    db: AsyncSession = Depends(get_session),
):
    assessment = await assessment_service.get_owned_assessment(db, assessment_id, user_id)
    if not assessment:
        raise HTTPException(404, detail={"code": 1003, "msg": "测评不存在"})
    return {"code": 0, "data": {
        "assessment_id": assessment.id,
        "status": assessment.status,
        "current_round": assessment.current_round,
        "total_rounds": assessment.total_rounds,
    }, "msg": "success"}

@router.post("/{assessment_id}/bind")
async def bind_assessment(assessment_id: int, user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    ok = await assessment_service.bind_assessment(db, assessment_id, user_id)
    if not ok:
        raise HTTPException(404, detail={"code": 1003, "msg": "测评不存在或已绑定"})
    return {"code": 0, "data": {"bound": True}, "msg": "success"}
