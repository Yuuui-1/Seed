from pydantic import BaseModel

class DimensionDetail(BaseModel):
    score: int
    confidence_interval: tuple[int, int] | None = None
    label: str
    strengths: str
    areas_for_improvement: str
    description: str
    evidence: list[str]

class ReportDetailResponse(BaseModel):
    id: int
    dimensions: dict[str, DimensionDetail]
    summary: str
    career_suggestions: list[dict]
    created_at: str

class ShareLinkResponse(BaseModel):
    share_url: str
    token: str
    expires_at: str
