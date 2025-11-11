# 🚀 Guia Rápido - Scraper Multi-Tribunal

## 📋 Opções Disponíveis

### 1️⃣ Scraping de Tribunal Único (Teste)
```bash
python test_single_tribunal.py
```
- ⚡ Rápido (1-5 minutos)
- 🎯 Testa um tribunal específico
- ✅ Ideal para validar funcionamento

### 2️⃣ Scraping de Todos os Tribunais
```bash
python main_multi_tribunal.py
```
- ⏱️ Demorado (30min - 3h)
- 🏛️ Processa 33 tribunais
- 📊 Gera consolidado completo

### 3️⃣ Scraping Tribunal Único (Original)
```bash
python main_selenium.py
```
- 🔧 Usa URL fixa do config.py
- 📄 Salva em results.json
- ⚡ Rápido

## 🎯 Fluxo Recomendado

### Primeira Vez

```bash
# 1. Teste com um tribunal
python test_single_tribunal.py

# 2. Se funcionou, rode todos
python main_multi_tribunal.py
```

### Uso Regular

```bash
# Processar todos os TJs e TRFs
python main_multi_tribunal.py
```

## ⚙️ Configurações Principais

### Escolher Tipo de Tribunal

Edite `config.py`:

```python
# Opções: "TJ", "TRF" ou "TODOS"
TIPO_TRIBUNAL = "TODOS"
```

### Ajustar Período

Edite `main_multi_tribunal.py`:

```python
SEARCH_PARAMS = {
    "texto": "distribuído",
    "dataDisponibilizacaoInicio": "2025-11-01",  # Altere aqui
    "dataDisponibilizacaoFim": "2025-11-10"      # Altere aqui
}
```

### Modo Rápido (Headless)

Edite `config.py`:

```python
HEADLESS = True  # Não abre janela
```

## 📁 Onde Ficam os Resultados

```
resultados_por_tribunal/
├── TJSP.json          # Por tribunal
├── TRF1.json
├── consolidado.json   # Todos juntos
└── resumo.json        # Estatísticas
```

## 🔧 Personalizar Lista de Tribunais

### Apenas Alguns Tribunais

Edite `tribunais.py`:

```python
# Exemplo: Apenas SP e RJ
TJS = [
    {"sigla": "TJSP", "nome": "Tribunal de Justiça de São Paulo"},
    {"sigla": "TJRJ", "nome": "Tribunal de Justiça do Rio de Janeiro"},
]

TRFS = [
    {"sigla": "TRF1", "nome": "Tribunal Regional Federal da 1ª Região"},
]
```

### Apenas TJs

```python
# config.py
TIPO_TRIBUNAL = "TJ"
```

### Apenas TRFs

```python
# config.py
TIPO_TRIBUNAL = "TRF"
```

## ⏱️ Tempo Estimado

| Modo | Tribunais | Tempo |
|------|-----------|-------|
| Teste | 1 | 1-5 min |
| Apenas TJs | 27 | 30-90 min |
| Apenas TRFs | 6 | 10-30 min |
| TODOS | 33 | 40-120 min |

## 💡 Dicas

### Para Teste Rápido
1. Use `test_single_tribunal.py`
2. Ou edite `tribunais.py` deixando 2-3 tribunais

### Para Produção
1. Configure `HEADLESS = True`
2. Use `TIPO_TRIBUNAL = "TODOS"`
3. Execute `main_multi_tribunal.py`
4. Aguarde (pode demorar 1-2 horas)

### Se Interromper
- Arquivos já salvos estão em `resultados_por_tribunal/`
- Edite `tribunais.py` removendo tribunais já processados
- Execute novamente

## 🐛 Problemas Comuns

### "Tribunal não encontrado no select"
- Verifique se a sigla está correta
- Aumente `INITIAL_LOAD_WAIT` no config.py

### Muito lento
- Ative `HEADLESS = True`
- Reduza `DELAY_BETWEEN_PAGES`

### Erro ao clicar em buscar
- Aumente `INITIAL_LOAD_WAIT`
- Verifique se o site está acessível

## 📊 Exemplo de Uso Completo

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate

# 2. Testar com um tribunal
python test_single_tribunal.py

# 3. Se OK, processar todos
python main_multi_tribunal.py

# 4. Verificar resultados
dir resultados_por_tribunal
```

## 🎓 Entendendo os Scripts

| Script | Função |
|--------|--------|
| `main_selenium.py` | Scraping básico (URL fixa) |
| `main_multi_tribunal.py` | Itera por tribunais |
| `test_single_tribunal.py` | Teste rápido |
| `tribunais.py` | Lista de tribunais |
| `config.py` | Configurações |

## ✅ Checklist Antes de Executar

- [ ] Ambiente virtual ativado
- [ ] Selenium instalado (`pip install selenium webdriver-manager`)
- [ ] `config.py` configurado
- [ ] Período definido em `main_multi_tribunal.py`
- [ ] Tipo de tribunal definido (`TJ`, `TRF` ou `TODOS`)
- [ ] Teste executado com sucesso

## 🚀 Pronto para Começar!

```bash
python main_multi_tribunal.py
```
