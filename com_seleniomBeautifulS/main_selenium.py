#!/usr/bin/env python3
"""
Scraper for comunica.pje.jus.br usando Selenium (executa JavaScript).
Necessário para sites que usam Angular/React para renderizar conteúdo.

Dependencies:
    pip install selenium webdriver-manager beautifulsoup4
"""

import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Importar configurações
try:
    from config import *
except ImportError:
    print("[!] Arquivo config.py não encontrado, usando configurações padrão")
    # Configurações padrão
    BASE_URL = "https://comunica.pje.jus.br/consulta?texto=distribu%C3%ADdo&dataDisponibilizacaoInicio=2025-11-01&dataDisponibilizacaoFim=2025-11-10"
    MAX_PAGES = 200
    MAX_CONSECUTIVE_EMPTY = 3
    DELAY_BETWEEN_PAGES = 3
    DELAY_WAIT_LOAD = 5
    LAZY_LOAD_INTERVAL = 5
    DELAY_MICRO = 0.5
    WAIT_TIMEOUT = 15
    INITIAL_LOAD_WAIT = 3
    HEADLESS = False
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    WINDOW_SIZE = "1920,1080"
    OUTPUT_FILE = "results.json"
    SAVE_SCREENSHOT = True
    SCREENSHOT_FILE = "debug_screenshot.png"
    PROGRESS_INTERVAL = 10
    VERBOSE = True

def setup_driver(headless=True):
    """Configura o driver do Chrome com opções otimizadas"""
    chrome_options = Options()
    
    if headless:
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

def extract_card_data(article_html):
    """
    Extract data from a single <article class="card"> HTML.
    Returns dict.
    """
    import re
    soup = BeautifulSoup(article_html, "html.parser")
    article = soup.find("article", class_="card")
    
    if not article:
        return {}
    
    data = {}

    # Process number
    proc_span = article.select_one(".numero-unico-formatado")
    if proc_span and proc_span.get_text(strip=True):
        data["processo"] = proc_span.get_text(strip=True).replace("Processo", "").strip()

    # Extract print/certidao link
    print_link = article.select_one('a[href*="certidao"]')
    if print_link:
        data["link_certidao"] = print_link.get("href")

    # Sidebar summary
    aside = article.select_one("aside.card-sumary")
    if aside:
        # Extract labeled fields
        for info in aside.select(".info"):
            info_sumary = info.select_one(".info-sumary")
            if not info_sumary:
                continue
                
            b = info_sumary.find("b")
            if b:
                key_text = b.get_text(strip=True).rstrip(":").lower()
                info_copy = BeautifulSoup(str(info_sumary), "html.parser")
                b_copy = info_copy.find("b")
                if b_copy:
                    b_copy.extract()
                value = info_copy.get_text(" ", strip=True)
                
                if key_text == "inteiro teor":
                    link = info_sumary.find("a")
                    if link and link.get("href"):
                        data["link_inteiro_teor"] = link.get("href")
                elif key_text not in ["parte(s)", "advogado(s)"]:
                    data[key_text] = value

        # Extract partes (parties)
        partes = []
        for parte_block in aside.select(".info-sumary"):
            tooltip = parte_block.select_one(".tooltip-polo")
            if tooltip:
                tooltip_span = tooltip.select_one(".tooltip-text")
                polo_tipo = tooltip_span.get_text(strip=True) if tooltip_span else ""
                
                parte_copy = BeautifulSoup(str(parte_block), "html.parser")
                tooltip_copy = parte_copy.select_one(".tooltip-polo")
                if tooltip_copy:
                    tooltip_copy.extract()
                nome = parte_copy.get_text(strip=True)
                
                if nome and polo_tipo:
                    partes.append({
                        "polo": polo_tipo,
                        "nome": nome
                    })
        if partes:
            data["partes"] = partes

        # Extract advogados
        advogados = []
        in_advogado_section = False
        for info in aside.select(".info"):
            info_text = info.get_text(strip=True)
            if "Advogado(s)" in info_text:
                in_advogado_section = True
                continue
            
            if in_advogado_section:
                if "OAB" in info_text:
                    info_sumary = info.select_one(".info-sumary")
                    if info_sumary:
                        icon = info_sumary.select_one("mat-icon")
                        if icon:
                            icon.extract()
                        lawyer_text = info_sumary.get_text(" ", strip=True)
                        if lawyer_text:
                            advogados.append(lawyer_text)
                elif info_text and not info.select_one("b"):
                    pass
                else:
                    break
        
        if advogados:
            data["advogados"] = advogados

    # Main panel distribution text
    panel = article.select_one("section.content-texto .tab_panel2")
    if panel:
        data["texto_distribuicao"] = panel.get_text(" ", strip=True)

    return data

