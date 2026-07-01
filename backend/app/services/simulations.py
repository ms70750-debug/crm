import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.config.business_rules.produtos import PRODUCT_RULES
from app.models import Simulation
from app.services.privacy import mask_cpf
from app.services.security import log_audit


def simulate_product(db: Session, produto: str, cpf: str, customer_id: int | None = None) -> dict:
    rule = PRODUCT_RULES[produto]
    if produto == "INSS":
        result = {
            "cpf": mask_cpf(cpf),
            "modo": "simulation",
            "beneficio": "1234567890",
            "convenio": "INSS",
            "margem_disponivel": rule["margem_maxima_demonstrativa"],
            "banco_pagamento": "Banco simulado",
            "elegivel": True,
            "regra_aplicada": rule,
        }
    else:
        saldo = 7420.35
        result = {
            "cpf": mask_cpf(cpf),
            "modo": "simulation",
            "saldo_estimado": saldo,
            "valor_liberado": 3820.0,
            "parcelas_antecipaveis": 10,
            "elegivel": True,
            "regra_aplicada": rule,
        }
    input_payload = {"cpf": mask_cpf(cpf), "produto": produto, "customer_id": customer_id}
    snapshot_payload = {"input": input_payload, "rule": rule, "result": result, "timestamp": datetime.utcnow().isoformat()}
    payload_hash = hashlib.sha256(json.dumps(snapshot_payload, sort_keys=True).encode()).hexdigest()
    simulation = Simulation(
        customer_id=customer_id,
        cpf_masked=mask_cpf(cpf),
        produto=produto,
        rule_id=rule["rule_id"],
        input_json=json.dumps(input_payload, ensure_ascii=False),
        result_json=json.dumps(result, ensure_ascii=False),
        payload_hash=payload_hash,
    )
    db.add(simulation)
    db.flush()
    log_audit(db, "simulation_created", "simulation", simulation.id, metadata={"cpf": cpf, "produto": produto, "rule_id": rule["rule_id"]})
    db.commit()
    result["snapshot"] = {"id": simulation.id, "payload_hash": payload_hash, "rule_id": rule["rule_id"]}
    return result
