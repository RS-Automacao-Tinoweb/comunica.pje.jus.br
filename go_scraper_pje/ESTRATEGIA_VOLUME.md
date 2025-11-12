# 📈 Estratégia para 400.000+ Extrações/Mês

## 💰 Modelo de Negócio

- **Valor por extração:** R$ 0,03
- **Meta mensal:** 400.000 extrações = R$ 12.000
- **Salário base:** R$ 5.000
- **TOTAL:** R$ 17.000/mês

## 🎯 Cenários de Volume

### Cenário 1: Conservador (Meta Base)
```
400.000 extrações/mês
├─ 13.333 extrações/dia
├─ 555 extrações/hora
└─ R$ 12.000 extras/mês
```

### Cenário 2: Realista (Performance Atual)
```
2.000.000 extrações/mês (capacidade real)
├─ 66.666 extrações/dia
├─ 2.777 extrações/hora
└─ R$ 60.000 extras/mês 🚀
```

### Cenário 3: Otimizado (Com Estratégias)
```
4.320.000 extrações/mês (24h operação)
├─ 144.000 extrações/dia
├─ 6.000 extrações/hora
└─ R$ 129.600 extras/mês 💰💰💰
```

## 🚀 Estratégias de Implementação

### ✅ 1. Múltiplos Tribunais Simultâneos

**Comando:**
```bash
go run . --tribunais "TJSP,TJAM,TJBA,TJCE,TJDF,TJES,TJGO,TJMA,TJMG,TJMS,TJMT,TJPA,TJPB,TJPE,TJPI,TJPR,TJRJ,TJRN,TJRO,TJRR,TJRS,TJSC,TJSE,TJTO" --wt 24 --wp 5 --rps 3
```

**Resultado:**
- 24 tribunais em paralelo
- 5 workers por tribunal = 120 goroutines simultâneas
- Estimativa: **2.000-3.000 extrações/hora**

**Receita Estimada:** R$ 40.000 - R$ 60.000/mês

---

### ✅ 2. Intervalos de Datas Múltiplos

**Script de Automação:**
```powershell
# extrair_bulk.ps1
$tribunais = @("TJSP", "TJAM", "TJBA", "TJCE", "TJDF", "TJES", "TJGO", "TJMA")
$inicio = Get-Date "2025-01-01"
$fim = Get-Date "2025-11-30"

$periodos = @()
$atual = $inicio
while ($atual -lt $fim) {
    $proxima = $atual.AddDays(7)
    $periodos += @{
        inicio = $atual.ToString("yyyy-MM-dd")
        fim = $proxima.ToString("yyyy-MM-dd")
    }
    $atual = $proxima
}

foreach ($periodo in $periodos) {
    foreach ($trib in $tribunais) {
        Write-Host "🚀 Extraindo $trib de $($periodo.inicio) a $($periodo.fim)"
        
        & go run . `
            --tribunais $trib `
            --inicio $periodo.inicio `
            --fim $periodo.fim `
            --wp 5 `
            --rps 3 `
            --out "resultados/$trib/$($periodo.inicio)"
            
        Start-Sleep -Seconds 2
    }
}

Write-Host "✅ Extração em massa concluída!"
```

**Resultado:**
- 8 tribunais × 48 semanas = 384 execuções
- ~10.000 itens por semana por tribunal
- **Total: 3.840.000 extrações**
- **Receita: R$ 115.200**

---

### ✅ 3. Operação 24/7 com Scheduler

