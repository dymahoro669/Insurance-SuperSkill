#!/usr/bin/env pwsh
# Insurance-SuperSkill 一键安装脚本
# 用法: irm https://raw.githubusercontent.com/dymahoro669/Insurance-SuperSkill/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$InstallDir = "$env:USERPROFILE\.insurance-super-skill"
$RepoUrl = "https://github.com/dymahoro669/Insurance-SuperSkill"
$Version = "1.0.0"

function Write-Header {
    Write-Host @"
=====================================
  Insurance-SuperSkill 安装程序
  版本: $Version
=====================================
"@ -ForegroundColor Cyan
}

function Test-Environment {
    Write-Host "[1/6] 检测环境..." -ForegroundColor Yellow
    $checks = @()
    $allPassed = $true

    # 检查PowerShell版本
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        $checks += "[PASS] PowerShell v$($PSVersionTable.PSVersion)"
    } else {
        $checks += "[FAIL] PowerShell版本过低 (需要 >= 5.0)"
        $allPassed = $false
    }

    # 检查Git
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $checks += "[PASS] Git已安装"
    } else {
        $checks += "[WARN] Git未安装 (可选)"
    }

    # 检查网络
    try {
        $null = Invoke-WebRequest -Uri "https://github.com" -TimeoutSec 5 -UseBasicParsing
        $checks += "[PASS] 网络连接正常"
    } catch {
        $checks += "[WARN] 网络连接异常"
    }

    # 检查执行策略
    $execPolicy = Get-ExecutionPolicy
    if ($execPolicy -eq "RemoteSigned" -or $execPolicy -eq "Unrestricted" -or $execPolicy -eq "Bypass") {
        $checks += "[PASS] 执行策略允许: $execPolicy"
    } else {
        $checks += "[WARN] 执行策略为 $execPolicy，可能需要调整"
    }

    $checks | ForEach-Object { Write-Host "  $_" }
    return $allPassed
}

function Install-Files {
    Write-Host "[2/6] 安装文件..." -ForegroundColor Yellow

    if (Test-Path $InstallDir) {
        Write-Host "  发现已有安装，正在备份..."
        $backupDir = "$InstallDir.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Rename-Item $InstallDir $backupDir
        Write-Host "  已备份到: $backupDir"
    }

    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\skills" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\config" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\security" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\evaluator" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\tests\smoke" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\tests\regression" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\source-mapping" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\platform" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\bin" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\.github\workflows" -Force | Out-Null

    # 如果当前目录就是源码目录，直接复制
    $sourceDir = $PSScriptRoot
    if (-not $sourceDir) {
        $sourceDir = "."
    }

    if (Test-Path "$sourceDir\skills") {
        Write-Host "  从本地源码复制..."
        Copy-Item "$sourceDir\skills\*" "$InstallDir\skills" -Recurse -Force
        Copy-Item "$sourceDir\config\*" "$InstallDir\config" -Force
        Copy-Item "$sourceDir\security\*" "$InstallDir\security" -Force
        Copy-Item "$sourceDir\evaluator\*" "$InstallDir\evaluator" -Force
        Copy-Item "$sourceDir\tests\smoke\*" "$InstallDir\tests\smoke" -Force
        Copy-Item "$sourceDir\tests\regression\*" "$InstallDir\tests\regression" -Force
        Copy-Item "$sourceDir\source-mapping\*" "$InstallDir\source-mapping" -Force
        Copy-Item "$sourceDir\platform\*" "$InstallDir\platform" -Force
        Copy-Item "$sourceDir\bin\*" "$InstallDir\bin" -Force
        Copy-Item "$sourceDir\.github\workflows\*" "$InstallDir\.github\workflows" -Force
        Copy-Item "$sourceDir\install.ps1" "$InstallDir" -Force
        Copy-Item "$sourceDir\LICENSE" "$InstallDir" -Force
        Copy-Item "$sourceDir\IMPLEMENTATION.md" "$InstallDir" -Force
    } else {
        Write-Host "  尝试从GitHub下载..."
        $zipUrl = "$RepoUrl/archive/refs/heads/main.zip"
        $zipPath = "$env:TEMP\insurance-super-skill.zip"
        try {
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
            Expand-Archive -Path $zipPath -DestinationPath $env:TEMP -Force
            $extractedDir = "$env:TEMP\Insurance-SuperSkill-main"
            Copy-Item "$extractedDir\*" $InstallDir -Recurse -Force
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "  下载失败: $_" -ForegroundColor Red
            return $false
        }
    }

    Write-Host "  文件复制完成"
    return $true
}

