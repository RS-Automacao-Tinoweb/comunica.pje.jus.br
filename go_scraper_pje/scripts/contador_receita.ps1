# 💰 Contador de Receita em Tempo Real
# Calcula quantas extrações foram feitas e quanto você já ganhou

param(
    [string]$DiretorioResultados = "D:\RS - LySA - EMPRESA\go_scraper_pje\resultados*",
    [double]$ValorPorExtracao = 0.03,
    [switch]$Watch
)

function Get-TotalExtracoes {
    param([string]$Path)
    
    $total = 0
    $arquivos = Get-ChildItem -Path $Path -Filter "*.json" -Recurse -ErrorAction SilentlyContinue
    
    foreach ($arquivo in $arquivos) {
        try {
            $conteudo = Get-Content $arquivo.FullName | ConvertFrom-Json
            if ($conteudo -is [Array]) {
                $total += $conteudo.Count
            } else {
                $total += 1
            }
        } catch {
            # Ignora arquivos inválidos
        }
    }
    
    return $total
}

function Show-Dashboard {
    param(
        [int]$TotalExtracoes,
        [double]$ValorPorExtracao
    )
    
    Clear-Host
    
    $receita = $TotalExtracoes * $ValorPorExtracao
    $meta = 400000
    $metaReceita = $meta * $ValorPorExtracao
    $progresso = [math]::Round(($TotalExtracoes / $meta) * 100, 2)
    
    # Projeções
    $diasNoMes = 30
    $diaAtual = (Get-Date).Day
    $extraçoesPorDia = if ($diaAtual -gt 0) { $TotalExtracoes / $diaAtual } else { 0 }
    $projecaoMes = [math]::Round($extraçoesPorDia * $diasNoMes)
    $receitaProjetada = $projecaoMes * $ValorPorExtracao
    
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        💰 DASHBOARD DE RECEITA - PJE SCRAPER 💰          ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Status atual
    Write-Host "📊 STATUS ATUAL ($(Get-Date -Format 'dd/MM/yyyy HH:mm:ss'))" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "   Extrações realizadas: " -NoNewline
    Write-Host "$TotalExtracoes" -ForegroundColor Green
    Write-Host "   Receita acumulada:    " -NoNewline
    Write-Host "R$ $receita" -ForegroundColor Green
    Write-Host ""
    
    # Meta
    Write-Host "🎯 META MENSAL" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "   Objetivo:             " -NoNewline
    Write-Host "$meta extrações = R$ $metaReceita" -ForegroundColor Cyan
    Write-Host "   Progresso:            " -NoNewline
    
    if ($progresso -ge 100) {
        Write-Host "$progresso% " -NoNewline -ForegroundColor Green
        Write-Host "✅ META ATINGIDA!" -ForegroundColor Green
    } elseif ($progresso -ge 75) {
        Write-Host "$progresso%" -ForegroundColor Yellow
    } elseif ($progresso -ge 50) {
        Write-Host "$progresso%" -ForegroundColor Cyan
    } else {
        Write-Host "$progresso%" -ForegroundColor White
    }
    
    # Barra de progresso
    $barraTotal = 50
    $barraPreenchida = [math]::Floor(($progresso / 100) * $barraTotal)
    $barraVazia = $barraTotal - $barraPreenchida
    
    Write-Host "   [" -NoNewline
    Write-Host ("█" * $barraPreenchida) -NoNewline -ForegroundColor Green
    Write-Host ("░" * $barraVazia) -NoNewline -ForegroundColor DarkGray
    Write-Host "]"
    
    $faltam = $meta - $TotalExtracoes
    if ($faltam -gt 0) {
        Write-Host "   Faltam:               " -NoNewline
        Write-Host "$faltam extrações (R$ $($faltam * $ValorPorExtracao))" -ForegroundColor Red
    }
    Write-Host ""
    
    # Projeção
    Write-Host "📈 PROJEÇÃO PARA FIM DO MÊS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "   Dia atual:            $diaAtual de $diasNoMes"
    Write-Host "   Extrações/dia:        " -NoNewline
    Write-Host "$([math]::Round($extraçoesPorDia, 0))" -ForegroundColor Cyan
    Write-Host "   Projeção mensal:      " -NoNewline
    
    if ($projecaoMes -ge $meta) {
        Write-Host "$projecaoMes extrações" -ForegroundColor Green
        Write-Host "   Receita projetada:    " -NoNewline
        Write-Host "R$ $receitaProjetada 🚀" -ForegroundColor Green
    } else {
        Write-Host "$projecaoMes extrações" -ForegroundColor Yellow
        Write-Host "   Receita projetada:    " -NoNewline
        Write-Host "R$ $receitaProjetada" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Salário total
    $salarioBase = 5000
    $receitaTotal = $salarioBase + $receita
    $receitaTotalProjetada = $salarioBase + $receitaProjetada
    
    Write-Host "💵 GANHO TOTAL" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "   Salário base:         R$ $salarioBase"
    Write-Host "   Bônus atual:          " -NoNewline
    Write-Host "R$ $receita" -ForegroundColor Green
    Write-Host "   Total atual:          " -NoNewline
    Write-Host "R$ $receitaTotal" -ForegroundColor Green
    Write-Host "   Bônus projetado:      " -NoNewline
    Write-Host "R$ $receitaProjetada" -ForegroundColor Cyan
    Write-Host "   Total projetado:      " -NoNewline
    Write-Host "R$ $receitaTotalProjetada 🎯" -ForegroundColor Cyan
    Write-Host ""
    
    # Dicas
    if ($progresso -lt 100) {
        Write-Host "💡 DICAS PARA ATINGIR META:" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        
        $extraçoesNecessariasPorDia = [math]::Ceiling($faltam / ($diasNoMes - $diaAtual))
        Write-Host "   • Extrair $extraçoesNecessariasPorDia extrações/dia até fim do mês"
        
        $tribunaisNecessarios = [math]::Ceiling($extraçoesNecessariasPorDia / 10000)
        Write-Host "   • Rodar com $tribunaisNecessarios+ tribunais simultâneos"
        Write-Host "   • Aumentar --wp para 10 e --rps para 5"
        Write-Host "   • Executar script bulk: .\scripts\extrair_bulk.ps1"
    } else {
        Write-Host "🎊 PARABÉNS! META ATINGIDA! 🎊" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
        $excedente = $TotalExtracoes - $meta
        $bonusExtra = $excedente * $ValorPorExtracao
        Write-Host "   Você superou a meta em $excedente extrações!"
        Write-Host "   Bônus extra: R$ $bonusExtra 💰"
    }
    
    Write-Host ""
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    if ($Watch) {
        Write-Host ""
        Write-Host "🔄 Atualizando em 10 segundos... (Ctrl+C para sair)" -ForegroundColor DarkGray
    }
}

# Execução
if ($Watch) {
    while ($true) {
        $total = Get-TotalExtracoes -Path $DiretorioResultados
        Show-Dashboard -TotalExtracoes $total -ValorPorExtracao $ValorPorExtracao
        Start-Sleep -Seconds 10
    }
} else {
    $total = Get-TotalExtracoes -Path $DiretorioResultados
    Show-Dashboard -TotalExtracoes $total -ValorPorExtracao $ValorPorExtracao
}
