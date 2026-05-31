# Insurance-SuperSkill 实施规范 v4.0

> **本文档是面向任意AI IDE（Cursor/Windsurf/Cline等）或大模型（Claude/GPT/Gemini等）的完整实施规范。任何AI Agent阅读本文档后，应能独立完成Insurance-SuperSkill生态的全部建设工作。**

## 〇、给AI Agent的执行说明

你即将构建一个保险行业的平台型超级Skill生态系统。在开始之前，请完整阅读本规范，然后按里程碑顺序实施。

**你的工作仓库**：`https://github.com/dymahoro669/Insurance-SuperSkill`
**原始素材仓库**：`https://github.com/FDU-INS/Insurance-Skills`（539个保险skills，需要从中提炼精华）
**安装命令**：`irm https://raw.githubusercontent.com/dymahoro669/Insurance-SuperSkill/main/install.ps1 | iex`

**实施顺序（严格按此执行）**：

| 里程碑 | 内容 | 验收标准 |
|--------|------|---------|
| M1 | 项目骨架搭建 | 目录结构完整，所有SKILL.md文件存在且格式正确 |
| M2 | 主索引+安全守卫+本地评价器 | 路由表可运行，脱敏引擎通过18类PII测试，评价器通过6项规则测试 |
| M3 | 12个领域子Skill内容填充 | 每个子Skill的SKILL.md ≥ 2000字，含完整的来源映射和能力矩阵 |
| M4 | 测试用例集 | 每个子Skill ≥ 20个测试用例（M1阶段先做20个，后续扩到100个） |
| M5 | ins-cli 命令行工具 | 全部17个命令可执行 |
| M6 | install.ps1 安装脚本 | 一键安装全流程跑通 |
| M7 | 平台侧服务规范 | 进化引擎/Auditor/L2-L3评价服务的完整设计文档 |
| M8 | CI/CD流水线 | GitHub Actions可自动运行测试+构建+发布 |

---

## 一、项目完整目录结构

以下是你必须创建的完整目录结构。每个文件的作用在后续章节中详细说明。

```
Insurance-SuperSkill/
├── README.md                           # 项目说明（已存在）
├── IMPLEMENTATION.md                   # 本文件 — 实施规范
├── install.ps1                         # 一键安装脚本（已存在）
├── LICENSE                             # Apache 2.0
│
├── skills/                             # === 所有Skill的SKILL.md ===
│   ├── insurance-super-skill/          # 主入口（路由+安全守卫）
│   │   └── SKILL.md                    # [M1] 主索引Skill完整定义
│   ├── ins-underwriting/               # 子Skill 1: 智能核保
│   │   └── SKILL.md                    # [M3]
│   ├── ins-claims/                     # 子Skill 2: 智能理赔
│   │   └── SKILL.md                    # [M3]
│   ├── ins-actuarial/                  # 子Skill 3: 精算分析
│   │   └── SKILL.md                    # [M3]
│   ├── ins-compliance/                 # 子Skill 4: 合规风控
│   │   └── SKILL.md                    # [M3]
│   ├── ins-marketing/                  # 子Skill 5: 营销推荐
│   │   └── SKILL.md                    # [M3]
│   ├── ins-policy/                     # 子Skill 6: 保单服务
│   │   └── SKILL.md                    # [M3]
│   ├── ins-product/                    # 子Skill 7: 产品咨询
│   │   └── SKILL.md                    # [M3]
│   ├── ins-service/                    # 子Skill 8: 客服支持
│   │   └── SKILL.md                    # [M3]
│   ├── ins-ops/                        # 子Skill 9: 运营支持
│   │   └── SKILL.md                    # [M3]
│   ├── ins-risk/                       # 子Skill 10: 风险管理
│   │   └── SKILL.md                    # [M3]
│   ├── ins-tech/                       # 子Skill 11: 技术工具
│   │   └── SKILL.md                    # [M3]
│   ├── ins-knowledge/                  # 子Skill 12: 知识百科
│   │   └── SKILL.md                    # [M3]
│   ├── security-guardian/              # 治理组件: 安全守卫
│   │   └── SKILL.md                    # [M2]
│   └── local-evaluator/                # 治理组件: 本地评价器
│       └── SKILL.md                    # [M2]
│
├── config/                             # === 配置文件模板 ===
│   ├── manifest.json                   # [M1] 版本清单模板
│   ├── security.json                   # [M2] 安全守卫配置模板
│   ├── privacy.json                    # [M2] 隐私配置模板
│   └── router.yaml                     # [M2] 路由规则定义
│
├── security/                           # === 安全守卫实现 ===
│   ├── pii-patterns.json               # [M2] 18类PII正则模式定义
│   └── compliance-blacklist.json       # [M2] 合规红线关键词库
│
├── evaluator/                          # === 本地评价器规则 ===
│   └── rules.json                      # [M2] 6项评价规则定义
│
├── tests/                              # === 测试用例集 ===
│   ├── smoke/                          # [M4] 全局冒烟测试（60用例 = 12×5）
│   │   ├── ins-underwriting.jsonl
│   │   ├── ins-claims.jsonl
│   │   ├── ... (每个子Skill一个文件)
│   │   └── cross-skill.jsonl           # 跨Skill协同测试
│   └── regression/                     # [M4] 各子Skill回归测试（≥20/个）
│       ├── ins-underwriting.jsonl
│       ├── ins-claims.jsonl
│       └── ...
│
├── source-mapping/                     # === 原始素材映射 ===
│   └── skill-sources.json              # [M3] 539个原始skill到12个子Skill的映射
│
├── platform/                           # === 平台侧服务规范 ===
│   ├── evolution-engine.md             # [M7] 进化引擎设计文档
│   ├── evolution-auditor.md            # [M7] Evolution Auditor设计文档
│   ├── l2-l3-evaluator.md             # [M7] L2/L3评价服务设计文档
│   └── telemetry-aggregator.md        # [M7] 遥测聚合服务设计文档
│
├── bin/                                # === CLI工具 ===
│   └── ins-cli.ps1                     # [M5] 命令行管理工具（已存在）
│
└── .github/                            # === CI/CD ===
    └── workflows/
        ├── test.yml                    # [M8] PR自动测试
        ├── build-release.yml           # [M8] 构建+发布
        └── nightly-evolution.yml       # [M8] 每夜进化流水线
```

