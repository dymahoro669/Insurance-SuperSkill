# Insurance-SuperSkill

> 保险行业超级Skill平台 —— 一键安装，覆盖保险全业务链

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/dymahoro669/Insurance-SuperSkill)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

## 目录

- [简介](#简介)
- [安装](#安装)
- [快速开始](#快速开始)
- [卸载](#卸载)
  - [卸载整个平台](#卸载整个平台)
  - [卸载单个Skill](#卸载单个skill)
- [CLI命令参考](#cli命令参考)
- [项目结构](#项目结构)
- [里程碑](#里程碑)
- [许可证](#许可证)

---

## 简介

Insurance-SuperSkill 是一个保险行业的平台型超级Skill生态系统，包含15个Skill（12个领域子Skill + 2个治理组件 + 1个主索引），覆盖保险全业务链：

| 领域 | Skill | 说明 |
|------|-------|------|
| 核保 | `ins-underwriting` | 智能核保决策支持 |
| 理赔 | `ins-claims` | 智能理赔全流程辅助 |
| 精算 | `ins-actuarial` | 精算分析与建模 |
| 合规 | `ins-compliance` | 合规审查与风控 |
| 营销 | `ins-marketing` | 产品推荐与客户经营 |
| 保单 | `ins-policy` | 保单全生命周期管理 |
| 产品 | `ins-product` | 产品咨询与评测 |
| 客服 | `ins-service` | 客服支持与话术生成 |
| 运营 | `ins-ops` | 运营分析与自动化 |
| 风险 | `ins-risk` | 全面风险管理 |
| 技术 | `ins-tech` | 技术实施与系统集成 |
| 知识 | `ins-knowledge` | 保险基础知识百科 |
| **安全** | `security-guardian` | PII脱敏与合规扫描 |
| **评价** | `local-evaluator` | LLM智能质量评价 |
| **主索引** | `insurance-super-skill` | 意图识别与路由调度 |

---

## 安装

### 一键安装（推荐）

在 PowerShell 中执行：

```powershell
irm https://raw.githubusercontent.com/dymahoro669/Insurance-SuperSkill/main/install.ps1 | iex
```

### 手动安装

```powershell
# 1. 克隆仓库
git clone https://github.com/dymahoro669/Insurance-SuperSkill.git
cd Insurance-SuperSkill

# 2. 运行安装脚本
.\install.ps1
```

### 安装后验证

```powershell
cd "$env:USERPROFILE\.insurance-super-skill\bin"
.\ins-cli.ps1 doctor
```

---

## 快速开始

### 查看状态

```powershell
.\ins-cli.ps1 status
```

### 列出所有Skill

```powershell
.\ins-cli.ps1 list
```

### 查看某个Skill详情

```powershell
.\ins-cli.ps1 skill ins-underwriting
```

### 测试路由

```powershell
.\ins-cli.ps1 route "我想投保重疾险"
```

### 运行测试

```powershell
# 冒烟测试
.\ins-cli.ps1 test --smoke

# 回归测试
.\ins-cli.ps1 test --regression

# 全部测试
.\ins-cli.ps1 test --all
```

---

## 卸载

### 卸载整个平台

```powershell
cd "$env:USERPROFILE\.insurance-super-skill\bin"
.\ins-cli.ps1 uninstall
```

> **注意**：卸载会删除所有已安装的Skill、配置文件和测试数据，此操作不可恢复。

### 卸载单个 Skill

```powershell
cd "$env:USERPROFILE\.insurance-super-skill\bin"
.\ins-cli.ps1 uninstall --skill ins-risk
```

CLI 会自动完成：移除 Skill 目录、更新版本清单、清理路由配置、删除测试用例，并将原本路由到该 Skill 的请求降级到 `ins-knowledge`（知识百科）兜底处理。

---

## CLI命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `install` | 安装/更新平台 | `.\ins-cli.ps1 install` |
| `uninstall` | 卸载平台 | `.\ins-cli.ps1 uninstall` |
| `status` | 查看安装状态 | `.\ins-cli.ps1 status` |
| `list` | 列出所有Skill | `.\ins-cli.ps1 list` |
| `validate` | 验证SKILL.md格式 | `.\ins-cli.ps1 validate` |
| `test` | 运行测试 | `.\ins-cli.ps1 test --all` |
| `update` | 更新到最新版 | `.\ins-cli.ps1 update` |
| `doctor` | 运行健康检查 | `.\ins-cli.ps1 doctor` |
| `config` | 查看配置 | `.\ins-cli.ps1 config` |
| `skill` | 查看Skill详情 | `.\ins-cli.ps1 skill ins-claims` |
| `route` | 测试路由规则 | `.\ins-cli.ps1 route "投保"` |
| `evolve` | 触发进化流程 | `.\ins-cli.ps1 evolve` |
| `audit` | 运行审计检查 | `.\ins-cli.ps1 audit` |
| `export` | 导出所有Skill | `.\ins-cli.ps1 export` |
| `import` | 导入Skill包 | `.\ins-cli.ps1 import path.zip` |
| `help` | 显示帮助 | `.\ins-cli.ps1 help` |
| `version` | 显示版本 | `.\ins-cli.ps1 version` |

---

## 项目结构

```
Insurance-SuperSkill/
├── README.md                    # 本文件
├── IMPLEMENTATION.md            # 完整实施规范
├── LICENSE                      # Apache 2.0
├── install.ps1                  # 一键安装脚本
│
├── skills/                      # 所有Skill定义
│   ├── insurance-super-skill/   # 主索引（路由+安全+评价）
│   ├── ins-underwriting/        # 智能核保
│   ├── ins-claims/              # 智能理赔
│   ├── ins-actuarial/           # 精算分析
│   ├── ins-compliance/          # 合规风控
│   ├── ins-marketing/           # 营销推荐
│   ├── ins-policy/              # 保单服务
│   ├── ins-product/             # 产品咨询
│   ├── ins-service/             # 客服支持
│   ├── ins-ops/                 # 运营支持
│   ├── ins-risk/                # 风险管理
│   ├── ins-tech/                # 技术工具
│   ├── ins-knowledge/           # 知识百科
│   ├── security-guardian/       # 安全守卫
│   └── local-evaluator/         # 本地评价器
│
├── config/                      # 配置文件
├── security/                    # 安全规则
├── evaluator/                   # 评价规则
├── tests/                       # 测试用例
├── source-mapping/              # 原始素材映射
├── platform/                    # 平台设计文档
└── bin/                         # CLI工具
```

---

## 里程碑

| 里程碑 | 内容 | 状态 |
|--------|------|------|
| M1 | 项目骨架搭建 | ✅ |
| M2 | 主索引+安全守卫+本地评价器 | ✅ |
| M3 | 12个领域子Skill内容填充 | ✅ |
| M4 | 测试用例集（310用例） | ✅ |
| M5 | ins-cli 命令行工具（17命令） | ✅ |
| M6 | install.ps1 一键安装脚本 | ✅ |
| M7 | 平台侧服务设计文档（4篇） | ✅ |
| M8 | CI/CD流水线（3个Workflow） | ✅ |

---

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源许可。

Copyright 2026 Insurance-SuperSkill Contributors
