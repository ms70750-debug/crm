import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.environment import demo_mode_enabled, public_demo_login_enabled
from app.services.readiness import production_mode_enabled
from app.database.session import get_db
from app.models import User
from app.schemas.security import (
    AdminBootstrapActivateRequest,
    AdminBootstrapValidateResponse,
    DemoLoginRequest,
    LoginRequest,
    LoginResponse,
    PasswordRecoveryConfirmRequest,
    PasswordRecoveryConfirmResponse,
    PasswordRecoveryRequest,
    PasswordRecoveryRequestResponse,
    PasswordRecoveryValidateResponse,
    UserRead,
)
from app.services.admin_bootstrap import (
    PASSWORD_RECOVERY_BASE_URL,
    PASSWORD_RECOVERY_TTL_MINUTES,
    AdminBootstrapBlocked,
    AdminBootstrapError,
    activate_admin_bootstrap_token,
    create_password_recovery_link,
    reset_password_with_recovery_token,
    validate_admin_bootstrap_token,
    validate_password_recovery_token,
)
from app.services.auth_email import AuthEmailError, send_password_recovery_email
from app.services.security import (
    SESSION_COOKIE_NAME,
    check_rate_limit,
    create_session_token,
    current_user,
    demo_token_expiration,
    log_audit,
    require_roles,
    revoke_session_from_payload,
    session_cookie_options,
    user_payload,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
DEMO_EMAIL_BY_ROLE = {
    "admin": "admin@bbbconsig.demo",
    "supervisor": "supervisor@bbbconsig.demo",
    "operador": "operador@bbbconsig.demo",
    "parceiro": "parceiro@bbbconsig.demo",
}


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"login:{client_ip}:{payload.email}", limit=10, window_seconds=60)
    user = db.scalar(select(User).where(User.email == payload.email))
    ok = bool(user and user.ativo and verify_password(payload.password, user.password_hash))
    log_audit(db, "login_success" if ok else "login_failed", "user", user.id if user else None, actor=payload.email, metadata={"email": payload.email, "ip": client_ip})
    db.commit()
    if not ok or not user:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    token = create_session_token(db, user)
    response.set_cookie(value=token, **session_cookie_options())
    db.commit()
    return {
        "access_token": token,
        "expires_at": demo_token_expiration(),
        "user": user_payload(user),
    }


@router.post("/demo-login", response_model=LoginResponse)
def demo_login(payload: DemoLoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    if production_mode_enabled() or not demo_mode_enabled() or not public_demo_login_enabled():
        raise HTTPException(status_code=403, detail="Login de demonstracao indisponivel fora do modo demo")
    role = payload.role.strip().lower()
    email = DEMO_EMAIL_BY_ROLE.get(role)
    if not email:
        raise HTTPException(status_code=400, detail="Perfil de demonstracao invalido")
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"demo-login:{client_ip}:{role}", limit=10, window_seconds=60)
    user = db.scalar(select(User).where(User.email == email, User.ativo.is_(True)))
    if not user:
        raise HTTPException(status_code=404, detail="Usuario de demonstracao nao encontrado")
    log_audit(db, "demo_login_success", "user", user.id, actor=email, actor_user_id=user.id, metadata={"role": role, "ip": client_ip})
    db.commit()
    token = create_session_token(db, user)
    response.set_cookie(value=token, **session_cookie_options())
    db.commit()
    return {
        "access_token": token,
        "expires_at": demo_token_expiration(),
        "user": user_payload(user),
    }


@router.get("/admin-bootstrap/validate", response_model=AdminBootstrapValidateResponse)
def validate_admin_bootstrap(
    request: Request,
    token: str | None = Header(default=None, alias="X-Admin-Bootstrap-Token"),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"admin-bootstrap-validate:{client_ip}", limit=6, window_seconds=60)
    try:
        record = validate_admin_bootstrap_token(db, token or "")
    except AdminBootstrapError:
        return {"valid": False, "expires_at": None}
    return {"valid": True, "expires_at": record.expires_at}


@router.post("/admin-bootstrap/activate", response_model=LoginResponse)
def activate_admin_bootstrap(payload: AdminBootstrapActivateRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"admin-bootstrap-activate:{client_ip}", limit=5, window_seconds=300)
    try:
        user = activate_admin_bootstrap_token(db, payload.token, payload.password, payload.password_confirmation)
    except AdminBootstrapBlocked as exc:
        raise HTTPException(status_code=409, detail="Ativacao indisponivel") from exc
    except AdminBootstrapError as exc:
        raise HTTPException(status_code=400, detail="Link invalido ou expirado") from exc
    token = create_session_token(db, user)
    response.set_cookie(value=token, **session_cookie_options())
    db.commit()
    return {
        "access_token": token,
        "expires_at": demo_token_expiration(),
        "user": user_payload(user),
    }


@router.post("/password-recovery/request", response_model=PasswordRecoveryRequestResponse)
def request_password_recovery(payload: PasswordRecoveryRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    email_key = (payload.email or "").strip().lower()[:140] or "blank"
    check_rate_limit(f"password-recovery-request:{client_ip}:{email_key}", limit=5, window_seconds=300)
    result = create_password_recovery_link(
        db,
        payload.email,
        reset_base_url=os.environ.get("PASSWORD_RECOVERY_BASE_URL", PASSWORD_RECOVERY_BASE_URL),
        created_by_source="api",
    )
    if result.created and result.link:
        try:
            send_password_recovery_email(db, to_email=payload.email, recovery_link=result.link, expires_minutes=PASSWORD_RECOVERY_TTL_MINUTES)
        except AuthEmailError:
            log_audit(db, "password_recovery_email_failed", "auth_email", actor="system", metadata={"email": payload.email})
            db.commit()
    return {
        "ok": True,
        "message": "Se o e-mail estiver cadastrado e ativo, um link de redefinicao sera preparado para envio seguro.",
    }


@router.get("/password-recovery/validate", response_model=PasswordRecoveryValidateResponse)
def validate_password_recovery(
    request: Request,
    token: str | None = Header(default=None, alias="X-Password-Recovery-Token"),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"password-recovery-validate:{client_ip}", limit=8, window_seconds=60)
    try:
        record = validate_password_recovery_token(db, token or "")
    except AdminBootstrapError:
        return {"valid": False, "expires_at": None}
    return {"valid": True, "expires_at": record.expires_at}


@router.post("/password-recovery/confirm", response_model=PasswordRecoveryConfirmResponse)
def confirm_password_recovery(payload: PasswordRecoveryConfirmRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"password-recovery-confirm:{client_ip}", limit=5, window_seconds=300)
    try:
        reset_password_with_recovery_token(db, payload.token, payload.password, payload.password_confirmation)
    except AdminBootstrapError as exc:
        raise HTTPException(status_code=400, detail="Link invalido, expirado ou senha invalida") from exc
    return {"ok": True}


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user_payload(user)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db), user: User = Depends(current_user)):
    revoke_session_from_payload(db, getattr(request.state, "auth_payload", {}), reason="logout")
    log_audit(db, "logout", "user", user.id, actor=user.email, actor_user_id=user.id)
    db.commit()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor"))):
    return [user_payload(item) for item in db.scalars(select(User).order_by(User.id)).all()]
