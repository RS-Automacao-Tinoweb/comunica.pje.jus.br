# 🔧 Guia de Ajustes - Lazy Loading

## ✅ Melhorias Implementadas

### 1. **Espera Inteligente para Lazy Loading**
- A cada 5 páginas (configurável), o script aguarda 5 segundos extras
- Permite que o site carregue as próximas páginas em background
- Evita parar prematuramente achando que não há mais dados

### 2. **Navegação por Botão "Próxima"**
- Usa o botão de navegação do site (mais confiável)
- Detecta quando o botão está desabilitado (fim real da paginação)
- Múltiplos seletores para garantir compatibilidade

### 3. **Detecção de Páginas Vazias**
- Para após 3 páginas vazias consecutivas (configurável)
- Evita loops infinitos
- Distingue entre "carregando" e "sem dados"

### 4. **Arquivo de Configuração**
- Todas as configurações em `config.py`
- Fácil ajustar sem mexer no código principal

## 🎯 Como Ajustar para Mais de 100 Páginas

### Opção 1: Aumentar Tempo de Lazy Loading

Edite `config.py`:

```python
# Aumentar tempo de espera para lazy loading
DELAY_WAIT_LOAD = 8  # Era 5, agora 8 segundos

# Aguardar lazy loading com mais frequência
LAZY_LOAD_INTERVAL = 3  # A cada 3 páginas (era 5)
```

### Opção 2: Aumentar Delay Entre Páginas

```python
# Dar mais tempo para o site processar
DELAY_BETWEEN_PAGES = 5  # Era 3, agora 5 segundos
```

### Opção 3: Aumentar Máximo de Páginas

```python
# Se souber que tem mais de 200 páginas
MAX_PAGES = 500  # Aumentar limite
```

### Opção 4: Aumentar Tolerância a Páginas Vazias

```python
# Aguardar mais páginas vazias antes de parar
MAX_CONSECUTIVE_EMPTY = 5  # Era 3, agora 5
```

## 📊 Configurações Recomendadas para 100+ Páginas

```python
# config.py - CONFIGURAÇÃO OTIMIZADA

# Paginação
MAX_PAGES = 500
MAX_CONSECUTIVE_EMPTY = 5

# Timing (mais conservador)
DELAY_BETWEEN_PAGES = 4
DELAY_WAIT_LOAD = 8
LAZY_LOAD_INTERVAL = 3
DELAY_MICRO = 1.0

# Timeout maior
WAIT_TIMEOUT = 20
INITIAL_LOAD_WAIT = 5

# Modo headless para performance
HEADLESS = True
```

## 🚀 Teste Rápido

1. **Primeira execução** - Use configurações padrão:
   ```bash
   python main_selenium.py
   ```

2. **Se parar cedo** - Aumente `DELAY_WAIT_LOAD`:
   ```python
   DELAY_WAIT_LOAD = 10  # 10 segundos
   ```

3. **Se ainda parar cedo** - Aumente `LAZY_LOAD_INTERVAL`:
   ```python
   LAZY_LOAD_INTERVAL = 2  # A cada 2 páginas
   ```

4. **Para máxima extração** - Use configuração conservadora:
   ```python
   DELAY_WAIT_LOAD = 10
   LAZY_LOAD_INTERVAL = 2
   MAX_CONSECUTIVE_EMPTY = 7
   HEADLESS = True  # Mais rápido
   ```

## 📈 Monitoramento

O script mostra progresso a cada 10 páginas:

```
[ℹ️] Progresso: 20/150 páginas
[ℹ️] Progresso: 30 páginas processadas, 45 registros
```

## ⚡ Dicas de Performance

### Para Máxima Velocidade:
```python
HEADLESS = True
DELAY_BETWEEN_PAGES = 2
DELAY_WAIT_LOAD = 5
LAZY_LOAD_INTERVAL = 5
```

### Para Máxima Confiabilidade:
```python
HEADLESS = False  # Ver o que está acontecendo
DELAY_BETWEEN_PAGES = 5
DELAY_WAIT_LOAD = 10
LAZY_LOAD_INTERVAL = 2
```

## 🐛 Troubleshooting

### Problema: Para na página 5
**Solução:** Aumente `DELAY_WAIT_LOAD` para 8-10 segundos

### Problema: Muitas páginas vazias
**Solução:** Aumente `MAX_CONSECUTIVE_EMPTY` para 5-7

### Problema: Muito lento
**Solução:** 
- Ative `HEADLESS = True`
- Reduza `DELAY_BETWEEN_PAGES` para 2
- Reduza `LAZY_LOAD_INTERVAL` para 5

### Problema: Pula páginas
**Solução:** Aumente `DELAY_BETWEEN_PAGES` para 4-5 segundos

## 📝 Exemplo de Uso

```bash
# 1. Editar config.py com suas preferências
# 2. Executar
python main_selenium.py

# 3. Aguardar (pode demorar para 100+ páginas)
# 4. Verificar results.json
```

## 🎓 Entendendo o Lazy Loading

O site carrega páginas em "lotes":
- Páginas 1-5: Carregadas imediatamente
- Páginas 6-10: Carregam quando você chega na página 5
- Páginas 11-15: Carregam quando você chega na página 10

Por isso, a cada 5 páginas, aguardamos mais tempo!
