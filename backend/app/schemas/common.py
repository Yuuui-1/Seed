from pydantic import BaseModel

class APIResponse(BaseModel):
    code: int = 0
    data: dict | list | None = None
    msg: str = "success"
