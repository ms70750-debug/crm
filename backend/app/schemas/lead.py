from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class LeadBase(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: str | None = None
    origem: str = "Manual"
    produto_interesse: str = "INSS"
    status: str = "Novo lead"
    prioridade: str = "Media"
    responsavel: str = "Equipe BBB"
    observacoes: str | None = None
    proximo_contato: str | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    nome: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    email: str | None = None
    origem: str | None = None
    produto_interesse: str | None = None
    status: str | None = None
    prioridade: str | None = None
    responsavel: str | None = None
    observacoes: str | None = None
    proximo_contato: str | None = None


class LeadRead(LeadBase, ORMModel):
    id: int
    data_criacao: datetime


class LeadTimelineEvent(BaseModel):
    tipo: str
    titulo: str
    descricao: str
    data: str | None = None


class LeadDetail(LeadRead):
    timeline: list[LeadTimelineEvent]
    historico: list[LeadTimelineEvent]
