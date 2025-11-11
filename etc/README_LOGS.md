# 📝 Sistema de Logs - Scraper PJE API

## 🎯 O Que É Registrado

Cada requisição feita à API é registrada com os seguintes detalhes:

### Informações Básicas
- ✅ **Timestamp** - Data e hora da requisição
- ✅ **Tribunal** - Sigla do tribunal (TJSP, TRF1, etc)
- ✅ **Página** - Número da página requisitada
- ✅ **Status** - `success` ou `error`

### Detalhes da Requisição
- ✅ **URL Completa** - URL exata que foi chamada
- ✅ **Parâmetros** - Todos os parâmetros enviados:
  - `pagina`
  - `itensPorPagina`
  - `siglaTribunal`
  - `dataDisponibilizacaoInicio`
  - `dataDisponibilizacaoFim`

### Resposta da API
- ✅ **Total Disponível** - Quantos itens existem no total
- ✅ **Itens Retornados** - Quantos itens vieram nesta página
- ✅ **Erro** - Mensagem de erro (se houver)

## 📁 Arquivo de Log

**Nome:** `scraper_requests.log`

**Formato:** JSON Lines (um JSON por linha)

**Localização:** Raiz do projeto

## 📊 Exemplo de Log

```json
{
  "timestamp": "2025-11-10 21:30:45",
  "tribunal": "TJSP",
  "pagina": 1,
  "url": "https://comunicaapi.pje.jus.br/api/v1/comunicacao?pagina=1&itensPorPagina=100&siglaTribunal=TJSP&dataDisponibilizacaoInicio=2025-11-06&dataDisponibilizacaoFim=2025-11-10",
  "params": {
    "pagina": 1,
    "itensPorPagina": 100,
    "siglaTribunal": "TJSP",
    "dataDisponibilizacaoInicio": "2025-11-06",
    "dataDisponibilizacaoFim": "2025-11-10"
  },
  "status": "success",
  "error": null,
  "response_summary": {
    "total_disponivel": 250,
    "itens_retornados": 100
  }
}
```

## 🔍 Como Visualizar os Logs

### Opção 1: Visualizador Interativo (Recomendado)

```bash
python visualizar_log.py
```

Menu interativo com opções:
1. **Resumo Geral** - Estatísticas de todas as requisições
2. **Logs Detalhados** - Ver todos os logs
3. **Logs com URLs** - Ver logs incluindo URLs completas
4. **Tribunal Específico** - Filtrar por tribunal
5. **Apenas Erros** - Ver somente requisições com erro
6. **Linha do Tempo** - Ver cronologia das requisições
7. **Exportar JSON** - Salvar logs em arquivo formatado

### Opção 2: Ler Arquivo Diretamente

```bash
# Ver últimas 10 linhas
Get-Content scraper_requests.log -Tail 10

# Ver todo o arquivo
Get-Content scraper_requests.log
```

### Opção 3: Analisar com Python

```python
import json

with open("scraper_requests.log", "r", encoding="utf-8") as f:
    for line in f:
        log = json.loads(line)
        print(f"{log['tribunal']} - Página {log['pagina']}: {log['response_summary']['itens_retornados']} itens")
```

## 📈 Exemplos de Análise

### Ver Resumo Geral

```bash
python visualizar_log.py
# Escolha opção 1
```

Saída:
```
================================================================================
RESUMO GERAL DOS LOGS
================================================================================
Total de requisições: 45
  ✅ Sucesso: 43
  ❌ Erros: 2

Tribunais processados: 5

ESTATÍSTICAS POR TRIBUNAL:
--------------------------------------------------------------------------------
  TJAC:
    - Requisições: 3 (✅ 3 | ❌ 0)
    - Páginas: 3
    - Itens retornados: 245
  TJSP:
    - Requisições: 15 (✅ 14 | ❌ 1)
    - Páginas: 15
    - Itens retornados: 1450
```

### Ver Linha do Tempo

```bash
python visualizar_log.py
# Escolha opção 6
```

