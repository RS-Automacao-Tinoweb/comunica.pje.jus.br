# 🚀 Scraper PJE em Go - Versão Modular e Concorrente

Scraper de alto desempenho para API do PJE (Processo Judicial Eletrônico) utilizando goroutines nativas do Go com arquitetura modular.

## 🎯 Características

- **✅ Concorrência Real**: Goroutines (não limitado pelo GIL como Python)
- **✅ Arquitetura Modular**: Código organizado em pacotes (config, models, ratelimiter, httpclient, cache, scraper)
- **✅ Cache Isolado por Execução**: Cada scraping gera pasta separada `cache/TRIBUNAL_DATA_HORA/`
- **✅ Rate Limiter Adaptativo**: Reduz taxa ao detectar 429, aumenta gradualmente após 30s
- **✅ Retry com Backoff + Jitter**: Respeita Retry-After da API
- **✅ Timeout Multi-Nível**: Por requisição e por goroutine
- **✅ Progress em Tempo Real**: Atualiza a cada 500ms
- **✅ Filtros Client-Side**: Filtra tipoComunicacao e codigoClasse localmente

## 📁 Estrutura Modular

```
go_scraper_pje/
├── internal/
│   ├── config/         → Configurações e parsing de CLI
│   ├── models/         → Estruturas de dados (ApiResponse, Resultado)
│   ├── ratelimiter/    → Rate limiter adaptativo com token bucket
│   ├── httpclient/     → Cliente HTTP com retry automático
│   ├── cache/          → Gerenciamento de cache isolado
│   └── scraper/        → Lógica principal de scraping
├── main.go             → Entry point (50 linhas!)
└── go.mod              → Dependências do módulo
```

## 🗂️ Cache Isolado por Execução

Cada execução gera uma pasta separada com padrão: **`TRIBUNAL_ANO-MÊS-DIA_HORA-MIN-SEG`**

**Exemplo:**
```
cache/
├── TJSP_2025-11-11_18-07-56/    ← Execução 1
│   ├── abc123...json
│   ├── def456...json
│   └── ...
├── TJSP_2025-11-11_20-30-10/    ← Execução 2
│   └── ...
└── TJAM_2025-11-12_09-15-00/    ← Outro tribunal
    └── ...
```

**Vantagens:**
- ✅ Sem confusão entre extrações diferentes
- ✅ Histórico completo de scrapes
- ✅ Fácil de limpar cache antigo
- ✅ Comparar resultados entre datas

## 📦 Requisitos

- Go 1.21 ou superior

## 🚀 Como Executar

### Compilar e Rodar Diretamente
```powershell
cd go_scraper_pje
go run . --tribunais TJSP --inicio 2025-11-06 --fim 2025-11-10
```

### Gerar Executável
```powershell
go build -o scraper_pje.exe
.\scraper_pje.exe --tribunais TJSP --inicio 2025-11-06 --fim 2025-11-10
```

