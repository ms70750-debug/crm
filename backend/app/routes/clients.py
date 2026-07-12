from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Proposal
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.services.crud import create_item, delete_item, get_item, update_item
from app.services.privacy import assert_demo_cpf_allowed, person_payload
from app.services.security import can_view_sensitive_data, log_audit, require_roles
from app.services.soft_delete import mark_deleted, restore_deleted

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("")
def list_clients(q: str | None = None, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    stmt = select(Client).where(Client.deleted_at.is_(None)).order_by(Client.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Client.nome.ilike(like), Client.cpf.ilike(like), Client.telefone.ilike(like)))
    return [person_payload(client, can_view_sensitive_data(user)) for client in db.scalars(stmt).all()]


@router.post("", status_code=201)
def create_client(payload: ClientCreate, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    assert_demo_cpf_allowed(payload.cpf)
    client = create_item(db, Client, payload)
    log_audit(db, "client_created", "cliente", client.id, actor=user.email, actor_user_id=user.id, metadata=payload.model_dump())
    db.commit()
    return person_payload(client, can_view_sensitive_data(user))


@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    client = get_item(db, Client, client_id)
    return person_payload(client, can_view_sensitive_data(user))


@router.get("/{client_id}/historico")
def get_client_history(client_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    client = get_item(db, Client, client_id)
    proposals = db.scalars(select(Proposal).where(Proposal.cliente_id == client.id).order_by(Proposal.id.desc())).all()
    return {"cliente": person_payload(client, can_view_sensitive_data(user)), "eventos": [{"tipo": "proposta", "status": p.status, "valor": p.valor_liberado} for p in proposals]}


@router.put("/{client_id}")
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor", "operador"))):
    if payload.cpf:
        assert_demo_cpf_allowed(payload.cpf)
    client = update_item(db, Client, client_id, payload)
    log_audit(db, "client_updated", "cliente", client.id, actor=user.email, actor_user_id=user.id, metadata=payload.model_dump(exclude_unset=True))
    db.commit()
    return person_payload(client, can_view_sensitive_data(user))


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor"))):
    client = get_item(db, Client, client_id)
    mark_deleted(client, user.id)
    log_audit(db, "client_soft_deleted", "cliente", client.id, actor=user.email, actor_user_id=user.id, metadata={"cpf": client.cpf, "email": client.email, "telefone": client.telefone})
    db.commit()
    return {"ok": True}


@router.post("/{client_id}/restore")
def restore_client(client_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor"))):
    client = get_item(db, Client, client_id)
    restore_deleted(client)
    log_audit(db, "client_restored", "cliente", client.id, actor=user.email, actor_user_id=user.id, metadata={"cpf": client.cpf})
    db.commit()
    return {"ok": True}
