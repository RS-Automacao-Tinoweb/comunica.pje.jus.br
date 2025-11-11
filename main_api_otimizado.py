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
import sys
import random
from datetime import datetime
from urllib.parse import urlencode
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import deque
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
TRIBUNAIS_ESPECIFICOS = ["TJAM"]

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
MAX_WORKERS_TRIBUNAIS = 3  # Quantos tribunais processar simultaneamente (REDUZIDO para estabilidade)
MAX_WORKERS_PAGINAS = 3    # Quantas páginas buscar simultaneamente por tribunal (REDUZIDO)

# Rate Limiting (requisições por segundo)
MAX_REQUESTS_PER_SECOND = 3   # REDUZIDO para evitar sobrecarga
RATE_LIMIT_ENABLED = True

# Timeouts
REQUEST_TIMEOUT = 30          # Timeout por requisição (segundos)
TRIBUNAL_TIMEOUT = 1800        # Timeout por tribunal (segundos) - 30 minutos
MAX_RETRIES = 3                # Número máximo de tentativas por requisição

# Cache
CACHE_ENABLED = True  # Ativa cache para evitar requisições repetidas

# Log
LOG_BATCH_SIZE = 50  # Escreve logs a cada 50 entradas
LOG_ENABLED = True

# ===== SISTEMAS DE CONTROLE =====

# Sessão por thread (thread-local) com HTTPAdapter
_thread_local = threading.local()

def criar_sessao_thread_local():
    s = getattr(_thread_local, "session", None)
    if s is None:
        s = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504], raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retries, pool_maxsize=20)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.headers.update(HEADERS)
        _thread_local.session = s
    return s

# Buffer de logs (thread-safe)
log_buffer = deque()
log_lock = threading.Lock()

class AdaptiveRateLimiter:
    def __init__(self, initial_rate=5, min_rate=1, max_rate=20):
        self.rate = float(initial_rate)
        self.min_rate = float(min_rate)
        self.max_rate = float(max_rate)
        self.tokens = self.rate
        self.capacity = float(max_rate)
        self.last_refill = time.time()
        self.lock = threading.Lock()
        self.consecutive_429 = 0
        self.last_429_time = 0.0

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed > 0:
            add = elapsed * self.rate
            self.tokens = min(self.capacity, self.tokens + add)
            self.last_refill = now

    def acquire(self):
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                need = (1.0 - self.tokens) / (self.rate if self.rate > 0 else 1.0)
            time.sleep(max(0.01, need))

    def on_429(self):
        with self.lock:
            self.consecutive_429 += 1
            self.last_429_time = time.time()
            factor = 0.6 ** self.consecutive_429
            new_rate = max(self.min_rate, self.rate * factor)
            self.rate = max(self.min_rate, new_rate)
            self.capacity = max(self.rate, self.min_rate)
            self.tokens = min(self.tokens, self.capacity)
            print(f"\n[rate_limiter] 429 detectado: nova taxa {self.rate:.2f} req/s")

    def on_success(self):
        with self.lock:
            if self.consecutive_429 > 0:
                self.consecutive_429 = max(0, self.consecutive_429 - 1)
            if time.time() - self.last_429_time > 30:
                self.rate = min(self.max_rate, self.rate + 0.5)
                self.capacity = max(self.capacity, self.rate)

rate_limiter = AdaptiveRateLimiter(initial_rate=MAX_REQUESTS_PER_SECOND, min_rate=1, max_rate=MAX_REQUESTS_PER_SECOND)


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