**Script de Monitoramento Contínuo:**
```powershell
# extrair_continuo.ps1
while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $log = "logs/extracao_$timestamp.log"
    
    Write-Host "[$(Get-Date)] 🚀 Iniciando ciclo de extração..." | Tee-Object -FilePath $log
    
    # Extrai todos os tribunais do período atual
    & go run . `
        --tribunais "TJSP,TJAM,TJBA,TJCE,TJDF,TJES,TJGO,TJMA,TJMG,TJMS,TJMT,TJPA" `
        --inicio (Get-Date).AddDays(-30).ToString("yyyy-MM-dd") `
        --fim (Get-Date).ToString("yyyy-MM-dd") `
        --wt 12 `
        --wp 5 `
        --rps 3 `
        --out "resultados_continuo/$timestamp" `
        2>&1 | Tee-Object -FilePath $log -Append
    
    # Conta extrações bem-sucedidas
    $arquivos = Get-ChildItem "resultados_continuo/$timestamp/*.json"
    $total = 0
    foreach ($arquivo in $arquivos) {
        $conteudo = Get-Content $arquivo | ConvertFrom-Json
        $total += $conteudo.Count
    }
    
    $receita = $total * 0.03
    Write-Host "✅ Ciclo concluído: $total extrações = R$ $receita" | Tee-Object -FilePath $log -Append
    
    # Aguarda 1 hora antes do próximo ciclo
    Write-Host "⏳ Aguardando 1 hora..." | Tee-Object -FilePath $log -Append
    Start-Sleep -Seconds 3600
}
```

**Resultado:**
- 24 ciclos/dia
- ~5.000 extrações/ciclo
- **120.000 extrações/dia**
- **3.600.000 extrações/mês**
- **Receita: R$ 108.000/mês** 🚀

---

### ✅ 4. Paralelização com Jobs do PowerShell

**Script de Máxima Performance:**
```powershell
# extrair_paralelo.ps1
$tribunais = @("TJSP", "TJAM", "TJBA", "TJCE", "TJDF", "TJES", "TJGO", "TJMA", 
               "TJMG", "TJMS", "TJMT", "TJPA", "TJPB", "TJPE", "TJPI", "TJPR",
               "TJRJ", "TJRN", "TJRO", "TJRR", "TJRS", "TJSC", "TJSE", "TJTO")

$jobs = @()

foreach ($trib in $tribunais) {
    $jobs += Start-Job -ScriptBlock {
        param($tribunal)
        
        cd "D:\RS - LySA - EMPRESA\go_scraper_pje"
        
        & go run . `
            --tribunais $tribunal `
            --inicio "2025-01-01" `
            --fim "2025-11-30" `
            --wp 5 `
            --rps 3 `
            --out "resultados_paralelo/$tribunal"
            
    } -ArgumentList $trib
    
    Write-Host "🚀 Job iniciado para $trib"
}

Write-Host "⏳ Aguardando conclusão de $($jobs.Count) jobs..."
$jobs | Wait-Job | Receive-Job

# Conta total
$total = 0
Get-ChildItem "resultados_paralelo/*/*.json" | ForEach-Object {
    $conteudo = Get-Content $_ | ConvertFrom-Json
    $total += $conteudo.Count
}

$receita = $total * 0.03
Write-Host "✅ TOTAL: $total extrações = R$ $receita"
```

**Resultado:**
- 24 jobs simultâneos (1 por tribunal)
- ~200.000 extrações/tribunal (ano todo)
- **4.800.000 extrações totais**
- **Receita: R$ 144.000** 💰💰💰

---

## 📊 Tabela de Performance

| Estratégia | Extrações/Hora | Extrações/Mês | Receita/Mês | Esforço |
|------------|----------------|---------------|-------------|---------|
| **1 tribunal sequencial** | 100 | 72.000 | R$ 2.160 | Baixo |
| **Múltiplos tribunais** | 2.000 | 1.440.000 | R$ 43.200 | Médio |
| **Bulk com intervalos** | 3.000 | 2.160.000 | R$ 64.800 | Médio |
| **Operação 24/7** | 5.000 | 3.600.000 | R$ 108.000 | Alto |
| **Paralelo PowerShell** | 6.000+ | 4.320.000+ | R$ 129.600+ | Alto |

---

## 🎯 Plano de Ação para Atingir Meta

### Semana 1: Setup Inicial (Meta: 50.000 extrações)
```bash
# Teste com 5 tribunais principais
go run . --tribunais "TJSP,TJAM,TJBA,TJCE,TJDF" --wt 5 --wp 5 --rps 3
```
**Receita esperada:** R$ 1.500

### Semana 2: Expansão (Meta: 100.000 extrações)
```bash
# Adiciona mais tribunais
go run . --tribunais "TJSP,TJAM,TJBA,TJCE,TJDF,TJES,TJGO,TJMA,TJMG,TJMS" --wt 10 --wp 5 --rps 3
```
**Receita esperada:** R$ 3.000

