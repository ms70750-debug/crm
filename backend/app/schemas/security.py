from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    email: str
    password: str


class DemoLoginRequest(BaseModel):
    role: str = "admin"


class UserRead(ORMModel):
    id: int
    nome: str
    email: str
    role: str
    ativo: bool
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserRead


class ConsentCreate(BaseModel):
    customer_id: int
    channel: str = "whatsapp"
    granted: bool = True
    source: str = "demo"


class ConsentRead(ConsentCreate, ORMModel):
    id: int
    ip_address: str | None = None
    created_at: datetime
    revoked_at: datetime | None = None
