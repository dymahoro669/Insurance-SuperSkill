# Insurance-SuperSkill Bootstrap
# 纯英文入口，绕过 PowerShell 5.1 iex 编码问题
# 用法: irm https://raw.githubusercontent.com/dymahoro669/Insurance-SuperSkill/main/bootstrap.ps1 | iex

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/dymahoro669/Insurance-SuperSkill"
$InstallScriptUrl = "$RepoUrl/raw/main/install.ps1"
$TmpFile = "$env:TEMP\ins-super-skill-install.ps1"

Write-Host "Insurance-SuperSkill Bootstrap" -ForegroundColor Cyan
Write-Host "Downloading installer..." -ForegroundColor Yellow

try {
    $client = New-Object System.Net.WebClient
    $client.Encoding = [System.Text.Encoding]::UTF8
    $client.DownloadFile($InstallScriptUrl, $TmpFile)
    Write-Host "Download OK" -ForegroundColor Green
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Running installer..." -ForegroundColor Yellow
& $TmpFile

Remove-Item $TmpFile -Force -ErrorAction SilentlyContinue
Write-Host "Bootstrap complete" -ForegroundColor Green
