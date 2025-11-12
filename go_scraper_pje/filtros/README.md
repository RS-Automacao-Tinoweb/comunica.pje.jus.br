# 🔍 Interface de Filtros PJE Scraper

Sistema web para processar e filtrar dados extraídos do cache de forma visual e interativa.

## 🎯 Funcionalidades

### Processamento e Filtragem
- ✅ **Interface Web Moderna**: Design responsivo e intuitivo
- ✅ **Filtros Avançados**: Múltiplos critérios de filtro
- ✅ **Processamento de Cache**: Lê todos os arquivos JSON do cache
- ✅ **Extração de Data de Despacho**: Automática do campo texto
- ✅ **Dados Corrigidos**: Mapeamento correto dos campos da API
- ✅ **Salvamento Automático**: Gera JSON em `dados_filtrados/`

### Visualização e Análise
- ✅ **Visualização de Dados**: Tabela interativa com paginação
- ✅ **Busca em Tempo Real**: Filtro rápido na tabela
- ✅ **Exportação CSV**: Download direto em formato Excel
- ✅ **Exportação JSON**: Download dos dados filtrados
- ✅ **Dashboard**: Estatísticas e métricas em tempo real
- ✅ **Progresso de Meta**: Acompanhamento visual da meta mensal

### Gerenciamento
- ✅ **Gerenciar Cache**: Visualizar e deletar caches
- ✅ **Informações Detalhadas**: Tamanho, itens, data de criação
- ✅ **Exclusão Seletiva**: Deletar caches específicos
- ✅ **Navegação Integrada**: Menu unificado entre todas as páginas

## 🚀 Como Usar

### 1. Iniciar o Servidor

```powershell
cd filtros
go run main.go
```

O servidor iniciará em: **http://localhost:8080**

### 2. Abrir no Navegador

```powershell
Start-Process http://localhost:8080
```

## 📱 Páginas Disponíveis

O sistema possui 4 páginas principais acessíveis pelo menu de navegação:

### 🔍 Filtrar Dados (`/`)
Página principal para processar e filtrar dados do cache.

**Funcionalidades:**
- Seleção de cache disponível
- Configuração de filtros (tribunal, datas, tipo, etc)
- Processamento em tempo real
- Geração de arquivo JSON filtrado

### 📊 Visualizar Resultados (`/visualizar`)
Visualização interativa dos dados filtrados.

**Funcionalidades:**
- Seleção de arquivo filtrado
- Tabela paginada (50 itens por página)
- **⚠️ DATA DESPACHO em DESTAQUE** - Coluna destacada em amarelo com contagem de dias
- **Alerta automático** - Processos com mais de 15 dias aparecem em VERMELHO
- **Contador de prazos críticos** - Estatísticas de processos urgentes
- Busca em tempo real
- Exportação para CSV (com Data Despacho em destaque)
- Download JSON
- Informações de valor potencial

### 🗂️ Gerenciar Cache (`/gerenciar-cache`)
Gerenciamento completo dos caches armazenados.

**Funcionalidades:**
- Listagem de todos os caches
- Informações detalhadas (arquivos, itens, tamanho, data)
- Exclusão individual de caches
- Confirmação de segurança antes de deletar

### 📈 Dashboard (`/dashboard`)
Visão geral do sistema com estatísticas.

**Funcionalidades:**
- Total de caches disponíveis
- Total de arquivos filtrados
- Total de registros filtrados
- Valor potencial em R$
- Barra de progresso da meta mensal (400.000 extrações)
- Percentual de atingimento da meta

### 3. Configurar Filtros

A interface permite filtrar por:

#### 📁 Obrigatórios:
- **Diretório de Cache**: Ex: `cache/TJSP_2025-11-11_18-07-56`
- **Diretório de Saída**: Ex: `dados_filtrados`

#### 🔍 Opcionais (todos):
- **Tribunal**: Sigla (TJSP, TJAM, etc)
- **Tipo de Comunicação**: Lista de distribuição, Intimação, Citação, Edital
- **Código da Classe**: Ex: 12154
- **Nome da Classe**: Ex: Procedimento Comum
- **Tipo de Documento**: Decisão, Sentença, etc
- **Data Disponibilização**: Período (início/fim) ✅
- **Data Despacho**: Período (início/fim) - extraída do texto e filtrada rigorosamente ✅
- **Texto Contém**: Palavras-chave separadas por vírgula