def scrape_page(driver, page_num=1, wait_for_load=False):
    """Extrai dados de uma página"""
    print(f"[*] Processando página {page_num}...")
    
    # Se wait_for_load=True, aguarda mais tempo para lazy loading
    if wait_for_load:
        print(f"  [⏳] Aguardando lazy loading ({DELAY_WAIT_LOAD}s)...")
        time.sleep(DELAY_WAIT_LOAD)
    
    # Wait for cards to load
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.card"))
        )
    except:
        print(f"  [!] Nenhum card encontrado na página {page_num}")
        return []
    
    # Get page source
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # Find all cards
    articles = soup.select("article.card")
    print(f"  [+] Encontrados {len(articles)} cards")
    
    results = []
    for article in articles:
        data = extract_card_data(str(article))
        if data:
            results.append(data)
    
    return results

def get_pagination_info(driver):
    """Detecta informações de paginação disponíveis no momento (PrimeNG p-paginator)"""
    try:
        # PrimeNG p-paginator - botões numéricos de página
        # Classe: ui-paginator-page
        page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
        
        page_numbers = []
        for btn in page_buttons:
            text = btn.text.strip()
            if text.isdigit():
                page_numbers.append(int(text))
        
        # Procura por informação de total de páginas (se houver)
        total_pages = None
        try:
            # Alguns paginadores mostram "1-10 de 150" ou similar
            page_info = driver.find_elements(By.CSS_SELECTOR, ".ui-paginator-current, .ui-paginator-info")
            for elem in page_info:
                text = elem.text
                import re
                # Padrões: "1 de 100", "Página 1 de 100", "1-10 de 150"
                match = re.search(r'de\s+(\d+)', text)
                if match:
                    total_pages = int(match.group(1))
                    break
        except:
            pass
        
        # Retorna o maior número de página visível e o total (se encontrado)
        max_visible = max(page_numbers) if page_numbers else None
        
        if VERBOSE and max_visible:
            print(f"  [📄] Páginas visíveis: {sorted(page_numbers)}")
        
        return max_visible, total_pages
    except Exception as e:
        if VERBOSE:
            print(f"  [!] Erro ao detectar paginação: {e}")
        return None, None

def navigate_to_page_number(driver, page_num):
    """Navega para uma página específica clicando no número"""
    try:
        # Procura pelo botão com o número da página
        page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
        
        for btn in page_buttons:
            if btn.text.strip() == str(page_num):
                # Scroll até o elemento
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.3)
                
                # Clica no botão
                btn.click()
                print(f"  [✓] Clicando na página {page_num}...")
                time.sleep(DELAY_BETWEEN_PAGES)
                return True
        
        return False
    except Exception as e:
        if VERBOSE:
            print(f"  [!] Erro ao clicar na página {page_num}: {e}")
        return False

def navigate_to_next_page(driver):
    """Navega para a próxima página usando o botão 'próxima' do PrimeNG p-paginator"""
    try:
        # PrimeNG p-paginator - botão "next" (seta direita)
        # Classe: ui-paginator-next
        # Quando desabilitado: ui-state-disabled
        
        # Procura pelo botão "next" do PrimeNG
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.ui-paginator-next")
            
            # Verifica se está desabilitado
            classes = next_button.get_attribute("class")
            if "ui-state-disabled" in classes:
                print("  [!] Botão 'próxima' está desabilitado - fim da paginação")
                return False
            
            # Verifica se está visível e habilitado
            if next_button.is_displayed() and next_button.is_enabled():
                # Scroll até o elemento para garantir que está visível
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)
                
                # Clica no botão usando JavaScript (mais confiável)
                driver.execute_script("arguments[0].click();", next_button)
                print(f"  [✓] Navegando para próxima página...")
                time.sleep(DELAY_BETWEEN_PAGES)
                return True
            else:
                print("  [!] Botão 'próxima' não está visível ou habilitado")
                return False
                
        except Exception as e:
            print(f"  [!] Erro ao encontrar botão 'próxima': {e}")
            return False
            
    except Exception as e:
        print(f"  [!] Erro ao navegar: {e}")
        return False

