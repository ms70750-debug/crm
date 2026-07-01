from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Client, Lead, Proposal, Task, User
from app.services.privacy import public_person_payload
from app.services.security import current_user, is_partner

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumo")
def get_summary(db: Session = Depends(get_db), user: User = Depends(current_user)):
    today = date.today().isoformat()
    lead_scope = [Lead.responsavel == user.nome] if is_partner(user) else []
    proposal_scope = (
        [Proposal.cliente_id == Client.id, Client.cpf == Lead.cpf, Lead.responsavel == user.nome]
        if is_partner(user)
        else []
    )
    total_leads = db.scalar(select(func.count()).select_from(Lead).where(*lead_scope)) or 0
    leads_novos = db.scalar(select(func.count()).select_from(Lead).where(Lead.status == "Novo lead", *lead_scope)) or 0
    leads_atrasados = (
        db.scalar(
            select(func.count())
            .select_from(Lead)
            .where(Lead.proximo_contato.is_not(None), Lead.proximo_contato != "", Lead.proximo_contato < today, *lead_scope)
        )
        or 0
    )
    proposal_from = (Proposal, Client, Lead) if is_partner(user) else (Proposal,)
    propostas_andamento = db.scalar(select(func.count()).select_from(*proposal_from).where(Proposal.status != "Aprovado", *proposal_scope)) or 0
    propostas_aprovadas = db.scalar(select(func.count()).select_from(*proposal_from).where(Proposal.status == "Aprovado", *proposal_scope)) or 0
    valor_aprovado = db.scalar(select(func.sum(Proposal.valor_liberado)).select_from(*proposal_from).where(Proposal.status == "Aprovado", *proposal_scope)) or 0
    tarefas_pendentes = 0 if is_partner(user) else db.scalar(select(func.count()).select_from(Task).where(Task.status != "Concluida")) or 0
    por_status = db.execute(select(Proposal.status, func.count()).select_from(*proposal_from).where(*proposal_scope).group_by(Proposal.status)).all()
    leads_por_status = db.execute(select(Lead.status, func.count()).where(*lead_scope).group_by(Lead.status).order_by(Lead.status)).all()
    leads_por_origem = db.execute(select(Lead.origem, func.count()).where(*lead_scope).group_by(Lead.origem).order_by(Lead.origem)).all()
    proximos = db.scalars(
        select(Lead)
        .where(Lead.proximo_contato.is_not(None), Lead.proximo_contato != "", *lead_scope)
        .order_by(Lead.proximo_contato)
        .limit(5)
    ).all()
    return {
        "cards": {
            "total_leads": total_leads,
            "leads_novos": leads_novos,
            "propostas_em_andamento": propostas_andamento,
            "propostas_aprovadas": propostas_aprovadas,
            "valor_total_aprovado": valor_aprovado,
            "tarefas_pendentes": tarefas_pendentes,
            "leads_atrasados": leads_atrasados,
        },
        "propostas_por_status": [{"status": status, "total": total} for status, total in por_status],
        "leads_por_status": [{"status": status, "total": total} for status, total in leads_por_status],
        "leads_por_origem": [{"origem": origem, "total": total} for origem, total in leads_por_origem],
        "proximos_contatos": [public_person_payload(lead) for lead in proximos],
    }
