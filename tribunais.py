"""
Lista de tribunais extraída do select do site PJE
Filtrada para incluir apenas TJs e TRFs
"""

# Lista completa de tribunais TJ (Tribunais de Justiça)
TJS = [
    {"sigla": "TJAC", "nome": "Tribunal de Justiça do Acre"},
    {"sigla": "TJAL", "nome": "Tribunal de Justiça de Alagoas"},
    {"sigla": "TJAM", "nome": "Tribunal de Justiça do Amazonas"},
    {"sigla": "TJAP", "nome": "Tribunal de Justiça do Amapá"},
    {"sigla": "TJBA", "nome": "Tribunal de Justiça da Bahia"},
    {"sigla": "TJCE", "nome": "Tribunal de Justiça do Ceará"},
    {"sigla": "TJDFT", "nome": "Tribunal de Justiça do Distrito Federal e Territórios"},
    {"sigla": "TJES", "nome": "Tribunal de Justiça do Espírito Santo"},
    {"sigla": "TJGO", "nome": "Tribunal de Justiça de Goiás"},
    {"sigla": "TJMA", "nome": "Tribunal de Justiça do Maranhão"},
    {"sigla": "TJMG", "nome": "Tribunal de Justiça de Minas Gerais"},
    {"sigla": "TJMS", "nome": "Tribunal de Justiça do Mato Grosso do Sul"},
    {"sigla": "TJMT", "nome": "Tribunal de Justiça do Mato Grosso"},
    {"sigla": "TJPA", "nome": "Tribunal de Justiça do Pará"},
    {"sigla": "TJPB", "nome": "Tribunal de Justiça da Paraíba"},
    {"sigla": "TJPE", "nome": "Tribunal de Justiça de Pernambuco"},
    {"sigla": "TJPI", "nome": "Tribunal de Justiça do Piauí"},
    {"sigla": "TJPR", "nome": "Tribunal de Justiça do Paraná"},
    {"sigla": "TJRJ", "nome": "Tribunal de Justiça do Rio de Janeiro"},
    {"sigla": "TJRN", "nome": "Tribunal de Justiça do Rio Grande do Norte"},
    {"sigla": "TJRO", "nome": "Tribunal de Justiça de Rondônia"},
    {"sigla": "TJRR", "nome": "Tribunal de Justiça de Roraima"},
    {"sigla": "TJRS", "nome": "Tribunal de Justiça do Rio Grande do Sul"},
    {"sigla": "TJSC", "nome": "Tribunal de Justiça de Santa Catarina"},
    {"sigla": "TJSE", "nome": "Tribunal de Justiça de Sergipe"},
    {"sigla": "TJSP", "nome": "Tribunal de Justiça de São Paulo"},
    {"sigla": "TJTO", "nome": "Tribunal de Justiça do Estado de Tocantins"},
]

# Lista de TRFs (Tribunais Regionais Federais)
TRFS = [
    {"sigla": "TRF1", "nome": "Tribunal Regional Federal da 1ª Região"},
    {"sigla": "TRF2", "nome": "Tribunal Regional Federal da 2ª Região"},
    {"sigla": "TRF3", "nome": "Tribunal Regional Federal da 3ª Região"},
    {"sigla": "TRF4", "nome": "Tribunal Regional Federal da 4ª Região"},
    {"sigla": "TRF5", "nome": "Tribunal Regional Federal da 5ª Região"},
    {"sigla": "TRF6", "nome": "Tribunal Regional Federal da 6ª Região"},
]

# Combinar TJs e TRFs
TODOS_TRIBUNAIS = TJS + TRFS

# Apenas TJs
APENAS_TJS = TJS

# Apenas TRFs
APENAS_TRFS = TRFS

def get_tribunais_por_tipo(tipo="TODOS"):
    """
    Retorna lista de tribunais filtrada por tipo
    
    Args:
        tipo: "TJ", "TRF" ou "TODOS"
    
    Returns:
        Lista de dicionários com sigla e nome
    """
    if tipo.upper() == "TJ":
        return APENAS_TJS
    elif tipo.upper() == "TRF":
        return APENAS_TRFS
    else:
        return TODOS_TRIBUNAIS

def get_siglas(tipo="TODOS"):
    """
    Retorna apenas as siglas dos tribunais
    
    Args:
        tipo: "TJ", "TRF" ou "TODOS"
    
    Returns:
        Lista de siglas
    """
    tribunais = get_tribunais_por_tipo(tipo)
    return [t["sigla"] for t in tribunais]
