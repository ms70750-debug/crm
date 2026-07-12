from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Lead, Proposal, User
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate
from app.services.crud import create_item, delete_item, get_item, update_item
from app.services.security import current_user, is_partner, log_audit, require_roles

router = APIRouter(prefix="/propostas", tags=["propostas"])


@router.get("", response_model=list[ProposalRead])
def list_proposals(status: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    stmt = select(Proposal).order_by(Proposal.id.desc())
    if is_partner(user):
        stmt = (
            stmt.select_from(Proposal, Client, Lead)
            .where(Proposal.cliente_id == Client.id, Client.cpf == Lead.cpf, Lead.responsavel == user.nome)
        )
    if status:
        stmt = stmt.where(Proposal.status == status)
    return db.scalars(stmt).all()


@router.post("", response_model=ProposalRead, status_code=201)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    proposal = create_item(db, Proposal, payload)
    log_audit(db, "proposal_created", "proposta", proposal.id, actor=user.email, actor_user_id=user.id, metadata=payload.model_dump())
    db.commit()
    return proposal


@router.get("/{proposal_id}", response_model=ProposalRead)
def get_proposal(proposal_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proposal = get_item(db, Proposal, proposal_id)
    if is_partner(user):
        allowed = db.scalar(
            select(Lead.id)
            .select_from(Lead, Client)
            .where(Client.id == proposal.cliente_id, Client.cpf == Lead.cpf, Lead.responsavel == user.nome)
        )
        if not allowed:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="Proposta nao atribuida ao parceiro")
    return proposal


@router.put("/{proposal_id}", response_model=ProposalRead)
def update_proposal(proposal_id: int, payload: ProposalUpdate, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    proposal = update_item(db, Proposal, proposal_id, payload)
    log_audit(db, "proposal_updated", "proposta", proposal.id, actor=user.email, actor_user_id=user.id, metadata=payload.model_dump(exclude_unset=True))
    db.commit()
    return proposal


@router.patch("/{proposal_id}/status", response_model=ProposalRead)
def update_proposal_status(proposal_id: int, payload: ProposalUpdate, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    proposal = update_item(db, Proposal, proposal_id, payload)
    log_audit(db, "proposal_status_updated", "proposta", proposal.id, actor=user.email, actor_user_id=user.id, metadata={"status": payload.status})
    db.commit()
    return proposal


@router.delete("/{proposal_id}")
def delete_proposal(proposal_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor"))):
    result = delete_item(db, Proposal, proposal_id)
    log_audit(db, "proposal_deleted", "proposta", proposal_id, actor=user.email, actor_user_id=user.id)
    db.commit()
    return result