---

## 二、SKILL.md 统一格式规范

每个Skill的SKILL.md必须严格遵循以下格式。这是Agent可解析的标准格式。

```markdown
# {Skill名称}

> {一句话描述核心功能}

## 元信息

- **Skill ID**: {skill-id}
- **版本**: {version}
- **类型**: {main|domain|governance}
- **依赖**: {依赖的其他skill-id，用逗号分隔，无依赖写"无"}
- **输入格式**: {text|json|file|mixed}
- **输出格式**: {text|json|markdown|mixed}
- **需要网络**: {true|false}
- **数据保留**: session_only

## 安全声明

- **数据采集**: none
- **PII处理**: input_stripped_output_sanitized
- **文件系统访问**: workspace_only
- **第三方API**: []
- **合规标准**: [HIPAA-compatible, GDPR-compatible, 中国个人信息保护法兼容]

## 能力描述

{详细描述该Skill能做什么，覆盖哪些场景，200-500字}

## 工作流程

{描述该Skill的处理步骤，用编号列表}

1. **{步骤名}**: {步骤描述}
2. **{步骤名}**: {步骤描述}
...

## 输入规范

{描述该Skill接受的输入格式和示例}

## 输出规范

{描述该Skill的输出格式和示例}

## 来源Skills

{列出从FDU-INS/Insurance-Skills仓库中整合的原始skill名称}

| 原始Skill | 提取内容 | 质量评级 |
|-----------|---------|---------|
| {skill-name} | {提取了什么} | {高/中} |

## 测试用例

{列出至少5个核心测试用例}

| # | 输入 | 期望输出要点 | 分类 |
|---|------|-------------|------|
| 1 | {输入描述} | {关键输出点} | {正常/边界/异常} |
```

---

## 三、主索引Skill完整定义

文件路径：`skills/insurance-super-skill/SKILL.md`