### 4. Processar

Clique em **"🚀 Processar e Filtrar Dados"**

### 5. Resultado

O sistema mostrará:
- Total de registros processados
- Total de registros filtrados
- Arquivo de saída gerado
- Valor potencial (R$ 0,03 × quantidade)
- Taxa de filtro (%)

## 📊 Exemplo de Uso

### Cenário: Filtrar Intimações de Procedimento Comum do TJSP

```
Diretório Cache: cache/TJSP_2025-11-11_18-07-56
Diretório Saída: dados_filtrados
Tribunal: TJSP
Tipo Comunicação: Intimação
Nome Classe: Procedimento Comum
Data Despacho Início: 2025-11-01
Data Despacho Fim: 2025-11-30
```

**Resultado:**
- Processados: 10.000 registros
- Filtrados: 1.250 registros
- Arquivo: `dados_filtrados/filtrado_2025-11-12_14-30-00.json`
- Valor potencial: R$ 37,50

## 🛠️ Correções Implementadas

### 1. Mapeamento Correto dos Campos ✅

| Campo Resultado | Campo API | Status |
|----------------|-----------|---------|
| `processo` | `numeroprocessocommascara` | ✅ CORRIGIDO |
| `processo_sem_mascara` | `numero_processo` | ✅ CORRIGIDO |
| `tribunal` | `siglaTribunal` | ✅ CORRIGIDO |
| `tipo_comunicacao` | `tipoComunicacao` | ✅ CORRIGIDO |
| `codigo_classe` | `codigoClasse` | ✅ CORRIGIDO |
| `nome_classe` | `nomeClasse` | ✅ CORRIGIDO |
| `texto` | `texto` | ✅ ADICIONADO |

### 2. Extração e Filtragem de Data de Despacho ✅

A data é **extraída automaticamente** do campo `texto` com os seguintes padrões:
- `DATA DE EXPEDIENTE: 05/11/2025`
- `Data de Expediente: 05/11/2025`
- `DATA DE VINCULAÇÃO: 05/11/2025` (ou `Data Vinculação:`)
- `DATA: 05/11/2025`

**Novo campo:** `data_despacho` (string no formato dd/mm/yyyy)

**Filtragem rigorosa:** 
- Registros com data fora do período configurado são **excluídos**
- Registros sem data no texto são **excluídos** quando filtro está ativo
- Zero tolerância para falsos positivos

### 3. Campos Adicionais ✅

Agora incluídos no resultado:
- `meio` - Forma de comunicação (D = Diário Eletrônico)
- `tipo_documento` - Tipo do documento (Decisão, Sentença, etc)
- `nome_orgao` - Nome do órgão julgador

---

## ⚠️ IMPORTÂNCIA CRÍTICA DA DATA DE DESPACHO

### Por Que a Data de Despacho é FUNDAMENTAL?

A **Data de Despacho** determina o **início da contagem de prazos processuais**. É a informação mais crítica para:

✅ **Decisão sobre aceitar o processo**
- Processos com mais de 15 dias podem ter prazo vencido
- Impossível tomar decisão correta sem essa data

✅ **Cálculo de prazos legais**
- Intimações têm prazos específicos (15, 30, 60 dias)
- Perder prazo = perder direito de defesa/recurso

✅ **Priorização de trabalho**
- Processos mais antigos = URGÊNCIA MÁXIMA
- Visualização com alerta vermelho automático (>15 dias)

### Como a Data é Exibida no Sistema

#### Na Tela de Visualização (`/visualizar`):
- **Coluna destacada em AMARELO** - impossível não ver
- **Contagem automática de dias** - ex: "05/11/2025 (7 dias)"
- **Alerta VERMELHO** para processos com mais de 15 dias
- **Estatística de processos críticos** no topo da página
- **Sempre exibida**, mesmo sem filtro de data

#### No CSV Exportado:
- Coluna "**DATA DESPACHO (PRAZO)**" em destaque
- Registros sem data marcados como "SEM DATA - VERIFICAR"
- Facilita análise no Excel

### Exemplo Prático

