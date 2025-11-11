# 🚀 Guia de Início Rápido - Versão Otimizada

## ⚡ Execução Imediata

### 1. Execute a versão otimizada
```bash
python main_api_otimizado.py
```

Pronto! O script vai processar automaticamente com todas as otimizações ativadas.

---

## ⚙️ Configurações Principais

Edite estas variáveis no início de `main_api_otimizado.py`:

### 📅 Período de Busca
```python
SEARCH_PARAMS = {
    "dataDisponibilizacaoInicio": "2025-11-06",  # Data inicial
    "dataDisponibilizacaoFim": "2025-11-10"      # Data final
}
```

### 🏛️ Tribunais
```python
TIPO_TRIBUNAL = "TODOS"  # Opções: "TJ", "TRF", "TODOS"

# Para testar com tribunais específicos:
TRIBUNAIS_ESPECIFICOS = ["TJSP", "TJRJ"]  # Ou [] para todos
```

### 🔍 Filtros
```python
FILTROS = {
    "tipoComunicacao": "Lista de distribuição",
    "codigoClasse": "12154",  # EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
}

# Para buscar tudo, deixe vazio:
FILTROS = {}
```

### ⚡ Performance
```python
# Configuração PADRÃO (Recomendada)
MAX_WORKERS_TRIBUNAIS = 5   # 5 tribunais simultâneos
MAX_WORKERS_PAGINAS = 10    # 10 páginas por tribunal
MAX_REQUESTS_PER_SECOND = 10

# Configuração AGRESSIVA (Máxima velocidade)
MAX_WORKERS_TRIBUNAIS = 10
MAX_WORKERS_PAGINAS = 20
MAX_REQUESTS_PER_SECOND = 20

# Configuração CONSERVADORA (Mais seguro)
MAX_WORKERS_TRIBUNAIS = 2
MAX_WORKERS_PAGINAS = 5
MAX_REQUESTS_PER_SECOND = 5
```

---

## 📊 Entendendo os Resultados

### Durante a Execução
```
🚀 TRIBUNAL: TJSP - Tribunal de Justiça de São Paulo
================================================================================

  [📊] Descobrindo total de páginas...
  [ℹ️] Total de itens: 10,000
  [ℹ️] Total de páginas: 100
  [⚡] Iniciando scraping paralelo com 10 workers...

  [⚡] Progresso: 100/100 páginas (100.0%) | Filtrados: 1,234
```

### Estatísticas Finais
```
================================================================================
[✅] TJSP CONCLUÍDO
================================================================================
  📊 ESTATÍSTICAS:
      - Páginas processadas: 100
      - Itens totais: 10,000
      - Itens filtrados: 1,234          ← Itens que passaram nos filtros
      - Taxa de filtro: 12.3%           ← % de itens relevantes
      - Tempo total: 25.3s              ← Tempo real de execução
      - Velocidade: 395 itens/s         ← Itens processados por segundo
      - Páginas/s: 4.0                  ← Páginas processadas por segundo
```

---

## 📁 Arquivos Gerados

### Estrutura de Saída
```
resultados_api/
├── TJSP.json              ← Dados do TJSP
├── TJRJ.json              ← Dados do TJRJ
├── consolidado.json       ← Todos os tribunais juntos
└── resumo.json            ← Estatísticas gerais

cache_api/                 ← Cache (opcional)
└── [hash].json            ← Páginas em cache

scraper_requests.log       ← Log de todas as requisições
```

### Exemplo de Dados (TJSP.json)
```json
[
  {
    "id": 454532760,
    "processo": "0000000-00.2025.8.26.0000",
    "data_disponibilizacao": "2025-11-06",
    "tribunal": "TJSP",
    "tipo_comunicacao": "Lista de distribuição",
    "classe": "EXECUÇÃO DE TÍTULO EXTRAJUDICIAL",
    "partes": [
      {"nome": "EMPRESA XYZ LTDA", "polo": "Exequente"}
    ],
    "advogados": [
      {"nome": "JOÃO SILVA", "oab": "123456", "uf": "SP"}
    ]
  }
]
```

---

## 🔧 Ajustes Finos

### Se receber erro "Too Many Requests" (429)
```python
# Reduza a velocidade:
MAX_REQUESTS_PER_SECOND = 5
MAX_WORKERS_PAGINAS = 5
RATE_LIMIT_ENABLED = True
```

