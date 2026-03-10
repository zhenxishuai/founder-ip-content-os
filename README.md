# 创始人IP内容操作系统 V4.2 - IPAUTO

这是一个基于Agent架构的自动化内容系统，旨在将您的深度思考（Hub文章）和外部热点，转化为可直接发布的、服务于增长与变现的视频脚本和跨平台内容。

## 当前版本：V4.2 (稳定运行版)

**核心策略：稳定生成 + 稳定推送 + 人工回填**

## 核心能力

- **双引擎工作流**: 同时运行"Hub驱动"和"热点驱动"两条生产线。
- **3分钟视频脚本生成**: 自动将结构化组件或热点选题，生成700-1000字的口播脚本。
- **热点自动抓取与分析**: （需外部配合）自动读取热点，分析并生成可拍选题。
- **爆款自动学习**: 自动分析高分内容的结构，沉淀为"爆款模板"资产，用于未来创作。
- **变现智能匹配**: 自动为内容匹配最合适的付费产品或服务，并生成定制化CTA。
- **QA质量保证**: 自动检查内容的合规性、重复度和营销感，并支持"回炉重写"。
- **🆕 每日飞书推送**: 每天09:00自动读取排期表，通过飞书机器人推送今日内容任务。

## 如何使用

### 1. 环境设置

```bash
# 安装依赖
pip3 install -r requirements.txt
```

### 2. Hub驱动工作流（生产端）

1.  将您的Hub长文（`.txt`或`.md`格式）放入 `01_Hub文章/` 目录。
2.  运行总控Agent：
    ```bash
    python3 -m agents.orchestrator_agent
    ```
3.  产出物将自动保存到 `13_交付包/`，排期表保存到 `09_排期表/schedule.csv`。

### 3. 热点驱动工作流

1.  通过外部工具（如n8n、定时脚本等）抓取热点，并将其写入 `assets/raw_trend_events.json` 文件。
    - 文件格式: `[{"title": "...", "summary": "...", "source": "...", "heat_score": 85}]`
2.  运行总控Agent（同上），系统会自动检测并处理热点。

### 4. 查看产出

- **视频脚本与交付物**: `13_交付包/` 目录
- **发布排期表**: `09_排期表/schedule.csv`
- **沉淀的资产**: `10_资产库/` 目录

### 5. 🆕 配置每日飞书推送（执行端）

系统包含 `push_agent.py`，可以读取当天的排期并通过飞书机器人发送任务卡片。

**A. 配置Webhook**

方式一（推荐）：设置环境变量（安全，不会泄露到代码仓库）：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的Webhook_ID"
```

方式二：直接修改 `agents/push_agent.py` 文件中的 `feishu_webhook_url` 变量。

**B. 手动测试推送**

```bash
python3 -m agents.push_agent
```

**C. 设置定时任务（每天09:00自动推送）**

在服务器上执行 `crontab -e`，然后添加以下内容：

```cron
# 每天早上09:00执行IPAUTO飞书推送
0 9 * * * FEISHU_WEBHOOK_URL="你的Webhook地址" /usr/bin/bash /home/ubuntu/founder-ip-content-os/run_push.sh >> /home/ubuntu/founder-ip-content-os/logs/cron.log 2>&1
```

> **注意**：请将路径替换为您服务器上的实际项目路径。建议提前创建 `logs/` 目录：`mkdir -p logs`

## 数据回填（人工）

当前阶段，播放量、点赞、评论、私信、咨询、成交等数据，请在发布后**人工回填**到 `10_资产库/metrics.json` 文件中。

格式参考：
```json
[
  {
    "content_id": "文件名或ID",
    "publish_date": "2026-03-10",
    "platform": "抖音",
    "views": 5000,
    "likes": 200,
    "comments": 30,
    "inquiries": 5,
    "conversions": 1
  }
]
```

## 系统架构

详细的Agent分工、工作流和资产库结构，请参见 `ARCHITECTURE.md`。

## 版本历史

| 版本 | 说明 |
| :--- | :--- |
| V4.2 | 新增PushAgent，实现每日飞书推送；明确"稳定生成+稳定推送+人工回填"策略 |
| V4.1 | 生产端完整实现：Hub拆解、脚本生成、QA验证、排期表生成 |
