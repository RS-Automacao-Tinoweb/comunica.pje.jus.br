#!/usr/bin/env python3
"""
Scraper PJE - Versão ULTRA OTIMIZADA
Performance máxima com paralelismo, cache e rate limiting inteligente!
"""

import json
import math
import requests
import time
import threading
import hashlib
from datetime import datetime
from urllib.parse import urlencode
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

# Importar lista de tribunais
from tribunais import get_tribunais_por_tipo

# ===== CONFIGURAÇÕES =====

# URL da API
API_BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

# Parâmetros de busca
SEARCH_PARAMS = {
    "dataDisponibilizacaoInicio": "2025-11-06",
    "dataDisponibilizacaoFim": "2025-11-10"
}

# Filtros específicos
FILTROS = {
    "tipoComunicacao": "Lista de distribuição",
    "codigoClasse": "12154",
}

# Tipo de tribunais
TIPO_TRIBUNAL = "TODOS"
TRIBUNAIS_ESPECIFICOS = ["TJSP"]

# Paginação
ITEMS_POR_PAGINA = 100  # Máximo permitido pela API

# Diretórios
OUTPUT_DIR = "resultados_api"
CACHE_DIR = "cache_api"
LOG_FILE = "scraper_requests.log"

# Headers para requisição
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ===== CONFIGURAÇÕES DE PERFORMANCE =====

# Paralelismo
MAX_WORKERS_TRIBUNAIS = 5  # Quantos tribunais processar simultaneamente
MAX_WORKERS_PAGINAS = 10   # Quantas páginas buscar simultaneamente por tribunal

# Rate Limiting (requisições por segundo)
MAX_REQUESTS_PER_SECOND = 10  # Ajuste conforme necessário
RATE_LIMIT_ENABLED = True

# Cache
CACHE_ENABLED = True  # Ativa cache para evitar requisições repetidas

# Log
LOG_BATCH_SIZE = 50  # Escreve logs a cada 50 entradas
LOG_ENABLED = True

# ===== SISTEMAS DE CONTROLE =====

# Session global para reuso de conexões HTTP
session = requests.Session()
session.headers.update(HEADERS)

# Buffer de logs (thread-safe)
log_buffer = deque()
log_lock = threading.Lock()

# Rate limiter simples (token bucket)
rate_limiter_lock = threading.Lock()
last_request_times = deque(maxlen=MAX_REQUESTS_PER_SECOND)


# ===== FUNÇÕES AUXILIARES =====

def calcular_total_paginas(total_itens, itens_por_pagina):
    """Calcula total de páginas baseado no count da API"""
    if itens_por_pagina <= 0:
        raise ValueError("itens_por_pagina deve ser maior que zero")
    if total_itens <= 0:
        return 0
    return math.ceil(total_itens / itens_por_pagina)


def gerar_cache_key(sigla_tribunal, pagina):
    """Gera chave única para cache baseada nos parâmetros"""
    params_str = f"{sigla_tribunal}_{pagina}_{ITEMS_POR_PAGINA}_{SEARCH_PARAMS['dataDisponibilizacaoInicio']}_{SEARCH_PARAMS['dataDisponibilizacaoFim']}"
    return hashlib.md5(params_str.encode()).hexdigest()


def ler_cache(cache_key):
    """Lê dados do cache se existir"""
    if not CACHE_ENABLED:
        return None
    
    cache_file = Path(CACHE_DIR) / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None


def salvar_cache(cache_key, data):
    """Salva dados no cache"""
    if not CACHE_ENABLED:
        return
    
    Path(CACHE_DIR).mkdir(exist_ok=True)
    cache_file = Path(CACHE_DIR) / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass


def rate_limit_wait():
    """Implementa rate limiting inteligente (token bucket)"""
    if not RATE_LIMIT_ENABLED:
        return
    
    with rate_limiter_lock:
        now = time.time()
        
        # Remove timestamps antigos (mais de 1 segundo)
        while last_request_times and now - last_request_times[0] > 1.0:
            last_request_times.popleft()
        
        # Se atingiu o limite, aguarda
        if len(last_request_times) >= MAX_REQUESTS_PER_SECOND:
            sleep_time = 1.0 - (now - last_request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_request_times.popleft()
        
        last_request_times.append(time.time())


def log_request_batch(sigla_tribunal, pagina, url, params, response_data=None, error=None):
    """Adiciona log ao buffer (será escrito em batch)"""
    if not LOG_ENABLED:
        return
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tribunal": sigla_tribunal,
        "pagina": pagina,
        "url": url,
        "params": params,
        "status": "success" if not error else "error",
        "error": str(error) if error else None,
        "response_summary": {
            "total_disponivel": response_data.get("count") if response_data else None,
            "itens_retornados": len(response_data.get("items", [])) if response_data else 0
        } if response_data and not error else None
    }
    
    with log_lock:
        log_buffer.append(log_entry)
        
        # Flush se atingiu o tamanho do batch
        if len(log_buffer) >= LOG_BATCH_SIZE:
            flush_logs()