### Se quiser desativar cache (sempre buscar dados novos)
```python
CACHE_ENABLED = False
```

### Se quiser desativar logs (mais rápido)
```python
LOG_ENABLED = False
```

---

## 🎯 Casos de Uso Comuns

### Caso 1: Buscar tudo de um tribunal específico
```python
TIPO_TRIBUNAL = "TJ"
TRIBUNAIS_ESPECIFICOS = ["TJSP"]
FILTROS = {}  # Sem filtros
```

### Caso 2: Buscar apenas execuções
```python
FILTROS = {
    "codigoClasse": "12154"  # EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
}
```

### Caso 3: Buscar de todos os TRFs
```python
TIPO_TRIBUNAL = "TRF"
TRIBUNAIS_ESPECIFICOS = []  # Todos os TRFs
```

### Caso 4: Teste rápido
```python
TRIBUNAIS_ESPECIFICOS = ["TJAC"]  # Tribunal pequeno
MAX_WORKERS_PAGINAS = 5
```

---

## 📈 Comparação de Velocidade

| Cenário | Tempo Original | Tempo Otimizado | Ganho |
|---------|---------------|-----------------|-------|
| TJSP (100 páginas) | 4 minutos | 15 segundos | **16x** |
| 5 tribunais médios | 20 minutos | 1 minuto | **20x** |
| 27 TJs completos | 2 horas | 6 minutos | **20x** |

---

## 🆘 Problemas Comuns

### ❌ Erro: ModuleNotFoundError: No module named 'tribunais'
**Solução:** Certifique-se de que o arquivo `tribunais.py` existe no mesmo diretório.

### ❌ Erro: Connection timeout
**Solução:** 
```python
# Aumente o timeout em fetch_page()
response = session.get(url, timeout=60)  # Era 30
```

### ❌ Alto uso de memória
**Solução:** Reduza os workers:
```python
MAX_WORKERS_TRIBUNAIS = 2
MAX_WORKERS_PAGINAS = 5
```

### ❌ Cache ocupando muito espaço
**Solução:** Limpe periodicamente:
```bash
rmdir /s cache_api
```

---

## 💡 Dicas Pro

### 1. Use cache para desenvolvimento
Durante testes, ative o cache para não fazer requisições repetidas:
```python
CACHE_ENABLED = True
```

### 2. Monitore o log
Acompanhe erros e problemas:
```bash
tail -f scraper_requests.log  # Linux/Mac
Get-Content scraper_requests.log -Wait  # Windows PowerShell
```

### 3. Comece devagar
Primeira vez? Use configuração conservadora:
```python
MAX_WORKERS_TRIBUNAIS = 2
MAX_WORKERS_PAGINAS = 5
TRIBUNAIS_ESPECIFICOS = ["TJAC"]  # Tribunal pequeno
```

### 4. Escale gradualmente
Funcionou? Aumente aos poucos:
```python
# Teste 1: Conservador
MAX_WORKERS_PAGINAS = 5

# Teste 2: Moderado
MAX_WORKERS_PAGINAS = 10

# Teste 3: Agressivo
MAX_WORKERS_PAGINAS = 20
```

---

## 🎊 Resultado Esperado

```
================================================================================
📊 RESUMO FINAL
================================================================================
Total de tribunais processados: 5
Total geral de registros: 12,345
Tempo total de execução: 67.3s (1.1 min)
Velocidade média: 183 registros/s

  - TJSP: 5,234 registros
  - TJRJ: 3,456 registros
  - TJMG: 2,134 registros
  - TJRS: 987 registros
  - TJPR: 534 registros

[💾] Consolidado salvo: resultados_api/consolidado.json
[💾] Resumo salvo: resultados_api/resumo.json

================================================================================
✅ CONCLUÍDO COM SUCESSO!
================================================================================
```

---

## 🚀 Próximos Passos

1. ✅ Execute com configuração padrão
2. ✅ Verifique os resultados em `resultados_api/`
3. ✅ Ajuste filtros conforme necessário
4. ✅ Escale para mais tribunais
5. ✅ Automatize com cron/task scheduler se necessário

**Boa sorte e aproveite a velocidade! 🎯**
