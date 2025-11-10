#!/usr/bin/env python3
"""
Script de teste para verificar a paginação do PrimeNG
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Importar configurações
try:
    from config import BASE_URL, HEADLESS
except:
    BASE_URL = "https://comunica.pje.jus.br/consulta?texto=distribu%C3%ADdo&dataDisponibilizacaoInicio=2025-11-01&dataDisponibilizacaoFim=2025-11-10"
    HEADLESS = False

def setup_driver():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def test_pagination():
    print("="*60)
    print("TESTE DE PAGINAÇÃO - PrimeNG p-paginator")
    print("="*60)
    print()
    
    driver = setup_driver()
    
    try:
        print(f"[*] Acessando: {BASE_URL}")
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("\n[1] Procurando elementos de paginação...")
        
        # Procura pelo container do paginador
        try:
            paginator = driver.find_element(By.CSS_SELECTOR, "p-paginator")
            print("  ✅ p-paginator encontrado")
        except:
            print("  ❌ p-paginator NÃO encontrado")
        
        # Procura pelos botões numéricos
        try:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
            print(f"  ✅ Botões numéricos: {len(page_buttons)} encontrados")
            for btn in page_buttons:
                print(f"     - Página {btn.text}: classes={btn.get_attribute('class')}")
        except Exception as e:
            print(f"  ❌ Botões numéricos NÃO encontrados: {e}")
        
        # Procura pelo botão "next"
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.ui-paginator-next")
            classes = next_button.get_attribute("class")
            is_disabled = "ui-state-disabled" in classes
            print(f"  ✅ Botão 'next' encontrado")
            print(f"     - Classes: {classes}")
            print(f"     - Desabilitado: {is_disabled}")
            print(f"     - Visível: {next_button.is_displayed()}")
            print(f"     - Habilitado: {next_button.is_enabled()}")
        except Exception as e:
            print(f"  ❌ Botão 'next' NÃO encontrado: {e}")
        
        # Procura pelo botão "prev"
        try:
            prev_button = driver.find_element(By.CSS_SELECTOR, "a.ui-paginator-prev")
            classes = prev_button.get_attribute("class")
            is_disabled = "ui-state-disabled" in classes
            print(f"  ✅ Botão 'prev' encontrado")
            print(f"     - Desabilitado: {is_disabled}")
        except Exception as e:
            print(f"  ❌ Botão 'prev' NÃO encontrado: {e}")
        
        print("\n[2] Testando clique no botão 'next'...")
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.ui-paginator-next")
            classes = next_button.get_attribute("class")
            
            if "ui-state-disabled" not in classes:
                print("  [*] Tentando clicar...")
                
                # Scroll até o elemento
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)
                
                # Clica usando JavaScript
                driver.execute_script("arguments[0].click();", next_button)
                print("  ✅ Clique executado!")
                
                time.sleep(3)
                
                # Verifica se mudou de página
                page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
                active_page = None
                for btn in page_buttons:
                    if "ui-state-active" in btn.get_attribute("class"):
                        active_page = btn.text
                        break
                
                print(f"  ✅ Página atual após clique: {active_page}")
                
                # Salva screenshot
                driver.save_screenshot("test_pagination_page2.png")
                print("  ✅ Screenshot salvo: test_pagination_page2.png")
            else:
                print("  ⚠️ Botão 'next' está desabilitado")
                
        except Exception as e:
            print(f"  ❌ Erro ao clicar: {e}")
        
        print("\n[3] Testando clique direto no número '2'...")
        try:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
            for btn in page_buttons:
                if btn.text.strip() == "2":
                    print("  [*] Botão '2' encontrado, clicando...")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(3)
                    print("  ✅ Clique executado!")
                    
                    # Salva screenshot
                    driver.save_screenshot("test_pagination_click_2.png")
                    print("  ✅ Screenshot salvo: test_pagination_click_2.png")
                    break
        except Exception as e:
            print(f"  ❌ Erro ao clicar no número 2: {e}")
        
        print("\n" + "="*60)
        print("TESTE CONCLUÍDO!")
        print("="*60)
        
    finally:
        print("\n[*] Fechando navegador em 5 segundos...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    test_pagination()
