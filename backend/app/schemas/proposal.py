from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ProposalBase(BaseModel):
    cliente_id: int
    produto: str = "INSS"
    banco: str = "Banco simulado"
    valor_liberado: float = 0
    parcela: float = 0
    prazo: int = 84
    status: str = "Em andamento"
    observacoes: str | None = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    cliente_id: int | None = None
    produto: str | None = None
    banco: str | None = None
    valor_liberado: float | None = None
    parcela: float | None = None
    prazo: int | None = None
    status: str | None = None
    observacoes: str | None = None


class ProposalRead(ProposalBase, ORMModel):
    id: int
    data_criacao: datetime
