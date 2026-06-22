from pydantic import BaseModel


class Principal(BaseModel):
    user_id: int
    role: str
    permissions: list[str]