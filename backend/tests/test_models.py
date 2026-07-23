from app.db.base import Base
from app.models.user import User
from app.models.assessment import Assessment, AssessmentAnswer
from app.models.report import Report
from app.models.share_link import ShareLink

def test_models_can_be_imported():
    tables = Base.metadata.tables
    assert "users" in tables
    assert "assessments" in tables
    assert "assessment_answers" in tables
    assert "reports" in tables
    assert "share_links" in tables
