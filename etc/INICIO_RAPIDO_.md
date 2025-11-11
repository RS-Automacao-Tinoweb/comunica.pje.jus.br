# ⚡ Início Rápido - Scraper PJE

## 🎯 Método Recomendado: API Direta

### Por quê?
- ⚡ **10x mais rápido** que Selenium
- 🎯 Dados já em JSON
- 💪 Mais confiável
- 🔧 Fácil de usar

## 🚀 3 Passos para Começar

### 1️⃣ Instalar

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar requests
pip install requests
```

### 2️⃣ Testar

```bash
python test_api.py
```

Você verá:
- ✅ Tipos de comunicação disponíveis
- ✅ Classes de processos
- ✅ Exemplo de dados

### 3️⃣ Executar

```bash
python main_api.py
```

## ⚙️ Configuração Rápida

Edite `main_api.py`:

```python
# Período
SEARCH_PARAMS = {
    "dataDisponibilizacaoInicio": "2025-11-01",
    "dataDisponibilizacaoFim": "2025-11-10"
}

# Filtros (já configurados!)
FILTROS = {
    "tipoComunicacao": "Lista de distribuição",
    "codigoClasse": "12154",  # EXECUÇÃO DE TÍTULO EXTRAJUDICIAL
}

# Tribunais
TIPO_TRIBUNAL = "TODOS"  # "TJ", "TRF" ou "TODOS"
```

## 📊 Resultados

```
resultados_api/
├── TJSP.json          # Por tribunal
├── TRF1.json
├── consolidado.json   # Todos juntos
└── resumo.json        # Estatísticas
```

## ⏱️ Tempo

- **1 tribunal:** 5-10 segundos
- **33 tribunais:** 5-15 minutos

## 🎓 Outros Métodos (Não Recomendados)

### Selenium (Lento)
```bash
python main_selenium.py
```
- ⏱️ 1-3 horas
- 🖥️ Abre navegador
- ⚠️ Use apenas se API falhar

### curl_cffi (Não Funciona)
```bash
python main.py
```
- ❌ Não executa JavaScript
- ❌ Não funciona com este site

## 💡 Dica

**Sempre use `main_api.py`** - É o mais rápido e confiável! 🚀

## 📚 Documentação Completa

- `README_API.md` - Guia completo da API
- `README_MULTI_TRIBUNAL.md` - Selenium multi-tribunal
- `GUIA_RAPIDO.md` - Guia do Selenium

## ✅ Resumo

```bash
# 1. Instalar
pip install requests

# 2. Testar
python test_api.py

# 3. Executar
python main_api.py

# 4. Ver resultados
dir resultados_api
```

Pronto! 🎉