def flush_logs():
    """Escreve todos os logs pendentes no arquivo"""
    if not LOG_ENABLED:
        return
    
    with log_lock:
        if not log_buffer:
            return
        
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                while log_buffer:
                    entry = log_buffer.popleft()
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[!] Erro ao escrever logs: {e}")


def resolver_tribunais():
    """Resolve lista de tribunais a processar"""
    tribunais_disponiveis = get_tribunais_por_tipo(TIPO_TRIBUNAL)
    
    if not TRIBUNAIS_ESPECIFICOS:
        return tribunais_disponiveis
    
    siglas_normalizadas = [s.strip().upper() for s in TRIBUNAIS_ESPECIFICOS if s.strip()]
    
    if not siglas_normalizadas:
        return tribunais_disponiveis
    
    tribunais_map = {t["sigla"].upper(): t for t in tribunais_disponiveis}
    faltantes = [s for s in siglas_normalizadas if s not in tribunais_map]
    
    if faltantes:
        raise ValueError(
            f"Siglas inválidas ({TIPO_TRIBUNAL}): {', '.join(sorted(faltantes))}"
        )
    
    return [tribunais_map[s] for s in siglas_normalizadas]


# ===== FUNÇÕES DE SCRAPING =====

def fetch_page(sigla_tribunal, pagina=1):
    """
    Faz requisição para uma página específica da API
    Usa Session para reuso de conexões e rate limiting inteligente
    """
    cache_key = gerar_cache_key(sigla_tribunal, pagina)
    
    # Tenta ler do cache primeiro
    cached_data = ler_cache(cache_key)
    if cached_data:
        return cached_data
    
    params = {
        "pagina": pagina,
        "itensPorPagina": ITEMS_POR_PAGINA,
        "siglaTribunal": sigla_tribunal,
        **SEARCH_PARAMS
    }
    
    url = f"{API_BASE_URL}?{urlencode(params)}"
    
    # Rate limiting
    rate_limit_wait()
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Salva no cache
        salvar_cache(cache_key, data)
        
        # Log
        log_request_batch(sigla_tribunal, pagina, url, params, response_data=data)
        
        return data
    
    except requests.exceptions.RequestException as e:
        log_request_batch(sigla_tribunal, pagina, url, params, error=str(e))
        return None


def filtrar_item(item):
    """Verifica se item atende aos filtros"""
    if FILTROS.get("tipoComunicacao"):
        if item.get("tipoComunicacao") != FILTROS["tipoComunicacao"]:
            return False
    
    if FILTROS.get("codigoClasse"):
        if str(item.get("codigoClasse")) != str(FILTROS["codigoClasse"]):
            return False
    
    return True


def extrair_dados_relevantes(item):
    """Extrai dados relevantes de um item"""
    return {
        "id": item.get("id"),
        "processo": item.get("numeroprocessocommascara"),
        "processo_sem_mascara": item.get("numero_processo"),
        "data_disponibilizacao": item.get("datadisponibilizacao"),
        "tribunal": item.get("siglaTribunal"),
        "tipo_comunicacao": item.get("tipoComunicacao"),
        "orgao": item.get("nomeOrgao"),
        "classe": item.get("nomeClasse"),
        "codigo_classe": item.get("codigoClasse"),
        "tipo_documento": item.get("tipoDocumento"),
        "meio": item.get("meiocompleto"),
        "link": item.get("link"),
        "hash": item.get("hash"),
        "texto": item.get("texto"),
        "partes": [
            {
                "nome": dest.get("nome"),
                "polo": dest.get("polo")
            }
            for dest in item.get("destinatarios", [])
        ],
        "advogados": [
            {
                "nome": adv.get("advogado", {}).get("nome"),
                "oab": adv.get("advogado", {}).get("numero_oab"),
                "uf": adv.get("advogado", {}).get("uf_oab")
            }
            for adv in item.get("destinatarioadvogados", [])
        ]
    }


def processar_pagina(sigla_tribunal, pagina):
    """Processa uma página individual (usado no paralelismo)"""
    data = fetch_page(sigla_tribunal, pagina)
    
    if not data or data.get("status") != "success":
        return []
    
    items = data.get("items", [])
    resultados = []
    
    for item in items:
        if filtrar_item(item):
            dados = extrair_dados_relevantes(item)
            resultados.append(dados)
    
    return resultados


