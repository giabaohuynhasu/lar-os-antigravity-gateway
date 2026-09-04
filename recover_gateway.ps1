# LAR-OS 1-Click Gateway Recovery Script
# Purpose: Cleanly kill any hung instances and restart LAR-OS Gateway on port 18797
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  LAR-OS EMERGENCY GATEWAY RECOVERY PROTOCOL" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$WorkspaceDir = "C:\Users\nswcl\.gemini\antigravity-ide\scratch\lar-os-antigravity-gateway"
$PythonExe = "C:\Users\nswcl\.gemini\antigravity-ide\scratch\.venv\Scripts\python.exe"
$GatewayScript = Join-Path $WorkspaceDir "lar_os_gateway.py"

# 1. Terminate any existing gateway instances on port 18797
Write-Host "[1/3] Scanning for hanging Gateway processes..." -ForegroundColor Yellow
$PortProcesses = Get-NetTCPConnection -LocalPort 18797 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($PortProcesses) {
    foreach ($pidToKill in $PortProcesses) {
        Write-Host "      Killing hung process PID $pidToKill on port 18797..." -ForegroundColor Red
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "      No active listener found on port 18797." -ForegroundColor Green
}

# 2. Launch Gateway cleanly in background
Write-Host "[2/3] Launching fresh Gateway instance..." -ForegroundColor Yellow
Start-Process -FilePath $PythonExe -ArgumentList "`"$GatewayScript`"" -WorkingDirectory $WorkspaceDir -WindowStyle Hidden

# 3. Wait up to 10 seconds for port 18797 to respond
Write-Host "[3/3] Verifying Gateway liveness on http://127.0.0.1:18797/health..." -ForegroundColor Yellow
$recovered = $false
for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:18797/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($resp.status -eq "healthy" -or $resp.gateway_status -eq "healthy") {
            Write-Host "      SUCCESS: Gateway is ONLINE and serving! (Attempt $i)" -ForegroundColor Green
            $recovered = $true
            break
        }
    } catch {
        Write-Host "      Waiting for Gateway boot... ($i/10)" -ForegroundColor Gray
    }
}

if (-not $recovered) {
    Write-Host "[-] Recovery warning: Gateway did not respond within 10s. Check logs." -ForegroundColor Red
    exit 1
} else {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  RECOVERY COMPLETE: LAR-OS GATEWAY FULLY RESTORED" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Cyan
    exit 0
}
