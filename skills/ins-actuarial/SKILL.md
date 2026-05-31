# 精算分析 Skill

> 保险精算专业分析与建模支持，覆盖定价、准备金、资本模型和IFRS17。

## 元信息

- **Skill ID**: ins-actuarial
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

精算分析Skill为保险公司提供专业级精算支持，覆盖产品定价、准备金评估、资本建模和财务报告。核心能力包括：毛保费与风险保费分解、费用加载分析、链梯法/Bornhuetter-Ferguson法/随机模型准备金计算、IBNR估计、综合成本率分析、VaR/CTE风险度量、蒙特卡洛模拟、IFRS17计量模型构建、以及投资组合评估。

## 工作流程

1. **需求识别**: 确定精算任务类型（定价/准备金/资本/财务报告）
2. **数据准备**: 整理历史赔付数据、保费数据、暴露数据
3. **方法选择**: 根据数据质量和业务场景选择适当的精算方法
4. **模型构建**: 构建精算模型并设定假设参数
5. **计算执行**: 执行精算计算，生成初步结果
6. **敏感性分析**: 对关键假设进行敏感性测试
7. **结果验证**: 使用替代方法或历史数据验证结果合理性
8. **报告输出**: 生成结构化的精算分析报告

## 输入规范

接受自然语言描述的精算需求，包括：
- 分析类型（定价/准备金/资本/IFRS17）
- 历史数据摘要（赔付率、费用率、增长率）
- 业务参数（保额、免赔额、等待期等）
- 假设条件（贴现率、通胀率、趋势因子）

## 输出规范

输出为结构化Markdown，包含：
- **计算方法**: 使用的精算方法和公式
- **假设说明**: 关键假设及其依据
- **结果摘要**: 核心计算结果
- **敏感性分析**: 不同假设下的结果变化
- **风险提示**: 模型局限性和不确定性说明

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| actuarial-modeling | 精算建模7阶段审查+自修复验证 | 高 |
| pricing-actuary | 定价精算（毛保费/风险保费/费用加载） | 高 |
| reserving-actuary | 准备金精算（链梯法/B-F法/IBNR） | 高 |
| risk-management-actuary | 风险管理精算（VaR/CTE/蒙特卡洛） | 高 |
| analyzing-loss-reserves | 损失准备金充足性评估 | 高 |
| analyzing-premium-pricing | 精算定价分析 | 高 |
| analyzing-property-casualty-lines | P&C业务线分析 | 高 |
| analyzing-insurance-financials | 保险公司财务分析 | 高 |
| analyzing-insurance-investments | 投资组合评估 | 高 |
| takaful-ifrs17 | 伊斯兰保险IFRS 17 | 高 |
| ifrs17-specialist | IFRS 17专家 | 中 |
| Corp Finance Tools - Specialty & Regulatory | 94个专业金融计算工具 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 计算某车险产品定价：历史赔付率65%，费用率25%，目标利润率5% | 风险保费计算；费用加载；最终毛保费 | normal |
| 2 | 使用链梯法估计未决赔款准备金 | 发展因子计算；终极损失估计；IBNR计算 | normal |
| 3 | IFRS17计量：一组寿险合同的履约现金流现值 | 折现现金流计算；合同服务边际；损失组成部分 | normal |
| 4 | 使用蒙特卡洛模拟计算99.5% VaR | 模拟路径设定；损失分布；VaR和CTE结果 | normal |
| 5 | 输入数据明显异常（赔付率>100%且持续下降） | 数据质量警告；建议核查数据源 | edge |
