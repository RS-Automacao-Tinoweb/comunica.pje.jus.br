#!/usr/bin/env python3
"""
Scraper PJE - Usando API Direta
Muito mais rápido e confiável que Selenium!
"""

import json
import math
import requests
import time
from datetime import datetime
from urllib.parse import urlencode
import os

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
    "tipoComunicacao": "Lista de distribuição",  # Apenas listas de distribuição
    "codigoClasse": "12154",  # EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
}

# Tipo de tribunais: "TJ", "TRF" ou "TODOS"
TIPO_TRIBUNAL = "TODOS"

# Lista opcional de tribunais específicos (siglas) para testes e ajustes rápidos
# Exemplo: ["TJSP"] ou ["TRF3"]
TRIBUNAIS_ESPECIFICOS = ["TJSP"]

# Paginação
ITEMS_POR_PAGINA = 100  # Máximo permitido pela API

# Diretório de saída
OUTPUT_DIR = "resultados_api"

# Configuração de log
LOG_FILE = "scraper_requests.log"

# Headers para requisição
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Delay entre requisições (segundos)
DELAY_BETWEEN_REQUESTS = 2  # Delay padrão entre páginas
MAX_DELAY_BETWEEN_REQUESTS = 3  # Delay máximo permitido
DELAY_BETWEEN_TRIBUNAIS = 2  # Delay entre diferentes tribunais


def calcular_total_paginas(total_itens, itens_por_pagina):
    """
    Calcula o total de páginas a partir do total informado pela API.
    
    Exemplo:
        - Se count=10000 e itensPorPagina=5, então total_paginas=2000
        - Se count=9785 e itensPorPagina=100, então total_paginas=98
    """
    if itens_por_pagina <= 0:
        raise ValueError("itens_por_pagina deve ser maior que zero")
    if total_itens <= 0:
        return 0
    return math.ceil(total_itens / itens_por_pagina)


