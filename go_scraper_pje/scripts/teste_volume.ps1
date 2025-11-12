# 🚀 Teste Rápido de Volume - Validação de Capacidade
# Testa com 3 tribunais para estimar capacidade real

$ErrorActionPreference = "Continue"

Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TESTE DE VOLUME - VALIDAÇÃO DE CAPACIDADE        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$baseDir = "D:\RS - LySA - EMPRESA\go_scraper_pje"
$outputDir = "$baseDir\teste_volume"
$tribunaisTeste = @("TJSP", "TJAM", "TJBA")

# Limpa resultados anteriores
if (Test-Path $outputDir) {
    Remove-Item -Recurse -Force $outputDir
}
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Host "🎯 Configuração do teste:" -ForegroundColor Yellow
Write-Host "   • Tribunais: $($tribunaisTeste -join ', ')"
Write-Host "   • Período: 2025-11-06 a 2025-11-10 (5 dias)"
Write-Host "   • Workers: 5 | RPS: 3"
Write-Host ""

$startTime = Get-Date
Write-Host "⏱️  Início: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Executa teste
& go run . `
    --tribunais ($tribunaisTeste -join ',') `
    --inicio "2025-11-06" `
    --fim "2025-11-10" `
    --wt 3 `
    --wp 5 `
    --rps 3 `
    --out $outputDir `
    --cache=false

$endTime = Get-Date
$duracao = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "⏱️  Fim: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host "⌛ Duração: ${duracao}s ($([math]::Round($duracao/60, 1)) min)" -ForegroundColor Cyan
Write-Host ""

# Analisa resultados
Write-Host "📊 Analisando resultados..." -ForegroundColor Yellow
Write-Host ""

$totalExtracoes = 0
$resultadosPorTribunal = @{}

