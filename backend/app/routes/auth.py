from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import User
from app.schemas.security import LoginRequest, LoginResponse, UserRead
from app.services.security import check_rate_limit, create_token, current_user, demo_token_expiration, log_audit, require_roles, user_payload, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "local"
    check_rate_limit(f"login:{client_ip}:{payload.email}", limit=10, window_seconds=60)
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
        "user": user_payload(user),
    }


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user_payload(user)


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), user=Depends(require_roles("admin", "supervisor"))):
    return [user_payload(item) for item in db.scalars(select(User).order_by(User.id)).all()]
