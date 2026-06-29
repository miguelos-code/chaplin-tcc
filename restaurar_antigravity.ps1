# ============================================================
#  Chaplin TCC - Restaurador de Historico do Antigravity
#  Execute este script no PowerShell apos instalar o Antigravity
#  no novo PC. Ele vai extrair todos os chats e memorias.
# ============================================================

$backupFile = Join-Path $PSScriptRoot "Antigravity_Backup.zip"
$destino    = Join-Path $env:USERPROFILE ".gemini\antigravity"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Restaurador de Historico - Antigravity"     -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se o backup existe
if (-not (Test-Path $backupFile)) {
    Write-Host "[ERRO] Arquivo 'Antigravity_Backup.zip' nao encontrado!" -ForegroundColor Red
    Write-Host "       Certifique-se de que este script esta na mesma pasta do .zip" -ForegroundColor Red
    pause
    exit 1
}

# 2. Verificar se o Antigravity ja foi instalado
if (-not (Test-Path $destino)) {
    Write-Host "[AVISO] A pasta do Antigravity nao existe ainda." -ForegroundColor Yellow
    Write-Host "        Criando: $destino" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $destino -Force | Out-Null
}

# 3. Extrair o backup
Write-Host "[1/3] Extraindo backup..." -ForegroundColor Green
Expand-Archive -Path $backupFile -DestinationPath $destino -Force

# 4. Conferir
$conversas = (Get-ChildItem "$destino\conversations\*.pb" -ErrorAction SilentlyContinue).Count
$brains    = (Get-ChildItem "$destino\brain" -Directory -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "[2/3] Verificando integridade..." -ForegroundColor Green
Write-Host "       Conversas restauradas: $conversas" -ForegroundColor White
Write-Host "       Pastas de contexto:    $brains" -ForegroundColor White

# 5. Resultado
Write-Host ""
if ($conversas -gt 0) {
    Write-Host "[3/3] SUCESSO! Historico restaurado com exito!" -ForegroundColor Green
    Write-Host "       Feche e reabra o Antigravity para carregar os chats." -ForegroundColor Cyan
} else {
    Write-Host "[3/3] ATENCAO: Nenhuma conversa encontrada. Verifique o .zip." -ForegroundColor Yellow
}

Write-Host ""
pause
