from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Client(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(140), index=True)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(140), nullable=True)
    data_nascimento: Mapped[str | None] = mapped_column(String(20), nullable=True)
    beneficio: Mapped[str | None] = mapped_column(String(40), nullable=True)
    convenio: Mapped[str] = mapped_column(String(80), default="INSS")
    banco_pagamento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
