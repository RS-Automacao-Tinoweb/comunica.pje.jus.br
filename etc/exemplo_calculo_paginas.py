#!/usr/bin/env python3
"""
Demonstração: O código NÃO está limitado a 100 páginas!
Ele calcula dinamicamente baseado no 'count' da API.
"""

import math

def calcular_total_paginas(total_itens, itens_por_pagina):
    """MESMA função usada no código principal"""
    return math.ceil(total_itens / itens_por_pagina)


print("="*80)
print("🎯 DEMONSTRAÇÃO: Cálculo Dinâmico de Páginas")
print("="*80)
print()

# Exemplos reais da API do PJE
exemplos = [
    {
        "descricao": "Seu exemplo (5 itens por página)",
        "count": 10000,
        "itens_por_pagina": 5
    },
    {
        "descricao": "Configuração atual (100 itens por página)",
        "count": 10000,
        "itens_por_pagina": 100
    },
    {
        "descricao": "TJSP com muitos dados",
        "count": 50000,
        "itens_por_pagina": 100
    },
    {
        "descricao": "TJRR (exemplo real)",
        "count": 9785,
        "itens_por_pagina": 100
    },
    {
        "descricao": "Tribunal pequeno",
        "count": 350,
        "itens_por_pagina": 100
    },
    {
        "descricao": "Caso extremo (1 milhão de itens)",
        "count": 1000000,
        "itens_por_pagina": 100
    }
]

for i, exemplo in enumerate(exemplos, 1):
    count = exemplo["count"]
    itens_por_pagina = exemplo["itens_por_pagina"]
    
    # CALCULA dinamicamente (sem limitação!)
    total_paginas = calcular_total_paginas(count, itens_por_pagina)
    
    print(f"{i}. {exemplo['descricao']}")
    print(f"   {'─'*70}")
    print(f"   📊 count (total de itens): {count:,}")
    print(f"   📄 itensPorPagina: {itens_por_pagina}")
    print(f"   🧮 Cálculo: ceil({count:,} / {itens_por_pagina}) = {total_paginas:,}")
    print(f"   ✅ O código IRÁ PROCESSAR: {total_paginas:,} páginas")
    print(f"   📍 De página=1 até página={total_paginas:,}")
    print()

print("="*80)
print("🎊 CONCLUSÃO")
print("="*80)
print("✅ O código NÃO tem limite fixo de páginas!")
print("✅ Ele calcula dinamicamente: total_paginas = ceil(count / itensPorPagina)")
print("✅ Se count=10000 e itensPorPagina=100, processa 100 páginas")
print("✅ Se count=10000 e itensPorPagina=5, processa 2000 páginas")
print("✅ Se count=1000000 e itensPorPagina=100, processa 10.000 páginas!")
print()
print("🚀 O 'ITEMS_POR_PAGINA = 100' é apenas o tamanho de cada página,")
print("   NÃO é um limite de quantas páginas processar!")
print("="*80)
