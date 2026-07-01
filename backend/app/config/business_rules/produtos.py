DEMO_NOTICE = "Valores demonstrativos. Nao usar para proposta real sem validacao comercial."

PRODUCT_RULES = {
    "INSS": {
        "rule_id": "BR-INSS-DEMO-001",
        "produto": "INSS",
        "convenio": "INSS",
        "margem_maxima_demonstrativa": 418.72,
        "taxa_demonstrativa": 1.78,
        "vigencia_inicial": "2026-07-01",
        "vigencia_final": None,
        "status": "ativo",
        "notice": DEMO_NOTICE,
    },
    "FGTS": {
        "rule_id": "BR-FGTS-DEMO-001",
        "produto": "FGTS",
        "convenio": "FGTS",
        "margem_maxima_demonstrativa": 0,
        "taxa_demonstrativa": 1.99,
        "vigencia_inicial": "2026-07-01",
        "vigencia_final": None,
        "status": "ativo",
        "notice": DEMO_NOTICE,
    },
}
