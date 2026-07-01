from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Lead, Proposal, Task


def seed_database(db: Session) -> None:
    if db.scalar(select(Lead).limit(1)):
        return

    leads = [
        Lead(nome="Maria Helena Souza", cpf="123.456.789-10", telefone="(11) 98888-1001", email="maria@example.com", origem="Landing page", produto_interesse="INSS", status="Novo lead", responsavel="Ana", proximo_contato="2026-07-02"),
        Lead(nome="Joao Pereira Lima", cpf="234.567.890-11", telefone="(21) 97777-2002", email="joao@example.com", origem="WhatsApp", produto_interesse="FGTS", status="Qualificado", responsavel="Bruno", proximo_contato="2026-07-03"),
        Lead(nome="Carla Martins", cpf="345.678.901-12", telefone="(31) 96666-3003", email="carla@example.com", origem="Indicação", produto_interesse="INSS", status="Simulado", responsavel="Ana", proximo_contato="2026-07-04"),
        Lead(nome="Roberto Alves", cpf="456.789.012-13", telefone="(41) 95555-4004", email="roberto@example.com", origem="Campanha", produto_interesse="FGTS", status="Proposta enviada", responsavel="Marina", proximo_contato="2026-07-05"),
    ]
    db.add_all(leads)

    clients = [
        Client(nome="Eliane Costa", cpf="567.890.123-14", telefone="(11) 94444-5005", email="eliane@example.com", data_nascimento="1964-08-12", beneficio="1234567890", convenio="INSS", banco_pagamento="Caixa"),
        Client(nome="Antonio Ramos", cpf="678.901.234-15", telefone="(71) 93333-6006", email="antonio@example.com", data_nascimento="1958-02-25", beneficio="9988776655", convenio="INSS", banco_pagamento="Banco do Brasil"),
    ]
    db.add_all(clients)
    db.flush()

    db.add_all(
        [
            Proposal(cliente_id=clients[0].id, produto="INSS", banco="Banco Alfa", valor_liberado=12800, parcela=342.5, prazo=84, status="Aprovado"),
            Proposal(cliente_id=clients[1].id, produto="FGTS", banco="Banco Beta", valor_liberado=4200, parcela=0, prazo=10, status="Em andamento"),
        ]
    )
    db.add_all(
        [
            Task(titulo="Conferir documentos da Maria", prioridade="Alta", responsavel="Ana", lead_id=1, data_vencimento="2026-07-02"),
            Task(titulo="Retornar proposta FGTS", prioridade="Media", responsavel="Bruno", lead_id=2, data_vencimento="2026-07-03"),
            Task(titulo="Validar simulacao INSS", status="Concluida", prioridade="Baixa", responsavel="Marina", cliente_id=1, data_vencimento="2026-06-30"),
        ]
    )
    db.commit()
