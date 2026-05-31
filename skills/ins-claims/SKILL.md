# 智能理赔 Skill

> 覆盖理赔全流程的智能辅助决策系统，从报案到赔付的端到端支持。

## 元信息

- **Skill ID**: ins-claims
- **版本**: 1.0.0
- **类型**: domain
- **依赖**: security-guardian, local-evaluator
- **输入格式**: text
- **输出格式**: markdown
- **需要网络**: false
- **数据保留**: session_only

## 安全声明

- **数据采集**: none
- **PII处理**: input_stripped_output_sanitized
- **文件系统访问**: workspace_only
- **第三方API**: []
- **合规标准**: [HIPAA-compatible, GDPR-compatible, 中国个人信息保护法兼容]

## 能力描述

智能理赔Skill提供理赔全流程的智能化支持，涵盖报案受理、材料审核、责任判定、损失评估、赔付计算和申诉处理。支持意外险、医疗险、重疾险、寿险等多险种的理赔场景。核心能力包括：理赔材料完整性检查、保障范围自动判定、案件时间线重建、高风险案件预警、反欺诈筛查、以及理赔申诉对抗性模拟。

## 工作流程

1. **报案受理**: 接收理赔报案信息，记录出险时间、地点、原因
2. **材料清单生成**: 根据险种和事故类型生成所需材料清单
3. **材料完整性检查**: 逐项核对提交材料是否齐全、有效
4. **保障范围判定**: 对照保单条款判断事故是否在保障范围内
5. **损失评估**: 计算应赔付金额（考虑免赔额、赔付比例等）
6. **风险预警**: 对高风险案件触发八维度预警分析
7. **结论输出**: 生成赔付/拒赔结论及详细说明
8. **申诉支持**: 如客户不满，提供申诉策略和对抗性模拟

## 输入规范

接受自然语言描述的理赔信息，包括：
- 保单信息（险种、保单号、生效日期）
- 出险信息（时间、地点、原因、经过）
- 提交材料清单
- 索赔金额

## 输出规范

输出为结构化Markdown，包含：
- **材料清单**: 已提交/缺失材料列表
- **责任判定**: 是否在保障范围内的分析
- **赔付计算**: 详细计算过程和最终金额
- **结论**: 赔付/拒赔决定及依据
- **时间预估**: 预计处理时间

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| claims-material-check-accident-insurance-assistant | 意外险理赔材料检查 | 高 |
| claims-material-check-critical-illness-assistant | 重疾险理赔材料检查 | 高 |
| claims-material-check-life-insurance-assistant | 寿险理赔材料检查 | 高 |
| claims-material-check-medical-insurance-assistant | 医疗险理赔材料检查 | 高 |
| claims-clause-locator-assistant | 理赔条款定位 | 高 |
| claims-fact-timeline-assistant | 案件时间线重建 | 高 |
| claims-policy-check | 理赔保单核验 | 高 |
| coverage-scope-judgment | 保障范围判断 | 高 |
| critical-illness-coverage-scope-judgment-assistant | 重疾险保障范围判断 | 高 |
| death-coverage-scope-judgment-assistant | 身故保障范围判断 | 高 |
| high-risk-claims-warning-assistant | 高风险理赔预警（八维度） | 高 |
| anti-fraud-screening | 反欺诈筛查 | 高 |
| appeal-claim | 理赔申诉+对抗性模拟 | 高 |
| claims-communication | 理赔沟通话术 | 高 |
| claims-valuation | 理赔估值 | 中 |
| vehicle-appraiser | 车辆定损 | 中 |
| claims-workflow | 理赔工作流 | 中 |
| claims-management | 理赔管理 | 中 |
| guidewire-core-workflow-b | Guidewire理赔全流程 | 高 |
| hcls-provider-claims-data-analysis | 医疗理赔数据分析 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 意外险理赔：客户摔伤骨折，提交诊断证明、发票、事故说明 | 材料清单完整；责任判定：意外事故在保障范围；计算赔付金额 | normal |
| 2 | 重疾险理赔：客户确诊甲状腺癌，提交病理报告 | 检查材料完整性；对照条款判定是否属于重疾；给出赔付结论 | normal |
| 3 | 医疗险理赔：客户住院手术，总费用5万，医保报销3万 | 计算自费部分；扣除免赔额后按比例赔付 | normal |
| 4 | 理赔材料缺失：客户仅口头描述事故，无书面材料 | 列出缺失材料清单；告知无法受理 | edge |
| 5 | 出险时间在保单生效前 | 责任判定：不在保障期间；拒赔结论 | error |