def log_request_batch(sigla_tribunal, pagina, url, params, response_data=None, error=None, tempo_resposta_ms=None, status_code=None):
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
        "status_code": status_code,
        "tempo_resposta_ms": tempo_resposta_ms,
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
    """"""
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
    
    for attempt in range(MAX_RETRIES):
        try:
            if RATE_LIMIT_ENABLED:
                rate_limiter.acquire()
            session_local = criar_sessao_thread_local()
            inicio_req = time.time()
            resp = session_local.get(url, timeout=REQUEST_TIMEOUT)
            tempo_resposta = time.time() - inicio_req

            if resp.status_code == 429:
                retry_after = None
                if "Retry-After" in resp.headers:
                    try:
                        retry_after = float(resp.headers.get("Retry-After"))
                    except Exception:
                        retry_after = None
                rate_limiter.on_429()
                if retry_after and retry_after > 0:
                    wait_time = retry_after + random.uniform(0.1, 0.5)
                    print(f"\n  [⚠️] {sigla_tribunal} - Página {pagina}: HTTP 429 com Retry-After {retry_after}s -> aguardando {wait_time:.2f}s")
                    time.sleep(wait_time)
                else:
                    base = (2 ** attempt)
                    jitter = random.uniform(0.2, 0.8)
                    wait_time = base + jitter
                    print(f"\n  [⚠️] {sigla_tribunal} - Página {pagina}: HTTP 429 - Aguardando {wait_time:.2f}s (tentativa {attempt+1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                continue

            if resp.status_code in (502, 503, 504):
                base = (2 ** attempt)
                jitter = random.uniform(0.1, 0.5)
                wait_time = base + jitter
                print(f"\n  [⚠️] {sigla_tribunal} - Página {pagina}: HTTP {resp.status_code} - Aguardando {wait_time:.2f}s")
                time.sleep(wait_time)
                continue

            resp.raise_for_status()
            data = resp.json()
            rate_limiter.on_success()

            salvar_cache(cache_key, data)
            log_request_batch(
                sigla_tribunal,
                pagina,
                url,
                params,
                response_data=data,
                tempo_resposta_ms=round(tempo_resposta * 1000, 2),
                status_code=resp.status_code,
            )
            return data

        except requests.exceptions.Timeout:
            base = (2 ** attempt)
            jitter = random.uniform(0.1, 0.6)
            wait_time = base + jitter
            print(f"\n  [⚠️] {sigla_tribunal} - Página {pagina}: Timeout - aguardando {wait_time:.1f}s (tentativa {attempt+1}/{MAX_RETRIES})")
            time.sleep(wait_time)
            continue

        except requests.exceptions.RequestException as e:
            base = (2 ** attempt)
            jitter = random.uniform(0.1, 0.6)
            wait_time = base + jitter
            print(f"\n  [⚠️] {sigla_tribunal} - Página {pagina}: RequestException {str(e)[:70]} - aguardando {wait_time:.1f}s")
            time.sleep(wait_time)
            continue

        except Exception as e:
            log_request_batch(sigla_tribunal, pagina, url, params, error=f"Erro inesperado: {str(e)}")
            print(f"\n  [❌] {sigla_tribunal} - Página {pagina}: Erro inesperado: {e}")
            return None

    log_request_batch(sigla_tribunal, pagina, url, params, error="Falha definitiva após retries")
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
    try:
        data = fetch_page(sigla_tribunal, pagina)
        
        if not data or data.get("status") != "success":
            return {"pagina": pagina, "resultados": [], "erro": "Dados inválidos ou status não success"}
        
        items = data.get("items", [])
        resultados = []
        
        for item in items:
            if filtrar_item(item):
                dados = extrair_dados_relevantes(item)
                resultados.append(dados)
        
        return {"pagina": pagina, "resultados": resultados, "erro": None}
    
    except Exception as e:
        print(f"\n  [❌] Erro ao processar página {pagina}: {str(e)}")
        return {"pagina": pagina, "resultados": [], "erro": str(e)}


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
        return {"resultados": [], "erros": [{"pagina": 1, "erro": "Falha ao obter primeira página"}], "paginas_processadas": 0}
    
    count_total = data_primeira.get("count", 0)
    total_paginas = calcular_total_paginas(count_total, ITEMS_POR_PAGINA)
    
    print(f"  [ℹ️] Total de itens: {count_total:,}")
    print(f"  [ℹ️] Total de páginas: {total_paginas:,}")
    print(f"  [⚡] Iniciando scraping paralelo com {MAX_WORKERS_PAGINAS} workers...\n")
    
    if total_paginas == 0:
        return {"resultados": [], "erros": [], "paginas_processadas": 0}
    
    # Processa primeira página
    resultado_primeira = processar_pagina(sigla, 1)
    all_results = resultado_primeira["resultados"]
    erros_paginas = []
    paginas_processadas = 1
    
    if resultado_primeira["erro"]:
        erros_paginas.append({"pagina": 1, "erro": resultado_primeira["erro"]})
    
    # Processa páginas restantes em paralelo com timeout
    if total_paginas > 1:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PAGINAS) as executor:
            # Submete todas as páginas
            futures = {
                executor.submit(processar_pagina, sigla, pag): pag 
                for pag in range(2, total_paginas + 1)
            }
            
            # Coleta resultados conforme completam (com timeout)
            paginas_processadas = 1
            paginas_com_erro = 0
            
            try:
                for future in as_completed(futures, timeout=TRIBUNAL_TIMEOUT):
                    pagina_num = futures[future]
                    try:
                        resultado = future.result(timeout=10)  # Timeout individual de 10s
                        
                        if resultado["erro"]:
                            erros_paginas.append({"pagina": pagina_num, "erro": resultado["erro"]})
                            paginas_com_erro += 1
                        
                        all_results.extend(resultado["resultados"])
                        paginas_processadas += 1
                        
                        # Progress
                        progresso = (paginas_processadas / total_paginas) * 100
                        print(f"  [⚡] Progresso: {paginas_processadas}/{total_paginas} páginas ({progresso:.1f}%) | Filtrados: {len(all_results):,} | Erros: {paginas_com_erro}", end="\r")
                    
                    except TimeoutError:
                        print(f"\n  [⚠️] Timeout na página {pagina_num}")
                        erros_paginas.append({"pagina": pagina_num, "erro": "Timeout"})
                        paginas_com_erro += 1
                    
                    except Exception as e:
                        print(f"\n  [❌] Erro ao processar resultado da página {pagina_num}: {str(e)}")
                        erros_paginas.append({"pagina": pagina_num, "erro": str(e)})
                        paginas_com_erro += 1
            
            except TimeoutError:
                print(f"\n\n  [❌] TIMEOUT GLOBAL: Tribunal {sigla} excedeu {TRIBUNAL_TIMEOUT}s")
                print(f"  [ℹ️] Páginas processadas até o timeout: {paginas_processadas}/{total_paginas}")
    
    tempo_total = time.time() - tempo_inicio
    
    print(f"\n\n{'='*80}")
    print(f"[✅] {sigla} CONCLUÍDO")
    print(f"{'='*80}")
    print(f"  📊 ESTATÍSTICAS:")
    print(f"      - Páginas processadas: {paginas_processadas:,}/{total_paginas:,}")
    print(f"      - Páginas com erro: {len(erros_paginas):,}")
    print(f"      - Taxa de sucesso: {(paginas_processadas/total_paginas*100 if total_paginas > 0 else 0):.1f}%")
    print(f"      - Itens totais disponíveis: {count_total:,}")
    print(f"      - Itens filtrados coletados: {len(all_results):,}")
    print(f"      - Taxa de filtro: {(len(all_results)/count_total*100 if count_total > 0 else 0):.1f}%")
    print(f"      - Tempo total: {tempo_total:.1f}s ({tempo_total/60:.1f} min)")
    if tempo_total > 0:
        print(f"      - Velocidade: {paginas_processadas/tempo_total:.1f} páginas/s")
    print(f"{'='*80}")
    
    if erros_paginas:
        print(f"\n  [⚠️] ERROS ENCONTRADOS ({len(erros_paginas)} páginas):")
        for erro in erros_paginas[:10]:  # Mostra até 10 erros
            print(f"      - Página {erro['pagina']}: {erro['erro'][:80]}")
        if len(erros_paginas) > 10:
            print(f"      ... e mais {len(erros_paginas) - 10} erros")
    print(f"{'='*80}\n")
    
    return {"resultados": all_results, "erros": erros_paginas, "paginas_processadas": paginas_processadas}


