from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.simulations import simulate_product

router = APIRouter(prefix="/consultas", tags=["consultas"])


@router.get("/inss/{cpf}")
def simulate_inss(cpf: str, db: Session = Depends(get_db)):
    return simulate_product(db, "INSS", cpf)


@router.get("/fgts/{cpf}")
def simulate_fgts(cpf: str, db: Session = Depends(get_db)):
    return simulate_product(db, "FGTS", cpf)
