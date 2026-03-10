#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PushAgent - 执行端Agent (V4.2)
负责读取排期表，并在指定时间通过飞书Webhook推送今日内容任务。
"""

import os
import csv
import json
import requests
from datetime import datetime

class PushAgent:
    """执行端Agent，负责推送每日任务到飞书。"""

    def __init__(self, root_path="/home/ubuntu/创始人IP系统/"):
        self.agent_name = "PushAgent"
        self.version = "1.0"
        self.root_path = root_path
        self.schedule_path = os.path.join(self.root_path, "09_排期表", "schedule.csv")
        # !!! 请将下面的URL替换为您自己的飞书机器人Webhook地址 !!!
        self.feishu_webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID")

    def get_today_task(self) -> dict | None:
        """从schedule.csv中读取今天的任务。"""
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            print(f"🔍 正在查找日期为 {today_str} 的任务...")
            with open(self.schedule_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get("publish_date") == today_str:
                        print(f"  ✓ 找到今日任务: {row['title']}")
                        return row
            print("  → 今天没有发布任务。")
            return None
        except FileNotFoundError:
            print(f"❌ 错误: 排期表文件未找到 at {self.schedule_path}")
            return None
        except Exception as e:
            print(f"❌ 读取排期表时发生未知错误: {e}")
            return None

    def send_feishu_notification(self, task: dict):
        """发送飞书卡片消息。"""
        if self.feishu_webhook_url.endswith("YOUR_WEBHOOK_ID"):
            print("❌ 错误: 飞书Webhook URL未配置，请修改push_agent.py或设置FEISHU_WEBHOOK_URL环境变量。")
            # 以本地打印代替真实推送
            print("\n--- 模拟飞书推送 ---")
            print(json.dumps(self._build_feishu_card(task), indent=2, ensure_ascii=False))
            print("--------------------\n")
            return

        headers = {"Content-Type": "application/json"}
        card_content = self._build_feishu_card(task)
        
        payload = {
            "msg_type": "interactive",
            "card": card_content
        }

        try:
            print("🚀 正在推送到飞书...")
            response = requests.post(self.feishu_webhook_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # 如果请求失败则抛出HTTPError
            result = response.json()
            if result.get("StatusCode") == 0:
                print("  ✓ 飞书任务卡片推送成功！")
            else:
                print(f"❌ 飞书API返回错误: {result.get('StatusMessage')}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 推送到飞书时发生网络错误: {e}")
        except Exception as e:
            print(f"❌ 推送过程中发生未知错误: {e}")

    def _build_feishu_card(self, task: dict) -> dict:
        """构建飞书卡片消息内容。"""
        content_type_map = {
            "long_video": "🎬 长视频脚本",
            "short_content": "✍️ 图文/短内容"
        }
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": "💡 IPAUTO - 今日内容发布任务",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**标题：** {task.get('title', '无标题')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**📅 发布日期**\n{task.get('publish_date')}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**📋 内容类型**\n{content_type_map.get(task.get('content_type'), '未知')}",
                                "tag": "lark_md"
                            }
                        }
                    ]
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"**请注意：**\n1.  请根据脚本内容，完成视频录制/图文撰写。\n2.  发布后，请及时在数据看板中**人工回填**相关数据。",
                        "tag": "lark_md"
                    }
                },
                 {
                    "tag": "note",
                    "elements": [
                        {
                            "content": f"脚本路径: {task.get('file_path')}",
                            "tag": "plain_text"
                        }
                    ]
                }
            ]
        }
        return card

    def execute(self):
        """执行单次推送任务。"""
        print(f"🤖 PushAgent V{self.version} 开始执行...")
        task = self.get_today_task()
        if task:
            self.send_feishu_notification(task)
        else:
            print("✨ 今日无事，保持创意！")

if __name__ == '__main__':
    # 使用 founder-ip-content-os-full 作为根目录
    agent = PushAgent(root_path="/home/ubuntu/founder-ip-content-os-full/")
    agent.execute()
