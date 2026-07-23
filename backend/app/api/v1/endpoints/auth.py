from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.core.deps import require_auth, get_current_user_id
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshRequest,
    ProfileUpdate, TokenResponse, UserResponse,
)
from app.services import auth_service
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_session)):
    existing = await auth_service.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(400, detail={"code": 1001, "msg": "邮箱已被注册"})
    user = await auth_service.create_user(db, req.email, req.password, req.nickname)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {
        "code": 0,
        "data": {
            "user": UserResponse(id=user.id, email=user.email, nickname=user.nickname).model_dump(),
            "access_token": access,
            "refresh_token": refresh,
        },
        "msg": "success",
    }

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_session)):
    user = await auth_service.authenticate(db, req.email, req.password)
    if not user:
        raise HTTPException(401, detail={"code": 1002, "msg": "邮箱或密码错误"})
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {
        "code": 0,
        "data": {
            "user": UserResponse(id=user.id, email=user.email, nickname=user.nickname).model_dump(),
            "access_token": access,
            "refresh_token": refresh,
        },
        "msg": "success",
    }

@router.post("/refresh")
async def refresh(req: RefreshRequest):
    payload = verify_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, detail={"code": 1002, "msg": "Refresh Token 无效或已过期"})
    user_id = int(payload["sub"])
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return {"code": 0, "data": {"access_token": access, "refresh_token": refresh}, "msg": "success"}

@router.post("/logout")
async def logout(user_id: int = Depends(require_auth)):
    return {"code": 0, "data": None, "msg": "success"}

@router.get("/me")
async def get_me(user_id: int = Depends(require_auth), db: AsyncSession = Depends(get_session)):
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, detail={"code": 1003, "msg": "用户不存在"})
    return {
        "code": 0,
        "data": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat(),
        },
        "msg": "success",
    }