foreach ($trib in $tribunaisTeste) {
    $jsonFile = "$outputDir\$trib.json"
    if (Test-Path $jsonFile) {
        $conteudo = Get-Content $jsonFile | ConvertFrom-Json
        $count = $conteudo.Count
        $totalExtracoes += $count
        $resultadosPorTribunal[$trib] = $count
        
        Write-Host "   $trib : " -NoNewline
        Write-Host "$count extrações" -ForegroundColor Green
    } else {
        Write-Host "   $trib : " -NoNewline
        Write-Host "ERRO - Arquivo não encontrado" -ForegroundColor Red
        $resultadosPorTribunal[$trib] = 0
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "                  📈 ANÁLISE DE CAPACIDADE             " -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""

# Métricas de performance
$extracoesPorSegundo = [math]::Round($totalExtracoes / $duracao, 2)
$extracoesPorMinuto = [math]::Round($extracoesPorSegundo * 60, 0)
$extracoesPorHora = [math]::Round($extracoesPorMinuto * 60, 0)
$extracoesPorDia = [math]::Round($extracoesPorHora * 24, 0)
$extracoesPorMes = [math]::Round($extracoesPorDia * 30, 0)

Write-Host "⚡ PERFORMANCE:" -ForegroundColor Yellow
Write-Host "   • Extrações/segundo: $extracoesPorSegundo"
Write-Host "   • Extrações/minuto:  $extracoesPorMinuto"
Write-Host "   • Extrações/hora:    $extracoesPorHora"
Write-Host "   • Extrações/dia:     $extracoesPorDia"
Write-Host ""

Write-Host "🎯 PROJEÇÕES:" -ForegroundColor Yellow
Write-Host "   • Mensal (3 tribunais): " -NoNewline
Write-Host "$extracoesPorMes extrações" -ForegroundColor Cyan

# Cálculo para atingir meta com todos os tribunais
$meta = 400000
$tribunaisTotais = 24  # Total de tribunais disponíveis
$fatorEscala = $tribunaisTotais / $tribunaisTeste.Count
$projecaoComTodosTribunais = [math]::Round($extracoesPorMes * $fatorEscala, 0)

Write-Host "   • Mensal (24 tribunais): " -NoNewline
if ($projecaoComTodosTribunais -ge $meta) {
    Write-Host "$projecaoComTodosTribunais extrações " -NoNewline -ForegroundColor Green
    Write-Host "✅ META ATINGIDA!" -ForegroundColor Green
} else {
    Write-Host "$projecaoComTodosTribunais extrações" -ForegroundColor Yellow
}
Write-Host ""

# Cálculo de receita
$receitaTeste = $totalExtracoes * 0.03
$receitaMensal3Trib = $extracoesPorMes * 0.03
$receitaMensal24Trib = $projecaoComTodosTribunais * 0.03

Write-Host "💰 RECEITA:" -ForegroundColor Yellow
Write-Host "   • Teste atual:          R$ $receitaTeste"
Write-Host "   • Mensal (3 tribunais): R$ $receitaMensal3Trib"
Write-Host "   • Mensal (24 tribunais): " -NoNewline
if ($receitaMensal24Trib -ge 12000) {
    Write-Host "R$ $receitaMensal24Trib " -NoNewline -ForegroundColor Green
    Write-Host "✅" -ForegroundColor Green
} else {
    Write-Host "R$ $receitaMensal24Trib" -ForegroundColor Yellow
}
Write-Host ""

# Recomendações
Write-Host "💡 RECOMENDAÇÕES:" -ForegroundColor Yellow

if ($projecaoComTodosTribunais -ge $meta) {
    Write-Host "   ✅ Capacidade suficiente para meta!" -ForegroundColor Green
    Write-Host "   • Usar script bulk: .\scripts\extrair_bulk.ps1" -ForegroundColor Green
    Write-Host "   • Configurar execução automática (Task Scheduler)" -ForegroundColor Green
} else {
    $faltam = $meta - $projecaoComTodosTribunais
    $tribunaisNecessarios = [math]::Ceiling(($meta / $extracoesPorMes))
    
    Write-Host "   ⚠️  Projeção abaixo da meta. Faltam: $faltam extrações" -ForegroundColor Yellow
    Write-Host "   • Aumentar workers: --wp 10" -ForegroundColor Yellow
    Write-Host "   • Aumentar RPS: --rps 5" -ForegroundColor Yellow
    Write-Host "   • Executar 24/7 com script contínuo" -ForegroundColor Yellow
    Write-Host "   • Usar $tribunaisNecessarios tribunais simultâneos" -ForegroundColor Yellow
}

Write-Host ""

# Comando sugerido
Write-Host "🚀 PRÓXIMO PASSO - PRODUÇÃO:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if ($projecaoComTodosTribunais -ge $meta) {
    Write-Host "go run . --tribunais `"TJSP,TJAM,TJBA,TJCE,TJDF,TJES,TJGO,TJMA`" --wt 8 --wp 5 --rps 3" -ForegroundColor Green
} else {
    Write-Host "go run . --tribunais `"TJSP,TJAM,TJBA,TJCE,TJDF,TJES,TJGO,TJMA`" --wt 8 --wp 10 --rps 5" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Magenta

# Salva relatório
$relatorio = @{
    data_teste = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    duracao_segundos = $duracao
    total_extracoes = $totalExtracoes
    extracoes_por_segundo = $extracoesPorSegundo
    extracoes_por_hora = $extracoesPorHora
    projecao_mensal_3_trib = $extracoesPorMes
    projecao_mensal_24_trib = $projecaoComTodosTribunais
    receita_teste = $receitaTeste
    receita_projetada = $receitaMensal24Trib
    meta_atingida = ($projecaoComTodosTribunais -ge $meta)
    resultados_por_tribunal = $resultadosPorTribunal
} | ConvertTo-Json

$relatorioFile = "$baseDir\logs\teste_volume_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
New-Item -ItemType Directory -Force -Path "$baseDir\logs" | Out-Null
$relatorio | Out-File -FilePath $relatorioFile

Write-Host ""
Write-Host "📄 Relatório salvo: $relatorioFile" -ForegroundColor Cyan