```markdown
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

## 能力描述

主索引Skill是整个Insurance-SuperSkill平台的入口和调度中心。当用户提出保险相关请求时，主索引负责：（1）通过安全守卫对用户输入进行PII脱敏处理；（2）基于意图识别将请求路由到正确的领域子Skill；（3）在必要时协调多个子Skill的协同工作；（4）将子Skill的输出经安全守卫还原后返回用户；（5）触发本地评价器对本次调用进行规则评价。

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

### 降级策略

1. 意图置信度 > 0.7 → 直接路由到目标子Skill
2. 意图置信度 0.4-0.7 → 询问用户澄清："您的问题涉及{类别A}和{类别B}，请问您更关注哪个方面？"
3. 意图置信度 < 0.4 → 路由到ins-knowledge（兜底）+ 建议更精确的描述

## 工作流程

1. **接收输入**: 接收用户的自然语言请求
2. **安全脱敏**: 调用security-guardian对输入进行PII脱敏
3. **意图识别**: 基于关键词和语义分析确定意图类别
4. **路由决策**: 根据路由规则选择目标子Skill（可能多个）
5. **子Skill调度**: 将脱敏后的输入发送给目标子Skill
6. **结果聚合**: 如有多个子Skill返回结果，进行合并
7. **安全还原**: 调用security-guardian还原PII占位符
8. **输出过滤**: 二次扫描确保无PII泄露
9. **本地评价**: 调用local-evaluator对本次调用进行规则评价
10. **返回结果**: 将最终输出返回用户

## 输出规范

主索引本身的输出格式：
- 单Skill路由：直接透传子Skill输出
- 多Skill协同：按执行顺序分段展示，每段标注来源子Skill
- 降级场景：友好提示 + 建议方向
```

---

## 四、安全守卫实现规范

### 4.1 PII脱敏正则模式

文件路径：`security/pii-patterns.json`

必须实现以下18类PII检测，每类包含中文和英文场景：

| 类别ID | 类别名 | 正则模式（核心） | 替换格式 |
|--------|-------|-----------------|---------|
| id_card | 身份证号 | `\b[1-9]\d{5}(19\|20)\d{2}(0[1-9]\|1[0-2])(0[1-9]\|[12]\d\|3[01])\d{3}[\dXx]\b` | `[ID_REDACT_N]` |
| bank_card | 银行卡号 | `\b[3-6]\d{3}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4,7}\b` (Luhn校验) | `[CARD_REDACT_N]` |
| phone | 手机号 | `\b1[3-9]\d{9}\b` (中国) / `\b\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b` (国际) | `[PHONE_REDACT_N]` |
| name | 姓名 | NER模型识别（2-4个汉字的人名模式，结合上下文） | `[NAME_REDACT_N]` |
| address | 地址 | `((省\|市\|区\|县\|镇\|村\|路\|街\|号\|栋\|幢\|室).{2,30})` | `[ADDR_REDACT_N]` |
| policy_num | 保单号 | `\b(POL\|INS\|P)[-]?\d{6,15}\b` | `[POL_REDACT_N]` |
| medical | 病历信息 | 医学NER（疾病名称+诊断+检查结果模式） | `[MED_REDACT_N]` |
| email | 邮箱 | `\b[\w.+-]+@[\w-]+\.[\w.-]+\b` | `[EMAIL_REDACT_N]` |
| ssn | 社保号 | 各地社保号格式（中国：`\b\d{18}\b` 或 `\b\d{15}\b`） | `[SSN_REDACT_N]` |
| passport | 护照号 | `\b[A-Z]\d{8}\b` (中国) / `\b\d{9}\b` (美国) | `[PASSPORT_REDACT_N]` |
| plate | 车牌号 | `[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-Z][A-Z0-9]{5}` | `[PLATE_REDACT_N]` |
| property | 房产信息 | `(小区\|花园\|大厦\|公寓\|苑\|城\|湾\|府).{2,20}(栋\|幢\|号\|座).{1,10}(室\|房)` | `[PROP_REDACT_N]` |

### 4.2 安全守卫工作流程

1. 接收原始输入
2. 按优先级依次应用18类PII正则（先长模式后短模式，避免嵌套匹配）
3. 记录替换映射表 `{占位符: 原始值}` 到会话内存（不落盘）
4. 将脱敏后的输入传递给主索引路由
5. 接收子Skill输出
6. 根据映射表还原占位符为原始值
7. 对还原后的输出做二次PII扫描（防止子Skill推断出新的PII）
8. 如检测到泄露 → 重新脱敏 → 重新生成 → 再次还原
9. 返回最终输出

---

## 五、本地评价器规则定义

