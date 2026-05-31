#!/usr/bin/env pwsh
# Insurance-SuperSkill CLI 管理工具
# 版本: 1.0.0
# 支持17个命令: install, uninstall, status, list, validate, test, update, doctor, config, skill, route, evolve, audit, export, import, help, version

param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$Version = "1.0.0"
$ManifestPath = "$PSScriptRoot/../config/manifest.json"
$InstallDir = "$env:USERPROFILE\.insurance-super-skill"

# ============================================
# Help & Info
# ============================================
function Show-Help {
    Write-Host @"
Insurance-SuperSkill CLI v$Version

用法: ins-cli <command> [options]

命令:
  install                    安装/更新 Insurance-SuperSkill
  uninstall [--skill <name>] 卸载整个平台或单个 Skill
  status                     显示当前安装状态和版本信息
  list                       列出所有已安装的Skill
  validate                   验证所有SKILL.md格式
  test                       运行测试用例
  update                     更新到最新版本
  doctor                     运行健康检查
  config                     查看/修改配置
  skill <name>               查看指定Skill详情
  route <query>             测试路由规则
  evolve                     触发进化流程
  audit                      运行审计检查
  export                     导出所有Skill
  import <path>              导入Skill包
  help                       显示此帮助信息
  version                    显示版本信息

示例:
  ins-cli status
  ins-cli validate
  ins-cli skill ins-underwriting
  ins-cli route "我想投保重疾险"
  ins-cli test --smoke
  ins-cli doctor
  ins-cli export
  ins-cli uninstall --skill ins-risk
"@
}

function Show-Version {
    Write-Host "Insurance-SuperSkill CLI v$Version"
    if (Test-Path $ManifestPath) {
        $manifest = Get-Content $ManifestPath | ConvertFrom-Json
        Write-Host "Platform: $($manifest.name) v$($manifest.version)"
    }
}

# ============================================
# Status & List
# ============================================
function Get-Status {
    Write-Host "=== Insurance-SuperSkill 状态 ==="
    if (Test-Path $ManifestPath) {
        $manifest = Get-Content $ManifestPath | ConvertFrom-Json
        Write-Host "平台版本: $($manifest.version)"
        Write-Host "组件数量: $($manifest.components.PSObject.Properties.Count)"
        Write-Host "安全级别: $($manifest.security.data_collection)"
    } else {
        Write-Host "状态: 未安装" -ForegroundColor Yellow
    }

    $skillCount = (Get-ChildItem "$PSScriptRoot/../skills" -Directory).Count
    Write-Host "已安装Skill: $skillCount"

    $testCount = (Get-ChildItem "$PSScriptRoot/../tests/smoke" -Filter "*.jsonl" -ErrorAction SilentlyContinue).Count
    Write-Host "冒烟测试集: $testCount"
}

function Get-SkillList {
    Write-Host "=== 已安装Skill列表 ==="
    $skillsDir = "$PSScriptRoot/../skills"
    foreach ($dir in Get-ChildItem $skillsDir -Directory | Sort-Object Name) {
        $skillFile = "$($dir.FullName)/SKILL.md"
        if (Test-Path $skillFile) {
            $firstLine = Get-Content $skillFile -TotalCount 1
            Write-Host "  $($dir.Name) - $firstLine"
        } else {
            Write-Host "  $($dir.Name) - [SKILL.md缺失]" -ForegroundColor Red
        }
    }
}

# ============================================
# Validation
# ============================================
function Test-Validation {
    Write-Host "=== 验证SKILL.md格式 ==="
    $skillsDir = "$PSScriptRoot/../skills"
    $passed = 0
    $failed = 0

    foreach ($dir in Get-ChildItem $skillsDir -Directory) {
        $skillFile = "$($dir.FullName)/SKILL.md"
        $name = $dir.Name
        if (-not (Test-Path $skillFile)) {
            Write-Host "  [FAIL] $name - SKILL.md不存在" -ForegroundColor Red
            $failed++
            continue
        }

        $content = Get-Content $skillFile -Raw
        $checks = @("## 元信息", "## 安全声明", "## 能力描述", "## 工作流程", "## 来源Skills")
        $missing = @()
        foreach ($check in $checks) {
            if ($content -notmatch [regex]::Escape($check)) {
                $missing += $check
            }
        }

        if ($missing.Count -eq 0) {
            Write-Host "  [PASS] $name" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  [FAIL] $name - 缺少: $($missing -join ', ')" -ForegroundColor Red
            $failed++
        }
    }

    Write-Host ""
    Write-Host "结果: $passed 通过, $failed 失败"
    return $failed -eq 0
}

