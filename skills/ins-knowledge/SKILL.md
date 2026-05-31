# 知识百科 Skill

> 保险行业基础知识问答与概念解释，覆盖术语、法规、原理和社保医保。

## 元信息

- **Skill ID**: ins-knowledge
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

知识百科Skill是Insurance-SuperSkill平台的兜底Skill，负责回答保险基础概念、术语解释、法规解读、社保医保知识和保险原理等通用问题。当用户问题无法明确路由到其他领域子Skill时，由知识百科提供准确、通俗的解答。核心能力包括：保险术语词典查询、保险法及相关法规解读、社保和医保政策解释、再保险基础知识、财产保险基础、以及各国保险制度对比。

## 工作流程

1. **问题理解**: 解析用户问题的核心概念
2. **知识检索**: 从知识库中检索相关知识点
3. **概念解释**: 用通俗语言解释专业概念
4. **关联知识**: 提供相关的扩展知识点
5. **示例说明**: 通过案例帮助理解
6. **来源标注**: 标注信息来源和适用范围
7. **输出**: 生成结构化的知识回答

## 输入规范

接受自然语言描述的知识查询，包括：
- 概念名称（如"什么是现金价值"）
- 法规条款（如"保险法第16条是什么"）
- 对比问题（如"社保和商保的区别"）
- 原理问题（如"大数定律在保险中的应用"）

## 输出规范

输出为结构化Markdown，包含：
- **概念解释**: 核心定义和通俗解释
- **适用场景**: 该概念在哪些场景中使用
- **示例说明**: 帮助理解的案例
- **相关概念**: 关联的知识点链接

## 来源Skills

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| social-security-advisor | 社保顾问 | 高 |
| social-security-expert | 社保专家 | 高 |
| social-insurance | 社会保险 | 高 |
| indian-insurance-basics | 印度保险基础 | 中 |
| Workers Compensation Australia | 澳洲工伤赔偿 | 中 |
| Australian Insurance Legislation Analysis | 澳洲保险法规 | 中 |
| property-insurance-basics | 财产保险基础 | 高 |
| reinsurance-basics | 再保险基础 | 高 |
| insurance-domain | 保险领域知识 | 高 |
| reviewing-business-terminology | 商业术语审查 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 什么是保险的"现金价值"？ | 定义解释；形成原因；与保费的区别；退保关系 | normal |
| 2 | 社保和医保有什么区别？ | 概念对比；覆盖范围；缴费方式；适用场景 | normal |
| 3 | 解释保险中的"大数定律" | 原理说明；保险应用；实际案例 | normal |
| 4 | 保险法第16条关于如实告知的规定 | 条款内容；法律后果；实务应用 | normal |
| 5 | 什么是再保险？有什么作用？ | 定义；分保方式；风险分散；行业应用 | normal |