## ⚙️ Parâmetros CLI

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--tribunais` | TJAM | Siglas separadas por vírgula (ex: TJSP,TJAM) |
| `--inicio` | 2025-11-06 | Data inicial (YYYY-MM-DD) |
| `--fim` | 2025-11-10 | Data final (YYYY-MM-DD) |
| `--itens` | 100 | Itens por página (máx 100) |
| `--wp` | 3 | Workers de páginas (goroutines simultâneas) |
| `--wt` | 1 | Workers de tribunais |
| `--rps` | 3 | Taxa inicial de req/s (adaptativa) |
| `--retries` | 3 | Tentativas por requisição |
| `--timeout` | 30 | Timeout por requisição (segundos) |
| `--cache` | true | Habilitar cache local |
| `--out` | resultados | Diretório de saída |
| `--cache-dir` | cache | Diretório de cache |
| `--tipo` | Lista de distribuição | Filtro tipoComunicacao |
| `--classe` | 12154 | Filtro codigoClasse |

## 📊 Exemplos de Uso

### Básico (1 tribunal)
```powershell
go run . --tribunais TJSP --inicio 2025-11-06 --fim 2025-11-10
```

### Múltiplos Tribunais
```powershell
go run . --tribunais "TJSP,TJAM,TJBA" --wp 5 --rps 5
```

### Modo Conservador (evitar 429)
```powershell
go run . --tribunais TJSP --wp 2 --rps 2
```

### Modo Agressivo (servidor robusto)
```powershell
go run . --tribunais TJSP --wp 10 --rps 10
```

### Sem Cache
```powershell
go run . --tribunais TJSP --cache=false
```

## 🔍 Logs e Debug

O código agora exibe logs detalhados:
- `[✓]` Primeira página OK (tempo, count, items)
- `[⚡]` Progresso em tempo real
- `[❌]` Erros de requisição/parsing
- `[⚠️]` Rate limit (429) detectado
- `[💾]` Arquivo salvo

Se não trouxer resultados, verifique:
1. **Erro de conexão**: Veja mensagem `[❌] ... erro na requisição`
2. **Erro 429**: Reduza `--rps` e `--wp`
3. **Filtros**: Confira `--tipo` e `--classe`
4. **Cache corrompido**: Use `--cache=false`

## 📁 Estrutura de Saída

```
resultados_go/
├── TJSP.json       # Array de resultados filtrados
├── TJAM.json
└── ...
```

Cada arquivo contém:
```json
[
  {
    "id": 123456,
    "processo": "0000000-00.2025.8.26.0000",
    "data_disponibilizacao": "2025-11-06",
    "tribunal": "TJSP",
    "tipo_comunicacao": "Lista de distribuição",
    ...
  }
]
```

## ⚡ Performance: Go vs Python

| Métrica | Python (threads) | Go (goroutines) |
|---------|------------------|-----------------|
| **Overhead/worker** | ~1-2 MB/thread | ~2 KB/goroutine |
| **Paralelismo real** | ❌ Limitado pelo GIL | ✅ Pleno (todos os CPUs) |
| **Workers simultâneos** | ~10-50 (prático) | ~1000+ (sem problemas) |
| **Taxa de req/s** | ~5-10 req/s estável | ~20-50 req/s estável |
| **Consumo de CPU** | Alto (threads bloqueiam) | Baixo (multiplexação) |
| **Tempo TJSP (10k itens)** | ~3-5 min | ~1-2 min |

## 🛠️ Troubleshooting

### Erro: "go: command not found"
Instale Go: https://go.dev/dl/

### Travando em X%
- Reduza `--wp` para 2 ou 3
- Reduza `--rps` para 2
- Aumente `--timeout` para 60

### Muitos 429s
```powershell
go run . --tribunais TJSP --wp 2 --rps 2
```

### 0 Resultados (mas sem erro)
- Verifique filtros: `--tipo` e `--classe`
- Tente outro tribunal: `--tribunais TJAM`
- Desative cache: `--cache=false`

## 🔄 Comparação com Python

**Python (`main_api_otimizado.py`):**
- ThreadPoolExecutor (pseudo-paralelismo)
- requests.Session (bloqueante)
- ~5-10 threads práticos

**Go (`main.go`):**
- Goroutines (paralelismo real)
- net/http (multiplexado)
- ~100-1000 goroutines sem problemas

**Recomendação:**
- Use **Go** para volumes grandes (>100k registros) ou múltiplos tribunais
- Use **Python** se precisar integrar com pandas/IA ou prototipagem rápida

## 📝 Logs do Rate Limiter

Quando detecta 429:
```
[rate_limiter] 429 detectado: nova taxa 1.80 req/s (consec=1)
[⚠️] TJSP - Página 42: HTTP 429 - Aguardando 1.47s (tentativa 1/3)
```

Após 30s sem 429, aumenta gradualmente:
```
[rate_limiter] Taxa aumentada para 2.30 req/s
```

## 🎯 Próximos Passos

Para otimizar ainda mais:
1. Aumentar `--wp` gradualmente (5 → 10 → 20)
2. Aumentar `--rps` gradualmente (3 → 5 → 10)
3. Monitorar logs e ajustar conforme 429s apareçam

---

**Dúvidas?** Consulte os logs detalhados durante a execução.
