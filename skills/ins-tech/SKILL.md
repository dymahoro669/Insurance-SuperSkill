# 技术工具 Skill

> 保险行业技术实施与系统集成支持，覆盖核心系统、数据处理和标准对接。

## 元信息

- **Skill ID**: ins-tech
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

技术工具Skill为保险公司的IT团队和实施顾问提供技术实施支持，覆盖核心保险系统（Guidewire等）配置、数据处理流程设计、API集成方案、表单自动化、标准对接（ACORD等）、以及保险数据分析。核心能力包括：Guidewire工作流配置、保单数据提取和转换、PDF表单自动填充、扫描件管理、标准对齐检查、以及车险和健康险数据的自动化分析。

## 工作流程

1. **技术需求分析**: 理解业务需求和技术约束
2. **方案设计**: 设计技术实施方案
3. **系统集成**: 规划系统间集成点和接口
4. **数据处理**: 设计数据提取、转换、加载流程
5. **表单配置**: 配置电子表单和自动化规则
6. **标准对接**: 确保符合ACORD等行业标准
7. **测试验证**: 生成测试用例和验证方案
8. **部署指导**: 提供部署和运维建议

## 输入规范

接受自然语言描述的技术需求，包括：
- 目标系统（Guidewire/核心系统/数据平台）
- 业务场景（核保/理赔/保单服务）
- 集成需求（API/数据同步/单点登录）
- 数据格式和来源

## 输出规范

输出为结构化Markdown，包含：
- **技术方案**: 推荐的架构和实现方案
- **集成步骤**: 详细的集成实施步骤
- **注意事项**: 技术风险和规避措施
- **测试方案**: 验证测试用例

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| guidewire-core-workflow-a | Guidewire核心工作流A | 高 |
| guidewire-core-workflow-b | Guidewire核心工作流B | 高 |
| guidewire-hello-world | Guidewire入门 | 中 |
| analyzing-auto-insurance-data | 车险数据分析 | 高 |
| healthsim | 健康险模拟 | 高 |
| pdf | PDF处理 | 中 |
| pdf-form-filler | PDF表单填充 | 高 |
| acroform-fill | AcroForm填充 | 高 |
| scan-organizer | 扫描件管理 | 中 |
| standards-alignment | 标准对齐 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 配置Guidewire核保工作流，增加自动核保规则 | 工作流步骤；规则配置；触发条件 | normal |
| 2 | 设计车险理赔数据从核心系统到数据仓库的ETL流程 | 数据源映射；转换规则；调度方案 | normal |
| 3 | 生成ACORD标准保单数据交换接口方案 | ACORD标准映射；API设计；字段对照 | normal |
| 4 | 配置PDF投保单自动填充，从CRM系统取数 | 表单字段映射；数据源连接；异常处理 | normal |
| 5 | 系统版本不兼容导致集成失败 | 兼容性分析；升级建议；替代方案 | edge |
