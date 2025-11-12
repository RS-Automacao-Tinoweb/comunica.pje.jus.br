# 🚀 Scripts de Maximização de Receita

Scripts PowerShell para atingir e superar a meta de **400.000 extrações/mês = R$ 12.000+**

## 📋 Scripts Disponíveis

### 1. 🧪 `teste_volume.ps1` - Teste Rápido
**Objetivo:** Validar capacidade real do sistema

```powershell
.\scripts\teste_volume.ps1
```

**O que faz:**
- ✅ Testa com 3 tribunais (TJSP, TJAM, TJBA)
- ✅ Calcula extrações/segundo, minuto, hora, dia
- ✅ Projeta capacidade mensal
- ✅ Verifica se atinge meta de 400k
- ✅ Gera relatório JSON

**Tempo estimado:** 1-2 minutos  
**Resultado esperado:** ~150-200 extrações = R$ 4,50-6,00

---

### 2. 📊 `extrair_bulk.ps1` - Extração em Massa
**Objetivo:** Extrair dados de múltiplos tribunais em períodos variados

```powershell
# Básico (padrão)
.\scripts\extrair_bulk.ps1

# Customizado
.\scripts\extrair_bulk.ps1 `
    -DiasPorPeriodo 7 `
    -Tribunais @("TJSP","TJAM","TJBA","TJCE","TJDF","TJES","TJGO","TJMA") `
    -WorkersPaginas 5 `
    -RPS 3
```

**Parâmetros:**
- `DiasPorPeriodo`: Dias por intervalo (padrão: 7)
- `Tribunais`: Array de siglas de tribunais
- `WorkersPaginas`: Workers paralelos (padrão: 5)
- `RPS`: Requisições por segundo (padrão: 3)

**O que faz:**
- ✅ Divide período de 2025-01-01 a 2025-11-30 em intervalos
- ✅ Extrai cada tribunal em cada intervalo
- ✅ Conta extrações e calcula receita em tempo real
- ✅ Mostra progresso a cada 10 execuções
- ✅ Gera relatório final JSON
- ✅ Projeta receita mensal

**Tempo estimado:** 2-4 horas (depende de tribunais)  
**Resultado esperado:** 500.000+ extrações = R$ 15.000+

---

### 3. 💰 `contador_receita.ps1` - Dashboard de Receita
**Objetivo:** Monitorar receita acumulada em tempo real

```powershell
# Execução única
.\scripts\contador_receita.ps1

# Modo watch (atualiza a cada 10s)
.\scripts\contador_receita.ps1 -Watch

# Customizar diretório e valor
.\scripts\contador_receita.ps1 `
    -DiretorioResultados "D:\RS - LySA - EMPRESA\go_scraper_pje\resultados_bulk" `
    -ValorPorExtracao 0.03 `
    -Watch
```

**O que mostra:**
```
╔═══════════════════════════════════════════════════════════╗
║        💰 DASHBOARD DE RECEITA - PJE SCRAPER 💰          ║
╚═══════════════════════════════════════════════════════════╝

📊 STATUS ATUAL
   Extrações realizadas: 250.000
   Receita acumulada:    R$ 7.500

🎯 META MENSAL
   Objetivo:             400.000 extrações = R$ 12.000
   Progresso:            62.5%
   [███████████████████████████░░░░░░░░░░░░░░░░░░░░░░░]
   Faltam:               150.000 extrações (R$ 4.500)

📈 PROJEÇÃO PARA FIM DO MÊS
   Dia atual:            15 de 30
   Extrações/dia:        16.667
   Projeção mensal:      500.000 extrações
   Receita projetada:    R$ 15.000 🚀

💵 GANHO TOTAL
   Salário base:         R$ 5.000
   Bônus atual:          R$ 7.500
   Total atual:          R$ 12.500
   Bônus projetado:      R$ 15.000
   Total projetado:      R$ 20.000 🎯
```

**Recursos:**
- ✅ Barra de progresso visual
- ✅ Projeção para fim do mês
- ✅ Cálculo de ganho total (salário + bônus)
- ✅ Dicas para atingir meta
- ✅ Modo watch para monitoramento contínuo

---

## 🎯 Fluxo Recomendado

### Dia 1: Validação
```powershell
# 1. Testar capacidade
.\scripts\teste_volume.ps1

# 2. Ver dashboard
.\scripts\contador_receita.ps1
```

### Dia 2-30: Produção
```powershell
# Executar extração em massa
.\scripts\extrair_bulk.ps1

# Monitorar receita (em outra janela)
.\scripts\contador_receita.ps1 -Watch
```

---

## 📈 Estratégias por Meta

### Meta Básica: 400.000/mês (R$ 12.000)
```powershell
.\scripts\extrair_bulk.ps1 `
    -Tribunais @("TJSP","TJAM","TJBA","TJCE","TJDF") `
    -DiasPorPeriodo 7 `
    -WorkersPaginas 5 `
    -RPS 3
