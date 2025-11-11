# 📖 Explicação: Como Funciona a Paginação

## 🎯 Sua Preocupação (100% Válida!)

> "Está pegando todos os itens de cada tribunal ou só o primeiro e depois vai pro próximo?"

## ✅ Resposta: PEGA TODOS OS ITENS!

### Como Funciona o Código

```python
def scrape_tribunal_api(tribunal):
    all_results = []
    pagina = 1
    
    while True:  # ← Loop infinito até acabar as páginas
        # 1. Busca página atual
        data = fetch_page(sigla, pagina)
        
        # 2. Processa TODOS os itens da página
        for item in items:
            if filtrar_item(item):
                all_results.append(dados)  # ← Acumula TODOS
        
        # 3. Verifica se há mais páginas
        if len(items) < ITEMS_POR_PAGINA:
            break  # ← Só para quando não há mais
        
        # 4. Próxima página
        pagina += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)  # ← PAUSA AQUI!
    
    return all_results  # ← Retorna TODOS os resultados acumulados
```

## 📊 Exemplo Prático

### Tribunal com 250 itens, 100 por página:

```
[1/33] Processando TJSP...
============================================================
TRIBUNAL: TJSP - Tribunal de Justiça de São Paulo
============================================================

  [📄] Requisitando página 1...
  [✓] Página 1:
      - Itens nesta página: 100
      - Filtrados nesta página: 15
      - Total processado: 100/250
      - Total filtrado acumulado: 15
  [⏳] Aguardando 1s antes da próxima página...

  [📄] Requisitando página 2...
  [✓] Página 2:
      - Itens nesta página: 100
      - Filtrados nesta página: 12
      - Total processado: 200/250
      - Total filtrado acumulado: 27
  [⏳] Aguardando 1s antes da próxima página...

  [📄] Requisitando página 3...
  [✓] Página 3:
      - Itens nesta página: 50
      - Filtrados nesta página: 8
      - Total processado: 250/250
      - Total filtrado acumulado: 35
  [!] Última página alcançada (retornou 50 < 100)

[✅] TJSP CONCLUÍDO:
    - Total de páginas: 3
    - Total processado: 250
    - Total filtrado: 35
```

## 🔍 Verificações de Segurança

O código tem **3 verificações** para garantir que pegou tudo:

### 1. Verifica se retornou menos itens
```python
if len(items) < ITEMS_POR_PAGINA:
    break  # Última página
```

### 2. Verifica se processou tudo
```python
if total_items_processados >= count_total_api:
    break  # Já pegou todos
```

### 3. Verifica se não há mais itens
```python
if not items:
    break  # Página vazia
```

## ⏱️ Pausas Entre Requisições

### Entre Páginas (mesmo tribunal)
```python
DELAY_BETWEEN_REQUESTS = 1  # 1 segundo
```

Aplicado em:
```python
pagina += 1
time.sleep(DELAY_BETWEEN_REQUESTS)  # ← AQUI
```

### Entre Tribunais
```python
DELAY_BETWEEN_TRIBUNAIS = 2  # 2 segundos
```

Aplicado em:
```python
for tribunal in tribunais:
    scrape_tribunal_api(tribunal)
    time.sleep(DELAY_BETWEEN_TRIBUNAIS)  # ← AQUI
```

## 🧪 Como Testar

### Teste 1: Verificar Paginação
```bash
python test_paginacao_api.py
```

Este script:
- ✅ Usa apenas 10 itens por página (para forçar múltiplas páginas)
- ✅ Mostra cada página sendo processada
- ✅ Verifica se há IDs duplicados
- ✅ Salva todos os IDs coletados

### Teste 2: Ver Logs Detalhados
```bash
python main_api.py
```

Você verá logs como:
```
[📄] Requisitando página 1...
[✓] Página 1:
    - Itens nesta página: 100
    - Filtrados nesta página: 15
    - Total processado: 100/250
    - Total filtrado acumulado: 15
[⏳] Aguardando 1s antes da próxima página...
```

## 📋 Fluxo Completo

```
INÍCIO
  ↓
Para cada TRIBUNAL:
  ↓
  Página 1 → Processa TODOS os 100 itens → Acumula resultados
  ↓ (pausa 1s)
  Página 2 → Processa TODOS os 100 itens → Acumula resultados
  ↓ (pausa 1s)
  Página 3 → Processa TODOS os 50 itens → Acumula resultados
  ↓
  Retorna TODOS os resultados acumulados
  ↓ (pausa 2s)
Próximo TRIBUNAL
  ↓
FIM
```

## 🎯 Garantias

1. ✅ **Processa TODAS as páginas** de cada tribunal
2. ✅ **Acumula TODOS os resultados** em `all_results`
3. ✅ **Pausa entre páginas** (evita sobrecarga)
4. ✅ **Pausa entre tribunais** (evita bloqueio)
5. ✅ **Logs detalhados** para acompanhar progresso

## 💡 Configurações Recomendadas

### Para Máxima Velocidade
```python
ITEMS_POR_PAGINA = 100  # Máximo permitido
DELAY_BETWEEN_REQUESTS = 0.5  # Mínimo seguro
DELAY_BETWEEN_TRIBUNAIS = 1
```

### Para Máxima Confiabilidade
```python
ITEMS_POR_PAGINA = 50  # Médio
DELAY_BETWEEN_REQUESTS = 2  # Mais seguro
DELAY_BETWEEN_TRIBUNAIS = 3
```

### Configuração Atual (Balanceada)
```python
ITEMS_POR_PAGINA = 100
DELAY_BETWEEN_REQUESTS = 1
DELAY_BETWEEN_TRIBUNAIS = 2
```

## 🐛 Como Saber se Está Funcionando

### Sinais de que está OK:
- ✅ Vê múltiplas páginas sendo processadas
- ✅ "Total processado" aumenta gradualmente
- ✅ "Total filtrado acumulado" aumenta
- ✅ Vê mensagem "Última página alcançada"

### Sinais de problema:
- ❌ Sempre processa apenas 1 página
- ❌ "Total processado" não bate com "count_total_api"
- ❌ Não vê pausas entre páginas

## 📝 Resumo

**SIM**, o código:
- ✅ Itera por **TODAS as páginas** de cada tribunal
- ✅ Processa **TODOS os itens** de cada página
- ✅ **Acumula** todos os resultados
- ✅ Tem **pausas** entre requisições
- ✅ Só vai para o próximo tribunal após **terminar o atual**

Execute `python test_paginacao_api.py` para ver na prática! 🚀