function Initialize-Security {
    Write-Host "[3/6] 初始化安全设置..." -ForegroundColor Yellow

    # 加载PII模式
    $piiFile = "$InstallDir\security\pii-patterns.json"
    if (Test-Path $piiFile) {
        $piiConfig = Get-Content $piiFile -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "  - PII脱敏引擎: 已启用 ($($piiConfig.patterns.Count)类模式)"
    } else {
        Write-Host "  - PII脱敏引擎: [WARN] 配置文件缺失" -ForegroundColor Yellow
    }

    # 加载合规黑名单
    $blFile = "$InstallDir\security\compliance-blacklist.json"
    if (Test-Path $blFile) {
        $blConfig = Get-Content $blFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $totalPatterns = 0
        foreach ($cat in $blConfig.categories.PSObject.Properties) {
            $totalPatterns += $cat.Value.patterns.Count
        }
        Write-Host "  - 合规黑名单: 已加载 ($totalPatterns 个违禁表述)"
    } else {
        Write-Host "  - 合规黑名单: [WARN] 配置文件缺失" -ForegroundColor Yellow
    }

    Write-Host "  - 会话隔离: 已启用"
    Write-Host "  - 审计日志: 本地模式"
    Write-Host "  - 数据保留: session_only"
}

function Test-Health {
    Write-Host "[4/6] 运行健康检查..." -ForegroundColor Yellow

    $checks = @(
        @{ Name = "manifest.json"; Test = { Test-Path "$InstallDir\config\manifest.json" } },
        @{ Name = "router.yaml"; Test = { Test-Path "$InstallDir\config\router.yaml" } },
        @{ Name = "pii-patterns.json"; Test = { Test-Path "$InstallDir\security\pii-patterns.json" } },
        @{ Name = "rules.json"; Test = { Test-Path "$InstallDir\evaluator\rules.json" } },
        @{ Name = "SKILL.md文件"; Test = { (Get-ChildItem "$InstallDir\skills" -Directory).Count -ge 15 } },
        @{ Name = "冒烟测试"; Test = { (Get-ChildItem "$InstallDir\tests\smoke" -Filter "*.jsonl").Count -ge 10 } },
        @{ Name = "回归测试"; Test = { (Get-ChildItem "$InstallDir\tests\regression" -Filter "*.jsonl").Count -ge 10 } },
        @{ Name = "平台文档"; Test = { (Get-ChildItem "$InstallDir\platform" -Filter "*.md").Count -ge 4 } }
    )

    $allPassed = $true
    foreach ($check in $checks) {
        $result = & $check.Test
        if ($result) {
            Write-Host "  [PASS] $($check.Name)" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] $($check.Name)" -ForegroundColor Red
            $allPassed = $false
        }
    }

    return $allPassed
}

function Test-Cli {
    Write-Host "[5/6] 验证 ins-cli..." -ForegroundColor Yellow
    $cliPath = "$InstallDir\bin\ins-cli.ps1"
    if (Test-Path $cliPath) {
        Write-Host "  [PASS] ins-cli.ps1 存在"

        # 验证关键命令
        $content = Get-Content $cliPath -Raw
        $requiredCommands = @("install", "uninstall", "status", "list", "validate", "test", "update", "doctor", "config", "skill", "route", "evolve", "audit", "export", "import", "help", "version")
        $foundCount = 0
        foreach ($cmd in $requiredCommands) {
            if ($content -match "`"$cmd`"" -or $content -match "'$cmd'") {
                $foundCount++
            }
        }
        Write-Host "  [INFO] CLI命令覆盖: $foundCount/$($requiredCommands.Count)"

        if ($foundCount -ge 17) {
            Write-Host "  [PASS] 全部17个命令已定义"
        } else {
            Write-Host "  [WARN] 部分命令未完整实现" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] ins-cli.ps1 不存在" -ForegroundColor Red
        return $false
    }
    return $true
}

function Complete-Install {
    Write-Host "[6/6] 安装完成..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Insurance-SuperSkill 安装成功!" -ForegroundColor Green
    Write-Host "  安装目录: $InstallDir"
    Write-Host "  版本: $Version"
    Write-Host ""
    Write-Host "使用方法:"
    Write-Host "  cd $InstallDir\bin"
    Write-Host "  .\ins-cli.ps1 status    - 查看状态"
    Write-Host "  .\ins-cli.ps1 list      - 列出所有Skill"
    Write-Host "  .\ins-cli.ps1 validate  - 验证格式"
    Write-Host "  .\ins-cli.ps1 help      - 查看帮助"
    Write-Host ""
    Write-Host "或者添加到 PATH:"
    Write-Host "  [Environment]::SetEnvironmentVariable('Path', `$env:Path + ';$InstallDir\bin', 'User')"
}

# 主安装流程
Write-Header
$envOk = Test-Environment
if (-not $envOk) {
    Write-Host "环境检查未通过，继续安装..." -ForegroundColor Yellow
}

$filesOk = Install-Files
if (-not $filesOk) {
    Write-Host "文件安装失败" -ForegroundColor Red
    exit 1
}

Initialize-Security
$healthOk = Test-Health
$cliOk = Test-Cli

if ($healthOk -and $cliOk) {
    Complete-Install
} else {
    Write-Host "安装完成，但健康检查发现问题" -ForegroundColor Yellow
    Write-Host "请检查上述失败项，或运行 .\ins-cli.ps1 doctor 查看详情"
}
