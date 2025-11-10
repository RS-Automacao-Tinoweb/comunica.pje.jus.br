# 🚀 Guia Rápido de Instalação

## Problema Identificado

O site **comunica.pje.jus.br** usa **Angular** para renderizar o conteúdo dinamicamente com JavaScript. 

- ❌ `main.py` (curl_cffi) → Não funciona (não executa JavaScript)
- ✅ `main_selenium.py` (Selenium) → **FUNCIONA** (executa JavaScript)

## Instalação Rápida

### 1. Instalar Dependências do Selenium

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar Selenium
pip install selenium webdriver-manager
```

### 2. Executar o Scraper

```bash
python main_selenium.py
```

## O que o Selenium faz?

1. **Abre um navegador Chrome real** (você verá a janela)
2. **Executa JavaScript** como um usuário normal
3. **Aguarda o conteúdo carregar** dinamicamente
4. **Extrai os dados** dos cards renderizados
5. **Navega pelas páginas** automaticamente
6. **Salva tudo em JSON**

## Modo Headless (Sem Janela)

Se quiser rodar sem abrir a janela do navegador, edite `main_selenium.py`:

```python
# Linha 230 - Mudar de False para True
driver = setup_driver(headless=True)  # Não abre janela
```

## Debug

O script salva automaticamente:

- `debug_screenshot.png` - Screenshot da primeira página
- `results.json` - Dados extraídos

## Diferenças Entre os Métodos

| Característica | curl_cffi (main.py) | Selenium (main_selenium.py) |
|----------------|---------------------|------------------------------|
| Executa JS | ❌ Não | ✅ Sim |
| Velocidade | ⚡ Rápido | 🐢 Mais lento |
| Sites Angular/React | ❌ Não funciona | ✅ Funciona |
| Uso de memória | 💚 Baixo | 🟡 Médio/Alto |
| Detecção de bot | 🟢 Difícil | 🟡 Possível |
| **Recomendado para PJE** | ❌ | ✅ |

## Próximos Passos

1. Execute `python main_selenium.py`
2. Aguarde o navegador abrir
3. Veja os dados sendo extraídos no terminal
4. Confira o arquivo `results.json`

## Troubleshooting

### Erro: "ChromeDriver not found"
```bash
pip install --upgrade webdriver-manager
```

### Erro: "Chrome binary not found"
- Instale o Google Chrome: https://www.google.com/chrome/

### Navegador não abre
- Verifique se o Chrome está instalado
- Tente rodar como administrador

### Muito lento
- Reduza o número de páginas no código (linha 269)
- Ative o modo headless (linha 230)
