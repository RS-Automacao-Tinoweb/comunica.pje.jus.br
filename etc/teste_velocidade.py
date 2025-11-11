#!/usr/bin/env python3
"""
Script de teste para comparar velocidade entre versões
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor

# Simula configurações
API_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
TOTAL_PAGINAS = 20  # Teste com 20 páginas

def fetch_sequencial():
    """Simula versão original - uma requisição por vez"""
    print("\n" + "="*60)
    print("TESTE 1: Versão ORIGINAL (Sequencial)")
    print("="*60)
    
    inicio = time.time()
    
    for i in range(1, TOTAL_PAGINAS + 1):
        # Simula requisição
        time.sleep(0.1)  # Simula latência da rede
        print(f"  Página {i}/{TOTAL_PAGINAS}", end="\r")
        
        # Delay fixo (problema da versão original)
        time.sleep(2)
    
    tempo_total = time.time() - inicio
    
    print(f"\n\n✓ Concluído em {tempo_total:.1f} segundos")
    print(f"  Velocidade: {TOTAL_PAGINAS/tempo_total:.2f} páginas/s")
    
    return tempo_total


def fetch_paralelo():
    """Simula versão otimizada - múltiplas requisições simultâneas"""
    print("\n" + "="*60)
    print("TESTE 2: Versão OTIMIZADA (Paralelo)")
    print("="*60)
    
    inicio = time.time()
    
    def processar_pagina(pagina):
        # Simula requisição
        time.sleep(0.1)  # Simula latência da rede
        return pagina
    
    # Processa 10 páginas por vez
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(processar_pagina, i) for i in range(1, TOTAL_PAGINAS + 1)]
        
        completadas = 0
        for future in futures:
            future.result()
            completadas += 1
            print(f"  Página {completadas}/{TOTAL_PAGINAS}", end="\r")
    
    tempo_total = time.time() - inicio
    
    print(f"\n\n✓ Concluído em {tempo_total:.1f} segundos")
    print(f"  Velocidade: {TOTAL_PAGINAS/tempo_total:.2f} páginas/s")
    
    return tempo_total


def main():
    print("="*60)
    print("🚀 TESTE DE PERFORMANCE - Original vs Otimizado")
    print("="*60)
    print(f"\nProcessando {TOTAL_PAGINAS} páginas...\n")
    
    # Teste sequencial
    tempo_original = fetch_sequencial()
    
    time.sleep(1)
    
    # Teste paralelo
    tempo_otimizado = fetch_paralelo()
    
    # Comparação
    print("\n" + "="*60)
    print("📊 COMPARAÇÃO")
    print("="*60)
    print(f"Versão Original:   {tempo_original:.1f}s")
    print(f"Versão Otimizada:  {tempo_otimizado:.1f}s")
    print(f"\n🚀 Ganho: {tempo_original/tempo_otimizado:.1f}x mais rápido!")
    print("="*60)
    
    # Projeção para caso real
    print("\n" + "="*60)
    print("📈 PROJEÇÃO PARA CASO REAL (100 páginas)")
    print("="*60)
    
    fator = 100 / TOTAL_PAGINAS
    proj_original = tempo_original * fator
    proj_otimizado = tempo_otimizado * fator
    
    print(f"Versão Original:   {proj_original:.1f}s ({proj_original/60:.1f} min)")
    print(f"Versão Otimizada:  {proj_otimizado:.1f}s ({proj_otimizado/60:.1f} min)")
    print(f"\n⏱️  Economia de tempo: {(proj_original - proj_otimizado)/60:.1f} minutos!")
    print("="*60)


if __name__ == "__main__":
    main()
