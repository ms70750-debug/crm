from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Lead, Proposal, Task, WhatsAppMessage
from app.schemas.lead import LeadCreate, LeadDetail, LeadRead, LeadTimelineEvent, LeadUpdate
from app.services.crud import create_item, delete_item, get_item, update_item

router = APIRouter(prefix="/leads", tags=["leads"])


def _lead_events(db: Session, lead: Lead) -> tuple[list[LeadTimelineEvent], list[LeadTimelineEvent]]:
    events = [
        LeadTimelineEvent(
            tipo="lead",
            titulo="Lead criado",
            descricao=f"Origem {lead.origem} com interesse em {lead.produto_interesse}.",
            data=lead.data_criacao.isoformat(),
        ),
        LeadTimelineEvent(
            tipo="status",
            titulo=f"Status atual: {lead.status}",
            descricao=f"Prioridade {lead.prioridade} sob responsabilidade de {lead.responsavel}.",
            data=lead.data_criacao.isoformat(),
        ),
    ]
    if lead.proximo_contato:
        events.append(
            LeadTimelineEvent(
                tipo="contato",
                titulo="Proximo contato agendado",
                descricao=f"Contato previsto para {lead.proximo_contato}.",
                data=lead.proximo_contato,
            )
        )

    tasks = db.scalars(select(Task).where(Task.lead_id == lead.id).order_by(Task.id.desc())).all()
    for task in tasks:
        events.append(
            LeadTimelineEvent(
                tipo="tarefa",
                titulo=task.titulo,
                descricao=f"{task.status} - prioridade {task.prioridade} - responsavel {task.responsavel}.",
                data=task.data_vencimento,
            )
        )

    messages = db.scalars(
        select(WhatsAppMessage)
        .where(WhatsAppMessage.destinatario_tipo == "lead", WhatsAppMessage.destinatario_id == lead.id)
        .order_by(WhatsAppMessage.id.desc())
    ).all()
    for message in messages:
        events.append(
            LeadTimelineEvent(
                tipo="whatsapp",
                titulo=f"WhatsApp simulado: {message.modelo}",
                descricao=message.mensagem,
                data=message.criado_em.isoformat(),
            )
        )

    client = db.scalar(select(Client).where(Client.cpf == lead.cpf))
    if client:
        proposals = db.scalars(select(Proposal).where(Proposal.cliente_id == client.id).order_by(Proposal.id.desc())).all()
        for proposal in proposals:
            events.append(
                LeadTimelineEvent(
                    tipo="proposta",
                    titulo=f"Proposta {proposal.produto} - {proposal.status}",
                    descricao=f"{proposal.banco} com valor liberado de R$ {proposal.valor_liberado:.2f}.",
                    data=proposal.data_criacao.isoformat(),
                )
            )

    history = [event for event in events if event.tipo in {"tarefa", "whatsapp", "proposta", "status"}]
    return events, history


@router.get("", response_model=list[LeadRead])
def list_leads(
    status: str | None = None,
    origem: str | None = None,
    produto_interesse: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Lead).order_by(Lead.id.desc())
    if status:
        stmt = stmt.where(Lead.status == status)
    if origem:
        stmt = stmt.where(Lead.origem == origem)
    if produto_interesse:
        stmt = stmt.where(Lead.produto_interesse == produto_interesse)
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


@router.get("/{lead_id}/detalhe", response_model=LeadDetail)
def get_lead_detail(lead_id: int, db: Session = Depends(get_db)):
    lead = get_item(db, Lead, lead_id)
    timeline, historico = _lead_events(db, lead)
    base = LeadRead.model_validate(lead).model_dump()
    return LeadDetail(**base, timeline=timeline, historico=historico)


@router.get("/{lead_id}/timeline", response_model=list[LeadTimelineEvent])
def get_lead_timeline(lead_id: int, db: Session = Depends(get_db)):
    lead = get_item(db, Lead, lead_id)
    timeline, _ = _lead_events(db, lead)
    return timeline


@router.get("/{lead_id}/historico", response_model=list[LeadTimelineEvent])
def get_lead_history(lead_id: int, db: Session = Depends(get_db)):
    lead = get_item(db, Lead, lead_id)
    _, historico = _lead_events(db, lead)
    return historico


@router.post("/{lead_id}/converter-cliente")
def convert_lead_to_client(lead_id: int, db: Session = Depends(get_db)):
    lead = get_item(db, Lead, lead_id)
    existing = db.scalar(select(Client).where(Client.cpf == lead.cpf))
    if existing:
        return {"cliente": _client_payload(existing), "criado": False}

    client = Client(
        nome=lead.nome,
        cpf=lead.cpf,
        telefone=lead.telefone,
        email=lead.email,
        convenio=lead.produto_interesse,
        observacoes=f"Convertido do lead #{lead.id}. {lead.observacoes or ''}".strip(),
    )
    db.add(client)
    lead.status = "Qualificado" if lead.status == "Novo lead" else lead.status
    db.commit()
    db.refresh(client)
    return {"cliente": _client_payload(client), "criado": True}


@router.post("/{lead_id}/gerar-proposta")
def create_proposal_from_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = get_item(db, Lead, lead_id)
    client = db.scalar(select(Client).where(Client.cpf == lead.cpf))
    if not client:
        converted = convert_lead_to_client(lead_id, db)
        client = converted["cliente"]
    if not client:
        raise HTTPException(status_code=400, detail="Nao foi possivel vincular cliente ao lead")

    proposal = Proposal(
        cliente_id=client.id,
        produto=lead.produto_interesse,
        banco="Banco simulado",
        valor_liberado=0,
        parcela=0,
        prazo=84,
        status="Em andamento",
        observacoes=f"Proposta gerada a partir do lead #{lead.id}.",
    )
    lead.status = "Proposta enviada"
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return {"proposta": _proposal_payload(proposal), "cliente": _client_payload(client)}


def _client_payload(client: Client) -> dict:
    return {
        "id": client.id,
        "nome": client.nome,
        "cpf": client.cpf,
        "telefone": client.telefone,
        "email": client.email,
        "convenio": client.convenio,
    }


def _proposal_payload(proposal: Proposal) -> dict:
    return {
        "id": proposal.id,
        "cliente_id": proposal.cliente_id,
        "produto": proposal.produto,
        "banco": proposal.banco,
        "valor_liberado": proposal.valor_liberado,
        "parcela": proposal.parcela,
        "prazo": proposal.prazo,
        "status": proposal.status,
    }


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    return update_item(db, Lead, lead_id, payload)


@router.patch("/{lead_id}/status", response_model=LeadRead)
def update_lead_status(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    return update_item(db, Lead, lead_id, payload)


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    return delete_item(db, Lead, lead_id)
