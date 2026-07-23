from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.db.session import get_session

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int | None:
    if not credentials:
        return None
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    return int(sub)

async def require_auth(user_id: int | None = Depends(get_current_user_id)) -> int:
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1002, "msg": "请先登录"},
        )
    return user_id
