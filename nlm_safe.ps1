# LAR-OS Safe NotebookLM PowerShell Wrapper
param (
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$nlmPath = "C:\Users\nswcl\.local\bin\nlm.exe"

# 1. Quick auth check
& $nlmPath login --check 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] NotebookLM auth expired. Auto re-authenticating..." -ForegroundColor Yellow
    & $nlmPath login 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] Auto re-authentication successful!" -ForegroundColor Green
    } else {
        Write-Host "[!] Re-authentication failed." -ForegroundColor Red
        exit 1
    }
}

# 2. Execute target command
& $nlmPath @ArgsList