Saída:
```
================================================================================
LINHA DO TEMPO DAS REQUISIÇÕES
================================================================================

📍 TJSP
--------------------------------------------------------------------------------
  2025-11-10 21:30:45 | ✅ Página  1 → 100 itens
  2025-11-10 21:30:47 | ✅ Página  2 → 100 itens
  2025-11-10 21:30:49 | ✅ Página  3 → 50 itens

📍 TRF1
--------------------------------------------------------------------------------
  2025-11-10 21:30:52 | ✅ Página  1 → 75 itens
```

### Ver Apenas Erros

```bash
python visualizar_log.py
# Escolha opção 5
```

### Filtrar por Tribunal

```bash
python visualizar_log.py
# Escolha opção 4
# Digite: TJSP
```

## 🎯 Casos de Uso

### 1. Verificar se Todas as Páginas Foram Processadas

```bash
python visualizar_log.py
# Opção 4 (Tribunal Específico)
# Digite o tribunal
```

Você verá todas as páginas requisitadas para aquele tribunal.

### 2. Identificar Problemas de Conexão

```bash
python visualizar_log.py
# Opção 5 (Apenas Erros)
```

Mostra todas as requisições que falharam.

### 3. Analisar Performance

Veja os timestamps para calcular:
- Tempo entre requisições
- Tempo total por tribunal
- Tempo médio por página

### 4. Validar Parâmetros

Verifique se os parâmetros estão corretos:
- Período de datas
- Itens por página
- Tribunal

### 5. Exportar para Análise Externa

```bash
python visualizar_log.py
# Opção 7 (Exportar JSON)
```

Gera arquivo `logs_analise.json` formatado para análise em outras ferramentas.

## 🔧 Configuração

### Alterar Nome do Arquivo de Log

Em `main_api.py`:
```python
LOG_FILE = "meu_log_customizado.log"
```

### Desabilitar Logs

Comente a linha em `fetch_page`:
```python
# log_request(sigla_tribunal, pagina, url, params, response_data=data)
```

### Adicionar Mais Informações ao Log

Edite a função `log_request` em `main_api.py`:
```python
log_entry = {
    # ... campos existentes ...
    "meu_campo_customizado": "valor"
}
```

## 📊 Informações no Console

Durante a execução, você verá:

```
[🌐] URL: https://comunicaapi.pje.jus.br/api/v1/comunicacao?pagina=1&...
[✓] Página 1:
    - Itens nesta página: 100
    - Filtrados nesta página: 15
    - Total processado: 100/250
    - Total filtrado acumulado: 15
```

## 💡 Dicas

### 1. Log é Limpo a Cada Execução
O arquivo de log é apagado no início de cada execução do scraper para evitar misturar dados de diferentes execuções.

### 2. Use o Visualizador
O `visualizar_log.py` torna muito mais fácil analisar os logs do que ler o arquivo bruto.

### 3. Exporte para Análise
Use a opção de exportar para JSON se quiser analisar os dados em Excel, Power BI, etc.

### 4. Verifique Erros Primeiro
Se algo deu errado, vá direto na opção "Apenas Erros" do visualizador.

### 5. Compare Total Disponível vs Retornado
Se `total_disponivel` for maior que `itens_retornados`, significa que há mais páginas.

## 🐛 Troubleshooting

### Arquivo de log não existe
Execute o scraper primeiro:
```bash
python main_api.py
```

### Logs aparecem duplicados
Isso é normal! Cada linha representa uma requisição. Se o scraper fez 3 requisições para o TJSP (páginas 1, 2, 3), você verá 3 linhas.

### Erro ao ler JSON
Certifique-se de que o arquivo não está corrompido. Você pode deletá-lo e executar o scraper novamente.

### Muitos logs
Se o arquivo ficar muito grande, você pode:
1. Processar menos tribunais por vez
2. Usar períodos menores
3. Exportar e arquivar logs antigos

## 📝 Resumo

**Para ver os logs:**
```bash
python visualizar_log.py
```

**Arquivo de log:**
```
scraper_requests.log
```

**Formato:**
```
JSON Lines (um JSON por linha)
```

**O que é registrado:**
- ✅ Cada requisição à API
- ✅ URL completa
- ✅ Parâmetros enviados
- ✅ Resposta recebida
- ✅ Erros (se houver)

**Use para:**
- 🔍 Verificar se todas as páginas foram processadas
- 🐛 Identificar erros
- 📊 Analisar performance
- ✅ Validar parâmetros
