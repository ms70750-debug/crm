from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(140), index=True)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str | None] = mapped_column(String(140), nullable=True)
    origem: Mapped[str] = mapped_column(String(80), default="Manual")
    produto_interesse: Mapped[str] = mapped_column(String(80), default="INSS")
    status: Mapped[str] = mapped_column(String(40), default="Novo lead", index=True)
    prioridade: Mapped[str] = mapped_column(String(20), default="Media", index=True)
    responsavel: Mapped[str] = mapped_column(String(80), default="Equipe BBB")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    proximo_contato: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
