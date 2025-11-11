# 🏛️ Scraper PJE - Múltiplos Tribunais

## 📋 Visão Geral

Este scraper permite extrair dados de **todos os TJs e TRFs** automaticamente, fazendo buscas separadas para cada tribunal.

## 🎯 Funcionalidades

- ✅ Itera automaticamente por todos os tribunais
- ✅ Filtra por tipo: TJ, TRF ou TODOS
- ✅ Salva resultados separados por tribunal
- ✅ Gera arquivo consolidado com todos os dados
- ✅ Cria resumo com estatísticas
- ✅ Suporta paginação automática para cada tribunal

## 📊 Tribunais Suportados

### TJs (27 tribunais)
TJAC, TJAL, TJAM, TJAP, TJBA, TJCE, TJDFT, TJES, TJGO, TJMA, TJMG, TJMS, TJMT, TJPA, TJPB, TJPE, TJPI, TJPR, TJRJ, TJRN, TJRO, TJRR, TJRS, TJSC, TJSE, TJSP, TJTO

### TRFs (6 tribunais)
TRF1, TRF2, TRF3, TRF4, TRF5, TRF6

**Total: 33 tribunais**

## 🚀 Como Usar

### 1. Configurar Parâmetros

Edite `config.py`:

```python
# Tipo de tribunais: "TJ", "TRF" ou "TODOS"
TIPO_TRIBUNAL = "TODOS"

# Período da busca (já configurado na URL)
# Edite as datas conforme necessário
```

### 2. Executar

```bash
python main_multi_tribunal.py
```

### 3. Aguardar

O script irá:
1. Processar cada tribunal sequencialmente
2. Mostrar progresso em tempo real
3. Salvar resultados individuais
4. Gerar consolidado ao final

## 📁 Estrutura de Saída

```
resultados_por_tribunal/
├── TJSP.json          # Resultados do TJSP
├── TRF1.json          # Resultados do TRF1
├── TRF2.json          # Resultados do TRF2
├── ...                # Um arquivo por tribunal
├── consolidado.json   # Todos os resultados juntos
└── resumo.json        # Estatísticas e resumo
```

### Formato dos Arquivos

#### Arquivo Individual (ex: TJSP.json)
```json
[
  {
    "processo": "1000029-46.2021.4.01.3811",
    "órgão": "PRESIDÊNCIA",
    "data de disponibilização": "10/11/2025",
    "partes": [...],
    "advogados": [...],
    ...
  }
]
```

#### Consolidado (consolidado.json)
```json
{
  "TJSP": {
    "tribunal": "Tribunal de Justiça de São Paulo",
    "total_registros": 150,
    "registros": [...]
  },
  "TRF1": {
    "tribunal": "Tribunal Regional Federal da 1ª Região",
    "total_registros": 45,
    "registros": [...]
  }
}
```

#### Resumo (resumo.json)
```json
{
  "data_execucao": "2025-11-10T14:30:00",
  "total_tribunais": 33,
  "total_registros": 1250,
  "tribunais": {
    "TJSP": {
      "nome": "Tribunal de Justiça de São Paulo",
      "total": 150
    },
    "TRF1": {
      "nome": "Tribunal Regional Federal da 1ª Região",
      "total": 45
    }
  }
}
```

## ⚙️ Configurações Avançadas

### Processar Apenas TJs

```python
# config.py
TIPO_TRIBUNAL = "TJ"
```

### Processar Apenas TRFs

```python
# config.py
TIPO_TRIBUNAL = "TRF"
```

### Ajustar Delays

```python
# config.py
DELAY_BETWEEN_TRIBUNAIS = 3  # Pausa entre tribunais
DELAY_BETWEEN_PAGES = 4      # Pausa entre páginas
```

### Modo Headless (Mais Rápido)

```python
# config.py
HEADLESS = True  # Não abre janela do navegador
```

## 📊 Exemplo de Saída

```
============================================================
SCRAPER PJE - MÚLTIPLOS TRIBUNAIS
============================================================

[*] Tribunais a processar: 33
[*] Tipo: TODOS
[*] Período: 2025-11-01 a 2025-11-10

[1/33] Processando TJAC...
============================================================
TRIBUNAL: TJAC - Tribunal de Justiça do Acre
============================================================

  [✓] Tribunal selecionado: TJAC - Tribunal de Justiça do Acre
  [✓] Página 1: 5 registros
  [✓] Página 2: 3 registros
  [!] Fim da paginação na página 2

[✓] TJAC: 8 registros coletados
  [💾] Salvo: resultados_por_tribunal/TJAC.json

[2/33] Processando TJAL...
...

============================================================
RESUMO FINAL
============================================================
Total de tribunais processados: 33
Total geral de registros: 1250

  - TJAC: 8 registros
  - TJAL: 12 registros
  - TJSP: 150 registros
  - TRF1: 45 registros
  ...

[💾] Consolidado salvo: resultados_por_tribunal/consolidado.json
[💾] Resumo salvo: resultados_por_tribunal/resumo.json

============================================================
CONCLUÍDO!
============================================================
```

## ⏱️ Tempo Estimado

- **Por tribunal**: 30s - 5min (depende do número de páginas)
- **33 tribunais**: 30min - 3h (média: 1h)

## 💡 Dicas

### Para Teste Rápido
1. Edite `tribunais.py` e deixe apenas 2-3 tribunais na lista
2. Execute para testar
3. Depois restaure a lista completa

### Para Máxima Velocidade
```python
# config.py
HEADLESS = True
DELAY_BETWEEN_PAGES = 2
DELAY_BETWEEN_TRIBUNAIS = 1
```

### Para Máxima Confiabilidade
```python
# config.py
HEADLESS = False  # Ver o que está acontecendo
DELAY_BETWEEN_PAGES = 4
DELAY_WAIT_LOAD = 8
```

## 🐛 Troubleshooting

### Erro ao selecionar tribunal
**Causa:** Select não carregou
**Solução:** Aumente `INITIAL_LOAD_WAIT` no config.py

### Tribunal sem resultados
**Normal:** Nem todo tribunal tem processos no período buscado

### Script muito lento
**Solução:** Ative `HEADLESS = True`

### Interrompeu no meio
**Solução:** Os arquivos já salvos estão em `resultados_por_tribunal/`
Você pode processar tribunais específicos editando `tribunais.py`

## 📝 Arquivos do Projeto

- `main_multi_tribunal.py` - Script principal
- `tribunais.py` - Lista de tribunais
- `config.py` - Configurações
- `main_selenium.py` - Funções de scraping (importadas)

## 🎓 Como Funciona

1. **Carrega lista de tribunais** de `tribunais.py`
2. **Para cada tribunal:**
   - Acessa página de busca
   - Seleciona tribunal no dropdown
   - Clica em "Buscar"
   - Extrai dados de todas as páginas
   - Salva em arquivo JSON individual
3. **Ao final:**
   - Gera arquivo consolidado
   - Gera resumo com estatísticas
   - Mostra relatório final

## 🚀 Próximos Passos

Após executar, você terá:
- ✅ Dados de todos os tribunais separados
- ✅ Arquivo consolidado para análise
- ✅ Resumo com estatísticas
- ✅ Pronto para importar em banco de dados ou Excel