def obter_delay_paginas():
    """
    Retorna o atraso entre páginas limitado a 3 segundos para manter rapidez.
    Garante que nunca ultrapassará MAX_DELAY_BETWEEN_REQUESTS (3 segundos).
    """
    if DELAY_BETWEEN_REQUESTS <= 0:
        return 0
    delay = min(DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
    return min(delay, 3)  # Garantia extra: nunca mais que 3 segundos


def resolver_tribunais():
    """Resolve a lista final de tribunais a serem processados."""
    tribunais_disponiveis = get_tribunais_por_tipo(TIPO_TRIBUNAL)

    if not TRIBUNAIS_ESPECIFICOS:
        return tribunais_disponiveis

    siglas_normalizadas = []
    for sigla in TRIBUNAIS_ESPECIFICOS:
        sigla_normalizada = sigla.strip().upper()
        if sigla_normalizada and sigla_normalizada not in siglas_normalizadas:
            siglas_normalizadas.append(sigla_normalizada)

    if not siglas_normalizadas:
        return tribunais_disponiveis

    tribunais_map = {tribunal["sigla"].upper(): tribunal for tribunal in tribunais_disponiveis}
    faltantes = [sigla for sigla in siglas_normalizadas if sigla not in tribunais_map]

    if faltantes:
        raise ValueError(
            "Siglas de tribunais inválidas ou fora do escopo selecionado ({}): {}".format(
                TIPO_TRIBUNAL, ", ".join(sorted(faltantes))
            )
        )

    return [tribunais_map[sigla] for sigla in siglas_normalizadas]


def log_request(sigla_tribunal, pagina, url, params, response_data=None, error=None):
    """Registra detalhes da requisição no arquivo de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": timestamp,
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
    
    # Salva no arquivo de log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def fetch_page(sigla_tribunal, pagina=1):
    """
    Faz requisição para uma página específica da API
    
    Args:
        sigla_tribunal: Sigla do tribunal (ex: "TJSP", "TRF1")
        pagina: Número da página (começa em 1)
    
    Returns:
        dict: Resposta da API ou None em caso de erro
    """
    params = {
        "pagina": pagina,
        "itensPorPagina": ITEMS_POR_PAGINA,
        "siglaTribunal": sigla_tribunal,
        **SEARCH_PARAMS
    }
    
    url = f"{API_BASE_URL}?{urlencode(params)}"
    
    # Log da URL que será requisitada
    print(f"  [🌐] URL: {url}")
    
    try:
        # Faz a requisição
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Log de sucesso
        log_request(sigla_tribunal, pagina, url, params, response_data=data)
        
        return data
    except requests.exceptions.RequestException as e:
        # Log de erro
        log_request(sigla_tribunal, pagina, url, params, error=str(e))
        print(f"  [!] Erro na requisição: {e}")
        return None


def filtrar_item(item):
    """
    Verifica se o item atende aos filtros configurados
    
    Args:
        item: Item do JSON da API
    
    Returns:
        bool: True se atende aos filtros, False caso contrário
    """
    # Filtro: tipoComunicacao
    if FILTROS.get("tipoComunicacao"):
        if item.get("tipoComunicacao") != FILTROS["tipoComunicacao"]:
            return False
    
    # Filtro: codigoClasse
    if FILTROS.get("codigoClasse"):
        if str(item.get("codigoClasse")) != str(FILTROS["codigoClasse"]):
            return False
    
    # Filtro: data atual (se configurado)
    # Descomente se quiser filtrar apenas data atual
    # data_hoje = datetime.now().strftime("%d/%m/%Y")
    # if item.get("datadisponibilizacao") != data_hoje:
    #     return False
    
    return True


def extrair_dados_relevantes(item):
    """
    Extrai apenas os dados relevantes de um item
    
    Args:
        item: Item completo do JSON da API
    
    Returns:
        dict: Dados relevantes extraídos
    """
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


def scrape_tribunal_api(tribunal):
    """
    Faz scraping de um tribunal usando a API do PJE.
    
    LÓGICA DE PAGINAÇÃO:
    1. Primeira requisição retorna o campo 'count' com total de itens
    2. Calcula total de páginas: ceil(count / itensPorPagina)
    3. Itera página por página (1, 2, 3... até total_paginas)
    4. Respeita delay máximo de 3 segundos entre requisições
    
    Exemplo:
        Se count=10000 e itensPorPagina=5:
        - Total páginas = 10000/5 = 2000 páginas
        - Itera de página=1 até página=2000
    
    Args:
        tribunal: Dict com 'sigla' e 'nome' do tribunal
    
    Returns:
        list: Lista de resultados filtrados
    """
    sigla = tribunal["sigla"]
    nome = tribunal["nome"]
    
    print(f"\n{'='*80}")
    print(f"TRIBUNAL: {sigla} - {nome}")
    print(f"{'='*80}\n")
    
    all_results = []
    pagina = 1
    total_paginas_previstas = None
    count_total_api = None
    total_items_processados = 0
    total_filtrados_acumulado = 0
    tempo_inicio = time.time()

    while True:
        # Faz requisição para a página atual
        print(f"  [📄] Requisitando página {pagina}/{total_paginas_previstas or '?'}...", end=" ")
        data = fetch_page(sigla, pagina)
        
        # Validação da resposta
        if not data:
            print(f"\n  [!] Erro: Nenhum dado retornado pela API")
            break
            
        if data.get("status") != "success":
            print(f"\n  [!] Erro: Status da API não é 'success': {data.get('status')}")
            break
        
        items = data.get("items", [])
        count_total_api = data.get("count", 0)

        # Na primeira página, calcula total de páginas baseado no 'count'
        if total_paginas_previstas is None:
            total_paginas_previstas = calcular_total_paginas(count_total_api, ITEMS_POR_PAGINA)
            print(f"\n\n  [ℹ️] INFORMAÇÕES DA API:")
            print(f"      - Total de itens (count): {count_total_api:,}")
            print(f"      - Itens por página: {ITEMS_POR_PAGINA}")
            print(f"      - Total de páginas a processar: {total_paginas_previstas:,}")
            print(f"      - Tempo estimado: {(total_paginas_previstas * DELAY_BETWEEN_REQUESTS) / 60:.1f} minutos\n")
            
            if total_paginas_previstas == 0:
                print("  [!] Nenhum item disponível para este tribunal.")
                break

        # Validação: verifica se há itens
        if not items:
            print(f"\n  [!] Nenhum item retornado na página {pagina}")
            # Se não há mais itens, encerra (pode ter chegado ao fim)
            if total_items_processados >= count_total_api:
                print(f"  [✓] Coleta completa: {total_items_processados} itens processados")
            break
        
        # Processa TODOS os itens da página atual
        items_filtrados_nesta_pagina = 0
        for item in items:
            if filtrar_item(item):
                dados = extrair_dados_relevantes(item)
                all_results.append(dados)
                items_filtrados_nesta_pagina += 1
        
        total_items_processados += len(items)
        total_filtrados_acumulado += items_filtrados_nesta_pagina
        
        # Calcula progresso e tempo estimado
        progresso_pct = (pagina / total_paginas_previstas) * 100 if total_paginas_previstas else 0
        tempo_decorrido = time.time() - tempo_inicio
        tempo_por_pagina = tempo_decorrido / pagina if pagina > 0 else 0
        paginas_restantes = total_paginas_previstas - pagina
        tempo_estimado_restante = paginas_restantes * tempo_por_pagina
        
        # Log compacto e informativo
        print(f"OK [{progresso_pct:.1f}%]")
        print(f"      ✓ Itens: {len(items)} | Filtrados: {items_filtrados_nesta_pagina} | Acumulado: {total_filtrados_acumulado}")
        print(f"      ⏱️  Tempo estimado restante: {tempo_estimado_restante/60:.1f} min")
        
        # Verifica se já coletou todos os itens disponíveis
        if total_items_processados >= count_total_api:
            print(f"\n  [✅] COLETA COMPLETA: Todos os {count_total_api:,} itens foram processados!")
            break
            
        # Verifica se chegou na última página calculada
        if pagina >= total_paginas_previstas:
            print(f"\n  [✅] ÚLTIMA PÁGINA ATINGIDA: {total_paginas_previstas}")
            # Validação final
            if total_items_processados < count_total_api:
                print(f"  [⚠️] ATENÇÃO: Processados {total_items_processados} de {count_total_api} itens")
                print(f"      Faltam {count_total_api - total_items_processados} itens")
            break

        # Próxima página
        pagina += 1
        delay = obter_delay_paginas()
        if delay > 0:
            time.sleep(delay)
    
    tempo_total = time.time() - tempo_inicio
    
    print(f"\n{'='*80}")
    print(f"[✅] {sigla} CONCLUÍDO")
    print(f"{'='*80}")
    print(f"  📊 ESTATÍSTICAS:")
    print(f"      - Páginas processadas: {pagina:,}")
    print(f"      - Itens processados: {total_items_processados:,} de {count_total_api:,}")
    print(f"      - Itens filtrados: {len(all_results):,}")
    print(f"      - Taxa de filtro: {(len(all_results)/total_items_processados*100 if total_items_processados > 0 else 0):.1f}%")
    print(f"      - Tempo total: {tempo_total/60:.1f} minutos")
    print(f"      - Velocidade: {total_items_processados/(tempo_total/60):.0f} itens/min")
    print(f"{'='*80}\n")
    
    return all_results


def main():
    print("="*60)
    print("SCRAPER PJE - API DIRETA (MUITO MAIS RÁPIDO!)")
    print("="*60)
    print()
    
    # Limpa arquivo de log anterior
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    # Mostra configurações
    print("[*] CONFIGURAÇÕES DE BUSCA:")
    print(f"    Período: {SEARCH_PARAMS['dataDisponibilizacaoInicio']} a {SEARCH_PARAMS['dataDisponibilizacaoFim']}")
    print(f"    Tipo Comunicação: {FILTROS.get('tipoComunicacao', 'TODOS')}")
    print(f"    Código Classe: {FILTROS.get('codigoClasse', 'TODOS')}")
    print(f"    Tipo Tribunal: {TIPO_TRIBUNAL}")
    print(
        "    Tribunais específicos: {}".format(
            TRIBUNAIS_ESPECIFICOS if TRIBUNAIS_ESPECIFICOS else "Todos conforme tipo selecionado"
        )
    )
    print()
    
    print("[*] CONFIGURAÇÕES DE PAGINAÇÃO:")
    print(f"    Itens por página: {ITEMS_POR_PAGINA}")
    print(f"    Delay entre páginas: {DELAY_BETWEEN_REQUESTS}s")
    print(f"    Delay entre tribunais: {DELAY_BETWEEN_TRIBUNAIS}s")
    print(f"    ⚠️  IMPORTANTE: Cada tribunal será processado página por página!")
    print()
    
    print("[*] SISTEMA DE LOG:")
    print(f"    📝 Arquivo de log: {LOG_FILE}")
    print(f"    📊 Cada requisição será registrada com URL, parâmetros e resposta")
    print(f"    💡 Use 'python visualizar_log.py' para ver os logs de forma amigável")
    print()
    
    # Cria diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Obtém lista de tribunais
    tribunais = resolver_tribunais()
    print(f"[*] Tribunais a processar: {len(tribunais)}")
    print()
    
    # Resultados consolidados
    resultados_consolidados = {}
    total_geral = 0
    
    for idx, tribunal in enumerate(tribunais, 1):
        sigla = tribunal["sigla"]
        
        print(f"\n[{idx}/{len(tribunais)}] Processando {sigla}...")
        
        # Scraping do tribunal
        resultados = scrape_tribunal_api(tribunal)
        
        # Salva resultados individuais
        if resultados:
            output_file = os.path.join(OUTPUT_DIR, f"{sigla}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"  [💾] Salvo: {output_file}")
            
            resultados_consolidados[sigla] = {
                "tribunal": tribunal["nome"],
                "total_registros": len(resultados),
                "registros": resultados
            }
            total_geral += len(resultados)
        else:
            print(f"  [!] Nenhum resultado para {sigla}")
        
        # Pausa entre tribunais
        if idx < len(tribunais):
            time.sleep(DELAY_BETWEEN_TRIBUNAIS)
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"Total de tribunais processados: {len(resultados_consolidados)}")
    print(f"Total geral de registros: {total_geral}")
    print()
    
    # Mostra resumo por tribunal
    for sigla, dados in resultados_consolidados.items():
        print(f"  - {sigla}: {dados['total_registros']} registros")
    
    # Salva consolidado
    consolidado_file = os.path.join(OUTPUT_DIR, "consolidado.json")
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
        "tribunais": {
            sigla: {
                "nome": dados["tribunal"],
                "total": dados["total_registros"]
            }
            for sigla, dados in resultados_consolidados.items()
        }
    }
    
    resumo_file = os.path.join(OUTPUT_DIR, "resumo.json")
    with open(resumo_file, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    print(f"[💾] Resumo salvo: {resumo_file}")
    
    print("\n" + "="*60)
    print("CONCLUÍDO!")
    print("="*60)


if __name__ == "__main__":
    main()