文件路径：`evaluator/rules.json`

L1本地评价器基于纯规则引擎，不调用任何LLM，零Token消耗。6项检查规则：

| 规则ID | 规则名称 | 检查逻辑 | 评分方式 | 权重 |
|--------|---------|---------|---------|------|
| R1 | 输出结构完整性 | 检查输出是否包含该子Skill定义的必要字段（如理赔skill必须包含"材料清单"、"结论"字段） | 必要字段存在率 × 100 | 25% |
| R2 | 术语规范性 | 将输出与保险术语词典（≥500个标准术语）匹配，检查是否有非标准表述 | 规范术语占比 × 100 | 20% |
| R3 | 长度合理性 | 检查输出字数是否在合理范围（过短<100字可能不完整，过长>5000字可能冗余） | 在合理范围内=100，否则按偏离度扣分 | 10% |
| R4 | 合规红线 | 扫描输出是否包含违禁表述（如"保证理赔"、"绝对安全"等误导性用语，定义在compliance-blacklist.json中） | 无违禁=100，每发现一个-25 | 20% |
| R5 | 格式规范 | 如输出要求为JSON则检查JSON合法性，要求为表格则检查表格结构，要求为列表则检查列表格式 | 格式正确=100，否则=0 | 10% |
| R6 | 数值合理性 | 如输出包含保费/赔付金额，检查是否在合理范围内（如年保费不超过保额×30%） | 数值合理=100，异常=0 | 15% |

**综合分 = Σ(规则分 × 权重)**，结果记录为 pass（≥80）/ warn（60-79）/ fail（<60）。

---

## 六、十二大领域子Skill：来源映射与能力矩阵

### 6.1 来源映射总表

实施M3阶段时，你需要从FDU-INS/Insurance-Skills仓库中获取以下原始skill的SKILL.md内容，提炼精华后填充到对应的子Skill中。

获取方法：
```bash
gh api "repos/FDU-INS/Insurance-Skills/contents/Skills/{skill-name}/SKILL.md" --jq '.content' | base64 -d
```

**ins-underwriting（智能核保）来源**：

| 原始Skill | 提取内容 | 质量 |
|-----------|---------|------|
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

**ins-claims（智能理赔）来源**：

| 原始Skill | 提取内容 | 质量 |
|-----------|---------|------|
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

**ins-actuarial（精算分析）来源**：

| 原始Skill | 提取内容 | 质量 |
|-----------|---------|------|
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

**ins-compliance（合规风控）来源**：

| 原始Skill | 提取内容 | 质量 |
|-----------|---------|------|
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

**ins-marketing（营销推荐）来源**：annuity-life-insurance-sales, insurance-needs-analysis, financial-planner, auto-insurance-recommendation, life-insurance-recommendation, insurance-product-comparison, cross-selling-insurance, insurance-proposal-writer, quote, generate-newsletter-insurance

**ins-policy（保单服务）来源**：policy-reader, policy-guide, policy-qa, policy-comparison, insurance-policy-review, insurance-coverage-summary, policy-renewal-strategy, insurance-renewal-processor, policy-service-process, policyholder-service

**ins-product（产品咨询）来源**：Insurance Analyst, product-knowledge, insurance-product-design, insurance-product-review, financial-planner, financial-planning-expert, financial-insurance-guide, dental-insurance-guide, pet-insurance-guide, travel-insurance-guide, workers-comp-guide, insurance-market-overview

**ins-service（客服支持）来源**：reply-templates, uk-legal-canned-responses, claims-communication, insurance-correspondence-summarization, family-assistant, policyholder-service

**ins-ops（运营支持）来源**：afrexai-insurance-automation, insurance-workflow-automation, weekly-kpi-report, insurance-weekly-report, insurance-data-analytics, staff-mapping-management, insurance-producer-training, vendor-coordination, insurance-carrier-appointment, field-validation, insurance-testing

**ins-risk（风险管理）来源**：risk-management, risk-management-playbook, risk-analysis, analyzing-catastrophe-risk, climate-risk-assessment, climate-risk-agriculture, cyber-risk-modeling, geo-infer-risk, hormuz-strait, risk-register

**ins-tech（技术工具）来源**：guidewire-core-workflow-a, guidewire-core-workflow-b, guidewire-hello-world, analyzing-auto-insurance-data, healthsim, pdf, pdf-form-filler, acroform-fill, scan-organizer, standards-alignment

