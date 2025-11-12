# 🚀 Guia Rápido de Extração

Script facilitado para executar scraper em todos os 30 tribunais.

## 📋 Uso Básico

### Todos os Tribunais (Modo Normal)
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025"
```

### Modo Conservador (evita 429)
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "30/11/2025" -Modo conservador
```

### Modo Agressivo (servidor robusto)
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Modo agressivo
```

## 🎯 Tribunais Específicos

### Apenas 1 Tribunal
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Tribunais "TJSP"
```

### Região Sudeste
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Tribunais "TJSP,TJRJ,TJMG,TJES"
```

### Tribunais Prioritários (maior volume)
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Tribunais "TJSP,TJRJ,TJMG,TJRS,TJPR,TJBA"
```

## 📅 Formatos de Data

Aceita ambos os formatos:

```powershell
# Formato brasileiro
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025"

# Formato ISO
.\extrair.ps1 -Inicio "2025-11-01" -Fim "2025-11-10"
```

## ⚙️ Modos de Execução

| Modo | Workers | RPS | Uso Recomendado |
|------|---------|-----|-----------------|
| **conservador** | 2 | 2 | Períodos longos (>15 dias) |
| **normal** | 5 | 3 | Uso diário (5-15 dias) |
| **agressivo** | 10 | 10 | Períodos curtos (<5 dias) |

## 📊 Todos os 30 Tribunais

### Por Região

#### Norte (7)
`TJAC, TJAM, TJAP, TJPA, TJRO, TJRR, TJTO`

#### Nordeste (9)
`TJAL, TJBA, TJCE, TJMA, TJPB, TJPE, TJPI, TJRN, TJSE`

#### Centro-Oeste (4)
`TJDFT, TJGO, TJMS, TJMT`

#### Sudeste (6)
`TJES, TJMG, TJMMG, TJMSP, TJRJ, TJSP`

#### Sul (4)
`TJMRS, TJPR, TJRS, TJSC`

## 🔧 Exemplos Práticos

### Extração Mensal Completa
```powershell
# Primeiro dia útil do mês
.\extrair.ps1 -Inicio "01/11/2025" -Fim "30/11/2025" -Modo conservador
```

### Extração Semanal Rápida
```powershell
# Toda segunda-feira
.\extrair.ps1 -Inicio "03/11/2025" -Fim "09/11/2025" -Modo agressivo
```

### Testar com 1 Tribunal
```powershell
# Antes de rodar todos, teste com 1
.\extrair.ps1 -Inicio "10/11/2025" -Fim "10/11/2025" -Tribunais "TJAM" -Modo normal
```

### Apenas Estados Grandes (Volume Alto)
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Tribunais "TJSP,TJRJ,TJMG" -Modo conservador
```

## 📁 Após Extração

O script mostrará o diretório de cache criado. Para filtrar:

```powershell
cd filtros
go run main.go
# Abra http://localhost:8080
```

## 🎯 Workflow Completo

### 1. Extrair Dados
```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025"
```

### 2. Filtrar Dados
```powershell
cd filtros
go run main.go
```

### 3. Configurar Filtros na Interface
- Selecione o cache criado
- Configure Data Despacho: 01/11/2025 a 10/11/2025
- Configure outros filtros desejados
- Clique em "Processar"

### 4. Resultado
Arquivo JSON filtrado em `dados_filtrados/filtrado_*.json`

## 💡 Dicas

### Evitar Erro 429 (Too Many Requests)
- Use modo **conservador** para períodos longos
- Reduza quantidade de tribunais simultâneos
- Ative cache (`-Cache $true`)

### Maximizar Performance
- Use modo **agressivo** para períodos curtos
- Execute em horários de menor carga (madrugada)
- Processe regiões separadamente

### Otimizar Custos
- Filtre na extração: use `--tipo` e `--classe`
- Cache evita requisições duplicadas
- Foque em tribunais com maior ROI

## 📊 Estimativa de Volume

**Meta: 400.000 extrações/mês**

| Período | Tribunais | Modo | Estimativa |
|---------|-----------|------|------------|
| 30 dias | 30 | conservador | ~420.000 |
| 15 dias | 30 | normal | ~210.000 |
| 10 dias | 30 | agressivo | ~140.000 |

**Valor: R$ 0,03 por extração**

---

**🚀 Pronto para começar!**

```powershell
.\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025"
```
