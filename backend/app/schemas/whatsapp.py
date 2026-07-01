from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class WhatsAppPreviewRequest(BaseModel):
    destinatario_tipo: str
    destinatario_id: int
    modelo: str


class WhatsAppSendRequest(WhatsAppPreviewRequest):
    mensagem: str


class WhatsAppPreview(BaseModel):
    telefone: str
    mensagem: str
    modo: str = "simulation"


class WhatsAppMessageRead(WhatsAppPreview, ORMModel):
    id: int
    destinatario_tipo: str
    destinatario_id: int
    modelo: str
    status: str
    criado_em: datetime
