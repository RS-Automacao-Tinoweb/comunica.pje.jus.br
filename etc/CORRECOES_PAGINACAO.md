# 🔧 Correções de Paginação - PrimeNG

## 🎯 Problema Identificado

O site usa **PrimeNG p-paginator** com estrutura HTML específica:

```html
<p-paginator>
  <a class="ui-paginator-prev ui-state-disabled">←</a>
  <a class="ui-paginator-page ui-state-active">1</a>
  <a class="ui-paginator-page">2</a>
  <a class="ui-paginator-page">3</a>
  <a class="ui-paginator-next">→</a>
</p-paginator>
```

### Classes Importantes:
- `ui-paginator-next` - Botão "próxima página" (seta →)
- `ui-paginator-prev` - Botão "página anterior" (seta ←)
- `ui-paginator-page` - Botões numéricos (1, 2, 3...)
- `ui-state-disabled` - Indica que o botão está desabilitado
- `ui-state-active` - Indica a página atual

## ✅ Correções Implementadas

### 1. **Seletor Correto para Botão "Next"**

**Antes:**
```python
# Seletores genéricos que não funcionavam
"[aria-label*='next']"
".mat-paginator-navigation-next"
```

**Depois:**
```python
# Seletor específico do PrimeNG
"a.ui-paginator-next"
```

### 2. **Detecção de Botão Desabilitado**

```python
classes = next_button.get_attribute("class")
if "ui-state-disabled" in classes:
    # Fim da paginação
    return False
```

### 3. **Clique com JavaScript**

```python
# Mais confiável que .click() normal
driver.execute_script("arguments[0].click();", next_button)
```

### 4. **Detecção de Páginas Visíveis**

```python
page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
for btn in page_buttons:
    if btn.text.isdigit():
        page_numbers.append(int(btn.text))
```

### 5. **Navegação Alternativa por Número**

Função adicional para clicar diretamente no número da página:

```python
def navigate_to_page_number(driver, page_num):
    page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.ui-paginator-page")
    for btn in page_buttons:
        if btn.text.strip() == str(page_num):
            btn.click()
            return True
```

## 🧪 Como Testar

### 1. Script de Teste

```bash
python test_pagination.py
```

Este script irá:
- ✅ Verificar se encontra os elementos de paginação
- ✅ Mostrar informações sobre os botões
- ✅ Testar clique no botão "next"
- ✅ Testar clique direto no número "2"
- ✅ Salvar screenshots para análise

### 2. Executar Scraper Completo

```bash
python main_selenium.py
```

## 📊 Saída Esperada

```
[*] Processando página 1...
  [+] Encontrados 1 cards
  [📄] Páginas visíveis: [1, 2, 3, 4, 5]
[+] Total de páginas detectado: 6
[*] Iniciando navegação pelas páginas (máx: 200)...

  [✓] Navegando para próxima página...
[*] Processando página 2...
  [+] Encontrados 1 cards
  [✓] Página 2: 1 registros

  [✓] Navegando para próxima página...
[*] Processando página 3...
  [+] Encontrados 1 cards
  [✓] Página 3: 1 registros
...
```

## 🐛 Troubleshooting

### Problema: "Botão 'próxima página' não encontrado"

**Causa:** O site pode estar carregando lentamente

**Solução 1:** Aumentar tempo de espera inicial
```python
# config.py
INITIAL_LOAD_WAIT = 5  # Era 3
```

**Solução 2:** Executar script de teste
```bash
python test_pagination.py
```

### Problema: Clica mas não muda de página

**Causa:** Clique não está sendo registrado

**Solução:** O código já usa `execute_script` para clicar via JavaScript (mais confiável)

### Problema: Para na página 5

**Causa:** Lazy loading - páginas 6+ ainda não carregaram

**Solução:** Aumentar `DELAY_WAIT_LOAD`
```python
# config.py
DELAY_WAIT_LOAD = 8  # Era 5
LAZY_LOAD_INTERVAL = 3  # A cada 3 páginas
```

## 📝 Arquivos Modificados

1. ✅ `main_selenium.py` - Corrigidos seletores de paginação
2. ✅ `test_pagination.py` - Novo script de teste
3. ✅ `README.md` - Adicionadas instruções de teste

## 🚀 Próximos Passos

1. Execute o teste: `python test_pagination.py`
2. Verifique os screenshots gerados
3. Se o teste passar, execute: `python main_selenium.py`
4. Ajuste `config.py` se necessário

## 💡 Dica

Se ainda tiver problemas, rode com `HEADLESS = False` no `config.py` para ver o navegador em ação e identificar o que está acontecendo.
