from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    destinatario_tipo: Mapped[str] = mapped_column(String(20))
    destinatario_id: Mapped[int] = mapped_column(Integer)
    telefone: Mapped[str] = mapped_column(String(30))
    modelo: Mapped[str] = mapped_column(String(80))
    mensagem: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="Registrada em simulacao")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deletion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
