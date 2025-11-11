# 🚀 Scraper PJE - API Direta (RECOMENDADO!)

## ⚡ Por Que Usar a API?

### Selenium (Antigo) ❌
- ⏱️ Lento (1-3 horas para 33 tribunais)
- 🖥️ Precisa abrir navegador
- 💾 Consome muita memória
- 🐛 Pode falhar com mudanças no HTML

### API Direta (Novo) ✅
- ⚡ **10x mais rápido** (5-15 minutos para 33 tribunais!)
- 🎯 Dados estruturados em JSON
- 💪 Mais confiável
- 🔧 Fácil de manter

## 📋 Filtros Configurados

O scraper já está configurado para buscar apenas:

✅ **Tipo de Comunicação:** "Lista de distribuição"  
✅ **Código de Classe:** 12154 (EXECUÇÃO DE TÍTULO EXTRAJUDICIAL)  
✅ **Período:** Configurável

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar apenas requests (super leve!)
pip install requests
```

### 2. Testar API (RECOMENDADO)

```bash
python test_api.py
```

Este teste irá:
- ✅ Fazer uma requisição para o TJSP
- ✅ Mostrar os tipos de comunicação disponíveis
- ✅ Mostrar as classes encontradas
- ✅ Salvar resposta em `teste_api_response.json`

### 3. Executar Scraper Completo

```bash
python main_api.py
```

## ⚙️ Configurações

Edite `main_api.py`:

### Período de Busca
```python
SEARCH_PARAMS = {
    "dataDisponibilizacaoInicio": "2025-11-01",  # Altere aqui
    "dataDisponibilizacaoFim": "2025-11-10"      # Altere aqui
}
```

### Filtros
```python
FILTROS = {
    "tipoComunicacao": "Lista de distribuição",  # Ou None para todos
    "codigoClasse": "12154",  # EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
}
```

### Tipo de Tribunal
```python
TIPO_TRIBUNAL = "TODOS"  # "TJ", "TRF" ou "TODOS"
```

### Itens por Página
```python
ITEMS_POR_PAGINA = 100  # Máximo: 100
```

## 📊 Exemplo de Saída

```
============================================================
SCRAPER PJE - API DIRETA (MUITO MAIS RÁPIDO!)
============================================================

[*] CONFIGURAÇÕES:
    Período: 2025-11-01 a 2025-11-10
    Tipo Comunicação: Lista de distribuição
    Código Classe: 12154
    Tipo Tribunal: TODOS

[*] Tribunais a processar: 33

[1/33] Processando TJAC...
============================================================
TRIBUNAL: TJAC - Tribunal de Justiça do Acre
============================================================

  [*] Buscando página 1...
  [✓] Página 1: 45 itens, 12 filtrados
      Total geral: 45 itens disponíveis
  [!] Última página alcançada

[✓] TJAC: 12 registros filtrados de 45 totais
  [💾] Salvo: resultados_api/TJAC.json

[2/33] Processando TJAL...
...

============================================================
RESUMO FINAL
============================================================
Total de tribunais processados: 33
Total geral de registros: 450

  - TJAC: 12 registros
  - TJSP: 85 registros
  - TRF1: 23 registros
  ...

[💾] Consolidado salvo: resultados_api/consolidado.json
[💾] Resumo salvo: resultados_api/resumo.json

