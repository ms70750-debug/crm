from pydantic import BaseModel

from app.schemas.common import ORMModel


class TaskBase(BaseModel):
    titulo: str
    descricao: str | None = None
    status: str = "Pendente"
    prioridade: str = "Media"
    responsavel: str = "Equipe BBB"
    lead_id: int | None = None
    cliente_id: int | None = None
    data_vencimento: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    status: str | None = None
    prioridade: str | None = None
    responsavel: str | None = None
    lead_id: int | None = None
    cliente_id: int | None = None
    data_vencimento: str | None = None


class TaskRead(TaskBase, ORMModel):
    id: int