def scrape_tribunal_api_paralelo(tribunal):
    """
    Versão OTIMIZADA com paralelismo de páginas
    Busca múltiplas páginas simultaneamente
    """
    sigla = tribunal["sigla"]
    nome = tribunal["nome"]
    
    print(f"\n{'='*80}")
    print(f"🚀 TRIBUNAL: {sigla} - {nome}")
    print(f"{'='*80}\n")
    
    tempo_inicio = time.time()
    
    # Primeira requisição para descobrir total de páginas
    print(f"  [📊] Descobrindo total de páginas...")
    data_primeira = fetch_page(sigla, 1)
    
    if not data_primeira or data_primeira.get("status") != "success":
        print(f"  [!] Erro ao buscar primeira página")
        return []
    
    count_total = data_primeira.get("count", 0)
    total_paginas = calcular_total_paginas(count_total, ITEMS_POR_PAGINA)
    
    print(f"  [ℹ️] Total de itens: {count_total:,}")
    print(f"  [ℹ️] Total de páginas: {total_paginas:,}")
    print(f"  [⚡] Iniciando scraping paralelo com {MAX_WORKERS_PAGINAS} workers...\n")
    
    if total_paginas == 0:
        return []
    
    # Processa primeira página
    all_results = processar_pagina(sigla, 1)
    
    # Processa páginas restantes em paralelo
    if total_paginas > 1:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PAGINAS) as executor:
            # Submete todas as páginas
            futures = {
                executor.submit(processar_pagina, sigla, pag): pag 
                for pag in range(2, total_paginas + 1)
            }
            
            # Coleta resultados conforme completam
            paginas_processadas = 1
            for future in as_completed(futures):
                pagina_num = futures[future]
                try:
                    resultados = future.result()
                    all_results.extend(resultados)
                    paginas_processadas += 1
                    
                    # Progress
                    progresso = (paginas_processadas / total_paginas) * 100
                    print(f"  [⚡] Progresso: {paginas_processadas}/{total_paginas} páginas ({progresso:.1f}%) | Filtrados: {len(all_results):,}", end="\r")
                
                except Exception as e:
                    print(f"\n  [!] Erro na página {pagina_num}: {e}")
    
    tempo_total = time.time() - tempo_inicio
    
    print(f"\n\n{'='*80}")
    print(f"[✅] {sigla} CONCLUÍDO")
    print(f"{'='*80}")
    print(f"  📊 ESTATÍSTICAS:")
    print(f"      - Páginas processadas: {total_paginas:,}")
    print(f"      - Itens totais: {count_total:,}")
    print(f"      - Itens filtrados: {len(all_results):,}")
    print(f"      - Taxa de filtro: {(len(all_results)/count_total*100 if count_total > 0 else 0):.1f}%")
    print(f"      - Tempo total: {tempo_total:.1f}s ({tempo_total/60:.1f} min)")
    print(f"      - Velocidade: {count_total/tempo_total:.0f} itens/s")
    print(f"      - Páginas/s: {total_paginas/tempo_total:.1f}")
    print(f"{'='*80}\n")
    
    return all_results


def processar_tribunal(tribunal):
    """Wrapper para processar tribunal (usado no paralelismo de tribunais)"""
    try:
        sigla = tribunal["sigla"]
        resultados = scrape_tribunal_api_paralelo(tribunal)
        return sigla, resultados, tribunal["nome"]
    except Exception as e:
        print(f"[!] Erro ao processar {tribunal['sigla']}: {e}")
        return tribunal["sigla"], [], tribunal["nome"]


