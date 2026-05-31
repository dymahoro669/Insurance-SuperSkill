# Insurance-SuperSkill 主索引

> 保险行业超级Skill平台主入口，负责意图识别、领域路由、安全防护和结果聚合。

## 元信息

- **Skill ID**: insurance-super-skill
- **版本**: 1.0.0
- **类型**: main
- **依赖**: ins-underwriting, ins-claims, ins-actuarial, ins-compliance, ins-marketing, ins-policy, ins-product, ins-service, ins-ops, ins-risk, ins-tech, ins-knowledge, security-guardian, local-evaluator
- **输入格式**: text
- **输出格式**: text
- **需要网络**: false
- **数据保留**: session_only

## 安全声明

- **数据采集**: none
- **PII处理**: input_stripped_output_sanitized
- **文件系统访问**: workspace_only
- **第三方API**: []
- **合规标准**: [HIPAA-compatible, GDPR-compatible, 中国个人信息保护法兼容]

## 能力描述

主索引Skill是整个Insurance-SuperSkill平台的入口和调度中心。当用户提出保险相关请求时，主索引负责：（1）通过安全守卫对用户输入进行PII脱敏处理；（2）基于意图识别将请求路由到正确的领域子Skill；（3）在必要时协调多个子Skill的协同工作；（4）将子Skill的输出经安全守卫还原后返回用户；（5）触发本地评价器调用大模型对本次输出进行语义级质量评价。

## 路由规则

### 意图分类 → 子Skill映射

| 意图类别 | 触发关键词 | 目标子Skill |
|---------|-----------|------------|
| 核保 | 投保,核保,告知,健康问卷,风险评级,加费,除外,拒保,承保,体检,既往症 | ins-underwriting |
| 理赔 | 理赔,报案,索赔,拒赔,申诉,材料,定损,赔付,出险,免赔,给付 | ins-claims |
| 精算 | 定价,准备金,IBNR,精算,费率,损失率,资本模型,IFRS17,综合成本率 | ins-actuarial |
| 合规 | 合规,审计,HIPAA,反洗钱,AML,监管,法规变化,COI,反欺诈 | ins-compliance |
| 营销 | 推荐,销售,获客,转化,报价,营销方案,交叉销售,续保率,客户画像 | ins-marketing |
| 保单 | 保单,续保,保全,批改,条款解读,覆盖范围,保单贷款,犹豫期 | ins-policy |
| 产品 | 产品介绍,险种,保障,比较,哪款好,规划,产品对比,产品评测 | ins-product |
| 客服 | 话术,FAQ,投诉,客户沟通,信函,满意度,回访,标准回答 | ins-service |
| 运营 | KPI,报告,自动化,工作流,团队,培训,绩效,渠道,佣金 | ins-ops |
| 风险 | 风险评估,巨灾,气候风险,网络风险,风险登记,累积暴露,再保险 | ins-risk |
| 技术 | API,Guidewire,数据处理,系统集成,表单,标准,ACORD,接口 | ins-tech |
| 知识 | 什么是,社保,医保,法规,术语,基础知识,概念解释,保险原理 | ins-knowledge |

### 跨Skill协同规则

当用户请求涉及多个领域时，按以下链条协同：

| 场景示例 | 协同链 |
|---------|--------|
| 理赔被拒+申诉 | ins-claims → ins-underwriting → ins-compliance |
| 产品推荐+报价 | ins-product → ins-marketing |
| 保单审查+续保 | ins-policy → ins-underwriting |
| 合规审计+风控 | ins-compliance → ins-risk |
| 新产品设计+定价 | ins-product → ins-actuarial → ins-compliance |

### 意图置信度计算

**执行主体**：由 `insurance-super-skill` **内部**的**意图识别引擎**负责计算，不是独立的 Skill。

> 意图识别是路由决策的前置步骤，天然属于主索引的职责范围。将其内嵌在主索引中可避免每轮路由产生额外的 Skill 调用开销，同时意图识别依赖的路由表（`router.yaml`）和会话状态均由主索引持有，耦合度最低。

