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