def main():
    """
    Main OTIMIZADO com paralelismo de tribunais e páginas
    """
    print("="*80)
    print("🚀 SCRAPER PJE - VERSÃO ULTRA OTIMIZADA")
    print("="*80)
    print()
    
    # Limpa log anterior
    if Path(LOG_FILE).exists():
        Path(LOG_FILE).unlink()
    
    # Mostra configurações
    print("[⚙️] CONFIGURAÇÕES:")
    print(f"    Período: {SEARCH_PARAMS['dataDisponibilizacaoInicio']} a {SEARCH_PARAMS['dataDisponibilizacaoFim']}")
    print(f"    Tipo Comunicação: {FILTROS.get('tipoComunicacao', 'TODOS')}")
    print(f"    Código Classe: {FILTROS.get('codigoClasse', 'TODOS')}")
    print(f"    Tipo Tribunal: {TIPO_TRIBUNAL}")
    print(f"    Tribunais específicos: {TRIBUNAIS_ESPECIFICOS or 'Todos'}")
    print()
    
    print("[⚡] OTIMIZAÇÕES ATIVADAS:")
    print(f"    ✓ requests.Session() - Reuso de conexões HTTP")
    print(f"    ✓ ThreadPoolExecutor - {MAX_WORKERS_TRIBUNAIS} tribunais paralelos")
    print(f"    ✓ Paralelismo de páginas - {MAX_WORKERS_PAGINAS} páginas simultâneas")
    print(f"    ✓ Rate Limiting - {MAX_REQUESTS_PER_SECOND} req/s {'(ATIVADO)' if RATE_LIMIT_ENABLED else '(DESATIVADO)'}")
    print(f"    ✓ Log em batch - {LOG_BATCH_SIZE} entradas {'(ATIVADO)' if LOG_ENABLED else '(DESATIVADO)'}")
    print(f"    ✓ Cache local - {'ATIVADO' if CACHE_ENABLED else 'DESATIVADO'}")
    print()
    
    # Cria diretórios
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    if CACHE_ENABLED:
        Path(CACHE_DIR).mkdir(exist_ok=True)
    
    # Obtém tribunais
    tribunais = resolver_tribunais()
    print(f"[📋] Tribunais a processar: {len(tribunais)}")
    print()
    
    tempo_inicio_total = time.time()
    resultados_consolidados = {}
    total_geral = 0
    
    # Processa tribunais em paralelo
    print(f"[🚀] Iniciando processamento paralelo de {len(tribunais)} tribunais...\n")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_TRIBUNAIS) as executor:
        futures = {executor.submit(processar_tribunal, t): t for t in tribunais}
        
        for future in as_completed(futures):
            tribunal = futures[future]
            try:
                sigla, resultados, nome = future.result()
                
                if resultados:
                    # Salva resultados individuais
                    output_file = Path(OUTPUT_DIR) / f"{sigla}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(resultados, f, ensure_ascii=False, indent=2)
                    
                    resultados_consolidados[sigla] = {
                        "tribunal": nome,
                        "total_registros": len(resultados),
                        "registros": resultados
                    }
                    total_geral += len(resultados)
                    print(f"[💾] {sigla}: {len(resultados):,} registros salvos")
                else:
                    print(f"[!] {sigla}: Nenhum resultado")
            
            except Exception as e:
                print(f"[!] Erro ao processar {tribunal['sigla']}: {e}")
    
    # Flush logs pendentes
    flush_logs()
    
    tempo_total_execucao = time.time() - tempo_inicio_total
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO FINAL")
    print("="*80)
    print(f"Total de tribunais processados: {len(resultados_consolidados)}")
    print(f"Total geral de registros: {total_geral:,}")
    print(f"Tempo total de execução: {tempo_total_execucao:.1f}s ({tempo_total_execucao/60:.1f} min)")
    print(f"Velocidade média: {total_geral/tempo_total_execucao:.0f} registros/s")
    print()
    
    # Detalhes por tribunal
    for sigla, dados in resultados_consolidados.items():
        print(f"  - {sigla}: {dados['total_registros']:,} registros")
    
    # Salva consolidado
    consolidado_file = Path(OUTPUT_DIR) / "consolidado.json"
    with open(consolidado_file, "w", encoding="utf-8") as f:
        json.dump(resultados_consolidados, f, ensure_ascii=False, indent=2)
    print(f"\n[💾] Consolidado salvo: {consolidado_file}")
    
    # Salva resumo
    resumo = {
        "data_execucao": datetime.now().isoformat(),
        "parametros_busca": SEARCH_PARAMS,
        "filtros": FILTROS,
        "tipo_tribunal": TIPO_TRIBUNAL,
        "total_tribunais": len(resultados_consolidados),
        "total_registros": total_geral,
        "tempo_execucao_segundos": tempo_total_execucao,
        "velocidade_registros_por_segundo": total_geral / tempo_total_execucao if tempo_total_execucao > 0 else 0,
        "otimizacoes": {
            "session_reuso": True,
            "paralelismo_tribunais": MAX_WORKERS_TRIBUNAIS,
            "paralelismo_paginas": MAX_WORKERS_PAGINAS,
            "rate_limiting": RATE_LIMIT_ENABLED,
            "cache": CACHE_ENABLED,
            "log_batch": LOG_ENABLED
        },
        "tribunais": {
            sigla: {
                "nome": dados["tribunal"],
                "total": dados["total_registros"]
            }
            for sigla, dados in resultados_consolidados.items()
        }
    }
    
    resumo_file = Path(OUTPUT_DIR) / "resumo.json"
    with open(resumo_file, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    print(f"[💾] Resumo salvo: {resumo_file}")
    
    print("\n" + "="*80)
    print("✅ CONCLUÍDO COM SUCESSO!")
    print("="*80)


if __name__ == "__main__":
    main()
