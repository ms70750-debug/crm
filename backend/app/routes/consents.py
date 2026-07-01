from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Consent
from app.schemas.security import ConsentCreate, ConsentRead
from app.services.security import log_audit, require_roles

router = APIRouter(prefix="/consents", tags=["consents"])


@router.get("", response_model=list[ConsentRead])
def list_consents(customer_id: int | None = None, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    stmt = select(Consent).order_by(Consent.id.desc())
    if customer_id:
        stmt = stmt.where(Consent.customer_id == customer_id)
    return db.scalars(stmt).all()


@router.post("", response_model=ConsentRead, status_code=201)
def create_consent(payload: ConsentCreate, request: Request, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    consent = Consent(
        customer_id=payload.customer_id,
        channel=payload.channel,
        granted=payload.granted,
        source=payload.source,
        ip_address=request.client.host if request.client else None,
        revoked_at=None if payload.granted else datetime.utcnow(),
    )
    db.add(consent)
    db.flush()
    log_audit(db, "consent_registered", "consent", consent.id, actor=user.email, actor_user_id=user.id, metadata=payload.model_dump())
    db.commit()
    db.refresh(consent)
    return consent


@router.post("/{consent_id}/revoke", response_model=ConsentRead)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    consent = db.get(Consent, consent_id)
    if not consent:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Consentimento nao encontrado")
    consent.granted = False
    consent.revoked_at = datetime.utcnow()
    log_audit(db, "consent_revoked", "consent", consent.id, actor=user.email, actor_user_id=user.id, metadata={"customer_id": consent.customer_id, "channel": consent.channel})
    db.commit()
    db.refresh(consent)
    return consent
