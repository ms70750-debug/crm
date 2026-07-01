from pydantic import BaseModel

from app.schemas.common import ORMModel


class ClientBase(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: str | None = None
    data_nascimento: str | None = None
    beneficio: str | None = None
    convenio: str = "INSS"
    banco_pagamento: str | None = None
    observacoes: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nome: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    email: str | None = None
    data_nascimento: str | None = None
    beneficio: str | None = None
    convenio: str | None = None
    banco_pagamento: str | None = None
    observacoes: str | None = None


class ClientRead(ClientBase, ORMModel):
    id: int
