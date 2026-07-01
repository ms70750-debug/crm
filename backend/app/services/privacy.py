import re


def only_digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def mask_cpf(value: str | None) -> str:
    digits = only_digits(value)
    if len(digits) < 3:
        return "***.***.***-**"
    return f"***.***.{digits[-4:-2]}{digits[-2:]}-**" if len(digits) < 11 else f"***.***.{digits[6:9]}-**"


def mask_phone(value: str | None) -> str:
    digits = only_digits(value)
    if len(digits) < 4:
        return "(***) *****-****"
    return f"(***) *****-{digits[-4:]}"


def mask_email(value: str | None) -> str:
    if not value or "@" not in value:
        return ""
    user, domain = value.split("@", 1)
    first = user[:1] or "*"
    return f"{first}***@{domain}"


def public_person_payload(item) -> dict:
    data = {
        "id": item.id,
        "nome": item.nome,
        "cpf": mask_cpf(item.cpf),
        "telefone": mask_phone(item.telefone),
        "email": mask_email(item.email),
    }
    for field in ["origem", "produto_interesse", "status", "prioridade", "responsavel", "proximo_contato", "convenio", "beneficio", "banco_pagamento", "observacoes"]:
        if hasattr(item, field):
            data[field] = getattr(item, field)
    for field in ["data_criacao", "deleted_at"]:
        if hasattr(item, field):
            value = getattr(item, field)
            data[field] = value.isoformat() if value else None
    return data
