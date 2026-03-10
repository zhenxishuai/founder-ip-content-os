#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPAUTO Web Server - V4.2
提供一个简单的Web界面和API，用于控制IPAUTO系统。
"""

import os
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 加载 .env 文件中的环境变量
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

ROOT_PATH = "/home/ubuntu/founder-ip-content-os-full/"
SCHEDULE_PATH = os.path.join(ROOT_PATH, "09_排期表", "schedule.csv")
HUB_PATH = os.path.join(ROOT_PATH, "01_Hub文章")
DELIVERY_PATH = os.path.join(ROOT_PATH, "13_交付包")

app = FastAPI(title="IPAUTO 控制台", version="4.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 工具函数 ──────────────────────────────────────────────

def read_schedule():
    rows = []
    if not os.path.exists(SCHEDULE_PATH):
        return rows
    with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows

def run_push_now():
    """在后台执行 push_agent"""
    import sys
    sys.path.insert(0, ROOT_PATH)
    from agents.push_agent import PushAgent
    agent = PushAgent(root_path=ROOT_PATH)
    agent.execute()

def run_orchestrator(hub_file_path: str = None):
    """在后台执行 orchestrator_agent"""
    env = os.environ.copy()
    cmd = ["python3", "-m", "agents.orchestrator_agent"]
    subprocess.Popen(cmd, cwd=ROOT_PATH, env=env)

# ── 定时任务：每天09:00自动推送 ──────────────────────────────
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
scheduler.add_job(run_push_now, CronTrigger(hour=9, minute=0))
scheduler.start()

# ── API 路由 ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """主控制台页面"""
    schedule = read_schedule()
    today = datetime.now().strftime("%Y-%m-%d")

    today_task = next((r for r in schedule if r.get("publish_date") == today), None)
    
    # 构建排期表HTML
    schedule_rows = ""
    for r in schedule:
        is_today = "background:#e8f5e9;font-weight:bold;" if r.get("publish_date") == today else ""
        type_badge = "🎬 长视频" if r.get("content_type") == "long_video" else "✍️ 短内容"
        schedule_rows += f"""
        <tr style="{is_today}">
            <td style="padding:8px 12px;">{r.get('publish_date','')}</td>
            <td style="padding:8px 12px;">{type_badge}</td>
            <td style="padding:8px 12px;">{r.get('title','')}</td>
        </tr>"""

    today_card = ""
    if today_task:
        today_card = f"""
        <div style="background:#e3f2fd;border-left:4px solid #1976d2;padding:16px;border-radius:4px;margin-bottom:24px;">
            <strong>📅 今日任务</strong><br>
            <span style="font-size:18px;font-weight:bold;">{today_task.get('title')}</span><br>
            <span style="color:#555;">类型：{'🎬 长视频脚本' if today_task.get('content_type')=='long_video' else '✍️ 短内容'}</span>
        </div>"""
    else:
        today_card = """<div style="background:#f5f5f5;padding:16px;border-radius:4px;margin-bottom:24px;color:#888;">今日暂无排期任务</div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IPAUTO 控制台 V4.2</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;margin:0;padding:20px;color:#333;}}
  .container{{max-width:900px;margin:0 auto;}}
  h1{{color:#1a237e;border-bottom:3px solid #3f51b5;padding-bottom:10px;}}
  .card{{background:#fff;border-radius:8px;padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);}}
  .btn{{display:inline-block;padding:10px 24px;border-radius:6px;border:none;cursor:pointer;font-size:15px;font-weight:600;text-decoration:none;margin-right:10px;margin-top:8px;}}
  .btn-primary{{background:#3f51b5;color:#fff;}}
  .btn-success{{background:#388e3c;color:#fff;}}
  .btn-warning{{background:#f57c00;color:#fff;}}
  .btn:hover{{opacity:.85;}}
  table{{width:100%;border-collapse:collapse;}}
  th{{background:#3f51b5;color:#fff;padding:10px 12px;text-align:left;}}
  tr:nth-child(even){{background:#f9f9f9;}}
  .status-ok{{color:#388e3c;font-weight:bold;}}
  .status-warn{{color:#f57c00;font-weight:bold;}}
  .upload-area{{border:2px dashed #3f51b5;border-radius:8px;padding:30px;text-align:center;color:#3f51b5;}}
  #result{{margin-top:12px;padding:12px;border-radius:6px;display:none;}}
</style>
</head>
<body>
<div class="container">
  <h1>🤖 IPAUTO 控制台 <span style="font-size:14px;color:#888;font-weight:normal;">V4.2 · 稳定生成 + 稳定推送 + 人工回填</span></h1>

  {today_card}

  <div class="card">
    <h2 style="margin-top:0;">⚡ 快捷操作</h2>
    <button class="btn btn-primary" onclick="triggerPush()">📨 立即推送今日任务到飞书</button>
    <button class="btn btn-success" onclick="document.getElementById('upload-section').scrollIntoView()">📝 上传 Hub 文章生成内容</button>
    <div id="result"></div>
  </div>

  <div class="card" id="upload-section">
    <h2 style="margin-top:0;">📝 上传 Hub 文章</h2>
    <p style="color:#555;">上传您的 Hub 长文（.txt 或 .md），系统将自动拆解并生成视频脚本和排期。</p>
    <div class="upload-area">
      <form id="upload-form" enctype="multipart/form-data">
        <input type="file" name="file" accept=".txt,.md" style="margin-bottom:12px;"><br>
        <button type="submit" class="btn btn-success">🚀 上传并开始生成</button>
      </form>
      <div id="upload-result" style="margin-top:12px;"></div>
    </div>
  </div>

  <div class="card">
    <h2 style="margin-top:0;">📅 发布排期表（未来14天）</h2>
    <table>
      <thead><tr><th>发布日期</th><th>内容类型</th><th>标题</th></tr></thead>
      <tbody>{schedule_rows if schedule_rows else '<tr><td colspan="3" style="padding:16px;text-align:center;color:#888;">暂无排期，请先上传Hub文章生成内容</td></tr>'}</tbody>
    </table>
  </div>

  <div class="card">
    <h2 style="margin-top:0;">⚙️ 系统状态</h2>
    <p>OpenAI API Key: <span class="{'status-ok' if os.environ.get('OPENAI_API_KEY') else 'status-warn'}">{'✅ 已配置' if os.environ.get('OPENAI_API_KEY') else '❌ 未配置'}</span></p>
    <p>飞书 Webhook: <span class="{'status-ok' if os.environ.get('FEISHU_WEBHOOK_URL','').endswith('YOUR_WEBHOOK_ID')==False and os.environ.get('FEISHU_WEBHOOK_URL') else 'status-warn'}">{'✅ 已配置' if os.environ.get('FEISHU_WEBHOOK_URL') and not os.environ.get('FEISHU_WEBHOOK_URL','').endswith('YOUR_WEBHOOK_ID') else '❌ 未配置'}</span></p>
    <p>排期表: <span class="{'status-ok' if os.path.exists(SCHEDULE_PATH) else 'status-warn'}">{'✅ 存在（' + str(len(read_schedule())) + ' 条）' if os.path.exists(SCHEDULE_PATH) else '❌ 不存在'}</span></p>
    <p style="color:#888;font-size:13px;">当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 定时推送：每天 09:00（需配置 Cron）</p>
  </div>
</div>

<script>
async function triggerPush() {{
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '推送中...';
  const res = await fetch('/api/push', {{method:'POST'}});
  const data = await res.json();
  const el = document.getElementById('result');
  el.style.display = 'block';
  el.style.background = data.success ? '#e8f5e9' : '#ffebee';
  el.style.color = data.success ? '#2e7d32' : '#c62828';
  el.textContent = data.message;
  btn.disabled = false;
  btn.textContent = '📨 立即推送今日任务到飞书';
}}

document.getElementById('upload-form').addEventListener('submit', async (e) => {{
  e.preventDefault();
  const formData = new FormData(e.target);
  const resultEl = document.getElementById('upload-result');
  resultEl.textContent = '⏳ 正在上传并处理，请稍候（约30-60秒）...';
  resultEl.style.color = '#1976d2';
  try {{
    const res = await fetch('/api/upload_hub', {{method:'POST', body: formData}});
    const data = await res.json();
    resultEl.textContent = data.message;
    resultEl.style.color = data.success ? '#2e7d32' : '#c62828';
    if (data.success) setTimeout(() => location.reload(), 3000);
  }} catch(err) {{
    resultEl.textContent = '上传失败：' + err.message;
    resultEl.style.color = '#c62828';
  }}
}});
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.post("/api/push")
async def api_push(background_tasks: BackgroundTasks):
    """立即触发飞书推送"""
    try:
        background_tasks.add_task(run_push_now)
        return JSONResponse({"success": True, "message": "✅ 推送任务已触发！请检查您的飞书群。"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"❌ 推送失败: {str(e)}"})


@app.post("/api/upload_hub")
async def api_upload_hub(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """上传Hub文章并触发内容生成"""
    try:
        os.makedirs(HUB_PATH, exist_ok=True)
        file_path = os.path.join(HUB_PATH, file.filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        background_tasks.add_task(run_orchestrator, file_path)
        return JSONResponse({
            "success": True,
            "message": f"✅ 文章《{file.filename}》已上传！系统正在后台生成内容，约60秒后刷新页面查看排期。"
        })
    except Exception as e:
        return JSONResponse({"success": False, "message": f"❌ 上传失败: {str(e)}"})


@app.get("/api/schedule")
async def api_schedule():
    """获取排期表JSON"""
    return JSONResponse(read_schedule())


@app.get("/api/status")
async def api_status():
    """系统状态检查"""
    return JSONResponse({
        "version": "4.2",
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "feishu_configured": bool(os.environ.get("FEISHU_WEBHOOK_URL")) and not os.environ.get("FEISHU_WEBHOOK_URL", "").endswith("YOUR_WEBHOOK_ID"),
        "schedule_exists": os.path.exists(SCHEDULE_PATH),
        "schedule_count": len(read_schedule()),
        "timestamp": datetime.now().isoformat()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