```

### Meta Intermediária: 1.000.000/mês (R$ 30.000)
```powershell
.\scripts\extrair_bulk.ps1 `
    -Tribunais @("TJSP","TJAM","TJBA","TJCE","TJDF","TJES","TJGO","TJMA","TJMG","TJMS") `
    -DiasPorPeriodo 7 `
    -WorkersPaginas 8 `
    -RPS 4
```

### Meta Avançada: 2.000.000/mês (R$ 60.000)
```powershell
# Todos os 24 tribunais
$todosTribunais = @(
    "TJSP","TJAM","TJBA","TJCE","TJDF","TJES","TJGO","TJMA",
    "TJMG","TJMS","TJMT","TJPA","TJPB","TJPE","TJPI","TJPR",
    "TJRJ","TJRN","TJRO","TJRR","TJRS","TJSC","TJSE","TJTO"
)

.\scripts\extrair_bulk.ps1 `
    -Tribunais $todosTribunais `
    -DiasPorPeriodo 7 `
    -WorkersPaginas 10 `
    -RPS 5
```

---

## 🔧 Automação com Task Scheduler

### Executar automaticamente a cada 6 horas

1. Abrir Task Scheduler (`taskschd.msc`)
2. Criar Tarefa Básica
3. Configurar:
   - **Nome:** Scraper PJE Bulk
   - **Gatilho:** Diário, repetir a cada 6 horas
   - **Ação:** Iniciar programa
     - **Programa:** `powershell.exe`
     - **Argumentos:** `-ExecutionPolicy Bypass -File "D:\RS - LySA - EMPRESA\go_scraper_pje\scripts\extrair_bulk.ps1"`

4. Salvar

**Resultado:** Extração automática 4x/dia = ~16.000 extrações/dia = ~480.000/mês = R$ 14.400

---

## 📊 Monitoramento de Logs

Todos os scripts geram logs em:
```
D:\RS - LySA - EMPRESA\go_scraper_pje\logs\
├── teste_volume_2025-11-11_23-30-00.json
├── relatorio_2025-11-11_23-45-00.json
├── TJSP_2025-01-01.log
└── ...
```

### Ver logs recentes:
```powershell
Get-ChildItem "D:\RS - LySA - EMPRESA\go_scraper_pje\logs" -Filter "*.json" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5
```

---

## 💡 Dicas de Otimização

### 1. Se receber muitos 429s:
```powershell
# Reduzir RPS e workers
.\scripts\extrair_bulk.ps1 -WorkersPaginas 3 -RPS 2
```

### 2. Se quiser maximizar velocidade:
```powershell
# Aumentar RPS e workers (cuidado com 429s!)
.\scripts\extrair_bulk.ps1 -WorkersPaginas 10 -RPS 5
```

### 3. Se quiser focar em período específico:
Edite `extrair_bulk.ps1`:
```powershell
$inicio = Get-Date "2025-10-01"  # Alterar aqui
$fim = Get-Date "2025-10-31"     # Alterar aqui
```

### 4. Para limpar cache antigo:
```powershell
Remove-Item -Recurse -Force "D:\RS - LySA - EMPRESA\go_scraper_pje\cache\*"
```

---

## 🎊 Metas e Conquistas

| Extrações | Receita | Ação |
|-----------|---------|------|
| 50.000 | R$ 1.500 | 🏅 Primeira conquista! |
| 100.000 | R$ 3.000 | 🏅 10% do potencial anual |
| 200.000 | R$ 6.000 | 🏅 Metade do salário! |
| 400.000 | R$ 12.000 | 🎯 **META ATINGIDA!** |
| 1.000.000 | R$ 30.000 | 🚀 6x o salário! |
| 2.000.000 | R$ 60.000 | 💰 12x o salário! |
| 4.000.000 | R$ 120.000 | 💎 24x o salário! |

---

## 🆘 Troubleshooting

### Script não executa
```powershell
# Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro "go: command not found"
```powershell
# Verificar instalação do Go
go version

# Se não instalado, baixar em: https://go.dev/dl/
```

### Contador de receita mostra 0
```powershell
# Verificar se há arquivos JSON
Get-ChildItem "D:\RS - LySA - EMPRESA\go_scraper_pje\resultados*\*.json" -Recurse
```

### Cache ocupando muito espaço
```powershell
# Ver tamanho do cache
Get-ChildItem "D:\RS - LySA - EMPRESA\go_scraper_pje\cache" -Recurse | 
    Measure-Object -Property Length -Sum | 
    Select-Object @{Name="Size(MB)";Expression={[math]::Round($_.Sum/1MB,2)}}

# Limpar cache antigo (manter últimas 3 execuções)
Get-ChildItem "D:\RS - LySA - EMPRESA\go_scraper_pje\cache" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -Skip 3 | 
    Remove-Item -Recurse -Force
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs em `logs/`
2. Executar teste de volume para diagnóstico
3. Ajustar parâmetros conforme necessidade

---

**🎯 BOA SORTE NA JORNADA PARA R$ 12.000+ POR MÊS!** 🚀💰
