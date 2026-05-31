#!/usr/bin/env pwsh
# Insurance-SuperSkill Platform 启动脚本
# 启动 FastAPI 平台服务 + 后台自动评价触发器

param(
    [switch]$NoAutoEval,
    [int]$Port = 8080,
    [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$PlatformDir = "$PSScriptRoot/platform/server"
$ClientDir = "$PSScriptRoot/platform/client"

# ---------------------------------------------------------------
# 1. 检测 Python
# ---------------------------------------------------------------
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command python3 -ErrorAction SilentlyContinue).Source }
if (-not $Python) {
    Write-Host "错误: 未找到 python 或 python3，请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

Write-Host "使用 Python: $Python" -ForegroundColor Gray

# ---------------------------------------------------------------
# 2. 检查依赖
# ---------------------------------------------------------------
$requirements = "$PlatformDir/requirements.txt"
if (Test-Path $requirements) {
    Write-Host "检查依赖..." -ForegroundColor Cyan
    & $Python -m pip install -q -r $requirements
}

# 检查 client 需要的 requests
& $Python -c "import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "安装 client 依赖 (requests)..." -ForegroundColor Cyan
    & $Python -m pip install -q requests
}

# ---------------------------------------------------------------
# 3. 启动 FastAPI 平台服务
# ---------------------------------------------------------------
Write-Host "=== 启动 Insurance-SuperSkill Platform ===" -ForegroundColor Cyan
Write-Host "地址: http://$Host`:$Port" -ForegroundColor Gray
Write-Host "API 文档: http://$Host`:$Port/docs" -ForegroundColor Gray
Write-Host ""

$platformJob = Start-Job -ScriptBlock {
    param($py, $dir, $h, $p)
    Set-Location $dir
    $env:PLATFORM_HOST = $h
    $env:PLATFORM_PORT = $p
    & $py -m uvicorn main:app --host $h --port $p
} -ArgumentList $Python, $PlatformDir, $Host, $Port

# 等待服务就绪
Write-Host "等待平台服务就绪..." -ForegroundColor Yellow
$maxWait = 30
$elapsed = 0
$ready = $false
while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds 1
    $elapsed++
    try {
        $resp = Invoke-RestMethod -Uri "http://$Host`:$Port/" -Method Get -TimeoutSec 2
        if ($resp.version) {
            $ready = $true
            break
        }
    } catch {
        # 继续等待
    }
}

if (-not $ready) {
    Write-Host "平台服务启动超时，查看日志:" -ForegroundColor Red
    Receive-Job $platformJob
    Remove-Job $platformJob -Force
    exit 1
}

Write-Host "平台服务已就绪 (v$($resp.version))" -ForegroundColor Green
Write-Host ""

# ---------------------------------------------------------------
# 4. 启动后台自动评价触发器 (可选)
# ---------------------------------------------------------------
$autoEvalJob = $null
if (-not $NoAutoEval) {
    Write-Host "=== 启动自动评价触发器 ===" -ForegroundColor Cyan
    $autoEvalJob = Start-Job -ScriptBlock {
        param($py, $clientDir, $url)
        Set-Location $clientDir
        & $py "$clientDir/auto_evaluator.py" --platform-url $url --daemon
    } -ArgumentList $Python, $ClientDir, "http://$Host`:$Port"

    Start-Sleep -Seconds 2
    if ($autoEvalJob.State -eq "Failed") {
        Write-Host "自动评价触发器启动失败:" -ForegroundColor Red
        Receive-Job $autoEvalJob
    } else {
        Write-Host "自动评价触发器已在后台运行" -ForegroundColor Green
    }
    Write-Host ""
}

# ---------------------------------------------------------------
# 5. 保持运行 / 信号处理
# ---------------------------------------------------------------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Platform 运行中. 按 Ctrl+C 停止服务." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    while ($true) {
        Start-Sleep -Seconds 5
        # 输出平台服务最近日志（如果有错误）
        if ($platformJob.State -eq "Failed") {
            Write-Host "[平台服务异常]" -ForegroundColor Red
            Receive-Job $platformJob
            break
        }
        if ($autoEvalJob -and $autoEvalJob.State -eq "Failed") {
            Write-Host "[自动评价器异常]" -ForegroundColor Red
            Receive-Job $autoEvalJob
            $autoEvalJob = $null
        }
    }
} finally {
    Write-Host ""
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    if ($autoEvalJob) {
        Stop-Job $autoEvalJob -ErrorAction SilentlyContinue
        Remove-Job $autoEvalJob -Force -ErrorAction SilentlyContinue
        Write-Host "自动评价触发器已停止" -ForegroundColor Gray
    }
    Stop-Job $platformJob -ErrorAction SilentlyContinue
    Remove-Job $platformJob -Force -ErrorAction SilentlyContinue
    Write-Host "平台服务已停止" -ForegroundColor Gray
}
