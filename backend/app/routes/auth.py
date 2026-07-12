from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.environment import demo_mode_enabled
from app.services.readiness import production_mode_enabled
from app.database.session import get_db
from app.models import User
from app.schemas.security import DemoLoginRequest, LoginRequest, LoginResponse, UserRead
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
    if production_mode_enabled() or not demo_mode_enabled():
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
