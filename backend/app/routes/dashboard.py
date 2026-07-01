from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Lead, Proposal, Task
from app.services.privacy import public_person_payload

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumo")
def get_summary(db: Session = Depends(get_db)):
    today = date.today().isoformat()
    total_leads = db.scalar(select(func.count()).select_from(Lead)) or 0
    leads_novos = db.scalar(select(func.count()).select_from(Lead).where(Lead.status == "Novo lead")) or 0
    leads_atrasados = (
        db.scalar(
            select(func.count())
            .select_from(Lead)
            .where(Lead.proximo_contato.is_not(None), Lead.proximo_contato != "", Lead.proximo_contato < today)
        )
        or 0
    )
    propostas_andamento = db.scalar(select(func.count()).select_from(Proposal).where(Proposal.status != "Aprovado")) or 0
    propostas_aprovadas = db.scalar(select(func.count()).select_from(Proposal).where(Proposal.status == "Aprovado")) or 0
    valor_aprovado = db.scalar(select(func.sum(Proposal.valor_liberado)).where(Proposal.status == "Aprovado")) or 0
    tarefas_pendentes = db.scalar(select(func.count()).select_from(Task).where(Task.status != "Concluida")) or 0
    por_status = db.execute(select(Proposal.status, func.count()).group_by(Proposal.status)).all()
    leads_por_status = db.execute(select(Lead.status, func.count()).group_by(Lead.status).order_by(Lead.status)).all()
    leads_por_origem = db.execute(select(Lead.origem, func.count()).group_by(Lead.origem).order_by(Lead.origem)).all()
    proximos = db.scalars(
        select(Lead)
        .where(Lead.proximo_contato.is_not(None), Lead.proximo_contato != "")
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
