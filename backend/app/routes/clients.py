from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Proposal
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.services.crud import create_item, delete_item, get_item, update_item

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClientRead])
def list_clients(q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Client).order_by(Client.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Client.nome.ilike(like), Client.cpf.ilike(like), Client.telefone.ilike(like)))
    return db.scalars(stmt).all()


@router.post("", response_model=ClientRead, status_code=201)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    return create_item(db, Client, payload)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    return get_item(db, Client, client_id)


@router.get("/{client_id}/historico")
def get_client_history(client_id: int, db: Session = Depends(get_db)):
    client = get_item(db, Client, client_id)
    proposals = db.scalars(select(Proposal).where(Proposal.cliente_id == client.id).order_by(Proposal.id.desc())).all()
    return {"cliente": client, "eventos": [{"tipo": "proposta", "status": p.status, "valor": p.valor_liberado} for p in proposals]}


@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db)):
    return update_item(db, Client, client_id, payload)


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    return delete_item(db, Client, client_id)
