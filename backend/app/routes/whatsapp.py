from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Consent, Lead, WhatsAppMessage
from app.schemas.whatsapp import WhatsAppMessageRead, WhatsAppPreview, WhatsAppPreviewRequest, WhatsAppSendRequest
from app.services.security import log_audit, require_roles

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

TEMPLATES = {
    "primeiro_contato": "Ola, {nome}. Aqui e da BBB Consig. Vi seu interesse em {produto}. Posso te ajudar com uma simulacao segura?",
    "documentos": "Ola, {nome}. Para avancarmos sua proposta {produto}, preciso confirmar seus documentos pendentes.",
    "proposta": "Ola, {nome}. Sua proposta {produto} esta pronta para revisao. Esta mensagem e apenas uma simulacao interna.",
}


def _find_recipient(db: Session, tipo: str, item_id: int):
    model = Lead if tipo == "lead" else Client if tipo == "cliente" else None
    if model is None:
        raise HTTPException(status_code=400, detail="Tipo deve ser lead ou cliente")
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Destinatario nao encontrado")
    return item


@router.get("/modelos")
def list_templates(user=Depends(require_roles("admin", "supervisor", "operador"))):
    return [{"id": key, "nome": key.replace("_", " ").title()} for key in TEMPLATES]


@router.get("/status")
def whatsapp_status(user=Depends(require_roles("admin", "supervisor", "operador"))):
    return {
        "integration": "Evolution API",
        "mode": "simulation",
        "real_send_enabled": False,
        "health": "simulated",
        "message": "Nenhuma mensagem real e enviada nesta fase.",
    }


@router.post("/preview", response_model=WhatsAppPreview)
def preview_message(payload: WhatsAppPreviewRequest, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    recipient = _find_recipient(db, payload.destinatario_tipo, payload.destinatario_id)
    template = TEMPLATES.get(payload.modelo, TEMPLATES["primeiro_contato"])
    produto = getattr(recipient, "produto_interesse", getattr(recipient, "convenio", "consignado"))
    return {"telefone": recipient.telefone, "mensagem": template.format(nome=recipient.nome, produto=produto)}


@router.post("/simular-envio", response_model=WhatsAppMessageRead, status_code=201)
def simulate_send(payload: WhatsAppSendRequest, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    recipient = _find_recipient(db, payload.destinatario_tipo, payload.destinatario_id)
    client = recipient if payload.destinatario_tipo == "cliente" else db.scalar(select(Client).where(Client.cpf == recipient.cpf))
    if not client:
        raise HTTPException(status_code=400, detail="Converta o lead em cliente antes de registrar WhatsApp simulado.")
    consent = db.scalar(
        select(Consent)
        .where(Consent.customer_id == client.id, Consent.channel == "whatsapp", Consent.granted.is_(True), Consent.revoked_at.is_(None))
        .order_by(Consent.id.desc())
    )
    if not consent:
        log_audit(
            db,
            action="whatsapp_simulation_blocked_without_consent",
            entity_type="whatsapp_message",
            actor=user.email,
            actor_user_id=user.id,
            metadata={"destinatario_tipo": payload.destinatario_tipo, "destinatario_id": payload.destinatario_id, "modelo": payload.modelo},
        )
        db.commit()
        raise HTTPException(status_code=403, detail="Opt-in de WhatsApp obrigatorio antes de registrar mensagem simulada.")
    message = WhatsAppMessage(
        destinatario_tipo=payload.destinatario_tipo,
        destinatario_id=payload.destinatario_id,
        telefone=recipient.telefone,
        modelo=payload.modelo,
        mensagem=payload.mensagem,
    )
    db.add(message)
    db.flush()
    log_audit(
        db,
        action="whatsapp_simulation_created",
        entity_type="whatsapp_message",
        entity_id=message.id,
        metadata={
            "destinatario_tipo": payload.destinatario_tipo,
            "destinatario_id": payload.destinatario_id,
            "modelo": payload.modelo,
            "status": message.status,
        },
    )
    db.commit()
    db.refresh(message)
    return message


@router.get("/historico", response_model=list[WhatsAppMessageRead])
def list_history(db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    return db.scalars(select(WhatsAppMessage).order_by(WhatsAppMessage.id.desc())).all()
