# 合规风控 Skill

> 保险行业合规审查与风险控制的综合支持系统。

## 元信息

- **Skill ID**: ins-compliance
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

合规风控Skill为保险公司提供全面的合规与风险管理支持，涵盖监管法规解读、内部合规审计、反欺诈筛查、数据隐私保护、监管申报管理和监管变化影响分析。核心能力包括：HIPAA/GDPR/中国个保法合规检查、反洗钱(AML)筛查、利益冲突(COI)审查、FRIA基本权利影响评估、网络安全合规、欺诈检测三级风险评估、以及监管变化对业务的影响分析。

## 工作流程

1. **合规需求识别**: 确定审查类型（法规/审计/反欺诈/隐私）
2. **法规库检索**: 匹配适用的法律法规和监管要求
3. **文档审查**: 对保单、营销材料、操作流程进行合规检查
4. **风险识别**: 识别潜在的合规风险和违规点
5. **整改建议**: 生成具体的整改措施和时间表
6. **合规报告**: 输出审查结论和合规状态评估
7. **跟踪管理**: 建立整改进度跟踪机制

## 输入规范

接受自然语言描述的合规需求，包括：
- 审查对象（产品/流程/文档/系统）
- 适用法规（保险法/消保法/数据安全法等）
- 具体场景描述
- 已有合规措施

## 输出规范

输出为结构化Markdown，包含：
- **合规结论**: 是否合规及依据
- **依据条款**: 引用的具体法规条款
- **风险点**: 识别的合规风险
- **整改建议**: 具体整改措施和优先级
- **时间要求**: 整改时限

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| compliance | 合规框架 | 中 |
| compliance-review | 合规审查 | 中 |
| compliance-audit-insurance | 保险合规审计 | 中 |
| compliance-officer | 合规官角色 | 中 |
| hipaa-compliance-auditor | HIPAA合规审计（18类标识符检测+脱敏） | 高 |
| coi-compliance-checker | COI合规检查 | 中 |
| anti-fraud-screening | 反欺诈筛查（三级风险评估） | 高 |
| managing-insurance-fraud-detection | 欺诈检测管理 | 高 |
| regulatory-change-impact | 监管变化影响分析 | 高 |
| managing-insurance-regulatory-filings | 监管申报管理 | 中 |
| fria-assessment | EU AI Act基本权利影响评估 | 高 |
| cybersecurity-compliance | 网络安全合规 | 中 |
| risk-management-playbook | 风险管理手册 | 高 |
| quality-compliance | 质量管理体系合规 | 高 |
| breach-credit-monitor | 数据泄露信用监控 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 审查一份重疾险产品条款是否符合健康保险管理办法 | 引用相关条款；检查等待期、免赔额、续保等合规性 | normal |
| 2 | 检查营销材料中是否有"保证理赔"等违规表述 | 识别违禁词；标注违规位置；建议修改方案 | normal |
| 3 | 对一份包含客户健康数据的报告进行HIPAA合规审查 | 18类标识符检测；脱敏建议；最小必要原则检查 | normal |
| 4 | 反洗钱筛查：客户短期内大额投保后迅速退保 | 三级风险评估；可疑交易报告建议 | normal |
| 5 | 新法规要求：监管发布互联网保险新规，分析对现有业务影响 | 变化点对比；影响业务模块；整改建议 | normal |