意图置信度采用 **多信号加权融合** 方法，综合关键词匹配、语义相似度和上下文信息：

```
意图置信度 = softmax(各意图原始得分)

原始得分(skill_i) = α·关键词得分 + β·语义相似度 + γ·上下文加分

其中：
- α = 0.5（关键词权重）
- β = 0.4（语义权重）
- γ = 0.1（上下文权重）

1. 关键词得分 = Σ(命中关键词权重) / 该skill关键词总数
   - 精确匹配（如"核保"）：权重 1.0
   - 模糊匹配（如"保险"）：权重 0.3
   - 未命中：0

2. 语义相似度 = cos(用户输入向量, skill描述向量)
   - 使用预训练语言模型编码
   - 取值范围 [-1, 1]，映射到 [0, 1]

3. 上下文加分：
   - 跨Skill场景命中：相关skill +0.2
   - 对话历史一致性：延续上一轮skill +0.15
   - 用户确认过的意图：+0.3

示例：
用户输入"理赔被拒了，想申诉"
- ins-claims: 关键词命中"理赔"(1.0) → 得分 0.9 → 置信度 0.42
- ins-underwriting: 跨场景"理赔申诉"加分 → 得分 0.6 → 置信度 0.28
- ins-compliance: 跨场景"理赔申诉"加分 → 得分 0.5 → 置信度 0.23
- 其他: 得分接近 0

→ 最高置信度 claims=0.42 < 0.7，但命中跨Skill协同场景
→ 触发协同链：ins-claims → ins-underwriting → ins-compliance
```

### 降级策略

1. **直接路由**：最高意图置信度 > 0.7 → 直接路由到目标子Skill
2. **澄清询问**：最高意图置信度 0.4-0.7，或 Top2 差距 < 0.2 → 询问用户澄清："您的问题涉及{类别A}和{类别B}，请问您更关注哪个方面？"
3. **兜底路由**：最高意图置信度 < 0.4 → 路由到 ins-knowledge + 建议更精确的描述

## 工作流程

1. **接收输入**: 接收用户的自然语言请求
2. **安全脱敏**: 调用security-guardian对输入进行PII脱敏
3. **意图识别**: 主索引内部的意图识别引擎加载 `router.yaml`，对用户输入执行关键词匹配、语义相似度计算和上下文加分，通过 softmax 归一化得到各子 Skill 的意图置信度
4. **路由决策**: 根据路由规则选择目标子Skill（可能多个）
5. **子Skill调度**: 将脱敏后的输入发送给目标子Skill
6. **结果聚合**: 如有多个子Skill返回结果，进行合并
7. **安全还原**: 调用security-guardian还原PII占位符
8. **输出过滤**: 二次扫描确保无PII泄露
9. **本地评价**: 调用local-evaluator，由大模型对输出进行8维度语义质量评价
10. **返回结果**: 将最终输出返回用户

## 来源Skills

主索引Skill本身不直接来源于FDU-INS仓库中的原始Skill，而是作为平台架构层整合以下治理组件：

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| security-guardian | PII脱敏引擎架构 | 高 |
| local-evaluator | LLM-as-Judge智能评价框架 | 高 |
| router-engine | 意图识别与路由框架 | 高 |

## 测试用例

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | 我想投保一份重疾险 | 路由到ins-underwriting | normal |
| 2 | 我的理赔被拒了，想申诉 | 跨Skill协同链：ins-claims→ins-underwriting→ins-compliance | normal |
| 3 | 保险是什么东西 | 路由到ins-knowledge（兜底） | normal |
| 4 | 帮我看看保单还要不要续保 | 路由到ins-policy，可能协同ins-underwriting | normal |
| 5 | 模糊输入："那个...保险的事" | 意图置信度低，路由到ins-knowledge+建议更精确描述 | edge |

## 输出规范

主索引本身的输出格式：
- 单Skill路由：直接透传子Skill输出
- 多Skill协同：按执行顺序分段展示，每段标注来源子Skill
- 降级场景：友好提示 + 建议方向
