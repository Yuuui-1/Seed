from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.core.deps import require_auth
from app.services import report_service, assessment_service, auth_service
from app.models.share_link import ShareLink

router = APIRouter()

@router.get("/")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: int = Depends(require_auth),
    db: AsyncSession = Depends(get_session),
):
    reports, total = await report_service.get_reports_by_user(db, user_id, page, page_size)
    items = []
    for r in reports:
        dims_summary = {}
        for dim, data in r.dimensions.items():
            dims_summary[dim] = {"score": data["score"], "label": data["label"]}
        items.append({"id": r.id, "created_at": r.created_at.isoformat(), "dimensions": dims_summary})
    return {"code": 0, "data": {"items": items, "total": total, "page": page, "page_size": page_size}, "msg": "success"}

@router.get("/by-assessment/{assessment_id}")
async def get_report_by_assessment(assessment_id: int, user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Report).where(Report.assessment_id == assessment_id, Report.user_id == user_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, detail={"code": 1003, "msg": "报告不存在"})
    return {
        "code": 0,
        "data": {
            "id": report.id,
            "assessment_id": report.assessment_id,
            "dimensions": report.dimensions,
            "summary": report.summary,
            "career_suggestions": report.career_suggestions,
            "created_at": report.created_at.isoformat(),
            "shared": False,
        },
        "msg": "success",
    }

@router.get("/{report_id}")
async def get_report(report_id: int, user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    report = await report_service.get_report(db, report_id, user_id)
    if not report:
        raise HTTPException(404, detail={"code": 1003, "msg": "报告不存在"})

    # Check if any share link exists
    share_result = await db.execute(select(ShareLink).where(ShareLink.report_id == report_id).limit(1))
    shared = share_result.scalar_one_or_none() is not None

    return {
        "code": 0,
        "data": {
            "id": report.id,
            "assessment_id": report.assessment_id,
            "dimensions": report.dimensions,
            "summary": report.summary,
            "career_suggestions": report.career_suggestions,
            "created_at": report.created_at.isoformat(),
            "shared": shared,
        },
        "msg": "success",
    }

@router.post("/generate/{assessment_id}")
async def generate_report_endpoint(assessment_id: int, user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    try:
        report = await assessment_service.finalize_report(db, assessment_id, user_id)
    except assessment_service.AssessmentNotFoundError:
        raise HTTPException(404, detail={"code": 1003, "msg": "测评不存在"})
    except assessment_service.AssessmentNotCompletedError:
        raise HTTPException(409, detail={"code": 1004, "msg": "测评尚未完成"})
    if not report:
        raise HTTPException(400, detail={"code": 1003, "msg": "测评不存在或无回答"})
    return {
        "code": 0,
        "data": {
            "id": report.id,
            "assessment_id": report.assessment_id,
            "dimensions": report.dimensions,
            "summary": report.summary,
            "career_suggestions": report.career_suggestions,
            "created_at": report.created_at.isoformat(),
        },
        "msg": "success",
    }

@router.post("/{report_id}/share")
async def share_report(report_id: int, user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    link = await report_service.create_share_link(db, report_id, user_id)
    if not link:
        raise HTTPException(404, detail={"code": 1003, "msg": "报告不存在"})
    return {
        "code": 0,
        "data": {"share_url": link.share_url, "token": link.token, "expires_at": link.expires_at.isoformat()},
        "msg": "success",
    }

@router.get("/shared/{token}")
async def view_shared_report(token: str, db: AsyncSession = Depends(get_session)):
    report = await report_service.get_report_by_token(db, token)
    if not report:
        raise HTTPException(404, detail={"code": 1003, "msg": "分享链接不存在或已过期"})

    user = await auth_service.get_user_by_id(db, report.user_id)
    share_from = user.nickname if user else "匿名用户"

    return {
        "code": 0,
        "data": {
            "dimensions": report.dimensions,
            "summary": report.summary,
            "career_suggestions": report.career_suggestions,
            "share_from": share_from,
        },
        "msg": "success",
    }