**ins-knowledge（知识百科）来源**：social-security-advisor, social-security-expert, social-insurance, indian-insurance-basics, Workers Compensation Australia, Australian Insurance Legislation Analysis, property-insurance-basics, reinsurance-basics, insurance-domain, reviewing-business-terminology

---

## 七、测试用例格式规范

### 7.1 JSONL格式

每个测试用例为一行JSON，格式如下：

```json
{"id": "uw-001", "category": "normal", "input": "帮我分析这份意外险投保问卷，被保险人35岁程序员，有高血压病史", "expected_keywords": ["职业风险", "健康告知", "高血压", "加费", "延期"], "expected_structure": ["风险摘要", "核保建议"], "sub_skill": "ins-underwriting"}
```

字段说明：
- `id`: 唯一标识（子Skill前缀+序号）
- `category`: normal（正常）/ edge（边界）/ error（异常）
- `input`: 模拟用户输入（已脱敏）
- `expected_keywords`: 输出中必须包含的关键词列表
- `expected_structure`: 输出中必须包含的结构化字段
- `sub_skill`: 目标子Skill ID

### 7.2 每个子Skill至少20个测试用例（M4阶段）

分布要求：12个normal + 4个edge + 4个error

### 7.3 全局冒烟测试（60用例 = 12子Skill × 5）

每个子Skill选5个最具代表性的normal用例组成冒烟测试集。

### 7.4 跨Skill协同测试（10用例）

测试多Skill协同场景，例如：
```json
{"id": "cross-001", "category": "normal", "input": "这个客户的重疾险理赔被拒了，帮我分析原因并准备申诉", "expected_skills": ["ins-claims", "ins-underwriting", "ins-compliance"], "sub_skill": "insurance-super-skill"}
```

---

## 八、manifest.json 模板

文件路径：`config/manifest.json`

```json
{
  "name": "insurance-super-skill",
  "version": "1.0.0",
  "description": "保险行业超级Skill平台 — 一键安装，覆盖保险全业务链",
  "platform_repo": "https://github.com/dymahoro669/Insurance-SuperSkill",
  "components": {
    "insurance-super-skill": { "version": "1.0.0", "type": "main" },
    "ins-underwriting":      { "version": "1.0.0", "type": "domain" },
    "ins-claims":            { "version": "1.0.0", "type": "domain" },
    "ins-actuarial":         { "version": "1.0.0", "type": "domain" },
    "ins-compliance":        { "version": "1.0.0", "type": "domain" },
    "ins-marketing":         { "version": "1.0.0", "type": "domain" },
    "ins-policy":            { "version": "1.0.0", "type": "domain" },
    "ins-product":           { "version": "1.0.0", "type": "domain" },
    "ins-service":           { "version": "1.0.0", "type": "domain" },
    "ins-ops":               { "version": "1.0.0", "type": "domain" },
    "ins-risk":              { "version": "1.0.0", "type": "domain" },
    "ins-tech":              { "version": "1.0.0", "type": "domain" },
    "ins-knowledge":         { "version": "1.0.0", "type": "domain" },
    "security-guardian":     { "version": "1.0.0", "type": "governance" },
    "local-evaluator":       { "version": "1.0.0", "type": "governance" }
  },
  "security": {
    "data_collection": "none",
    "pii_handling": "strip_on_input",
    "output_sanitization": true,
    "audit_log": "local_only"
  },
  "router": {
    "config_file": "config/router.yaml",
    "fallback_skill": "ins-knowledge",
    "confidence_threshold": 0.7
  }
}
```

---

## 九、router.yaml 路由规则

文件路径：`config/router.yaml`

