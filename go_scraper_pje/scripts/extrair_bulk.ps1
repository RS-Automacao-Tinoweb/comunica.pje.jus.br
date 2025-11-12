# 📊 Script de Extração em Massa para Maximizar Receita
# Objetivo: 400.000+ extrações/mês = R$ 12.000+

param(
    [int]$DiasPorPeriodo = 7,
    [string[]]$Tribunais = @("TJSP", "TJAM", "TJBA", "TJCE", "TJDF", "TJES", "TJGO", "TJMA"),
    [int]$WorkersPaginas = 5,
    [int]$RPS = 3
)

$ErrorActionPreference = "Continue"

# Cores para output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "╔══════════════════════════════════════════════════════╗"
Write-Info "║     EXTRAÇÃO EM MASSA - MAXIMIZAÇÃO DE RECEITA       ║"
Write-Info "║     R$ 0,03 por extração bem-sucedida                ║"
Write-Info "╚══════════════════════════════════════════════════════╝"
Write-Host ""

# Configuração
$inicio = Get-Date "2025-01-01"
$fim = Get-Date "2025-11-30"
$baseDir = "D:\RS - LySA - EMPRESA\go_scraper_pje"
$outputBase = "$baseDir\resultados_bulk"
$logDir = "$baseDir\logs"

# Cria diretórios
New-Item -ItemType Directory -Force -Path $outputBase | Out-Null
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Gera períodos
Write-Info "📅 Gerando períodos de extração..."
$periodos = @()
$atual = $inicio
while ($atual -lt $fim) {
    $proxima = $atual.AddDays($DiasPorPeriodo)
    if ($proxima -gt $fim) { $proxima = $fim }
    
    $periodos += @{
        inicio = $atual.ToString("yyyy-MM-dd")
        fim = $proxima.ToString("yyyy-MM-dd")
    }
    $atual = $proxima.AddDays(1)
}

Write-Success "✅ $($periodos.Count) períodos gerados"
Write-Info "🏛️  $($Tribunais.Count) tribunais configurados"
Write-Info "🎯 Total de execuções: $($periodos.Count * $Tribunais.Count)"
Write-Host ""

# Estatísticas
$totalExtracoes = 0
$totalReceita = 0.0
$execucoesComSucesso = 0
$execucoesComErro = 0

# Loop principal
$contador = 0
$totalExecucoes = $periodos.Count * $Tribunais.Count

foreach ($periodo in $periodos) {
    foreach ($trib in $Tribunais) {
        $contador++
        $progresso = [math]::Round(($contador / $totalExecucoes) * 100, 1)
        
        Write-Host ""
        Write-Info "[$contador/$totalExecucoes - $progresso%] 🚀 $trib: $($periodo.inicio) → $($periodo.fim)"
        
        $outputDir = "$outputBase\$trib\$($periodo.inicio)"
        $logFile = "$logDir\${trib}_$($periodo.inicio).log"
        
        try {
            # Executa scraper
            $startTime = Get-Date
            
            & go run . `
                --tribunais $trib `
                --inicio $periodo.inicio `
                --fim $periodo.fim `
                --wp $WorkersPaginas `
                --rps $RPS `
                --out $outputDir `
                --cache=true `
                2>&1 | Tee-Object -FilePath $logFile
            
            $endTime = Get-Date
            $duracao = ($endTime - $startTime).TotalSeconds
            
            # Conta extrações
            $jsonFile = "$outputDir\$trib.json"
            if (Test-Path $jsonFile) {
                $conteudo = Get-Content $jsonFile | ConvertFrom-Json
                $count = $conteudo.Count
                $receita = $count * 0.03
                
                $totalExtracoes += $count
                $totalReceita += $receita
                $execucoesComSucesso++
                
                Write-Success "   ✅ $count extrações | R$ $receita | ${duracao}s"
            } else {
                Write-Warning "   ⚠️  Arquivo JSON não encontrado"
                $execucoesComErro++
            }
            
        } catch {
            Write-Error "   ❌ Erro: $_"
            $execucoesComErro++
        }
        
        # Status parcial a cada 10 execuções
        if ($contador % 10 -eq 0) {
            Write-Host ""
            Write-Info "📊 STATUS PARCIAL:"
            Write-Info "   • Extrações: $totalExtracoes"
            Write-Info "   • Receita: R$ $totalReceita"
            Write-Info "   • Sucesso: $execucoesComSucesso | Erro: $execucoesComErro"
            Write-Host ""
        }
        
        # Pequeno delay entre execuções
        Start-Sleep -Seconds 2
    }
}

# Resumo final
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "                  📊 RESUMO FINAL                      " -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Success "✅ Execuções com sucesso: $execucoesComSucesso"
Write-Error   "❌ Execuções com erro: $execucoesComErro"
Write-Info    "📈 Total de extrações: $totalExtracoes"
Write-Success "💰 Receita gerada: R$ $totalReceita"
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""

# Salva relatório
$relatorio = @{
    data_execucao = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    total_execucoes = $totalExecucoes
    execucoes_sucesso = $execucoesComSucesso
    execucoes_erro = $execucoesComErro
    total_extracoes = $totalExtracoes
    receita_total = $totalReceita
    tribunais = $Tribunais
    periodos = $periodos.Count
} | ConvertTo-Json

$relatorioFile = "$logDir\relatorio_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
$relatorio | Out-File -FilePath $relatorioFile

Write-Info "📄 Relatório salvo: $relatorioFile"

# Projeção mensal
$diasExecutados = ($fim - $inicio).Days
$extraçoesPorDia = $totalExtracoes / $diasExecutados
$projecaoMensal = [math]::Round($extraçoesPorDia * 30)
$receitaMensal = $projecaoMensal * 0.03

Write-Host ""
Write-Host "🎯 PROJEÇÃO MENSAL:" -ForegroundColor Yellow
Write-Host "   • $projecaoMensal extrações/mês" -ForegroundColor Yellow
Write-Host "   • R$ $receitaMensal/mês" -ForegroundColor Yellow
Write-Host ""

if ($projecaoMensal -ge 400000) {
    Write-Success "🎊 META DE 400.000 EXTRAÇÕES ATINGIDA! 🎊"
} else {
    $faltam = 400000 - $projecaoMensal
    Write-Warning "⚠️  Faltam $faltam extrações para atingir meta"
    Write-Info "💡 Sugestão: Aumentar --wp ou adicionar mais tribunais"
}
