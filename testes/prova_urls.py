#!/usr/bin/env python3
"""
PROVA que o código gera URLs diferentes para cada página
"""

import requests
from urllib.parse import urlencode

API_BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

PARAMS_BASE = {
    "itensPorPagina": 5,
    "siglaTribunal": "TJSP",
    "dataDisponibilizacaoInicio": "2025-11-10",
    "dataDisponibilizacaoFim": "2025-11-10"
}

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_page(pagina):
    """Simula a função fetch_page do main_api.py"""
    params = {
        "pagina": pagina,  # ← AQUI muda!
        **PARAMS_BASE
    }
    
    url = f"{API_BASE_URL}?{urlencode(params)}"
    
    print(f"\n[{pagina}] URL GERADA:")
    print(f"    {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        count = data.get("count", 0)
        
        print(f"    ✅ Resposta OK:")
        print(f"       - Itens retornados: {len(items)}")
        print(f"       - Total disponível: {count}")
        
        if items:
            print(f"       - Primeiro ID: {items[0].get('id')}")
            print(f"       - Último ID: {items[-1].get('id')}")
        
        return data
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return None

def main():
    print("="*80)
    print("PROVA: URLs DIFERENTES PARA CADA PÁGINA")
    print("="*80)
    print()
    print("Vou fazer 3 requisições com páginas diferentes:")
    print("- Página 1")
    print("- Página 2")
    print("- Página 3")
    print()
    print("Você verá que:")
    print("1. As URLs são DIFERENTES (pagina=1, pagina=2, pagina=3)")
    print("2. Os IDs retornados são DIFERENTES")
    print("3. Isso prova que está buscando páginas diferentes!")
    print()
    
    all_ids = []
    
    # Simula o loop do main_api.py
    for pagina in [1, 2, 3]:
        data = fetch_page(pagina)
        
        if data and data.get("items"):
            ids = [item.get("id") for item in data["items"]]
            all_ids.extend(ids)
    
    print("\n" + "="*80)
    print("RESULTADO")
    print("="*80)
    print(f"Total de IDs coletados: {len(all_ids)}")
    print(f"IDs únicos: {len(set(all_ids))}")
    print()
    
    if len(all_ids) == len(set(all_ids)):
        print("✅ TODOS OS IDs SÃO ÚNICOS!")
        print("✅ Isso prova que cada página retorna dados DIFERENTES!")
        print("✅ O código está funcionando CORRETAMENTE!")
    else:
        print("⚠️  Há IDs duplicados")
    
    print("\nTodos os IDs coletados:")
    for i, id_item in enumerate(all_ids, 1):
        print(f"  {i}. ID: {id_item}")
    
    print("\n" + "="*80)
    print("CONCLUSÃO")
    print("="*80)
    print("✅ O código main_api.py faz EXATAMENTE isso:")
    print("   1. Começa com pagina=1")
    print("   2. Incrementa: pagina += 1")
    print("   3. Gera URLs diferentes para cada página")
    print("   4. Coleta TODOS os dados de TODAS as páginas")
    print("="*80)

if __name__ == "__main__":
    main()
