import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402
from app.models import AdminBootstrapToken, AuditLog, Client, Consent, Simulation, User  # noqa: E402
from app.services.admin_bootstrap import (  # noqa: E402
    activate_admin_bootstrap_token,
    create_admin_bootstrap_link,
    create_password_recovery_link,
    reset_password_with_recovery_token,
    token_hash,
    validate_password_recovery_token,
)
from app.services.security import hash_password  # noqa: E402

EXPECTED_TABLES = (
    "admin_bootstrap_tokens",
    "audit_logs",
    "auth_sessions",
    "backup_audit_logs",
    "clientes",
    "consents",
    "leads",
    "propostas",
    "schema_migrations",
    "simulations",
    "tarefas",
    "users",
    "whatsapp_messages",
)
SOURCE_ADMIN_EMAIL = "restore-admin@example.test"
SOURCE_ADMIN_PASSWORD = "RestoreAdmin@2026!"
RESTORE_ADMIN_PASSWORD = "RestoreAdmin@2026#"
SYNTHETIC_CPF = "000.000.000-00"


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL ausente para PostgreSQL descartavel.")
    parsed = urlsplit(url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "postgres"}:
        raise RuntimeError("Validacao de restore aceita somente PostgreSQL local descartavel.")
    query = parse_qs(parsed.query)
    if query.get("sslmode", [""])[0] == "require":
        raise RuntimeError("PostgreSQL descartavel do CI deve usar sslmode=disable.")
    return url


def engine():
    return create_engine(database_url())


def session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=engine())


def table_count(conn) -> int:
    return int(
        conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                """
            )
        ).scalar()
        or 0
    )


def row_counts(conn) -> dict[str, int]:
    return {table: int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0) for table in EXPECTED_TABLES}


def schema_metrics(conn) -> dict[str, int]:
    return {
        "tables": table_count(conn),
        "indexes": int(conn.execute(text("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'")).scalar() or 0),
        "constraints": int(
            conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.table_constraints
                    WHERE table_schema = 'public'
                    """
                )
            ).scalar()
            or 0
        ),
        "migrations": int(conn.execute(text("SELECT COUNT(*) FROM schema_migrations")).scalar() or 0),
    }


