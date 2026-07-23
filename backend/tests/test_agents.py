import pytest
from app.agents.question_selector import (
    load_questions, select_next_question, calculate_dimension_score,
    calculate_all_scores, DIMENSIONS, TOTAL_ROUNDS,
)
from app.agents.report_generator import (
    generate_dimension_report, generate_career_suggestions, generate_summary,
)
from app.agents.orchestrator import get_first_question, get_next_question

@pytest.mark.asyncio
async def test_load_questions():
    questions = load_questions()
    assert len(questions) == 36
    assert questions[0]["id"] == "q001"
    assert all(d in DIMENSIONS for q in questions for d in [q["dimension"]])

@pytest.mark.asyncio
async def test_select_next_question_empty():
    q = await select_next_question([], {})
    assert q is not None
    assert q["id"] == "q001"

@pytest.mark.asyncio
async def test_select_next_question_round_robin():
    # After answering thinking questions, should pick from uncovered dimension
    answered_ids = ["q001", "q002", "q003", "q004", "q005", "q006"]
    answered_dims = {"thinking": 6}
    q = await select_next_question(answered_ids, answered_dims)
    assert q is not None
    assert q["dimension"] != "thinking"

@pytest.mark.asyncio
async def test_select_next_question_all_answered():
    questions = load_questions()
    all_ids = [q["id"] for q in questions]
    all_dims = {d: 6 for d in DIMENSIONS}
    q = await select_next_question(all_ids, all_dims)
    assert q is None

@pytest.mark.asyncio
async def test_calculate_dimension_score():
    answers = [
        {"question_id": "q001", "answer_value": 5, "target_dimension": "thinking"},
        {"question_id": "q002", "answer_value": 4, "target_dimension": "thinking"},
    ]
    score, conf = calculate_dimension_score(answers, "thinking")
    assert 70 <= score <= 100
    assert 0 <= conf <= 1

@pytest.mark.asyncio
async def test_calculate_all_scores():
    questions = load_questions()
    answers = [{"question_id": q["id"], "answer_value": q["id"] == questions[0]["id"] and 5 or 3, "target_dimension": q["dimension"]} for q in questions[:6]]
    scores = calculate_all_scores(answers)
    assert len(scores) == 6
    assert scores["thinking"]["score"] > 0

@pytest.mark.asyncio
async def test_get_first_question():
    q = await get_first_question()
    assert q["round"] == 1
    assert "question_id" in q
    assert len(q["options"]) == 5

@pytest.mark.asyncio
async def test_get_next_question():
    q = await get_next_question(["q001"], {"thinking": 1}, 1, [])
    assert q is not None
    assert q["round"] == 2

@pytest.mark.asyncio
async def test_get_next_question_complete():
    questions = load_questions()
    all_ids = [q["id"] for q in questions]
    q = await get_next_question(all_ids, {"thinking": 6, "creativity": 6, "execution": 6, "social": 6, "emotional": 6, "drive": 6}, TOTAL_ROUNDS, [])
    assert q is None

@pytest.mark.asyncio
async def test_generate_dimension_report():
    report = await generate_dimension_report("thinking", 85, ["第1题：测试问题"])
    assert report["strengths"] != ""
    assert len(report["evidence"]) > 0

@pytest.mark.asyncio
async def test_generate_career_suggestions():
    scores = {"thinking": {"score": 85}, "creativity": {"score": 60}, "execution": {"score": 90}, "social": {"score": 70}, "emotional": {"score": 55}, "drive": {"score": 80}}
    suggestions = await generate_career_suggestions(scores)
    assert len(suggestions) > 0
    assert all("direction" in s for s in suggestions)

@pytest.mark.asyncio
async def test_generate_summary():
    scores = {"thinking": {"score": 85, "label": "思维力"}, "creativity": {"score": 60, "label": "创造力"}, "execution": {"score": 90, "label": "执行力"}, "social": {"score": 70, "label": "社交力"}, "emotional": {"score": 55, "label": "情绪力"}, "drive": {"score": 80, "label": "驱动力"}}
    summary = await generate_summary(scores)
    assert "思维力" in summary or "执行力" in summary
