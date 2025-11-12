# 🔍 Script para Iniciar Interface de Filtros PJE
# Inicia servidor web na porta 8080

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🔍 INICIANDO INTERFACE DE FILTROS PJE 🔍        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$baseDir = "D:\RS - LySA - EMPRESA\go_scraper_pje"
$filtrosDir = "$baseDir\filtros"

# Verifica se diretório existe
if (-not (Test-Path $filtrosDir)) {
    Write-Host "❌ Diretório filtros não encontrado: $filtrosDir" -ForegroundColor Red
    exit 1
}

# Navega para diretório
Set-Location $filtrosDir

Write-Host "📁 Diretório: $filtrosDir" -ForegroundColor Yellow
Write-Host "🌐 Porta: 8080" -ForegroundColor Yellow
Write-Host ""

# Verifica se porta 8080 está livre
$portaOcupada = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portaOcupada) {
    Write-Host "⚠️  Porta 8080 já está em uso!" -ForegroundColor Yellow
    Write-Host "   Tentando matar processo..." -ForegroundColor Yellow
    
    $processo = Get-Process -Id $portaOcupada.OwningProcess -ErrorAction SilentlyContinue
    if ($processo) {
        Stop-Process -Id $processo.Id -Force
        Write-Host "   ✅ Processo encerrado" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
}

Write-Host "🚀 Iniciando servidor..." -ForegroundColor Green
Write-Host ""

# Inicia servidor
try {
    # Abre navegador após 3 segundos
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:8080"
    } | Out-Null
    
    # Inicia servidor (bloqueante)
    go run main.go
}
catch {
    Write-Host "❌ Erro ao iniciar servidor: $_" -ForegroundColor Red
    exit 1
}