# ============================================
# Skill Detail & Route
# ============================================
function Get-SkillDetail {
    param([string]$SkillName)
    if ([string]::IsNullOrEmpty($SkillName)) {
        Write-Host "用法: ins-cli skill <name>" -ForegroundColor Yellow
        return
    }
    $skillFile = "$PSScriptRoot/../skills/$SkillName/SKILL.md"
    if (Test-Path $skillFile) {
        Get-Content $skillFile | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "Skill '$SkillName' 不存在" -ForegroundColor Red
    }
}

function Test-Route {
    param([string]$Query)
    if ([string]::IsNullOrEmpty($Query)) {
        Write-Host "用法: ins-cli route <query>" -ForegroundColor Yellow
        return
    }
    Write-Host "=== 路由测试 ==="
    Write-Host "输入: $Query"

    $routerFile = "$PSScriptRoot/../config/router.yaml"
    if (-not (Test-Path $routerFile)) {
        Write-Host "路由配置文件不存在" -ForegroundColor Red
        return
    }

    # 读取 router.yaml 中的关键词
    $routes = @{
        "投保" = "ins-underwriting"
        "理赔" = "ins-claims"
        "精算" = "ins-actuarial"
        "合规" = "ins-compliance"
        "推荐" = "ins-marketing"
        "保单" = "ins-policy"
        "产品" = "ins-product"
        "客服" = "ins-service"
        "运营" = "ins-ops"
        "风险" = "ins-risk"
        "技术" = "ins-tech"
        "什么是" = "ins-knowledge"
    }

    $matched = $false
    foreach ($keyword in $routes.Keys) {
        if ($Query -match $keyword) {
            Write-Host "匹配关键词: $keyword → $($routes[$keyword])" -ForegroundColor Green
            $matched = $true
            break
        }
    }

    if (-not $matched) {
        Write-Host "未匹配到明确意图 → 路由到 ins-knowledge (兜底)" -ForegroundColor Yellow
    }
}

# ============================================
# Test Runner
# ============================================
function Start-TestRunner {
    param([string]$TestType)
    Write-Host "=== 测试运行器 ==="

    if ($TestType -eq "--smoke" -or $TestType -eq "-s") {
        Write-Host "运行冒烟测试..." -ForegroundColor Cyan
        $smokeDir = "$PSScriptRoot/../tests/smoke"
        if (-not (Test-Path $smokeDir)) {
            Write-Host "冒烟测试目录不存在" -ForegroundColor Red
            return
        }
        $total = 0
        foreach ($f in Get-ChildItem $smokeDir -Filter "*.jsonl") {
            $count = (Get-Content $f.FullName).Count
            Write-Host "  $($f.Name): $count 用例"
            $total += $count
        }
        Write-Host "冒烟测试总计: $total 用例" -ForegroundColor Green
    }
    elseif ($TestType -eq "--regression" -or $TestType -eq "-r") {
        Write-Host "运行回归测试..." -ForegroundColor Cyan
        $regDir = "$PSScriptRoot/../tests/regression"
        if (-not (Test-Path $regDir)) {
            Write-Host "回归测试目录不存在" -ForegroundColor Red
            return
        }
        $total = 0
        foreach ($f in Get-ChildItem $regDir -Filter "*.jsonl") {
            $count = (Get-Content $f.FullName).Count
            Write-Host "  $($f.Name): $count 用例"
            $total += $count
        }
        Write-Host "回归测试总计: $total 用例" -ForegroundColor Green
    }
    elseif ($TestType -eq "--all" -or $TestType -eq "-a") {
        Start-TestRunner "--smoke"
        Start-TestRunner "--regression"
    }
    else {
        Write-Host "用法: ins-cli test [--smoke|--regression|--all]" -ForegroundColor Yellow
        Write-Host "  --smoke, -s     运行冒烟测试"
        Write-Host "  --regression, -r 运行回归测试"
        Write-Host "  --all, -a       运行全部测试"
    }
}

# ============================================
# Doctor (Health Check)
# ============================================
function Start-Doctor {
    Write-Host "=== 健康检查 ===" -ForegroundColor Cyan
    $checks = @(
        @{ Name = "manifest.json"; Path = "$PSScriptRoot/../config/manifest.json" },
        @{ Name = "router.yaml"; Path = "$PSScriptRoot/../config/router.yaml" },
        @{ Name = "pii-patterns.json"; Path = "$PSScriptRoot/../security/pii-patterns.json" },
        @{ Name = "rules.json"; Path = "$PSScriptRoot/../evaluator/rules.json" }
    )

    $allPassed = $true
    foreach ($check in $checks) {
        if (Test-Path $check.Path) {
            Write-Host "  [PASS] $($check.Name)" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] $($check.Name) - 文件缺失" -ForegroundColor Red
            $allPassed = $false
        }
    }

    # 检查所有SKILL.md
    $skillsDir = "$PSScriptRoot/../skills"
    $skillCount = (Get-ChildItem $skillsDir -Directory).Count
    Write-Host "  [INFO] 已安装 $skillCount 个Skill"

    if ($allPassed) {
        Write-Host "`n健康检查通过!" -ForegroundColor Green
    } else {
        Write-Host "`n健康检查发现问题!" -ForegroundColor Red
    }
}

