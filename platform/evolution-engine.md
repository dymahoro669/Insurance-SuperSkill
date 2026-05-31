# 进化引擎设计文档

> Insurance-SuperSkill 平台的自动进化系统，负责驱动 Skill 的持续迭代与质量提升。

## 1. 设计目标

进化引擎是 Insurance-SuperSkill 平台的"自修复"核心，通过持续收集评价数据、识别质量短板、自动生成进化计划并验证，实现 Skill 生态的自动化演进。

核心目标：
- **零人工干预**：评价→识别→计划→验证→发布全流程自动化
- **质量可追踪**：每次进化前后的评分变化可量化对比
- **风险可控**：进化失败自动回滚，避免质量退化
- **收敛稳定**：避免频繁无意义改动，确保进化方向正确

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      进化引擎 (Evolution Engine)              │
├─────────────────────────────────────────────────────────────┤
│  输入层 → 分析层 → 决策层 → 执行层 → 验证层 → 发布层          │
│                                                             │
│  [L1数据]   [优先级]   [计划]    [改动]   [测试]   [版本]    │
│  [L2发现]   [目标]     [限流]    [构建]   [审计]   [标签]    │
│  [L3报告]   [影响]     [策略]    [验证]   [报告]   [通知]    │
│  [遥测]     [预测]     [选择]    [回归]   [评分]   [归档]    │
└─────────────────────────────────────────────────────────────┘
```

## 3. 输入 Schema

### 3.1 L1 统计数据

```json
{
  "period": "2026-05-01 ~ 2026-05-31",
  "skill_stats": {
    "ins-claims": {
      "call_count": 1523,
      "pass_rate": 0.82,
      "warn_rate": 0.13,
      "fail_rate": 0.05,
      "avg_score": 78.5,
      "dimension_scores": {
        "D1": 85, "D2": 80, "D3": 90, "D4": 95,
        "D5": 75, "D6": 70, "D7": 72, "D8": 88
      }
    }
  },
  "hot_issues": [
    {
      "skill_id": "ins-claims",
      "dimension": "D7",
      "issue": "语义一致性得分偏低",
      "frequency": 142,
      "sample_inputs": ["理赔被拒怎么办", "为什么我的赔付还没到账"]
    }
  ]
}
```

### 3.2 L2 发现报告

```json
{
  "findings": [
    {
      "id": "F-2026-001",
      "severity": "high",
      "category": "语义偏差",
      "description": "ins-claims 在处理申诉场景时，回答偏离用户核心诉求",
      "affected_skills": ["ins-claims", "ins-compliance"],
      "root_cause": "协同链中缺少申诉材料清单的输出要求",
      "recommendation": "在 ins-claims 的 expected_structure 中增加'申诉材料清单'"
    }
  ]
}
```

### 3.3 L3 专家报告

```json
{
  "reports": [
    {
      "id": "R-2026-001",
      "reviewer": "senior-actuary",
      "skill_id": "ins-actuarial",
      "issue": "准备金计算假设说明不充分",
      "suggestion": "增加对趋势因子选择依据的解释",
      "priority": 2
    }
  ]
}
```

## 4. 进化策略

### 4.1 优先级算法

```
优先级得分 = (1 - pass_rate) × 100 + failure_frequency × 5 + expert_priority × 10

- pass_rate: 该Skill的通过率
- failure_frequency: 失败次数
- expert_priority: 专家报告优先级（1-5）
```

### 4.2 进化限流

- **每轮最大进化 Skill 数**: 2 个
- **每 Skill 最大改动数**: 3 处
- **冷却期**: 同一 Skill 进化后至少间隔 7 天才能再次进化
- **回滚窗口**: 进化发布后 24 小时内可一键回滚

### 4.3 改动类型

| 类型 | 说明 | 示例 |
|------|------|------|
| T1-结构调整 | 修改 expected_structure | 增加"申诉材料清单"字段 |
| T2-内容增强 | 扩充能力描述或工作流程 | 增加反欺诈识别步骤 |
| T3-Prompt优化 | 优化LLM评价Prompt | 细化语义一致性评价标准 |
| T4-规则更新 | 更新合规黑名单或PII模式 | 新增一类PII检测 |

## 5. 输出 Schema

### 5.1 进化计划

```json
{
  "plan_id": "EVP-2026-0531-001",
  "created_at": "2026-05-31T02:00:00Z",
  "target_skills": [
    {
      "skill_id": "ins-claims",
      "changes": [
        {
          "type": "T1",
          "field": "expected_structure",
          "action": "add",
          "value": "申诉材料清单",
          "reason": "L2发现报告F-2026-001"
        },
        {
          "type": "T2",
          "field": "能力描述",
          "action": "append",
          "value": "支持理赔申诉全流程，包括申诉材料准备、申诉策略制定和进度跟踪。",
          "reason": "语义一致性D7得分偏低"
        }
      ]
    }
  ],
  "expected_impact": {
    "ins-claims": { "D7": "+8分", "overall": "+5分" }
  }
}
```

### 5.2 进化报告

```json
{
  "plan_id": "EVP-2026-0531-001",
  "status": "published",
  "executed_at": "2026-05-31T02:30:00Z",
  "results": {
    "ins-claims": {
      "before_score": 78.5,
      "after_score": 84.2,
      "delta": "+5.7",
      "regression_passed": true,
      "auditor_score": {
        "INT": 92, "USA": 88, "CON": 90, "EFF": 85, "PRO": 91, "REA": 89
      }
    }
  },
  "version_bump": "1.0.0 → 1.0.1"
}
```

## 6. 触发条件

1. **定时触发**: 每夜 02:00 (nightly-evolution.yml)
2. **手动触发**: `ins-cli evolve`
3. **事件触发**: 某 Skill 连续 3 天 fail 率 > 10%

## 7. 回滚机制

```
if 进化发布后 24h 内:
  - 收到 ≥3 条负面反馈
  - 或回归测试失败率 > 5%
  - 或 Auditor 总分 < 75
→ 自动回滚到上一版本
→ 冻结该 Skill 进化 7 天
→ 通知运维团队
```
