import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Lead, Proposal, Task, User
from app.services.admin_bootstrap import normalize_email
from app.services.security import hash_password

# Dados exclusivamente ficticios para demonstracao. Nao usar CPF, beneficio,
# conta bancaria, contrato ou dados pessoais reais nestes seeds.
DEMO_USERS = [
    ("Admin Demo", "admin@bbbconsig.demo", "BbbConsig@2026", "admin"),
    ("Supervisora Demo", "supervisor@bbbconsig.demo", "Supervisor@2026", "supervisor"),
    ("Operador Demo", "operador@bbbconsig.demo", "Operador@2026", "operador"),
    ("Parceiro Demo", "parceiro@bbbconsig.demo", "Parceiro@2026", "parceiro"),
]


def seed_database(db: Session) -> None:
    for nome, email, password, role in DEMO_USERS:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            user.nome = nome
            user.role = role
            user.ativo = True
        else:
            db.add(User(nome=nome, email=email, password_hash=hash_password(password), role=role))
    db.commit()

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


def ensure_primary_admin_from_env(db: Session) -> bool:
    email = os.environ.get("PRIMARY_ADMIN_EMAIL", "").strip()
    password = os.environ.get("PRIMARY_ADMIN_PASSWORD", "")
    name = os.environ.get("PRIMARY_ADMIN_NAME", "").strip() or "Administrador Principal"
    if not email or not password:
        return False

    normalized_email = normalize_email(email)
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user:
        user.nome = name
        user.role = "admin"
        user.ativo = True
    else:
        db.add(
            User(
                nome=name,
                email=normalized_email,
                password_hash=hash_password(password),
                role="admin",
                ativo=True,
            )
        )
    db.commit()
    return True
