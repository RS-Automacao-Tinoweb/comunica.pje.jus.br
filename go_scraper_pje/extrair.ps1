<#
.SYNOPSIS
    Script para facilitar extração de dados do PJE

.DESCRIPTION
    Permite executar o scraper com configurações pré-definidas para todos os tribunais

.PARAMETER Inicio
    Data inicial (formato: YYYY-MM-DD ou DD/MM/YYYY)

.PARAMETER Fim
    Data final (formato: YYYY-MM-DD ou DD/MM/YYYY)

.PARAMETER Tribunais
    Tribunais específicos (separados por vírgula) ou "TODOS"

.PARAMETER Modo
    Modo de execução: "conservador", "normal", "agressivo"

.PARAMETER Cache
    Habilitar cache (padrão: true)

.EXAMPLE
    .\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025"
    Extrai dados de todos os tribunais no modo normal

.EXAMPLE
    .\extrair.ps1 -Inicio "2025-11-01" -Fim "2025-11-10" -Modo agressivo
    Extrai dados em modo agressivo

.EXAMPLE
    .\extrair.ps1 -Inicio "01/11/2025" -Fim "10/11/2025" -Tribunais "TJSP,TJAM,TJBA"
    Extrai dados apenas dos tribunais especificados
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Inicio,
    
    [Parameter(Mandatory=$true)]
    [string]$Fim,
    
    [Parameter(Mandatory=$false)]
    [string]$Tribunais = "TODOS",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("conservador", "normal", "agressivo")]
    [string]$Modo = "normal",
    
    [Parameter(Mandatory=$false)]
    [bool]$Cache = $true
)

# Lista completa de tribunais
$TodosTribunais = @(
    "TJAC", "TJAL", "TJAM", "TJAP", "TJBA", "TJCE", "TJDFT", "TJES",
    "TJGO", "TJMA", "TJMG", "TJMMG", "TJMRS", "TJMS", "TJMSP", "TJMT",
    "TJPA", "TJPB", "TJPE", "TJPI", "TJPR", "TJRJ", "TJRN", "TJRO",
    "TJRR", "TJRS", "TJSC", "TJSE", "TJSP", "TJTO"
)

# Configurações de modo
$Configs = @{
    "conservador" = @{ wp = 2; rps = 2; wt = 1 }
    "normal"      = @{ wp = 5; rps = 3; wt = 1 }
    "agressivo"   = @{ wp = 10; rps = 10; wt = 2 }
}

# Converte data brasileira para ISO se necessário
function Convert-ToISODate {
    param([string]$Data)
    
    if ($Data -match '^\d{2}/\d{2}/\d{4}$') {
        $parts = $Data.Split('/')
        return "$($parts[2])-$($parts[1])-$($parts[0])"
    }
    return $Data
}

# Banner
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   Extracao de Dados PJE - Todos os Tribunais" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Converte datas
$DataInicio = Convert-ToISODate $Inicio
$DataFim = Convert-ToISODate $Fim

# Define tribunais
$ListaTribunais = if ($Tribunais -eq "TODOS") {
    $TodosTribunais -join ","
} else {
    $Tribunais
}

# Pega configuração do modo
$Config = $Configs[$Modo]

# Exibe configuração
Write-Host "Configuracao:" -ForegroundColor Yellow
Write-Host "   Periodo: $DataInicio a $DataFim"
Write-Host "   Tribunais: $(if ($Tribunais -eq 'TODOS') { 'TODOS (30 tribunais)' } else { $Tribunais })"
Write-Host "   Modo: $Modo (wp=$($Config.wp), rps=$($Config.rps), wt=$($Config.wt))"
Write-Host "   Cache: $Cache"
Write-Host ""

# Confirma execução
$Confirma = Read-Host "Deseja continuar? (S/N)"
if ($Confirma -ne "S" -and $Confirma -ne "s") {
    Write-Host "[X] Operacao cancelada" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "[OK] Iniciando extracao..." -ForegroundColor Green
Write-Host ""

# Monta comando
$Comando = "go run . --tribunais `"$ListaTribunais`" --inicio $DataInicio --fim $DataFim --wp $($Config.wp) --rps $($Config.rps) --wt $($Config.wt) --cache=$Cache"

# Executa
Write-Host "Executando: $Comando" -ForegroundColor Gray
Write-Host ""

Invoke-Expression $Comando

# Resultado
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Extracao concluida com sucesso!" -ForegroundColor Green
    
    # Mostra último cache criado
    $UltimoCache = Get-ChildItem "cache" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($UltimoCache) {
        Write-Host ""
        Write-Host "Cache criado em: cache\$($UltimoCache.Name)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Para filtrar os dados:" -ForegroundColor Yellow
        Write-Host "   cd filtros" -ForegroundColor Gray
        Write-Host "   go run main.go" -ForegroundColor Gray
        Write-Host "   Acesse: http://localhost:8080" -ForegroundColor Gray
    }
} else {
    Write-Host "[ERRO] Erro na extracao (codigo: $LASTEXITCODE)" -ForegroundColor Red
}
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