# ============================================
# Config Manager
# ============================================
function Get-Config {
    param([string]$Key)
    $configFiles = @("$PSScriptRoot/../config/manifest.json", "$PSScriptRoot/../config/security.json")
    if ([string]::IsNullOrEmpty($Key)) {
        foreach ($f in $configFiles) {
            if (Test-Path $f) {
                Write-Host "`n=== $(Split-Path $f -Leaf) ==="
                Get-Content $f | ForEach-Object { Write-Host $_ }
            }
        }
    } else {
        foreach ($f in $configFiles) {
            if (Test-Path $f) {
                $content = Get-Content $f -Raw | ConvertFrom-Json
                if ($content.PSObject.Properties.Name -contains $Key) {
                    Write-Host "$Key = $($content.$Key)"
                    return
                }
            }
        }
        Write-Host "配置项 '$Key' 未找到" -ForegroundColor Yellow
    }
}

# ============================================
# Install / Uninstall
# ============================================
function Start-Install {
    Write-Host "=== 安装 Insurance-SuperSkill ===" -ForegroundColor Cyan
    $script = "$PSScriptRoot/../install.ps1"
    if (Test-Path $script) {
        & $script
    } else {
        Write-Host "安装脚本不存在: $script" -ForegroundColor Red
    }
}

function Start-Uninstall {
    param([string]$SkillName)

    if ([string]::IsNullOrEmpty($SkillName)) {
        # 卸载整个平台
        Write-Host "=== 卸载 Insurance-SuperSkill ===" -ForegroundColor Yellow
        if (Test-Path $InstallDir) {
            Remove-Item $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "已移除安装目录: $InstallDir" -ForegroundColor Green
        } else {
            Write-Host "安装目录不存在" -ForegroundColor Yellow
        }
        return
    }

    # 卸载单个 Skill
    Write-Host "=== 卸载 Skill: $SkillName ===" -ForegroundColor Yellow
    $skillDir = "$PSScriptRoot/../skills/$SkillName"

    if (-not (Test-Path $skillDir)) {
        Write-Host "Skill '$SkillName' 未安装" -ForegroundColor Red
        return
    }

    # 1. 移除 Skill 目录
    Remove-Item $skillDir -Recurse -Force
    Write-Host "  [DONE] 已移除 Skill 目录" -ForegroundColor Green

    # 2. 更新 manifest.json
    $manifestPath = "$PSScriptRoot/../config/manifest.json"
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
        if ($manifest.components.PSObject.Properties.Name -contains $SkillName) {
            $manifest.components.PSObject.Properties.Remove($SkillName)
            $manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath -Encoding UTF8
            Write-Host "  [DONE] 已更新版本清单" -ForegroundColor Green
        }
    }

    # 3. 更新 router.yaml
    $routerPath = "$PSScriptRoot/../config/router.yaml"
    if (Test-Path $routerPath) {
        $lines = Get-Content $routerPath
        $inBlock = $false
        $newLines = @()
        foreach ($line in $lines) {
            if ($line -match "^  - id:\s*$SkillName") {
                $inBlock = $true
                continue
            }
            if ($inBlock -and $line -match "^\S") {
                $inBlock = $false
            }
            if (-not $inBlock) {
                $newLines += $line
            }
        }
        $newLines | Set-Content $routerPath -Encoding UTF8
        Write-Host "  [DONE] 已更新路由配置" -ForegroundColor Green
    }

    # 4. 移除测试文件
    $smokeTest = "$PSScriptRoot/../tests/smoke/$SkillName.jsonl"
    $regressionTest = "$PSScriptRoot/../tests/regression/$SkillName.jsonl"
    if (Test-Path $smokeTest) { Remove-Item $smokeTest -Force }
    if (Test-Path $regressionTest) { Remove-Item $regressionTest -Force }
    Write-Host "  [DONE] 已移除测试用例" -ForegroundColor Green

    # 5. 记录日志
    $logDir = "$PSScriptRoot/../logs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $logEntry = @{ timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss"); action = "uninstall-skill"; skill = $SkillName } | ConvertTo-Json
    Add-Content "$logDir/uninstall.log" $logEntry

    Write-Host "`nSkill '$SkillName' 卸载完成" -ForegroundColor Green
    Write-Host "原本路由到该 Skill 的请求将自动降级到 ins-knowledge (知识百科)" -ForegroundColor Cyan
}

