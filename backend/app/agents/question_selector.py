import json
import math
from pathlib import Path

_questions = None

def load_questions() -> list[dict]:
    global _questions
    if _questions is None:
        path = Path(__file__).parent.parent / "data" / "questions.json"
        with open(path, "r", encoding="utf-8") as f:
            _questions = json.load(f)
    return _questions

DIMENSIONS = ["thinking", "creativity", "execution", "social", "emotional", "drive"]
DIMENSION_LABELS = {
    "thinking": "思维力", "creativity": "创造力", "execution": "执行力",
    "social": "社交力", "emotional": "情绪力", "drive": "驱动力",
}
TOTAL_ROUNDS = 24  # Min ~3 questions per dimension; adaptive may extend to 30

async def select_next_question(answered_ids: list[str], answered_dimensions: dict[str, int]) -> dict | None:
    """Select next question prioritizing uncovered dimensions, then low-coverage ones."""
    questions = load_questions()
    available = [q for q in questions if q["id"] not in answered_ids]
    if not available:
        return None

    # Phase 1: round-robin across dimensions first
    missing = [d for d in DIMENSIONS if answered_dimensions.get(d, 0) == 0]
    if missing:
        target = missing[0]
        candidates = [q for q in available if q["dimension"] == target]
        if candidates:
            return candidates[0]

    # Phase 2: fill dimensions with least questions
    min_count = min(answered_dimensions.values()) if answered_dimensions else 0
    target_dims = [d for d in DIMENSIONS if answered_dimensions.get(d, 0) <= min_count]
    candidates = [q for q in available if q["dimension"] in target_dims]
    if candidates:
        return candidates[0]

    return available[0]

def calculate_dimension_score(answers: list[dict], dimension: str) -> tuple[float, float]:
    """Calculate weighted score and confidence for a dimension."""
    dim_questions = [q for q in load_questions() if q["dimension"] == dimension]
    dim_answers = [
        a for a in answers
        if any(q["id"] == a.get("question_id") for q in dim_questions)
    ]
    if not dim_answers:
        return 0.0, 0.0

    total_weight = 0.0
    weighted_sum = 0.0
    values = []

    for ans in dim_answers:
        q = next((q for q in dim_questions if q["id"] == ans["question_id"]), None)
        if q is None:
            continue
        raw = ans["answer_value"]
        if q["reverse"]:
            raw = 6 - raw
        weight = q["weight"]
        weighted_sum += raw * weight
        total_weight += weight
        values.append(raw)

    if total_weight == 0:
        return 0.0, 0.0

    score = (weighted_sum / total_weight) * 20  # Map 1-5 to 0-100
    std = math.sqrt(sum((v - (score / 20)) ** 2 for v in values) / len(values)) if len(values) > 1 else 1.0
    confidence = 1.0 - min(std / 2.5, 0.9)
    return round(score, 1), round(confidence, 3)

def calculate_all_scores(answers: list[dict]) -> dict:
    """Calculate scores for all six dimensions."""
    result = {}
    for dim in DIMENSIONS:
        score, confidence = calculate_dimension_score(answers, dim)
        result[dim] = {
            "score": score,
            "confidence": confidence,
            "confidence_interval": [max(0, score - (1 - confidence) * 15), min(100, score + (1 - confidence) * 15)],
            "label": DIMENSION_LABELS[dim],
            "answers_count": len([a for a in answers if a.get("target_dimension") == dim]),
        }
    return result
