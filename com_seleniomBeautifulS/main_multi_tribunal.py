#!/usr/bin/env python3
"""
Scraper PJE - Múltiplos Tribunais
Itera por todos os TJs e TRFs fazendo buscas separadas
"""

import json
import time
import os
from datetime import datetime
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# Importar lista de tribunais
from tribunais import get_tribunais_por_tipo

# Importar configurações
try:
    from config import *
except ImportError:
    print("[!] Usando configurações padrão")
    HEADLESS = False
    DELAY_BETWEEN_PAGES = 3
    DELAY_WAIT_LOAD = 5
    LAZY_LOAD_INTERVAL = 5
    DELAY_MICRO = 0.5
    WAIT_TIMEOUT = 15
    INITIAL_LOAD_WAIT = 3
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    WINDOW_SIZE = "1920,1080"
    MAX_PAGES = 200
    MAX_CONSECUTIVE_EMPTY = 3
    PROGRESS_INTERVAL = 10
    VERBOSE = True

# URL base (sem filtro de tribunal)
BASE_URL = "https://comunica.pje.jus.br/consulta"

# Parâmetros de busca
SEARCH_PARAMS = {
    "texto": "distribuído",
    "dataDisponibilizacaoInicio": "2025-11-01",
    "dataDisponibilizacaoFim": "2025-11-10"
}

# Tipo de tribunais para buscar: "TJ", "TRF" ou "TODOS"
TIPO_TRIBUNAL = "TODOS"

# Diretório de saída
OUTPUT_DIR = "resultados_por_tribunal"

def setup_driver():
    """Configura o driver do Chrome"""
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
    chrome_options.add_argument(f"--user-agent={USER_AGENT}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def select_tribunal(driver, sigla_tribunal):
    """
    Seleciona um tribunal específico no select do formulário
    
    Args:
        driver: WebDriver do Selenium
        sigla_tribunal: Sigla do tribunal (ex: "TJSP", "TRF1")
    
    Returns:
        bool: True se conseguiu selecionar, False caso contrário
    """
    try:
        # Aguarda o select estar disponível
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[formcontrolname='siglaTribunal']"))
        )
        
        # Cria objeto Select
        select = Select(select_element)
        
        # Seleciona pela sigla (value contém a sigla)
        for option in select.options:
            if sigla_tribunal in option.text:
                select.select_by_visible_text(option.text)
                print(f"  [✓] Tribunal selecionado: {option.text}")
                time.sleep(1)  # Aguarda aplicação do filtro
                return True
        
        print(f"  [!] Tribunal {sigla_tribunal} não encontrado no select")
        return False
        
    except Exception as e:
        print(f"  [!] Erro ao selecionar tribunal: {e}")
        return False

def click_search_button(driver):
    """Clica no botão de buscar"""
    try:
        # Procura pelo botão de buscar
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.btn-primary")
        search_button.click()
        time.sleep(INITIAL_LOAD_WAIT)
        return True
    except Exception as e:
        print(f"  [!] Erro ao clicar em buscar: {e}")
        return False

# Importar funções do main_selenium.py
from main_selenium import (
    extract_card_data,
    scrape_page,
    get_pagination_info,
    navigate_to_next_page
)

def scrape_tribunal(driver, tribunal):
    """
    Faz scraping de um tribunal específico
    
    Args:
        driver: WebDriver do Selenium
        tribunal: Dict com 'sigla' e 'nome' do tribunal
    
    Returns:
        list: Lista de resultados extraídos
    """
    sigla = tribunal["sigla"]
    nome = tribunal["nome"]
    
    print(f"\n{'='*60}")
    print(f"TRIBUNAL: {sigla} - {nome}")
    print(f"{'='*60}\n")
    
    all_results = []
    
    try:
        # Vai para a página inicial
        driver.get(BASE_URL)
        time.sleep(2)
        
        # Seleciona o tribunal
        if not select_tribunal(driver, sigla):
            print(f"[!] Não foi possível selecionar {sigla}, pulando...")
            return []
        
        # Clica em buscar
        if not click_search_button(driver):
            print(f"[!] Não foi possível iniciar busca para {sigla}")
            return []
        
        # Extrai primeira página
        results = scrape_page(driver, page_num=1)
        all_results.extend(results)
        print(f"  [✓] Página 1: {len(results)} registros")
        
        # Detecta paginação
        max_visible, total_pages = get_pagination_info(driver)
        
        if total_pages:
            print(f"[+] Total de páginas: {total_pages}")
        elif max_visible:
            print(f"[+] Páginas visíveis: até {max_visible}")
        
        # Navega pelas páginas
        page_num = 2
        consecutive_empty = 0
        
        while page_num <= MAX_PAGES:
            # Lazy loading
            wait_for_load = (page_num % LAZY_LOAD_INTERVAL == 1 and page_num > 1)
            
            # Navega
            if not navigate_to_next_page(driver):
                print(f"  [!] Fim da paginação na página {page_num - 1}")
                break
            
            # Extrai dados
            results = scrape_page(driver, page_num, wait_for_load=wait_for_load)
            
            if results:
                all_results.extend(results)
                consecutive_empty = 0
                print(f"  [✓] Página {page_num}: {len(results)} registros")
            else:
                consecutive_empty += 1
                if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                    print(f"  [!] {MAX_CONSECUTIVE_EMPTY} páginas vazias - parando")
                    break
            
            # Progresso
            if page_num % PROGRESS_INTERVAL == 0:
                print(f"  [ℹ️] Progresso: {page_num} páginas, {len(all_results)} registros")
            
            page_num += 1
            time.sleep(DELAY_MICRO)
        
        print(f"\n[✓] {sigla}: {len(all_results)} registros coletados")
        
    except Exception as e:
        print(f"[!] Erro ao processar {sigla}: {e}")
    
    return all_results

def main():
    print("="*60)
    print("SCRAPER PJE - MÚLTIPLOS TRIBUNAIS")
    print("="*60)
    print()
    
    # Cria diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Obtém lista de tribunais
    tribunais = get_tribunais_por_tipo(TIPO_TRIBUNAL)
    print(f"[*] Tribunais a processar: {len(tribunais)}")
    print(f"[*] Tipo: {TIPO_TRIBUNAL}")
    print(f"[*] Período: {SEARCH_PARAMS['dataDisponibilizacaoInicio']} a {SEARCH_PARAMS['dataDisponibilizacaoFim']}")
    print()
    
    # Setup driver
    driver = setup_driver()
    
    # Resultados consolidados
    resultados_consolidados = {}
    total_geral = 0
    
    try:
        for idx, tribunal in enumerate(tribunais, 1):
            sigla = tribunal["sigla"]
            
            print(f"\n[{idx}/{len(tribunais)}] Processando {sigla}...")
            
            # Scraping do tribunal
            resultados = scrape_tribunal(driver, tribunal)
            
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
            
            # Pequena pausa entre tribunais
            if idx < len(tribunais):
                time.sleep(2)
        
    finally:
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
        
        # Fecha navegador
        print("\n[*] Fechando navegador...")
        driver.quit()
        
        print("\n" + "="*60)
        print("CONCLUÍDO!")
        print("="*60)

if __name__ == "__main__":
    main()