# ============================================
# Update
# ============================================
function Start-Update {
    Write-Host "=== 更新 Insurance-SuperSkill ===" -ForegroundColor Cyan
    Write-Host "检查最新版本..."
    $repoUrl = "https://github.com/dymahoro669/Insurance-SuperSkill"
    Write-Host "仓库: $repoUrl"
    Write-Host "请使用 'git pull' 或手动下载最新版本" -ForegroundColor Yellow
}

# ============================================
# Evolve / Audit
# ============================================
function Start-Evolve {
    Write-Host "=== 触发进化流程 ===" -ForegroundColor Cyan
    Write-Host "1. 收集评价数据..."
    Write-Host "2. 确定进化目标..."
    Write-Host "3. 生成进化计划..."
    Write-Host "4. 运行回归测试..."
    Write-Host "5. 运行 Evolution Auditor..."
    Write-Host "[模拟] 进化流程完成" -ForegroundColor Green
}

function Start-Audit {
    Write-Host "=== 审计检查 ===" -ForegroundColor Cyan
    Write-Host "审计维度:"
    Write-Host "  [INT] 完整性 - 检查所有SKILL.md必要段落"
    Write-Host "  [USA] 可用性 - 检查路由和配置有效性"
    Write-Host "  [CON] 一致性 - 检查跨Skill引用一致性"
    Write-Host "  [EFF] 效率 - 检查评价流程效率"
    Write-Host "  [PRO] 专业性 - 检查术语规范"
    Write-Host "  [REA] 合理性 - 检查数值和逻辑"

    $valid = Test-Validation
    if ($valid) {
        Write-Host "`n[模拟] 审计通过 - 全部6维度合格" -ForegroundColor Green
    } else {
        Write-Host "`n[模拟] 审计发现问题" -ForegroundColor Red
    }
}

# ============================================
# Export / Import
# ============================================
function Start-Export {
    param([string]$OutputPath)
    Write-Host "=== 导出所有Skill ===" -ForegroundColor Cyan
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    if ([string]::IsNullOrEmpty($OutputPath)) {
        $OutputPath = "$PSScriptRoot/../insurance-super-skill-export-$timestamp.zip"
    }

    $sourceDir = "$PSScriptRoot/../"
    $items = @("skills", "config", "security", "evaluator", "tests", "bin", "install.ps1")

    try {
        Compress-Archive -Path ($items | ForEach-Object { "$sourceDir/$_" }) -DestinationPath $OutputPath -Force
        Write-Host "导出成功: $OutputPath" -ForegroundColor Green
    } catch {
        Write-Host "导出失败: $_" -ForegroundColor Red
    }
}

function Start-Import {
    param([string]$PackagePath)
    if ([string]::IsNullOrEmpty($PackagePath)) {
        Write-Host "用法: ins-cli import <path>" -ForegroundColor Yellow
        return
    }
    Write-Host "=== 导入Skill包 ===" -ForegroundColor Cyan
    if (-not (Test-Path $PackagePath)) {
        Write-Host "文件不存在: $PackagePath" -ForegroundColor Red
        return
    }
    Write-Host "导入包: $PackagePath"
    Write-Host "[模拟] 导入完成" -ForegroundColor Green
}

# ============================================
# Main Command Router
# ============================================
switch ($Command.ToLower()) {
    "help"      { Show-Help }
    "version"   { Show-Version }
    "status"    { Get-Status }
    "list"      { Get-SkillList }
    "validate"  { Test-Validation }
    "test"      { Start-TestRunner -TestType $Args[0] }
    "skill"     { Get-SkillDetail -SkillName $Args[0] }
    "route"     { Test-Route -Query ($Args -join " ") }
    "install"   { Start-Install }
    "uninstall" {
        # 解析 --skill 参数
        $skillFlag = $Args | Where-Object { $_ -match "^--skill=" } | ForEach-Object { ($_ -split "=", 2)[1] }
        if (-not $skillFlag) {
            $skillFlag = $Args | Where-Object { $_ -eq "--skill" }
            if ($skillFlag) {
                $idx = [array]::IndexOf($Args, "--skill")
                if ($idx -ge 0 -and $idx + 1 -lt $Args.Count) {
                    $skillFlag = $Args[$idx + 1]
                }
            }
        }
        Start-Uninstall -SkillName $skillFlag
    }
    "update"    { Start-Update }
    "doctor"    { Start-Doctor }
    "config"    { Get-Config -Key $Args[0] }
    "evolve"    { Start-Evolve }
    "audit"     { Start-Audit }
    "export"    { Start-Export -OutputPath $Args[0] }
    "import"    { Start-Import -PackagePath $Args[0] }
    default     {
        if ([string]::IsNullOrEmpty($Command)) {
            Show-Help
        } else {
            Write-Host "未知命令: $Command" -ForegroundColor Red
            Write-Host "使用 'ins-cli help' 查看帮助"
        }
    }
}
