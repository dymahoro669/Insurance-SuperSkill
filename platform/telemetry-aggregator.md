# 遥测聚合服务设计文档

> 全平台数据收集、聚合与分析系统，为进化引擎和评价服务提供数据燃料。

## 1. 设计目标

- **全链路追踪**: 从用户输入到最终输出的完整调用链可追踪
- **实时聚合**: 毫秒级延迟的实时数据统计
- **隐私保护**: 所有遥测数据经PII脱敏后上报
- **可扩展**: 支持新Skill和新维度指标的自动发现

## 2. 数据模型

### 2.1 调用事件 (Invocation Event)

```json
{
  "event_id": "inv-20260531-001",
  "timestamp": "2026-05-31T08:15:32.123Z",
  "session_id": "sess-a1b2c3d4",
  "trace_id": "trace-xyz789",
  "request": {
    "user_input": "我想投保一份重疾险",
    "client_info": { "platform": "web", "version": "1.0.0" }
  },
  "routing": {
    "primary_skill": "ins-underwriting",
    "confidence": 0.85,
    "route_chain": ["insurance-super-skill", "ins-underwriting"],
    "cross_skill_invoked": false
  },
  "execution": {
    "start_time": "2026-05-31T08:15:32.150Z",
    "end_time": "2026-05-31T08:15:33.890Z",
    "duration_ms": 1740,
    "tokens_used": 1250,
    "model": "claude-sonnet-4-6"
  },
  "evaluation": {
    "l1_score": 82,
    "l1_verdict": "pass",
    "l2_triggered": false,
    "l3_triggered": false
  },
  "output_summary": {
    "length": 856,
    "format": "markdown",
    "has_pii": false
  }
}
```

### 2.2 聚合指标 (Aggregated Metrics)

```json
{
  "period": "2026-05-31T00:00:00Z/2026-05-31T23:59:59Z",
  "skill_metrics": {
    "ins-underwriting": {
      "invocations": 1523,
      "avg_duration_ms": 1850,
      "avg_tokens": 1200,
      "l1_pass_rate": 0.82,
      "l1_warn_rate": 0.13,
      "l1_fail_rate": 0.05,
      "avg_score": 78.5,
      "dimension_avg": {
        "D1": 85, "D2": 80, "D3": 90, "D4": 95,
        "D5": 75, "D6": 70, "D7": 72, "D8": 88
      },
      "top_issues": [
        { "dimension": "D7", "count": 142, "description": "语义一致性偏低" }
      ],
      "routing_accuracy": 0.94
    }
  },
  "system_metrics": {
    "total_invocations": 18500,
    "avg_response_time_ms": 1650,
    "error_rate": 0.003,
    "pii_detection_rate": 0.12,
    "cross_skill_rate": 0.08
  }
}
```

## 3. 架构设计

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Skill调用   │────→│  本地缓冲   │────→│  批量上报   │
│  (产生事件)  │     │  (内存队列) │     │  (压缩后)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  实时监控    │←────│  聚合引擎    │←────│  数据存储   │
│  (Dashboard)│     │  (流计算)   │     │  (时序DB)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ↓             ↓
            ┌──────────┐  ┌──────────┐
            │ 进化引擎  │  │ L2/L3    │
            │ (输入)   │  │ 评价服务  │
            └──────────┘  └──────────┘
```

## 4. 核心组件

### 4.1 事件采集器 (Event Collector)

- **位置**: 内嵌在 insurance-super-skill 主索引中
- **采样率**: 100%（所有调用都采集）
- **脱敏**: 用户输入在采集前经过 security-guardian 处理
- **缓冲**: 内存队列，最大 1000 条，满则丢弃最旧
- **上报间隔**: 5秒或队列满时触发

### 4.2 聚合引擎 (Aggregation Engine)

- **时间窗口**: 支持 1min / 5min / 1h / 1d / 7d / 30d
- **聚合函数**: count / avg / sum / min / max / percentile
- **维度下钻**: Skill / 维度 / 时间段 / 客户端类型
- **实时性**: 99% 的指标在调用后 10 秒内可见

### 4.3 数据存储 (Data Store)

| 数据类型 | 存储方案 | 保留期 |
|---------|---------|--------|
| 原始事件 | 本地日志文件 | 7天 |
| 聚合指标 | 本地 SQLite | 90天 |
| 长期趋势 | 可选云端 | 永久 |

### 4.4 监控面板 (Dashboard)

```
Insurance-SuperSkill 实时监控面板

┌─────────────────────────────────────────┐
│  总调用: 18,500  │  平均响应: 1.65s     │
│  通过率: 82%    │  失败率: 0.3%        │
└─────────────────────────────────────────┘

Skill质量排行榜 (24h)
┌──────────────┬──────┬──────┬──────┬──────┐
│ Skill        │ 调用 │ 通过 │ 平均 │ 趋势 │
├──────────────┼──────┼──────┼──────┼──────┤
│ ins-claims   │ 1523 │ 82%  │ 78.5 │  ↑   │
│ ins-actuarial│  890 │ 88%  │ 85.2 │  →   │
│ ins-policy   │ 2100 │ 79%  │ 75.1 │  ↓   │
└──────────────┴──────┴──────┴──────┴──────┘

维度得分热力图
D1 ████████░░ 80
D2 ███████░░░ 70
D3 █████████░ 90
D4 ██████████ 95
D5 ██████░░░░ 60
...
```

## 5. 隐私设计

```
原始调用
    │
    ↓  security-guardian 脱敏
    │
脱敏后事件
    ├──→ 本地存储 (完整脱敏)
    │
    └──→ 上报云端 (可选，进一步匿名化)
            - 移除 session_id
            - 移除时间戳精确到小时
            - 哈希化 trace_id
```

## 6. API 接口

### 查询聚合指标

```http
GET /api/v1/metrics?skill=ins-claims&period=24h&dimensions=D1,D4,D7

Response:
{
  "skill": "ins-claims",
  "period": "24h",
  "invocations": 1523,
  "avg_score": 78.5,
  "dimensions": {
    "D1": { "avg": 85, "min": 40, "max": 100 },
    "D4": { "avg": 95, "min": 60, "max": 100 },
    "D7": { "avg": 72, "min": 20, "max": 100 }
  }
}
```

### 查询原始事件

```http
GET /api/v1/events?skill=ins-claims&verdict=fail&limit=10

Response:
{
  "events": [
    {
      "event_id": "inv-xxx",
      "timestamp": "2026-05-31T08:15:32Z",
      "l1_score": 45,
      "l1_verdict": "fail",
      "failed_dimensions": ["D4", "D7"]
    }
  ]
}
```

## 7. 与进化引擎的集成

```
遥测聚合服务 ──每日 02:00──→ 推送日报给进化引擎
    │                              │
    │                              ↓
    │                       进化引擎分析
    │                       - 识别质量下滑Skill
    │                       - 计算进化优先级
    │                              │
    │                              ↓
    │                       生成进化计划
    │
    └──→ 进化执行后，遥测数据反馈效果
         - 对比进化前后指标
         - 生成进化效果报告
```