def assert_schema(conn) -> dict:
    tables = {
        str(row)
        for row in conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                """
            )
        ).scalars()
    }
    missing = set(EXPECTED_TABLES) - tables
    if missing:
        raise RuntimeError(f"Tabelas ausentes: {sorted(missing)}")
    metrics = schema_metrics(conn)
    if metrics["indexes"] <= 0 or metrics["constraints"] <= 0:
        raise RuntimeError("Indices ou constraints ausentes.")
    if metrics["migrations"] < 7:
        raise RuntimeError("Menos de 7 migrations PostgreSQL aplicadas.")
    return metrics


def seed_source(metrics_path: Path) -> None:
    Session = session_factory()
    now = datetime.utcnow()
    with Session.begin() as db:
        if db.scalar(select(User).where(User.email == SOURCE_ADMIN_EMAIL)):
            raise RuntimeError("Banco de origem nao esta vazio para dados sinteticos.")
        admin = User(
            nome="Admin Restore Sintetico",
            email=SOURCE_ADMIN_EMAIL,
            password_hash=hash_password(SOURCE_ADMIN_PASSWORD),
            role="admin",
            ativo=True,
            created_at=now,
            updated_at=now,
        )
        user = User(
            nome="Usuario Restore Sintetico",
            email="restore-user@example.test",
            password_hash=hash_password("RestoreUser@2026!"),
            role="operador",
            ativo=True,
            created_at=now,
            updated_at=now,
        )
        db.add_all([admin, user])
        db.flush()

        client = Client(
            nome="Cliente Restore Ficticio",
            cpf=SYNTHETIC_CPF,
            telefone="11900000000",
            email="cliente.restore@example.test",
            convenio="INSS",
            created_at=now,
            updated_at=now,
        )
        deleted_client = Client(
            nome="Cliente Soft Delete Ficticio",
            cpf="000.000.000-01",
            telefone="11900000001",
            email="softdelete.restore@example.test",
            convenio="FGTS",
            deleted_at=now,
            deleted_by=admin.id,
            deletion_reason="validacao sintetica",
            created_at=now,
            updated_at=now,
        )
        db.add_all([client, deleted_client])
        db.flush()

        db.add_all(
            [
                Consent(
                    customer_id=client.id,
                    channel="whatsapp",
                    granted=True,
                    purpose="validacao_restore",
                    status="active",
                    source="github-actions-sintetico",
                    terms_version="minuta-lgpd-v1",
                    created_at=now,
                    updated_at=now,
                ),
                Simulation(
                    customer_id=client.id,
                    cpf_masked="***.***.000-00",
                    produto="INSS",
                    rule_id="restore-ci",
                    rule_version="demo-v1",
                    created_by_user_id=admin.id,
                    input_json=json.dumps({"cpf": "***.***.000-00"}),
                    result_json=json.dumps({"status": "aprovado_sintetico"}),
                    payload_hash="restore-ci-synthetic-hash",
                    created_at=now,
                    updated_at=now,
                ),
                AuditLog(
                    actor_user_id=admin.id,
                    actor=admin.email,
                    action="restore_source_seeded",
                    entity_type="restore_validation",
                    metadata_json=json.dumps({"synthetic": True}),
                    created_at=now,
                    updated_at=now,
                ),
                AdminBootstrapToken(
                    user_id=admin.id,
                    email=admin.email,
                    token_hash=token_hash("synthetic-used-bootstrap-token"),
                    purpose="first_admin_activation",
                    expires_at=now + timedelta(minutes=60),
                    used_at=now,
                    created_at=now,
                    updated_at=now,
                    created_by_source="github_actions_restore_validation",
                ),
            ]
        )

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps({"last_synthetic_data_at": now.isoformat(), "email_domain": "example.test"}) + "\n", encoding="utf-8")
    print("Dados sinteticos de origem criados.")


def validate_source() -> None:
    with engine().connect() as conn:
        metrics = assert_schema(conn)
        counts = row_counts(conn)
    required_rows = {
        "admin_bootstrap_tokens": 1,
        "audit_logs": 1,
        "clientes": 2,
        "consents": 1,
        "simulations": 1,
        "users": 2,
    }
    for table, minimum in required_rows.items():
        if counts.get(table, 0) < minimum:
            raise RuntimeError(f"Dados sinteticos insuficientes em {table}.")
    print(f"Origem validada: {metrics['tables']} tabelas, {metrics['migrations']} migrations.")


def token_from_link(link: str) -> str:
    token = parse_qs(urlsplit(link).query).get("token", [""])[0]
    if len(token) < 32:
        raise RuntimeError("Token sintetico invalido.")
    return token


def validate_restore() -> None:
    with engine().connect() as conn:
        metrics = assert_schema(conn)
        counts_before = row_counts(conn)
        deleted_rows = int(conn.execute(text("SELECT COUNT(*) FROM clientes WHERE deleted_at IS NOT NULL")).scalar() or 0)
    if deleted_rows < 1:
        raise RuntimeError("Registro com soft delete ausente apos restore.")

    api = TestClient(app)
    health = api.get("/healthz")
    if health.status_code != 200 or health.json().get("database") != "ok":
        raise RuntimeError("Health check falhou no banco restaurado.")

    login = api.post("/auth/login", json={"email": SOURCE_ADMIN_EMAIL, "password": SOURCE_ADMIN_PASSWORD})
    if login.status_code != 200:
        raise RuntimeError("Login sintetico falhou apos restore.")
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    if api.get("/auth/me", headers=headers).status_code != 200:
        raise RuntimeError("Sessao sintetica invalida apos restore.")
    if api.post("/auth/logout", headers=headers).status_code != 200:
        raise RuntimeError("Logout sintetico falhou apos restore.")
    if api.get("/auth/me", headers=headers).status_code != 401:
        raise RuntimeError("Token reutilizado apos logout nao foi bloqueado.")

    Session = session_factory()
    with Session() as db:
        activation = create_admin_bootstrap_link(
            db,
            SOURCE_ADMIN_EMAIL,
            activation_base_url="https://example.test/ativar-admin",
            github_run_id="restore-ci",
            created_by_source="restore_validation",
        )
        activation_token = token_from_link(activation.link)
        activated = activate_admin_bootstrap_token(db, activation_token, RESTORE_ADMIN_PASSWORD, RESTORE_ADMIN_PASSWORD)
        if activated.email != SOURCE_ADMIN_EMAIL:
            raise RuntimeError("Ativacao sintetica retornou usuario inesperado.")

        recovery = create_password_recovery_link(
            db,
            SOURCE_ADMIN_EMAIL,
            reset_base_url="https://example.test/redefinir-senha",
            created_by_source="restore_validation",
        )
        if not recovery.created or not recovery.link:
            raise RuntimeError("Recuperacao sintetica nao criou token.")
        recovery_token = token_from_link(recovery.link)
        validate_password_recovery_token(db, recovery_token)
        reset_password_with_recovery_token(db, recovery_token, SOURCE_ADMIN_PASSWORD, SOURCE_ADMIN_PASSWORD)
        try:
            validate_password_recovery_token(db, recovery_token)
        except Exception:
            pass
        else:
            raise RuntimeError("Token de recuperacao reutilizado nao foi bloqueado.")

        expired = AdminBootstrapToken(
            user_id=activated.id,
            email=SOURCE_ADMIN_EMAIL,
            token_hash=token_hash("synthetic-expired-token-with-enough-length"),
            purpose="password_recovery",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
            created_by_source="restore_validation",
        )
        cross_purpose = AdminBootstrapToken(
            user_id=activated.id,
            email=SOURCE_ADMIN_EMAIL,
            token_hash=token_hash("synthetic-cross-purpose-token-with-enough-length"),
            purpose="first_admin_activation",
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            created_by_source="restore_validation",
        )
        db.add_all([expired, cross_purpose])
        db.commit()
        for blocked in ("synthetic-expired-token-with-enough-length", "synthetic-cross-purpose-token-with-enough-length"):
            try:
                validate_password_recovery_token(db, blocked)
            except Exception:
                continue
            raise RuntimeError("Token invalido foi aceito na recuperacao.")

    login_after_reset = api.post("/auth/login", json={"email": SOURCE_ADMIN_EMAIL, "password": SOURCE_ADMIN_PASSWORD})
    if login_after_reset.status_code != 200:
        raise RuntimeError("Login apos recuperacao sintetica falhou.")
    headers = {"Authorization": f"Bearer {login_after_reset.json()['access_token']}"}
    clients = api.get("/clientes", headers=headers)
    if clients.status_code != 200 or "Cliente Restore Ficticio" not in clients.text:
        raise RuntimeError("Cliente ficticio restaurado nao foi lido pelo backend.")
    consent = api.post("/consents", headers=headers, json={"customer_id": 1, "channel": "whatsapp", "source": "restore-ci"})
    if consent.status_code != 201:
        raise RuntimeError("Consentimento sintetico falhou apos restore.")
    simulation = api.get(f"/consultas/inss/{SYNTHETIC_CPF}", headers=headers)
    if simulation.status_code != 200:
        raise RuntimeError("Simulacao sintetica falhou apos restore.")
    deleted = api.delete("/clientes/1", headers=headers)
    if deleted.status_code != 200:
        raise RuntimeError("Soft delete sintetico falhou apos restore.")

    with engine().connect() as conn:
        counts_after = row_counts(conn)
        audit_count = int(conn.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar() or 0)
        consent_count = int(conn.execute(text("SELECT COUNT(*) FROM consents")).scalar() or 0)
        simulation_count = int(conn.execute(text("SELECT COUNT(*) FROM simulations")).scalar() or 0)
        soft_delete_count = int(conn.execute(text("SELECT COUNT(*) FROM clientes WHERE deleted_at IS NOT NULL")).scalar() or 0)
    if audit_count < 4 or consent_count < 2 or simulation_count < 2 or soft_delete_count < 1:
        raise RuntimeError("Integridade funcional incompleta apos restore.")
    if counts_after["users"] < counts_before["users"]:
        raise RuntimeError("Contagem de usuarios diminuiu apos validacao.")
    print(f"Restore validado: {metrics['tables']} tabelas, login, auth, consentimento, audit log, simulacao e soft delete OK.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida backup/restore PostgreSQL descartavel no CI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    seed = subparsers.add_parser("seed-source")
    seed.add_argument("--metrics", type=Path, default=Path("restore-metrics/source.json"))
    subparsers.add_parser("validate-source")
    subparsers.add_parser("validate-restore")
    args = parser.parse_args(argv)

    if os.environ.get("SUPABASE_DIRECT_URL") or os.environ.get("DIRECT_URL", "").startswith("postgresql://"):
        raise RuntimeError("Use somente DATABASE_URL local descartavel neste script.")
    if os.environ.get("REAL_DATA_MODE", "false").lower() != "false":
        raise RuntimeError("REAL_DATA_MODE deve permanecer false.")
    if args.command == "seed-source":
        seed_source(args.metrics)
    elif args.command == "validate-source":
        validate_source()
    elif args.command == "validate-restore":
        validate_restore()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
