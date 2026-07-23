from pydantic import BaseModel, Field

class AnswerRequest(BaseModel):
    question_id: str
    answer_value: int = Field(ge=1, le=5)
    session_id: str | None = None

class QuestionResponse(BaseModel):
    question_id: str
    round: int
    agent_message: str
    question_text: str
    options: list[dict]
    target_dimension: str

class ProgressResponse(BaseModel):
    assessment_id: int
    status: str
    current_round: int
    total_rounds: int
    dimensions_progress: dict | None = None
