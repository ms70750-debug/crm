from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Proposal
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate
from app.services.crud import create_item, delete_item, get_item, update_item

router = APIRouter(prefix="/propostas", tags=["propostas"])


@router.get("", response_model=list[ProposalRead])
def list_proposals(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Proposal).order_by(Proposal.id.desc())
    if status:
        stmt = stmt.where(Proposal.status == status)
    return db.scalars(stmt).all()


@router.post("", response_model=ProposalRead, status_code=201)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    return create_item(db, Proposal, payload)


@router.get("/{proposal_id}", response_model=ProposalRead)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    return get_item(db, Proposal, proposal_id)


@router.put("/{proposal_id}", response_model=ProposalRead)
def update_proposal(proposal_id: int, payload: ProposalUpdate, db: Session = Depends(get_db)):
    return update_item(db, Proposal, proposal_id, payload)


@router.patch("/{proposal_id}/status", response_model=ProposalRead)
def update_proposal_status(proposal_id: int, payload: ProposalUpdate, db: Session = Depends(get_db)):
    return update_item(db, Proposal, proposal_id, payload)


@router.delete("/{proposal_id}")
def delete_proposal(proposal_id: int, db: Session = Depends(get_db)):
    return delete_item(db, Proposal, proposal_id)