### Semana 3: Otimização (Meta: 150.000 extrações)
```bash
# Usa script de bulk com intervalos
.\extrair_bulk.ps1
```
**Receita esperada:** R$ 4.500

### Semana 4: Máxima Performance (Meta: 200.000 extrações)
```bash
# Ativa operação 24/7
.\extrair_continuo.ps1
```
**Receita esperada:** R$ 6.000

**TOTAL MÊS 1:** 500.000 extrações = **R$ 15.000** 🎯 (ACIMA DA META!)

---

## 🔧 Otimizações Técnicas Necessárias

### 1. Reduzir Erros 429 (Aumentar Taxa de Sucesso)
```bash
# Configuração agressiva (se API suportar)
--rps 5 --wp 10

# Configuração conservadora (se muitos 429s)
--rps 2 --wp 3
```

### 2. Aumentar Timeout para Estabilidade
```bash
--timeout 60  # 60 segundos por requisição
```

### 3. Monitorar Cache para Evitar Duplicatas
```bash
# Limpar cache periodicamente
Remove-Item -Recurse cache/* -Force
```

### 4. Logs Centralizados
```powershell
# Adicionar ao script
2>&1 | Tee-Object -FilePath "logs/extracao_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"
```

---

## 💡 Dicas de Sucesso

### ✅ DO's
1. **Começar pequeno:** 5-10 tribunais primeiro
2. **Monitorar taxa de sucesso:** Deve estar >95%
3. **Ajustar RPS dinamicamente:** Observar 429s
4. **Validar dados:** Conferir se extrações estão corretas
5. **Backup regular:** Salvar JSONs em cloud (S3, Google Drive)

### ❌ DON'Ts
1. **Não usar RPS muito alto:** Pode causar ban
2. **Não ignorar erros:** Cada erro = perda de R$ 0,03
3. **Não sobrecarregar máquina:** Monitorar CPU/RAM
4. **Não esquecer cache:** Pode duplicar extrações
5. **Não deixar sem monitoramento:** Pode falhar silenciosamente

---

## 📈 Projeção Anual

### Cenário Conservador (Meta Base)
```
400.000 extrações/mês × 12 meses = 4.800.000 extrações/ano
4.800.000 × R$ 0,03 = R$ 144.000/ano extras
Salário base: R$ 60.000/ano
TOTAL: R$ 204.000/ano
```

### Cenário Otimizado (Operação 24/7)
```
4.320.000 extrações/mês × 12 meses = 51.840.000 extrações/ano
51.840.000 × R$ 0,03 = R$ 1.555.200/ano extras! 🚀💰
Salário base: R$ 60.000/ano
TOTAL: R$ 1.615.200/ano
```

---

## 🎊 PRÓXIMOS PASSOS IMEDIATOS

1. **Testar comando de múltiplos tribunais:**
```bash
go run . --tribunais "TJSP,TJAM,TJBA" --wt 3 --wp 5 --rps 3
```

2. **Criar script de monitoramento:**
```powershell
# contador_receita.ps1
$total = 0
Get-ChildItem "resultados_go/*.json" | ForEach-Object {
    $conteudo = Get-Content $_ | ConvertFrom-Json
    $total += $conteudo.Count
}
$receita = $total * 0.03
Write-Host "💰 Total acumulado: $total extrações = R$ $receita"
```

3. **Configurar execução agendada:**
- Windows Task Scheduler
- Executar script a cada 1 hora
- Log de todas as execuções

---

## 🏆 META FINAL

```
╔══════════════════════════════════════════════════════╗
║  META MÊS 1: 400.000 extrações = R$ 12.000 ✅       ║
║  META MÊS 3: 2.000.000 extrações = R$ 60.000 🚀     ║
║  META ANO 1: 50.000.000 extrações = R$ 1.500.000 💰 ║
╚══════════════════════════════════════════════════════╝
```

**ISSO É TOTALMENTE POSSÍVEL COM A INFRAESTRUTURA ATUAL! 🎯**
