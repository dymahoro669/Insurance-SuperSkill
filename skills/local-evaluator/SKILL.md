# 本地评价器 Skill

> LLM-as-Judge 智能评价器，调用大模型对 Skill 输出进行多维度质量评估。

## 元信息

- **Skill ID**: local-evaluator
- **版本**: 1.0.0
- **类型**: governance
- **依赖**: 无
- **输入格式**: json
- **输出格式**: json
- **需要网络**: true
- **数据保留**: session_only

## 安全声明

- **数据采集**: none
- **PII处理**: input_stripped_output_sanitized
- **文件系统访问**: workspace_only
- **第三方API**: [大模型推理接口]
- **合规标准**: [HIPAA-compatible, GDPR-compatible, 中国个人信息保护法兼容]

## 能力描述

本地评价器是 Insurance-SuperSkill 平台的智能质量评价组件，采用 **LLM-as-Judge** 架构。每次 Skill 调用完成后，评价器将 Skill 的输出内容、原始用户输入、以及结构化评价 Prompt 一起提交给大模型，由大模型从多个维度进行语义级质量判断。相比规则引擎，LLM 评价器能够识别深层逻辑问题、语义不一致、专业深度不足等规则难以捕捉的质量缺陷。评价结果用于实时监控 Skill 质量、触发进化流程和保障输出可靠性。

## 工作流程

1. **接收评价请求**: 接收主索引发送的评价请求（包含用户原始输入、Skill ID、Skill 输出内容）
2. **加载评价模板**: 从 `evaluator/rules.json` 加载该 Skill 对应的评价维度模板
3. **构建评价 Prompt**: 组装结构化评价 Prompt（含角色定义、评价维度、评分标准、输出格式）
4. **调用 LLM 评价**: 将 Prompt 提交给大模型，获取语义级质量判断
5. **解析评分结果**: 解析 LLM 返回的结构化评分 JSON
6. **规则预检辅助**（可选）: 对明显问题（如输出为空、格式完全错误）进行快速规则预检
7. **综合判定**: 根据 LLM 评分结果输出 pass / warn / fail 评级
8. **结果输出**: 返回评分详情和评价建议

## 评价维度（8维）

| 维度ID | 维度名称 | 评价内容 | 权重 |
|--------|---------|---------|------|
| D1 | 输出结构完整性 | 是否包含该 Skill 要求的必要结构和字段 | 20% |
| D2 | 术语规范性 | 保险专业术语使用是否准确、标准 | 15% |
| D3 | 长度合理性 | 内容详略是否得当，无冗余或遗漏 | 10% |
| D4 | 合规红线 | 是否存在误导性、违规或违禁表述 | 20% |
| D5 | 格式规范 | 输出格式是否符合要求（表格/列表/JSON等） | 10% |
| D6 | 数值合理性 | 保费、赔付金额等数值是否在合理区间 | 10% |
| D7 | 语义一致性 | 输出是否真正回答了用户提出的问题 | 10% |
| D8 | 逻辑自洽性 | 输出内部是否存在自相矛盾 | 5% |

## 输入规范

JSON 格式输入：
```json
{
  "skill_id": "ins-claims",
  "user_input": "我的意外险理赔需要哪些材料？",
  "skill_output": "Skill 生成的输出文本",
  "expected_format": "markdown",
  "context": {
    "conversation_history": [],
    "route_chain": ["insurance-super-skill", "ins-claims"]
  }
}
```

## 输出规范

JSON 格式输出：
```json
{
  "overall": "pass",
  "score": 85,
  "evaluator": "llm-judge-v1",
  "dimensions": {
    "D1": { "score": 90, "reason": "包含材料清单、结论、时间预估三个必要字段" },
    "D2": { "score": 85, "reason": "术语基本规范，'免赔额'使用正确" },
    "D3": { "score": 95, "reason": "长度适中，约800字" },
    "D4": { "score": 100, "reason": "未发现违禁表述" },
    "D5": { "score": 90, "reason": "Markdown 格式正确，表格结构完整" },
    "D6": { "score": 80, "reason": "赔付金额计算逻辑合理" },
    "D7": { "score": 85, "reason": "回答了用户问题，但可更具体" },
    "D8": { "score": 90, "reason": "内部逻辑一致" }
  },
  "improvement_suggestions": [
    "建议补充具体材料提交方式（线上/线下）",
    "可增加理赔进度查询渠道说明"
  ]
}
```

## 评分标准

- **pass（通过）**: 综合分 ≥ 80，所有维度无 fail
- **warn（警告）**: 综合分 60-79，或某一维度得分 < 60
- **fail（失败）**: 综合分 < 60，或 D4（合规红线）得分 < 60，或 D7（语义一致性）得分 < 40

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| evaluator-engine | 评价引擎框架 | 高 |
| quality-checker | 质量检查通用框架 | 高 |
| llm-as-judge | LLM 评价方法论文 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 完整合规的理赔输出，回答了用户问题 | overall: pass; D4=100; D7≥80 | normal |
| 2 | 包含"保证理赔"的输出 | D4低分（<60）; overall: fail | error |
| 3 | 缺少"材料清单"字段的理赔输出 | D1低分; overall: warn | edge |
| 4 | 包含明显异常数值（年保费>保额） | D6低分; overall: warn | edge |
| 5 | 输出仅10个字，未回答用户问题 | D3=0; D7=0; overall: fail | error |
| 6 | 输出内部逻辑矛盾（先说赔付后说拒赔） | D8低分; overall: warn | edge |
| 7 | 格式完全错误（要求JSON但返回纯文本） | D5=0; overall: warn | error |
