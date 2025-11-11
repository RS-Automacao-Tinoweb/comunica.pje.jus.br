#!/usr/bin/env python3
"""
Teste de Paginação da API
Demonstra que TODAS as páginas são processadas
"""

import json
import requests
import time
from urllib.parse import urlencode

# Configurações
API_BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

PARAMS_BASE = {
    "siglaTribunal": "TJSP",
    "dataDisponibilizacaoInicio": "2025-11-10",
    "dataDisponibilizacaoFim": "2025-11-10"
}

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

ITEMS_POR_PAGINA = 10  # Pequeno para testar paginação
DELAY = 1

def fetch_page(pagina):
    """Busca uma página específica"""
    params = {
        **PARAMS_BASE,
        "pagina": pagina,
        "itensPorPagina": ITEMS_POR_PAGINA
    }
    
    url = f"{API_BASE_URL}?{urlencode(params)}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [!] Erro: {e}")
        return None

def main():
    print("="*60)
    print("TESTE DE PAGINAÇÃO - API")
    print("="*60)
    print()
    print(f"Tribunal: {PARAMS_BASE['siglaTribunal']}")
    print(f"Período: {PARAMS_BASE['dataDisponibilizacaoInicio']}")
    print(f"Itens por página: {ITEMS_POR_PAGINA}")
    print()
    
    all_ids = []
    pagina = 1
    total_processado = 0
    
    while True:
        print(f"\n[📄] PÁGINA {pagina}")
        print("-" * 60)
        
        data = fetch_page(pagina)
        
        if not data or data.get("status") != "success":
            print(f"[!] Erro ao buscar página {pagina}")
            break
        
        items = data.get("items", [])
        count_total = data.get("count", 0)
        
        if not items:
            print(f"[!] Nenhum item na página {pagina}")
            break
        
        # Coleta IDs para verificar duplicatas
        ids_desta_pagina = [item.get("id") for item in items]
        all_ids.extend(ids_desta_pagina)
        
        total_processado += len(items)
        
        # Mostra detalhes
        print(f"  Itens retornados: {len(items)}")
        print(f"  Total disponível: {count_total}")
        print(f"  Total processado até agora: {total_processado}/{count_total}")
        print(f"  IDs desta página: {ids_desta_pagina[:3]}... (mostrando 3 primeiros)")
        
        # Mostra alguns tipos de comunicação
        tipos = {}
        for item in items:
            tipo = item.get("tipoComunicacao")
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print(f"  Tipos nesta página:")
        for tipo, count in tipos.items():
            print(f"    - {tipo}: {count}")
        
        # Verifica se há mais páginas
        if len(items) < ITEMS_POR_PAGINA:
            print(f"\n[!] Última página (retornou {len(items)} < {ITEMS_POR_PAGINA})")
            break
        
        if total_processado >= count_total:
            print(f"\n[!] Todos os {count_total} itens foram coletados")
            break
        
        # Próxima página
        pagina += 1
        print(f"\n[⏳] Aguardando {DELAY}s antes da próxima página...")
        time.sleep(DELAY)
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"Total de páginas processadas: {pagina}")
    print(f"Total de itens coletados: {len(all_ids)}")
    print(f"IDs únicos: {len(set(all_ids))}")
    
    if len(all_ids) != len(set(all_ids)):
        print(f"⚠️  ATENÇÃO: Há {len(all_ids) - len(set(all_ids))} IDs duplicados!")
    else:
        print("✅ Nenhum ID duplicado - Paginação funcionando corretamente!")
    
    # Salva todos os IDs
    with open("test_paginacao_ids.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_paginas": pagina,
            "total_itens": len(all_ids),
            "ids_unicos": len(set(all_ids)),
            "todos_ids": all_ids
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[💾] IDs salvos em: test_paginacao_ids.json")
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO!")
    print("="*60)

if __name__ == "__main__":
    main()
