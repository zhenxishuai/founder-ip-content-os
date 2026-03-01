#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendCrawlerAgent - 热点处理Agent (V4.1核心)
"""

import json
import os
from typing import List, Dict, Any

class TrendCrawlerAgent:
    """读取外部抓取的热点，进行处理并写入资产库。"""

    def __init__(self, asset_path: str):
        self.agent_name = "TrendCrawlerAgent"
        self.version = "4.1-Decoupled"
        self.asset_path = asset_path
        self.raw_events_path = os.path.join(self.asset_path, "raw_trend_events.json")
        self.processed_events_path = os.path.join(self.asset_path, "trend_events.json")

    def process_raw_trends(self) -> bool:
        """
        读取原始热点文件，处理后存入标准资产库。
        """
        try:
            with open(self.raw_events_path, 'r', encoding='utf-8') as f:
                raw_events = json.load(f)
        except FileNotFoundError:
            print("✓ TrendCrawlerAgent: 未找到原始热点文件，跳过本次处理。")
            return False
        except json.JSONDecodeError:
            print("✗ TrendCrawlerAgent: 原始热点文件格式错误。")
            return False

        # 此处可以添加去重、聚类、风险标注等复杂逻辑
        # 为简化，我们直接进行格式化和保存
        processed_events = self._format_events(raw_events)

        self._save_events(processed_events)
        return True

    def _format_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将原始事件格式化为系统标准格式。"""
        formatted = []
        for event in events:
            # 这是一个假设的格式转换，实际应根据外部源的格式调整
            formatted.append({
                "event_id": event.get("id", f"trend_{hash(event.get('title'))}"),
                "title": event.get("title", "无标题"),
                "summary": event.get("summary", ""),
                "source": event.get("source", "Unknown"),
                "heat_score": event.get("heat_score", 50),
                "timestamp": event.get("timestamp", "")
            })
        return formatted

    def _save_events(self, new_events: List[Dict[str, Any]]):
        """将处理后的事件增量更新到资产库。"""
        existing_events = []
        if os.path.exists(self.processed_events_path):
            with open(self.processed_events_path, 'r', encoding='utf-8') as f:
                existing_events = json.load(f)
        
        existing_ids = {e["event_id"] for e in existing_events}
        
        added_count = 0
        for event in new_events:
            if event["event_id"] not in existing_ids:
                existing_events.append(event)
                added_count += 1

        with open(self.processed_events_path, 'w', encoding='utf-8') as f:
            json.dump(existing_events, f, ensure_ascii=False, indent=2)
        
        print(f"✓ TrendCrawlerAgent: {added_count}个新热点已处理并存入资产库。")
