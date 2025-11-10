# Scraper PJE - Consulta Processual

## Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual

**Opção A - Automática (Recomendado):**
```bash
setup.bat
```

**Opção B - Manual:**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Desativar o Ambiente Virtual
```bash
deactivate
```

## Estrutura do Projeto

```
RS - LySA - EMPRESA/
├── venv/                  # Ambiente virtual (não versionado)
├── main.py               # Arquivo principal
├── requirements.txt      # Dependências do projeto
├── setup.bat            # Script de configuração automática
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Este arquivo
```

## Sobre o Projeto

Script para extrair dados de processos judiciais do site **comunica.pje.jus.br**.

### Funcionalidades

- ✅ Extração automática de dados dos processos
- ✅ Suporte a paginação automática
- ✅ Extração de partes (polo ativo/passivo)
- ✅ Extração de advogados com OAB
- ✅ Links para certidão e inteiro teor
- ✅ Exportação em formato JSON

## Dependências

- **curl-cffi**: Requisições HTTP com impersonation (evita bloqueios)
- **beautifulsoup4**: Parser HTML para extração de dados

## Como Usar

### ⚠️ IMPORTANTE: Escolha o Método Correto

O site **comunica.pje.jus.br** usa **Angular/JavaScript** para renderizar o conteúdo. Existem 2 métodos:

#### Método 1: `main.py` (curl_cffi - NÃO FUNCIONA)
- ❌ Não executa JavaScript
- ❌ Não consegue extrair dados de sites Angular/React
- ⚠️ Use apenas para sites estáticos

#### Método 2: `main_selenium.py` (Selenium - RECOMENDADO) ✅
- ✅ Executa JavaScript como navegador real
- ✅ Funciona com sites Angular/React/Vue
- ✅ Suporta paginação dinâmica

### 1. Instalar Dependências

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar Selenium e dependências
pip install selenium webdriver-manager
```

### 2. Testar Paginação (Opcional mas Recomendado)

```bash
# Testar se a paginação está funcionando corretamente
python test_pagination.py
```

Este script irá:
- ✅ Verificar se os botões de paginação são encontrados
- ✅ Testar clique no botão "próxima"
- ✅ Testar clique direto nos números de página
- ✅ Salvar screenshots para debug

### 3. Executar o Scraper

```bash
# Método RECOMENDADO (com JavaScript)
python main_selenium.py

# Método alternativo (sem JavaScript - não funciona neste site)
python main.py
```

### 2. Configurar Parâmetros de Busca

Edite a variável `BASE_URL` no arquivo `main.py`:

```python
BASE_URL = "https://comunica.pje.jus.br/consulta?texto=distribuído&dataDisponibilizacaoInicio=2025-11-01&dataDisponibilizacaoFim=2025-11-10"
```

### 3. Resultado

Os dados serão salvos em `results.json` com a seguinte estrutura:

```json
[
  {
    "processo": "1000029-46.2021.4.01.3811",
    "link_certidao": "https://comunicaapi.pje.jus.br/api/v1/comunicacao/...",
    "órgão": "PRESIDÊNCIA",
    "data de disponibilização": "10/11/2025",
    "tipo de comunicação": "Lista de distribuição",
    "meio": "Diário de Justiça Eletrônico Nacional",
    "link_inteiro_teor": "https://eproctnu.cjf.jus.br/eproc/...",
    "partes": [
      {
        "polo": "Polo Passivo",
        "nome": "INSTITUTO NACIONAL DO SEGURO SOCIAL - INSS"
      },
      {
        "polo": "Polo Ativo",
        "nome": "NICES ANTONIO DA SILVA"
      }
    ],
    "advogados": [
      "ENIO ANDRADE RABELO - OAB MG-106974"
    ],
    "texto_distribuicao": "Processo 1000029-46.2021.4.01.3811 distribuido para PRESIDÊNCIA..."
  }
]
```

## Comandos Úteis

```bash
# Listar pacotes instalados
pip list

# Atualizar requirements.txt
pip freeze > requirements.txt

# Instalar novo pacote
pip install nome-do-pacote

# Atualizar pacote
pip install --upgrade nome-do-pacote
```

## Configurações Avançadas

### Ajustar Delay entre Requisições

Edite a variável `DELAY` no `main.py` (padrão: 0.6 segundos):

```python
DELAY = 1.0  # 1 segundo entre requisições
```

### Timeout de Requisições

```python
session = requests.Session(impersonate=IMPERSONATE, verify=True, timeout=60)
```
