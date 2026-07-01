from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Lead
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from app.services.crud import create_item, delete_item, get_item, update_item

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadRead])
def list_leads(status: str | None = None, q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Lead).order_by(Lead.id.desc())
    if status:
        stmt = stmt.where(Lead.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Lead.nome.ilike(like), Lead.cpf.ilike(like), Lead.telefone.ilike(like)))
    return db.scalars(stmt).all()


@router.post("", response_model=LeadRead, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    return create_item(db, Lead, payload)


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    return get_item(db, Lead, lead_id)


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    return update_item(db, Lead, lead_id, payload)


@router.patch("/{lead_id}/status", response_model=LeadRead)
def update_lead_status(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    return update_item(db, Lead, lead_id, payload)


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    return delete_item(db, Lead, lead_id)
