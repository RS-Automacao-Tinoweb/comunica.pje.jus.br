"""
Configurações do Scraper PJE
Ajuste estes valores conforme necessário
"""

# ===== CONFIGURAÇÕES DE BUSCA =====

# URL base da consulta (edite os parâmetros de data e texto aqui)
BASE_URL = "https://comunica.pje.jus.br/consulta?texto=distribu%C3%ADdo&dataDisponibilizacaoInicio=2025-11-01&dataDisponibilizacaoFim=2025-11-10"

# ===== CONFIGURAÇÕES DE PAGINAÇÃO =====

# Máximo de páginas para processar (segurança contra loops infinitos)
MAX_PAGES = 200

# Número de páginas vazias consecutivas antes de parar
MAX_CONSECUTIVE_EMPTY = 3

# ===== CONFIGURAÇÕES DE TIMING =====

# Tempo de espera entre navegação de páginas (segundos)
DELAY_BETWEEN_PAGES = 3

# Tempo para aguardar lazy loading de novas páginas (segundos)
# Aumente este valor se o site estiver carregando devagar
DELAY_WAIT_LOAD = 5

# Intervalo para aguardar lazy loading (a cada X páginas)
# Ex: Se LAZY_LOAD_INTERVAL = 5, aguarda a cada 5 páginas (6, 11, 16, 21...)
LAZY_LOAD_INTERVAL = 5

# Pequeno delay entre páginas (segundos)
DELAY_MICRO = 0.5

# Timeout para aguardar elementos carregarem (segundos)
WAIT_TIMEOUT = 15

# Tempo inicial de espera após carregar a primeira página (segundos)
INITIAL_LOAD_WAIT = 3

# ===== CONFIGURAÇÕES DO NAVEGADOR =====

# Executar em modo headless (sem janela visível)
# True = não abre janela | False = abre janela do Chrome
HEADLESS = False

# User Agent para simular navegador real
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Tamanho da janela do navegador
WINDOW_SIZE = "1920,1080"

# ===== CONFIGURAÇÕES DE SAÍDA =====

# Nome do arquivo de saída JSON
OUTPUT_FILE = "results.json"

# Salvar screenshot da primeira página para debug
SAVE_SCREENSHOT = True

# Nome do arquivo de screenshot
SCREENSHOT_FILE = "debug_screenshot.png"

# ===== CONFIGURAÇÕES DE LOG =====

# Mostrar progresso a cada X páginas
PROGRESS_INTERVAL = 10

# Modo verbose (mais detalhes no log)
VERBOSE = True
