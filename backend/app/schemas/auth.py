from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)
    nickname: str = Field(min_length=2, max_length=20)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str

class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

class ProfileUpdate(BaseModel):
    nickname: str | None = Field(None, min_length=2, max_length=20)