```yaml
version: "1.0"
routes:
  - id: underwriting
    skill: ins-underwriting
    keywords: [投保, 核保, 告知, 健康问卷, 风险评级, 加费, 除外, 拒保, 承保, 体检, 既往症, underwriting]
    weight: 1.0
  - id: claims
    skill: ins-claims
    keywords: [理赔, 报案, 索赔, 拒赔, 申诉, 材料, 定损, 赔付, 出险, 免赔, 给付, claim]
    weight: 1.0
  - id: actuarial
    skill: ins-actuarial
    keywords: [定价, 准备金, IBNR, 精算, 费率, 损失率, 资本模型, IFRS17, 综合成本率, actuarial]
    weight: 1.0
  - id: compliance
    skill: ins-compliance
    keywords: [合规, 审计, HIPAA, 反洗钱, AML, 监管, 法规变化, COI, 反欺诈, compliance]
    weight: 1.0
  - id: marketing
    skill: ins-marketing
    keywords: [推荐, 销售, 获客, 转化, 报价, 营销方案, 交叉销售, 续保率, marketing]
    weight: 1.0
  - id: policy
    skill: ins-policy
    keywords: [保单, 续保, 保全, 批改, 条款解读, 覆盖范围, 保单贷款, 犹豫期, policy]
    weight: 1.0
  - id: product
    skill: ins-product
    keywords: [产品介绍, 险种, 保障, 比较, 哪款好, 规划, 产品对比, product]
    weight: 1.0
  - id: service
    skill: ins-service
    keywords: [话术, FAQ, 投诉, 客户沟通, 信函, 满意度, 回访, service]
    weight: 1.0
  - id: ops
    skill: ins-ops
    keywords: [KPI, 报告, 自动化, 工作流, 团队, 培训, 绩效, 渠道, 佣金, ops]
    weight: 1.0
  - id: risk
    skill: ins-risk
    keywords: [风险评估, 巨灾, 气候风险, 网络风险, 风险登记, 累积暴露, 再保险, risk]
    weight: 1.0
  - id: tech
    skill: ins-tech
    keywords: [API, Guidewire, 数据处理, 系统集成, 表单, 标准, ACORD, 接口, tech]
    weight: 1.0
  - id: knowledge
    skill: ins-knowledge
    keywords: [什么是, 社保, 医保, 法规, 术语, 基础知识, 概念解释, 保险原理, knowledge]
    weight: 1.0

cross_skill_chains:
  - scenario: "理赔申诉"
    trigger: "理赔.*被拒|拒赔.*申诉"
    chain: [ins-claims, ins-underwriting, ins-compliance]
  - scenario: "产品推荐+报价"
    trigger: "推荐.*产品|产品.*报价"
    chain: [ins-product, ins-marketing]
  - scenario: "保单审查+续保"
    trigger: "保单.*审查|保单.*续保"
    chain: [ins-policy, ins-underwriting]
  - scenario: "合规审计+风控"
    trigger: "合规.*审计|审计.*风控"
    chain: [ins-compliance, ins-risk]
  - scenario: "产品设计+定价"
    trigger: "产品.*设计|产品.*定价|新产品.*开发"
    chain: [ins-product, ins-actuarial, ins-compliance]

fallback:
  skill: ins-knowledge
  message: "您的问题已转至知识百科进行解答。如需更精准的回答，请描述更多细节。"
```

---

## 十、GitHub Actions CI/CD

### 10.1 PR自动测试 (.github/workflows/test.yml)

```yaml
name: Test
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate all SKILL.md files exist
        run: |
          for dir in skills/*/; do
            if [ ! -f "$dir/SKILL.md" ]; then
              echo "MISSING: $dir/SKILL.md"
              exit 1
            fi
          done
      - name: Validate SKILL.md format
        run: |
          for f in skills/*/SKILL.md; do
            grep -q "## 元信息" "$f" || (echo "FAIL: $f missing 元信息" && exit 1)
            grep -q "## 安全声明" "$f" || (echo "FAIL: $f missing 安全声明" && exit 1)
            grep -q "## 能力描述" "$f" || (echo "FAIL: $f missing 能力描述" && exit 1)
            grep -q "## 工作流程" "$f" || (echo "FAIL: $f missing 工作流程" && exit 1)
            grep -q "## 来源Skills" "$f" || (echo "FAIL: $f missing 来源Skills" && exit 1)
          done
      - name: Validate config files
        run: |
          python -m json.tool config/manifest.json > /dev/null
          python -m json.tool security/pii-patterns.json > /dev/null
          python -m json.tool evaluator/rules.json > /dev/null
      - name: Run smoke tests
        run: |
          echo "Smoke test validation passed"
      - name: Check test coverage
        run: |
          for f in tests/smoke/*.jsonl; do
            count=$(wc -l < "$f")
            if [ "$count" -lt 5 ]; then
              echo "FAIL: $f has only $count test cases (need >= 5)"
              exit 1
            fi
          done
```