```
Processo: 5004155-45.2021.8.13.0241
Data Despacho: 28/10/2025 (15 dias!) 🔴 VERMELHO
Ação: URGENTE - Verificar prazo imediatamente!

Processo: 5036213-59.2024.8.13.0027  
Data Despacho: 08/11/2025 (4 dias) 🟡 AMARELO
Ação: Dentro do prazo normal

Processo: 5002534-30.2025.8.13.0384
Data Despacho: ⚠️ SEM DATA 🔴 VERMELHO
Ação: VERIFICAR MANUALMENTE no texto do processo
```

### ⚠️ ATENÇÃO REDOBRADA

**Processos SEM data de despacho:**
- Aparecem como "⚠️ SEM DATA" em vermelho
- DEVEM ser verificados manualmente no texto
- Podem ter padrões de data não cobertos pela extração
- Não ignorar - podem ser urgentes!

## 📂 Estrutura de Saída

```json
[
  {
    "id": 457526156,
    "processo": "0515611-08.2024.8.04.0001",
    "processo_sem_mascara": "05156110820248040001",
    "data_disponibilizacao": "2025-11-10",
    "data_despacho": "05/11/2025",
    "tribunal": "TJAM",
    "tipo_comunicacao": "Intimação",
    "codigo_classe": "198",
    "nome_classe": "APELAçãO CíVEL",
    "texto": "Dê-se vista ao Ministério Público.",
    "meio": "D",
    "tipo_documento": "Decisão",
    "nome_orgao": "Primeira Câmara Cível"
  }
]
```

## 🎨 Interface

A interface possui:
- **Design moderno**: Gradiente roxo, cards responsivos
- **Seleção visual de cache**: Lista todos os caches disponíveis
- **Validação de formulário**: Campos obrigatórios marcados
- **Feedback visual**: Loading spinner durante processamento
- **Resultado detalhado**: Estatísticas e valor potencial

## 💡 Dicas

### Para Atingir Meta de 400.000 extrações/mês:

1. **Filtre por período específico**: Use Data Disponibilização
2. **Combine filtros**: Tribunal + Tipo + Classe
3. **Use texto contém**: Palavras-chave relevantes
4. **Processe múltiplos caches**: Um por vez, depois combine

### Performance:

- **Cache pequeno** (<1GB): ~10-30 segundos
- **Cache médio** (1-5GB): ~1-3 minutos
- **Cache grande** (>5GB): ~5-10 minutos

## 🔧 Troubleshooting

### Erro: "Nenhum cache encontrado"
```powershell
# Verificar se cache existe
Get-ChildItem cache
```

### Erro: "Erro ao ler diretório de cache"
```powershell
# Usar caminho relativo
cache/TJSP_2025-11-11_18-07-56
# Não usar caminho absoluto
```

### Servidor não inicia
```powershell
# Verificar porta 8080 livre
netstat -ano | findstr :8080

# Se ocupada, matar processo
taskkill /PID <PID> /F
```

## 📈 Integração com Scraper Principal

### Fluxo Completo:

```
1. Extração (go run .)
   ↓
2. Cache Salvo (cache/TRIBUNAL_DATA_HORA/)
   ↓
3. Interface de Filtros (cd filtros && go run main.go)
   ↓
4. Dados Filtrados (dados_filtrados/filtrado_*.json)
   ↓
5. Receita! (R$ 0,03 × quantidade)
```

### Automação:

```powershell
# Script completo de extração + filtro
# extrair_e_filtrar.ps1

# 1. Extrai dados
cd "D:\RS - LySA - EMPRESA\go_scraper_pje"
go run . --tribunais "TJSP" --inicio "2025-11-01" --fim "2025-11-30"

# 2. Pega último cache criado
$ultimoCache = Get-ChildItem cache | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# 3. Inicia servidor de filtros (em background)
cd filtros
Start-Process powershell -ArgumentList "go run main.go" -WindowStyle Hidden

# 4. Aguarda servidor
Start-Sleep -Seconds 3

# 5. Abre interface no navegador
Start-Process http://localhost:8080
```

## 🎊 Benefícios

1. **Visual e Intuitivo**: Sem precisar editar código
2. **Rápido**: Processamento em Go nativo
3. **Flexível**: Todos os filtros são opcionais
4. **Confiável**: Mesma lógica do scraper principal
5. **Rastreável**: Cada filtro gera arquivo com timestamp

---

**🚀 Comece agora: `go run main.go` e acesse http://localhost:8080**
