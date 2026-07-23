from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.report import Report
from app.models.share_link import ShareLink
from app.core.config import get_settings

settings = get_settings()

async def get_report(db: AsyncSession, report_id: int, user_id: int) -> Report | None:
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def get_reports_by_user(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 20) -> tuple[list[Report], int]:
    query = select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc())
    count_query = select(Report).where(Report.user_id == user_id)

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return list(result.scalars().all()), total

async def create_share_link(db: AsyncSession, report_id: int, user_id: int) -> ShareLink | None:
    # Verify ownership
    report = await get_report(db, report_id, user_id)
    if not report:
        return None

    import secrets
    from datetime import datetime, timedelta, UTC

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=30)

    link = ShareLink(report_id=report_id, token=token, expires_at=expires_at)
    db.add(link)
    await db.commit()
    await db.refresh(link)

    link.share_url = f"{settings.SHARE_LINK_BASE_URL}/{token}"
    return link

async def get_report_by_token(db: AsyncSession, token: str) -> Report | None:
    from datetime import datetime, UTC
    result = await db.execute(
        select(Report).join(ShareLink).where(
            ShareLink.token == token,
            ShareLink.expires_at > datetime.now(UTC),
        )
    )
    return result.scalar_one_or_none()
