from app.agents.question_selector import (
    load_questions, select_next_question, calculate_all_scores, TOTAL_ROUNDS,
)
from app.agents.report_generator import (
    generate_dimension_report, generate_career_suggestions, generate_summary,
)

OPTIONS = [
    {"value": 1, "label": "非常不符合"},
    {"value": 2, "label": "不太符合"},
    {"value": 3, "label": "一般"},
    {"value": 4, "label": "比较符合"},
    {"value": 5, "label": "非常符合"},
]

DIMENSION_AGENT_MESSAGES = {
    "thinking": "接下来想了解你的思维方式...",
    "creativity": "很好，来看看你的创造力...",
    "execution": "现在来了解你的执行力...",
    "social": "来看看你在团队中的角色...",
    "emotional": "接下来关注你的情绪调节能力...",
    "drive": "最后来探索你的内在驱动力...",
}

async def get_first_question() -> dict:
    """Get the first question from the question bank."""
    questions = load_questions()
    q = questions[0]
    return {
        "question_id": q["id"],
        "round": 1,
        "agent_message": DIMENSION_AGENT_MESSAGES.get(q["dimension"], "让我们开始吧..."),
        "question_text": q["text"],
        "options": OPTIONS,
        "target_dimension": q["dimension"],
    }

async def get_next_question(answered_ids: list[str], answered_dimensions: dict[str, int], current_round: int, answers: list[dict]) -> dict | None:
    """Select next question using agent strategy. Returns None if complete."""
    if current_round >= TOTAL_ROUNDS:
        return None

    q = await select_next_question(answered_ids, answered_dimensions)
    if q is None:
        return None

    return {
        "question_id": q["id"],
        "round": current_round + 1,
        "agent_message": DIMENSION_AGENT_MESSAGES.get(q["dimension"], "继续..."),
        "question_text": q["text"],
        "options": OPTIONS,
        "target_dimension": q["dimension"],
    }

async def generate_report(answers: list[dict]) -> dict:
    """Generate full report from answers."""
    scores = calculate_all_scores(answers)

    dimensions = {}
    for dim, data in scores.items():
        evidence = [f"第{a['round_number']}题：" + a["question_text"] for a in answers if a.get("target_dimension") == dim]
        report = await generate_dimension_report(dim, data["score"], evidence)
        dimensions[dim] = {
            "score": data["score"],
            "confidence_interval": data["confidence_interval"],
            "label": data["label"],
            "strengths": report["strengths"],
            "areas_for_improvement": report.get("areas_for_improvement", ""),
            "description": report["description"],
            "evidence": report.get("evidence", []),
        }

    career = await generate_career_suggestions(scores)
    summary = await generate_summary(scores)

    return {
        "dimensions": dimensions,
        "summary": summary,
        "career_suggestions": career,
    }
