# 智能核保 Skill

> 基于保险医学和风险评估模型的智能核保决策支持系统。

## 元信息

- **Skill ID**: ins-underwriting
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

智能核保Skill覆盖保险核保全生命周期，从投保申请接收、健康告知分析、风险评估到核保结论生成。支持寿险、重疾险、医疗险、意外险、年金险等多险种的问卷分析和风险评级。核心能力包括：多维风险识别（职业风险、健康风险、财务风险、生活方式风险）、核保结论解释（标准体、加费、除外、延期、拒保）、以及复杂案件的复核支持。

## 工作流程

1. **投保信息接收**: 接收投保申请、健康问卷、财务告知等输入
2. **告知完整性审查**: 检查必填项是否完整，识别遗漏信息
3. **风险维度分析**: 从健康、职业、财务、生活方式四个维度评估风险
4. **风险评级计算**: 综合各维度风险计算总体风险等级
5. **核保结论生成**: 根据风险评级输出标准体/加费/除外/延期/拒保结论
6. **结论解释输出**: 生成面向客户和代理人的结论解释说明
7. **复核标记**: 对高风险或边缘案件标记建议复核

## 输入规范

接受自然语言描述的投保信息，包括：
- 被保人基本信息（年龄、性别、职业类别）
- 健康告知（既往病史、家族病史、体检结果）
- 财务告知（收入、负债、已有保额）
- 投保计划（险种、保额、缴费期限）

## 输出规范

输出为结构化Markdown，包含：
- **风险摘要**: 各维度风险概述
- **核保建议**: 具体核保结论及依据
- **结论解释**: 面向客户的通俗解释
- **补问建议**: 如信息不足，列出需补充的问题

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| underwriting-analysis | 核保系统分析框架、预测模型、定价充足性 | 高 |
| underwriting | 核保领域知识、提交到绑定生命周期 | 高 |
| accident-insurance-underwriting-questionnaire-assistant | 意外险问卷分析：职业/活动/交通风险提取 | 高 |
| annuity-insurance-underwriting-questionnaire-assistant | 年金险问卷分析：健康/缴费/合理性风险 | 高 |
| health-insurance-underwriting-questionnaire-assistant | 健康险问卷审查：五维度风险分析+补问建议 | 高 |
| critical-illness-underwriting-questionnaire-assistant | 重疾险问卷分析 | 高 |
| life-insurance-underwriting-questionnaire-assistant | 寿险问卷分析 | 高 |
| medical-insurance-underwriting-questionnaire-assistant | 医疗险问卷分析 | 高 |
| underwriting-questionnaire-precheck-assistant | 问卷初审流程 | 中 |
| underwriting-questionnaire-review | 问卷复核流程 | 中 |
| underwriting-questionnaire-secondary-review-assistant | 问卷二次复核 | 中 |
| underwriting-review-opinion-assistant | 复核意见整理 | 中 |
| underwriting-workflow-orchestrator-assistant | 核保案件全流程编排 | 中 |
| underwriting-conclusion-explanation | 核保结论解读（标准体/加费/除外/延期/拒保） | 中 |
| flood-zone-lookup | FEMA洪水风险查询 | 高 |
| prior-authorization-review | 事先授权审查 | 高 |
| extraction-policy-summary-ar | 保单结构化提取 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 35岁程序员投保重疾险，有高血压病史（150/95），无其他异常 | 风险摘要含高血压、职业风险低；建议加费或标准体视控制情况 | normal |
| 2 | 50岁建筑工人投保意外险，高空作业 | 职业风险等级高；建议加费或除外高风险作业 | normal |
| 3 | 28岁女性投保医疗险，告知乳腺癌家族史 | 健康风险需关注；建议标准体或加费视年龄 | normal |
| 4 | 60岁退休老人投保年金险，年收入仅2万但申请年缴10万 | 财务核保不通过；建议降低保额或补充收入证明 | normal |
| 5 | 投保信息完全缺失，仅说"想买保险" | 补问建议列出所有必填项 | edge |
