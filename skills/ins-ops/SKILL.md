# 运营支持 Skill

> 保险运营智能化支持，覆盖KPI分析、自动化、培训和工作流优化。

## 元信息

- **Skill ID**: ins-ops
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

运营支持Skill为保险公司运营团队提供数据驱动的高效运营支持，覆盖KPI监控与报告、业务流程自动化、团队绩效管理、渠道分析、佣金计算、培训需求分析和供应商协调。核心能力包括：自动生成周/月/季度运营报告、关键指标异常预警、流程瓶颈识别和优化建议、代理人绩效分析、渠道产能评估、以及培训效果追踪。

## 工作流程

1. **运营需求识别**: 确定分析类型（KPI/流程/团队/渠道）
2. **数据收集**: 汇总相关运营数据
3. **指标计算**: 计算关键运营指标
4. **趋势分析**: 分析指标变化趋势和异常点
5. **问题诊断**: 识别运营问题和根因
6. **改进建议**: 生成针对性的改进方案
7. **报告输出**: 生成结构化的运营分析报告

## 输入规范

接受自然语言描述的运营需求，包括：
- 分析周期（周/月/季度/年）
- 关注指标（保费/赔付/费用/人力等）
- 具体场景（团队/渠道/产品/区域）

## 输出规范

输出为结构化Markdown，包含：
- **KPI分析**: 关键指标及同比环比
- **问题识别**: 运营痛点和根因
- **改进建议**: 具体措施和预期效果
- **实施步骤**: 改进行动计划

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| afrexai-insurance-automation | 保险自动化 | 高 |
| insurance-workflow-automation | 保险工作流自动化 | 高 |
| weekly-kpi-report | 周KPI报告 | 高 |
| insurance-weekly-report | 保险周报 | 高 |
| insurance-data-analytics | 保险数据分析 | 高 |
| staff-mapping-management | 人员映射管理 | 中 |
| insurance-producer-training | 代理人培训 | 高 |
| vendor-coordination | 供应商协调 | 中 |
| insurance-carrier-appointment | 保险公司任命 | 中 |
| field-validation | 字段验证 | 中 |
| insurance-testing | 保险测试 | 中 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 生成上周团队KPI报告：保费50万，新单20件，继续率85% | KPI达成率；同比环比；改进建议 | normal |
| 2 | 分析某渠道产能下降原因 | 数据趋势；根因分析；优化方案 | normal |
| 3 | 设计新人代理人培训计划 | 培训模块；考核标准；时间安排 | normal |
| 4 | 自动化处理续保提醒流程 | 流程设计；触发条件；消息模板 | normal |
| 5 | 数据缺失无法计算KPI | 数据质量警告；建议补充数据 | edge |