def processar_tribunal(tribunal):
    """Wrapper para processar tribunal (usado no paralelismo de tribunais)"""
    try:
        sigla = tribunal["sigla"]
        resultado = scrape_tribunal_api_paralelo(tribunal)
        return sigla, resultado["resultados"], tribunal["nome"], resultado.get("erros", []), resultado.get("paginas_processadas", 0)
    except Exception as e:
        print(f"\n[❌] Erro crítico ao processar {tribunal['sigla']}: {e}")
        import traceback
        traceback.print_exc()
        return tribunal["sigla"], [], tribunal["nome"], [{"erro": str(e)}], 0


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
    
    erros_tribunais = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_TRIBUNAIS) as executor:
        futures = {executor.submit(processar_tribunal, t): t for t in tribunais}
        
        for future in as_completed(futures):
            tribunal = futures[future]
            try:
                sigla, resultados, nome, erros, paginas_proc = future.result(timeout=TRIBUNAL_TIMEOUT + 60)
                
                if resultados:
                    # Salva resultados individuais
                    output_file = Path(OUTPUT_DIR) / f"{sigla}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(resultados, f, ensure_ascii=False, indent=2)
                    
                    resultados_consolidados[sigla] = {
                        "tribunal": nome,
                        "total_registros": len(resultados),
                        "paginas_processadas": paginas_proc,
                        "erros": len(erros),
                        "registros": resultados
                    }
                    total_geral += len(resultados)
                    print(f"[💾] {sigla}: {len(resultados):,} registros salvos | {len(erros)} erros")
                else:
                    print(f"[!] {sigla}: Nenhum resultado")
                
                if erros:
                    erros_tribunais.append({"tribunal": sigla, "erros": erros})
            
            except TimeoutError:
                print(f"\n[❌] {tribunal['sigla']}: Timeout total do tribunal")
                erros_tribunais.append({"tribunal": tribunal['sigla'], "erro": "Timeout total"})
            
            except Exception as e:
                print(f"\n[❌] {tribunal['sigla']}: Erro crítico - {str(e)}")
                erros_tribunais.append({"tribunal": tribunal['sigla'], "erro": str(e)})
    
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
    if tempo_total_execucao > 0:
        print(f"Velocidade média: {total_geral/tempo_total_execucao:.0f} registros/s")
    print(f"Tribunais com erros: {len(erros_tribunais)}")
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