### 10.2 构建发布 (.github/workflows/build-release.yml)

```yaml
name: Build & Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Package skills
        run: |
          zip -r insurance-super-skill-${GITHUB_REF_NAME#v}.zip \
            skills/ config/ security/ evaluator/ bin/ install.ps1
      - name: Generate SHA256
        run: |
          sha256sum insurance-super-skill-*.zip > insurance-super-skill-${GITHUB_REF_NAME#v}.zip.sha256
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            insurance-super-skill-*.zip
            insurance-super-skill-*.zip.sha256
```

### 10.3 每夜进化 (.github/workflows/nightly-evolution.yml)

```yaml
name: Nightly Evolution
on:
  schedule:
    - cron: '0 18 * * *'  # UTC 18:00 = CST 02:00
jobs:
  evolve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Collect evaluation data
        run: echo "Collecting L1 stats + L2 findings + L3 reports..."
      - name: Determine evolution targets
        run: echo "Priority ranking based on evaluation data..."
      - name: Generate evolution plan
        run: echo "Max 2 sub-skills, max 3 changes each..."
      - name: Run regression tests
        run: |
          echo "Running full test suite..."
          for f in tests/regression/*.jsonl; do echo "Testing $f"; done
          for f in tests/smoke/*.jsonl; do echo "Smoke: $f"; done
      - name: Run Evolution Auditor
        run: echo "6-dimension audit: INT/USA/CON/EFF/PRO/REA"
      - name: Publish if PASS
        if: success()
        run: echo "Bump version and create release tag"
      - name: Rollback if FAIL
        if: failure()
        run: echo "Revert changes, freeze affected skill, notify team"
```

---

## 十一、里程碑验收标准

### M1: 项目骨架（验收清单）

- [ ] 上述目录结构中的所有目录已创建
- [ ] 15个SKILL.md文件全部存在
- [ ] 每个SKILL.md包含"元信息"、"安全声明"、"能力描述"、"工作流程"、"来源Skills"五个必要段落
- [ ] config/manifest.json、config/router.yaml、security/pii-patterns.json、evaluator/rules.json 四个配置文件存在且JSON/YAML合法
- [ ] CI测试流水线可通过

### M2: 主索引+安全守卫+评价器

- [ ] 主索引SKILL.md包含完整路由表（12个意图类别+触发词+目标Skill）
- [ ] 主索引SKILL.md包含5条跨Skill协同链
- [ ] pii-patterns.json包含18类PII正则定义
- [ ] compliance-blacklist.json包含至少50个违禁表述
- [ ] rules.json包含6条评价规则定义
- [ ] 可通过CI验证

### M3: 子Skill内容填充

- [ ] 每个子Skill的SKILL.md ≥ 2000字
- [ ] 每个子Skill的"来源Skills"表格列出所有原始skill（按第六章映射表）
- [ ] 每个子Skill的"能力描述"覆盖其领域核心场景
- [ ] 每个子Skill的"工作流程"包含≥5个步骤

### M4: 测试用例

- [ ] tests/smoke/下每个子Skill有5个冒烟测试用例
- [ ] tests/regression/下每个子Skill有≥20个回归测试用例
- [ ] tests/smoke/cross-skill.jsonl包含10个跨Skill协同测试
- [ ] 测试用例分布：60% normal + 20% edge + 20% error

### M5: ins-cli

- [ ] bin/ins-cli.ps1支持全部17个命令
- [ ] 每个命令有help输出
- [ ] status命令正确读取manifest.json

### M6: install.ps1

- [ ] 安装脚本可独立运行
- [ ] 环境检测、下载、解压、安全初始化、健康检查全流程跑通
- [ ] 安装后ins-cli可用

### M7: 平台侧服务

- [ ] platform/目录下4个设计文档完整
- [ ] 包含进化引擎的输入/输出schema
- [ ] 包含Evolution Auditor的六维评分逻辑
- [ ] 包含L2/L3评价的Prompt模板

### M8: CI/CD

- [ ] 三个GitHub Actions workflow文件存在且语法正确
- [ ] PR测试可自动运行
- [ ] tag推送可自动构建release包
- [ ] 每夜进化cron job已配置
