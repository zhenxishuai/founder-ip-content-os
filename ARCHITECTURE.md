# 创始人IP内容操作系统 V4 — 增长与变现操作系统

## 系统总目标

本系统不是"内容生产工具"，而是一个**增长与变现操作系统（Growth & Monetization OS）**。

它的核心逻辑是：通过自动化的内容生产、热点捕捉、爆款学习和变现匹配，让创始人IP的内容影响力随时间指数级增长，并将流量持续转化为商业价值。

---

## V4 系统架构

### 双引擎工作流

```
Hub文章（深度思考）
        ↓
  HubParserAgent
        ↓
   组件库（JSON）
        ↓
LongVideoScriptAgent
        ↓
  MonetizationAgent
        ↓
    视频脚本输出



热点事件（实时）
        ↓
TrendCrawlerAgent（TrendRadar集成）
        ↓
TrendAnalyzerAgent
        ↓
LongVideoScriptAgent
        ↓
  MonetizationAgent
        ↓
    视频脚本输出



发布后数据
        ↓
    metrics.json
        ↓
  LearningAgent
        ↓
  structure_library.json（爆款模板库）
```

---

## 7个核心Agent

| Agent | 职责 | 版本 |
|---|---|---|
| **HubParserAgent** | 将Hub长文解析为结构化JSON组件（观点/金句/案例/框架/冲突点/行动清单/关键词/适用人群） | V2（LLM真实提取） |
| **LongVideoScriptAgent** | 将组件或热点选题转化为3分钟视频口播脚本 | V4新增 |
| **TrendCrawlerAgent** | 集成TrendRadar，自动抓取11个平台的实时热点 | V4（TrendRadar集成） |
| **TrendAnalyzerAgent** | 将热点事件转化为可拍视频的选题角度 | V4新增 |
| **LearningAgent** | 分析内容表现数据，识别爆款，提取结构模板，写入资产库 | V4新增 |
| **MonetizationAgent** | 分析内容脚本，匹配最佳变现产品，生成定制化CTA | V4新增 |
| **OrchestratorAgent** | 总控调度，执行双引擎工作流，管理资产库，生成排期表 | V4升级 |

---

## 资产库结构

```
10_资产库/
├── asset_library.json          # 核心资产库（组件/钩子/锚点/CTA）
├── asset_schema.json           # 数据模型定义
├── structure_library.json      # 爆款结构模板库（LearningAgent写入）
├── trend_events.json           # 实时热点事件库（TrendCrawler写入）
├── trend_angles.json           # 热点选题角度库（TrendAnalyzer写入）
├── metrics.json                # 内容表现数据（外部输入）
├── monetization_products.json  # 变现产品库（人工维护）
└── voice_spec.md               # 口吻规范文件
```

---

## 资产评分与复利机制

每条资产都包含以下复利字段：

```json
{
    "id": "comp_hash12345",
    "content": "...",
    "usage_count": 3,
    "score": 8.5,
    "last_seen_at": "2026-03-01T00:00:00"
}
```

**评分公式（LearningAgent）：**

```
score = (完播率 × 0.4) + (转发率 × 0.3) + (收藏率 × 0.2) + (评论率 × 0.1)
```

当`score > 80`时，LearningAgent自动触发爆款学习流程，提取结构模板并写入`structure_library.json`。

**智能调用优先级：**

```
优先级 = score × (1 - 使用次数系数) × 平台匹配度
```

---

## 排期策略（V4长视频优先）

| 星期 | 内容类型 |
|---|---|
| 周一 | 长视频（Hub驱动） |
| 周二 | 短内容（图文/短视频） |
| 周三 | 长视频（热点驱动） |
| 周四 | 短内容 |
| 周五 | 长视频（Hub驱动） |
| 周六 | 短内容 |
| 周日 | 长视频（热点驱动） |

**目标：每周4条长视频 + 3条短内容 = 7条跨平台内容**

---

## GitHub技能集成

### TrendRadar（已集成）
**项目地址**: https://github.com/sansan0/TrendRadar  
**Star数**: 47.6k

TrendCrawlerAgent已集成TrendRadar，具备以下能力：
- 同时监控11个主流平台（知乎、抖音、B站、微博、百度热搜等）
- 支持关键词精准筛选
- AI智能分析热点趋势
- 支持MCP协议，可与AI对话系统直接集成

### MediaCrawler（评估完成，可选集成）
**项目地址**: https://github.com/NanmiCoder/MediaCrawler  
**Star数**: 44.5k

可用于采集各平台爆款内容样本，供LearningAgent进行模式识别。注意：需遵守爬虫合规规定，仅用于学习研究目的。

---

## 如何使用

### 1. Hub驱动工作流
将Hub长文放入 `01_Hub文章/` 目录，然后运行：
```bash
cd /home/ubuntu/创始人IP系统/11_Agent脚本/
python3 orchestrator_agent.py
```

### 2. 热点驱动工作流
系统会自动通过TrendRadar抓取热点，无需手动操作。

### 3. 标记爆款（触发学习回路）
在 `10_资产库/metrics.json` 中，为内容添加表现数据：
```json
{
    "content_id": "your_content_id",
    "completion_rate": 0.85,
    "share_rate": 0.12,
    "save_rate": 0.08,
    "comment_rate": 0.05
}
```
然后运行LearningAgent，系统会自动识别爆款并更新结构模板库。

### 4. 维护变现产品库
在 `10_资产库/monetization_products.json` 中添加您的付费产品：
```json
{
    "product_id": "your_product_id",
    "name": "产品名称",
    "keywords": ["关键词1", "关键词2"],
    "target_audience": ["目标人群"],
    "cta_suggestion": "定制化的行动号召语句"
}
```

---

## V4系统进化路线图

| 版本 | 核心升级 | 状态 |
|---|---|---|
| V1 | 基础内容生产（7个Agent骨架） | ✅ 已完成 |
| V2 | LLM真实提取 + 幂等性 + 资产库写入 | ✅ 已完成 |
| V3 | 质量指标修复 + 处理标记 + 去重 | ✅ 已完成 |
| **V4** | **3分钟视频脚本 + 热点抓取 + 爆款学习 + 变现优化 + TrendRadar集成** | **✅ 当前版本** |
| V5（规划中） | 自动发布 + 数据回流 + 秘塔搜索集成 + IMA知识库接入 | 规划中 |
