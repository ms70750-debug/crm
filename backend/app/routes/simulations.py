from fastapi import APIRouter

router = APIRouter(prefix="/consultas", tags=["consultas"])


@router.get("/inss/{cpf}")
def simulate_inss(cpf: str):
    return {
        "cpf": cpf,
        "modo": "simulation",
        "beneficio": "1234567890",
        "convenio": "INSS",
        "margem_disponivel": 418.72,
        "banco_pagamento": "Banco simulado",
        "elegivel": True,
    }


@router.get("/fgts/{cpf}")
def simulate_fgts(cpf: str):
    return {
        "cpf": cpf,
        "modo": "simulation",
        "saldo_estimado": 7420.35,
        "valor_liberado": 3820.0,
        "parcelas_antecipaveis": 10,
        "elegivel": True,
    }
