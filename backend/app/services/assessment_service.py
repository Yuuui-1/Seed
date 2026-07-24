from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.assessment import Assessment, AssessmentAnswer
from app.models.report import Report
from app.agents.orchestrator import get_first_question, get_next_question, generate_report
from app.agents.question_selector import TOTAL_ROUNDS

PREVIEW_MARKER = 3

class AssessmentNotFoundError(Exception):
    """The assessment does not exist or is not owned by the current user."""


class AssessmentNotCompletedError(Exception):
    """The assessment exists but is not ready for report generation."""


async def create_assessment(db: AsyncSession, user_id: int | None, session_id: str | None) -> Assessment:
    assessment = Assessment(
        user_id=user_id,
        session_id=session_id,
        status="in_progress",
        total_rounds=TOTAL_ROUNDS,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment

async def get_assessment(db: AsyncSession, assessment_id: int) -> Assessment | None:
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    return result.scalar_one_or_none()

async def get_owned_assessment(
    db: AsyncSession, assessment_id: int, user_id: int
) -> Assessment | None:
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()

async def get_assessment_answers(db: AsyncSession, assessment_id: int) -> list[AssessmentAnswer]:
    result = await db.execute(
        select(AssessmentAnswer)
        .where(AssessmentAnswer.assessment_id == assessment_id)
        .order_by(AssessmentAnswer.round_number)
    )
    return list(result.scalars().all())

async def start_assessment_flow(db: AsyncSession, user_id: int | None, session_id: str | None) -> tuple[Assessment, dict]:
    assessment = await create_assessment(db, user_id, session_id)
    question = await get_first_question()
    return assessment, question

async def submit_answer(
    db: AsyncSession,
    assessment_id: int,
    user_id: int,
    question_id: str,
    answer_value: int,
) -> tuple[Assessment, dict | None]:
    assessment = await get_owned_assessment(db, assessment_id, user_id)
    if not assessment or assessment.status != "in_progress":
        return assessment, None

    from app.agents.question_selector import load_questions
    questions = load_questions()
    q = next((q for q in questions if q["id"] == question_id), None)
    if not q:
        return assessment, None

    next_round = assessment.current_round + 1
    answer = AssessmentAnswer(
        assessment_id=assessment_id,
        round_number=next_round,
        question_id=question_id,
        question_text=q["text"],
        answer_value=answer_value,
        target_dimension=q["dimension"],
    )
    db.add(answer)
    assessment.current_round = next_round

    if next_round >= TOTAL_ROUNDS:
        assessment.status = "completed"
        await db.commit()
        await db.refresh(assessment)
        # Auto-generate report if user is authenticated
        if assessment.user_id is not None:
            try:
                await finalize_report(db, assessment_id, assessment.user_id)
            except: pass
        return assessment, {"type": "complete", "assessment_id": assessment.id}

    await db.commit()
    await db.refresh(assessment)

    is_preview = (next_round == PREVIEW_MARKER)
    if assessment.status == "completed":
        return assessment, {"type": "complete", "assessment_id": assessment.id}

    # Get answered data for agent selection
    all_answers = await get_assessment_answers(db, assessment_id)
    answered_ids = [a.question_id for a in all_answers]
    answered_dims = {}
    for a in all_answers:
        answered_dims[a.target_dimension] = answered_dims.get(a.target_dimension, 0) + 1

    answers_data = [
        {"round_number": a.round_number, "question_id": a.question_id,
         "question_text": a.question_text, "answer_value": a.answer_value,
         "target_dimension": a.target_dimension}
        for a in all_answers
    ]

    next_q = await get_next_question(answered_ids, answered_dims, next_round, answers_data)
    if next_q is None:
        assessment.status = "completed"
        await db.commit()
        return assessment, {"type": "complete", "assessment_id": assessment.id}

    result = {
        "type": "question",
        **next_q,
    }
    if is_preview:
        result["preview"] = {
            "dimension": "thinking",
            "score": _quick_preview(answers_data, "thinking"),
            "message": "初步评估完成，想看完整六维报告吗？",
            "show_register_prompt": assessment.user_id is None,
        }
    return assessment, result

async def finalize_report(db: AsyncSession, assessment_id: int, user_id: int) -> Report | None:
    """Generate and save report after assessment completion."""
    assessment = await get_owned_assessment(db, assessment_id, user_id)
    if assessment is None:
        raise AssessmentNotFoundError
    if assessment.status != "completed":
        raise AssessmentNotCompletedError

    existing = await db.execute(
        select(Report).where(
            Report.assessment_id == assessment_id,
            Report.user_id == user_id,
        )
    )
    existing_report = existing.scalar_one_or_none()
    if existing_report:
        return existing_report

    answers = await get_assessment_answers(db, assessment_id)
    if not answers:
        return None

    answers_data = [
        {"round_number": a.round_number, "question_id": a.question_id,
         "question_text": a.question_text, "answer_value": a.answer_value,
         "target_dimension": a.target_dimension}
        for a in answers
    ]

    report_data = await generate_report(answers_data)
    report = Report(
        user_id=user_id,
        assessment_id=assessment_id,
        dimensions=report_data["dimensions"],
        summary=report_data["summary"],
        career_suggestions=report_data["career_suggestions"],
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

async def undo_last_answer(db: AsyncSession, assessment_id: int, user_id: int) -> tuple[bool, dict | None]:
    """Delete the last answer and decrement current_round. Returns (success, undone_question_data)."""
    assessment = await get_owned_assessment(db, assessment_id, user_id)
    if not assessment or assessment.status != "in_progress" or assessment.current_round == 0:
        return False, None
    answers = await get_assessment_answers(db, assessment_id)
    if not answers:
        return False, None
    last = answers[-1]
    undone_q = {"question_id": last.question_id, "question_text": last.question_text, "answer_value": last.answer_value, "target_dimension": last.target_dimension}
    await db.delete(last)
    assessment.current_round -= 1
    await db.commit()
    return True, undone_q

async def bind_assessment(db: AsyncSession, assessment_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id, Assessment.user_id.is_(None))
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        return False
    await db.execute(
        update(Assessment).where(Assessment.id == assessment_id).values(user_id=user_id)
    )
    await db.commit()
    return True

def _quick_preview(answers: list[dict], dimension: str) -> int:
    """Quick scoring for preview."""
    dim_answers = [a for a in answers if a.get("target_dimension") == dimension]
    if not dim_answers:
        return 70
    return int(sum(a["answer_value"] for a in dim_answers) / len(dim_answers) * 20)
