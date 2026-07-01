from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Proposal(Base):
    __tablename__ = "propostas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    produto: Mapped[str] = mapped_column(String(80), default="INSS")
    banco: Mapped[str] = mapped_column(String(80), default="Banco simulado")
    valor_liberado: Mapped[float] = mapped_column(Float, default=0)
    parcela: Mapped[float] = mapped_column(Float, default=0)
    prazo: Mapped[int] = mapped_column(Integer, default=84)
    status: Mapped[str] = mapped_column(String(40), default="Em andamento", index=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
