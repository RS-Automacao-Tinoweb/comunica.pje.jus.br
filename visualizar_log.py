#!/usr/bin/env python3
"""
Visualizador de Logs do Scraper
Mostra os logs de requisições de forma organizada e amigável
"""

import json
import os
from datetime import datetime
from collections import defaultdict

LOG_FILE = "scraper_requests.log"

def load_logs():
    """Carrega todos os logs do arquivo"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ Arquivo de log não encontrado: {LOG_FILE}")
        print("Execute o scraper primeiro: python main_api.py")
        return []
    
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    return logs

def show_summary(logs):
    """Mostra resumo geral dos logs"""
    if not logs:
        print("Nenhum log encontrado.")
        return
    
    total = len(logs)
    success = sum(1 for log in logs if log.get("status") == "success")
    errors = sum(1 for log in logs if log.get("status") == "error")
    
    # Agrupa por tribunal
    por_tribunal = defaultdict(list)
    for log in logs:
        por_tribunal[log.get("tribunal")].append(log)
    
    print("="*80)
    print("RESUMO GERAL DOS LOGS")
    print("="*80)
    print(f"Total de requisições: {total}")
    print(f"  ✅ Sucesso: {success}")
    print(f"  ❌ Erros: {errors}")
    print(f"\nTribunais processados: {len(por_tribunal)}")
    print()
    
    # Mostra estatísticas por tribunal
    print("ESTATÍSTICAS POR TRIBUNAL:")
    print("-" * 80)
    for tribunal, tribunal_logs in sorted(por_tribunal.items()):
        success_count = sum(1 for log in tribunal_logs if log.get("status") == "success")
        error_count = sum(1 for log in tribunal_logs if log.get("status") == "error")
        total_pages = len(set(log.get("pagina") for log in tribunal_logs))
        
        # Total de itens retornados
        total_items = 0
        for log in tribunal_logs:
            if log.get("response_summary"):
                total_items += log["response_summary"].get("itens_retornados", 0)
        
        print(f"  {tribunal}:")
        print(f"    - Requisições: {len(tribunal_logs)} (✅ {success_count} | ❌ {error_count})")
        print(f"    - Páginas: {total_pages}")
        print(f"    - Itens retornados: {total_items}")
    
    print()

def show_detailed_logs(logs, tribunal=None, show_urls=False):
    """Mostra logs detalhados"""
    filtered_logs = logs
    
    if tribunal:
        filtered_logs = [log for log in logs if log.get("tribunal") == tribunal]
        if not filtered_logs:
            print(f"❌ Nenhum log encontrado para o tribunal: {tribunal}")
            return
    
    print("="*80)
    print(f"LOGS DETALHADOS{f' - {tribunal}' if tribunal else ''}")
    print("="*80)
    print()
    
    for i, log in enumerate(filtered_logs, 1):
        status_emoji = "✅" if log.get("status") == "success" else "❌"
        
        print(f"[{i}] {status_emoji} {log.get('timestamp')} | {log.get('tribunal')} | Página {log.get('pagina')}")
        
        if show_urls:
            print(f"    URL: {log.get('url')}")
        
        if log.get("response_summary"):
            summary = log["response_summary"]
            print(f"    Total disponível: {summary.get('total_disponivel')}")
            print(f"    Itens retornados: {summary.get('itens_retornados')}")
        
        if log.get("error"):
            print(f"    ⚠️  Erro: {log.get('error')}")
        
        print()

def show_errors(logs):
    """Mostra apenas os logs com erro"""
    error_logs = [log for log in logs if log.get("status") == "error"]
    
    if not error_logs:
        print("✅ Nenhum erro encontrado!")
        return
    
    print("="*80)
    print(f"ERROS ENCONTRADOS ({len(error_logs)})")
    print("="*80)
    print()
    
    for i, log in enumerate(error_logs, 1):
        print(f"[{i}] {log.get('timestamp')} | {log.get('tribunal')} | Página {log.get('pagina')}")
        print(f"    URL: {log.get('url')}")
        print(f"    ⚠️  Erro: {log.get('error')}")
        print()

def show_timeline(logs):
    """Mostra linha do tempo das requisições"""
    if not logs:
        print("Nenhum log encontrado.")
        return
    
    print("="*80)
    print("LINHA DO TEMPO DAS REQUISIÇÕES")
    print("="*80)
    print()
    
    current_tribunal = None
    for log in logs:
        tribunal = log.get("tribunal")
        pagina = log.get("pagina")
        status = log.get("status")
        timestamp = log.get("timestamp")
        
        status_emoji = "✅" if status == "success" else "❌"
        
        # Mostra separador quando muda de tribunal
        if tribunal != current_tribunal:
            if current_tribunal is not None:
                print()
            print(f"📍 {tribunal}")
            print("-" * 80)
            current_tribunal = tribunal
        
        items = ""
        if log.get("response_summary"):
            items = f" → {log['response_summary'].get('itens_retornados')} itens"
        
        print(f"  {timestamp} | {status_emoji} Página {pagina:2d}{items}")
    
    print()

def export_to_json(logs, output_file="logs_analise.json"):
    """Exporta logs para arquivo JSON formatado"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Logs exportados para: {output_file}")

def main():
    print("="*80)
    print("VISUALIZADOR DE LOGS - SCRAPER PJE API")
    print("="*80)
    print()
    
    logs = load_logs()
    
    if not logs:
        return
    
    while True:
        print("\n" + "="*80)
        print("MENU")
        print("="*80)
        print("1. Resumo Geral")
        print("2. Logs Detalhados (todos)")
        print("3. Logs Detalhados com URLs")
        print("4. Logs de um Tribunal Específico")
        print("5. Apenas Erros")
        print("6. Linha do Tempo")
        print("7. Exportar para JSON")
        print("0. Sair")
        print()
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == "1":
            show_summary(logs)
        
        elif choice == "2":
            show_detailed_logs(logs, show_urls=False)
        
        elif choice == "3":
            show_detailed_logs(logs, show_urls=True)
        
        elif choice == "4":
            tribunal = input("Digite a sigla do tribunal (ex: TJSP): ").strip().upper()
            show_detailed_logs(logs, tribunal=tribunal, show_urls=True)
        
        elif choice == "5":
            show_errors(logs)
        
        elif choice == "6":
            show_timeline(logs)
        
        elif choice == "7":
            output = input("Nome do arquivo (padrão: logs_analise.json): ").strip()
            if not output:
                output = "logs_analise.json"
            export_to_json(logs, output)
        
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
