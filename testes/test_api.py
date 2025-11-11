#!/usr/bin/env python3
"""
Teste rápido da API - Um único tribunal
"""

import json
import requests
from urllib.parse import urlencode

# Configurações
API_BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

PARAMS = {
    "pagina": 1,
    "itensPorPagina": 5,
    "siglaTribunal": "TJSP",
    "dataDisponibilizacaoInicio": "2025-11-01",
    "dataDisponibilizacaoFim": "2025-11-10"
}

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def main():
    print("="*60)
    print("TESTE DA API - TJSP")
    print("="*60)
    print()
    
    url = f"{API_BASE_URL}?{urlencode(PARAMS)}"
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Total de itens: {data.get('count')}")
        print(f"Itens retornados: {len(data.get('items', []))}")
        print()
        
        # Mostra primeiro item
        if data.get('items'):
            item = data['items'][0]
            print("PRIMEIRO ITEM:")
            print(f"  ID: {item.get('id')}")
            print(f"  Processo: {item.get('numeroprocessocommascara')}")
            print(f"  Tribunal: {item.get('siglaTribunal')}")
            print(f"  Tipo: {item.get('tipoComunicacao')}")
            print(f"  Classe: {item.get('nomeClasse')} (código: {item.get('codigoClasse')})")
            print(f"  Data: {item.get('datadisponibilizacao')}")
            print(f"  Órgão: {item.get('nomeOrgao')}")
            print()
            
            # Conta por tipo de comunicação
            tipos = {}
            for item in data['items']:
                tipo = item.get('tipoComunicacao')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            print("TIPOS DE COMUNICAÇÃO:")
            for tipo, count in tipos.items():
                print(f"  - {tipo}: {count}")
            print()
            
            # Conta por código de classe
            classes = {}
            for item in data['items']:
                classe = item.get('codigoClasse')
                nome = item.get('nomeClasse')
                classes[classe] = nome
            
            print("CLASSES ENCONTRADAS:")
            for codigo, nome in classes.items():
                print(f"  - {codigo}: {nome}")
            print()
            
            # Salva resposta completa
            with open("teste_api_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("[💾] Resposta completa salva em: teste_api_response.json")
        
        print("\n" + "="*60)
        print("TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"[!] ERRO: {e}")

if __name__ == "__main__":
    main()