============================================================
CONCLUÍDO!
============================================================
```

## 📁 Estrutura de Saída

```
resultados_api/
├── TJSP.json          # Dados filtrados do TJSP
├── TRF1.json          # Dados filtrados do TRF1
├── ...
├── consolidado.json   # Todos os dados juntos
└── resumo.json        # Estatísticas
```

## 📄 Formato dos Dados

Cada registro contém:

```json
{
  "id": 456690087,
  "processo": "1019209-79.2017.8.26.0506",
  "processo_sem_mascara": "10192097920178260506",
  "data_disponibilizacao": "10/11/2025",
  "tribunal": "TJSP",
  "tipo_comunicacao": "Lista de distribuição",
  "orgao": "7ª Vara Cível - Ribeirão Preto",
  "classe": "EXECUÇÃO DE TÍTULO EXTRAJUDICIAL",
  "codigo_classe": "12154",
  "tipo_documento": "Edital",
  "meio": "Plataforma Nacional de Editais",
  "link": "https://esaj.tjsp.jus.br",
  "hash": "MlkWByzDGYzOskhjhQm9JdRebmAjON",
  "texto": "<html>...</html>",
  "partes": [
    {
      "nome": "BANCO DO BRASIL S/A",
      "polo": "A"
    },
    {
      "nome": "MOTOSIDCAR VEICULOS EIRELI",
      "polo": "P"
    }
  ],
  "advogados": [
    {
      "nome": "MARLON SOUZA DO NASCIMENTO",
      "oab": "422271N",
      "uf": "SP"
    }
  ]
}
```

## ⏱️ Tempo Estimado

| Tribunais | Tempo (API) | Tempo (Selenium) |
|-----------|-------------|------------------|
| 1 | 5-10s | 1-5 min |
| 27 TJs | 3-8 min | 30-90 min |
| 6 TRFs | 1-2 min | 10-30 min |
| 33 TODOS | 5-15 min | 40-120 min |

**API é ~10x mais rápida!** ⚡

## 🎯 Códigos de Classe Disponíveis

Se quiser buscar outras classes, veja alguns códigos comuns:

- `7` - PROCEDIMENTO COMUM CÍVEL
- `81` - BUSCA E APREENSÃO EM ALIENAÇÃO FIDUCIÁRIA
- `159` - EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
- `12154` - EXECUÇÃO DE TÍTULO EXTRAJUDICIAL (outro código)

Para ver todos os códigos disponíveis, execute `test_api.py` e veja a seção "CLASSES ENCONTRADAS".

## 🔧 Filtros Avançados

### Apenas Data Atual

Descomente no `main_api.py`:

```python
def filtrar_item(item):
    # ... código existente ...
    
    # Filtro: data atual
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    if item.get("datadisponibilizacao") != data_hoje:
        return False
    
    return True
```

### Múltiplos Códigos de Classe

```python
FILTROS = {
    "tipoComunicacao": "Lista de distribuição",
    "codigoClasse": ["12154", "159", "7"]  # Lista de códigos
}

# E ajuste a função filtrar_item:
def filtrar_item(item):
    if FILTROS.get("codigoClasse"):
        codigos = FILTROS["codigoClasse"]
        if isinstance(codigos, list):
            if str(item.get("codigoClasse")) not in [str(c) for c in codigos]:
                return False
        else:
            if str(item.get("codigoClasse")) != str(codigos):
                return False
    # ...
```

## 💡 Dicas

### Para Máxima Velocidade
```python
ITEMS_POR_PAGINA = 100  # Máximo permitido
DELAY_BETWEEN_REQUESTS = 0.5  # Reduzir delay
DELAY_BETWEEN_TRIBUNAIS = 1
```

### Para Evitar Bloqueios
```python
ITEMS_POR_PAGINA = 50
DELAY_BETWEEN_REQUESTS = 2
DELAY_BETWEEN_TRIBUNAIS = 3
```

## 🐛 Troubleshooting

### Erro 429 (Too Many Requests)
- Aumente `DELAY_BETWEEN_REQUESTS`
- Reduza `ITEMS_POR_PAGINA`

### Timeout
- Aumente o timeout na função `fetch_page`
- Verifique sua conexão com a internet

### Nenhum resultado
- Verifique os filtros em `FILTROS`
- Execute `test_api.py` para ver dados disponíveis
- Ajuste o período em `SEARCH_PARAMS`

## 📝 Comparação de Métodos

| Característica | API | Selenium | curl_cffi |
|----------------|-----|----------|-----------|
| Velocidade | ⚡⚡⚡ | 🐌 | ⚡⚡ |
| Confiabilidade | ✅✅✅ | ⚠️ | ❌ |
| Dados | JSON | HTML | HTML |
| Memória | 💚 Baixa | 🔴 Alta | 💚 Baixa |
| Manutenção | ✅ Fácil | ⚠️ Média | ❌ Difícil |

**Recomendação:** Use sempre a API! 🚀

## 🎓 Entendimento da API

### URL da API
```
https://comunicaapi.pje.jus.br/api/v1/comunicacao
```

### Parâmetros Aceitos
- `pagina` - Número da página (começa em 1)
- `itensPorPagina` - Itens por página (máx: 100)
- `siglaTribunal` - Sigla do tribunal (ex: TJSP, TRF1)
- `dataDisponibilizacaoInicio` - Data início (formato: YYYY-MM-DD)
- `dataDisponibilizacaoFim` - Data fim (formato: YYYY-MM-DD)

### Resposta
```json
{
  "status": "success",
  "message": "Sucesso",
  "count": 10000,  // Total de itens
  "items": [...]   // Array de itens
}
```

## ✅ Checklist

- [ ] `requests` instalado
- [ ] Teste executado (`python test_api.py`)
- [ ] Período configurado
- [ ] Filtros ajustados
- [ ] Tipo de tribunal definido

## 🚀 Pronto!

```bash
python main_api.py
```

Aproveite a velocidade da API! ⚡
