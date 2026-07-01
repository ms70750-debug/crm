from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import User
from app.schemas.security import LoginRequest, LoginResponse
from app.services.security import check_rate_limit, create_token, demo_token_expiration, log_audit, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"login:{client_ip}:{payload.email}", limit=5, window_seconds=60)
    user = db.scalar(select(User).where(User.email == payload.email))
    ok = bool(user and user.ativo and verify_password(payload.password, user.password_hash))
    log_audit(db, "login_success" if ok else "login_failed", "user", user.id if user else None, actor=payload.email, metadata={"email": payload.email, "ip": client_ip})
    db.commit()
    if not ok or not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    return {
        "access_token": create_token(user),
        "expires_at": demo_token_expiration(),
        "user": {"id": user.id, "nome": user.nome, "email": user.email, "role": user.role},
    }
