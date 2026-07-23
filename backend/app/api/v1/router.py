from fastapi import APIRouter
from app.api.v1.endpoints import auth, assessment, report, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
api_router.include_router(report.router, prefix="/reports", tags=["reports"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