def main():
    print("="*60)
    print("SCRAPER PJE - USANDO SELENIUM (COM JAVASCRIPT)")
    print("="*60)
    print()
    
    # Setup driver
    print("[*] Iniciando navegador Chrome...")
    if VERBOSE:
        print(f"  - Modo: {'Headless' if HEADLESS else 'Visual'}")
        print(f"  - Máximo de páginas: {MAX_PAGES}")
        print(f"  - Delay entre páginas: {DELAY_BETWEEN_PAGES}s")
        print(f"  - Delay lazy loading: {DELAY_WAIT_LOAD}s (a cada {LAZY_LOAD_INTERVAL} páginas)")
    driver = setup_driver(headless=HEADLESS)
    
    all_results = []
    
    try:
        # Load first page
        print(f"[+] Acessando: {BASE_URL}")
        driver.get(BASE_URL)
        time.sleep(INITIAL_LOAD_WAIT)  # Wait for page to load
        
        # Save screenshot for debugging
        if SAVE_SCREENSHOT:
            driver.save_screenshot(SCREENSHOT_FILE)
            print(f"[DEBUG] Screenshot salvo em {SCREENSHOT_FILE}")
        
        # Extract from first page
        results = scrape_page(driver, page_num=1)
        all_results.extend(results)
        
        # Detecta informações de paginação
        max_visible, total_pages = get_pagination_info(driver)
        
        if total_pages:
            print(f"[+] Total de páginas detectado: {total_pages}")
        elif max_visible:
            print(f"[+] Páginas visíveis: até {max_visible} (pode haver mais)")
        else:
            print("[*] Paginação não detectada, usando navegação incremental")
        
        # Navega pelas páginas usando botão "próxima"
        page_num = 2
        consecutive_empty = 0
        max_consecutive_empty = MAX_CONSECUTIVE_EMPTY
        
        print(f"[*] Iniciando navegação pelas páginas (máx: {MAX_PAGES})...")
        print()
        
        while page_num <= MAX_PAGES:
            # Verifica se precisa aguardar lazy loading (a cada X páginas)
            wait_for_load = (page_num % LAZY_LOAD_INTERVAL == 1 and page_num > 1)
            
            # Tenta navegar para próxima página
            if not navigate_to_next_page(driver):
                print(f"[!] Não foi possível avançar da página {page_num - 1}")
                break
            
            # Extrai dados da página
            results = scrape_page(driver, page_num, wait_for_load=wait_for_load)
            
            if results:
                all_results.extend(results)
                consecutive_empty = 0
                print(f"  [✓] Página {page_num}: {len(results)} registros")
            else:
                consecutive_empty += 1
                print(f"  [!] Página {page_num}: vazia ({consecutive_empty}/{max_consecutive_empty})")
                
                if consecutive_empty >= max_consecutive_empty:
                    print(f"\n[!] {max_consecutive_empty} páginas vazias consecutivas - finalizando")
                    break
            
            # Atualiza informações de paginação
            if page_num % PROGRESS_INTERVAL == 0:
                max_visible, total_pages = get_pagination_info(driver)
                if total_pages:
                    print(f"  [ℹ️] Progresso: {page_num}/{total_pages} páginas")
                else:
                    print(f"  [ℹ️] Progresso: {page_num} páginas processadas, {len(all_results)} registros")
            
            page_num += 1
            
            # Pequeno delay entre páginas
            time.sleep(DELAY_MICRO)
        
    finally:
        print()
        print(f"[+] Total de registros coletados: {len(all_results)}")
        
        # Save results
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"[+] Resultados salvos em {OUTPUT_FILE}")
        
        # Close browser
        print("[*] Fechando navegador...")
        driver.quit()
        print()
        print("="*60)
        print("CONCLUÍDO!")
        print("="*60)

if __name__ == "__main__":
    main()
