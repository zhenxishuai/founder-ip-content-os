#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendAnalyzerAgent - 热点变选题Agent (V4核心)
"""

import json
import os
from typing import List, Dict, Any

# 假设我们有一个LLM客户端，这里用占位符表示
from openai import OpenAI

class TrendAnalyzerAgent:
    """将原始热点事件转化为可拍摄的视频选题"""

    def __init__(self, asset_path: str):
        self.agent_name = "TrendAnalyzerAgent"
        self.version = "4.0"
        self.client = OpenAI() # 假设API Key等已配置
        self.asset_path = asset_path

    def analyze_trends(self, trend_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析一批热点事件，为每个事件生成多个选题角度。

        Args:
            trend_events: 从TrendCrawlerAgent获取的热点事件列表。

        Returns:
            包含多个选题角度的列表。
        """
        all_angles = []
        for event in trend_events:
            prompt = self._build_prompt(event)
            try:
                response = self.client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=[
                        {"role": "system", "content": "你是一位顶级的增长与变现战略顾问，拥有敏锐的商业嗅觉。你的任务是将一个普通的热点新闻，转化为与创始人、企业家高度相关的、深刻且反常识的视频选题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                raw_response = response.choices[0].message.content
                
                if '```json' in raw_response:
                    clean_response = raw_response.split('```json')[1].split('```')[0].strip()
                else:
                    clean_response = raw_response.strip()
                
                generated_angles = json.loads(clean_response).get("angles", [])
                
                for angle in generated_angles:
                    if all(k in angle for k in ["angle_title", "hook", "core_argument", "video_potential_score"]):
                        angle["source_event_id"] = event.get("event_id")
                        angle["source_event_title"] = event.get("title")
                        all_angles.append(angle)

            except Exception as e:
                print(f"✗ {self.agent_name} 分析事件 '{event.get('title')}' 失败: {e}")
        
        return all_angles

    def _build_prompt(self, event: Dict[str, Any]) -> str:
        """为单个热点事件构建分析Prompt"""
        prompt = f"""
        # 任务
        我将为你提供一个热点事件。请你作为“增长与变现战略顾问”，从创始人和企业家的视角出发，为这个事件构思 1-3 个独特的、可拍摄成3分钟中视频的选题角度。你的分析必须穿透事件表面，挖掘其背后的商业逻辑、增长机会或潜在风险。

        # 热点事件信息
        - **标题**: {event.get('title')}
        - **摘要**: {event.get('summary')}
        - **热度值**: {event.get('heat_score')}

        # 选题角度要求
        每个选题角度都必须包含以下四个要素：
        1.  **angle_title (选题标题)**: 一个极具吸引力、能引发目标受众（创始人/企业家）好奇心的视频标题。
        2.  **hook (核心钩子)**: 视频开头3秒内，一个能瞬间抓住用户的反常识观点或尖锐提问。
        3.  **core_argument (核心论点)**: 清晰、深刻、可支撑起一个3分钟视频的核心论证观点。要体现你的战略顾问身份，提供价值，而不是简单复述新闻。
        4.  **video_potential_score (视频潜力分)**: 你对这个选题成为爆款的潜力打分（0-100分），需要综合考虑其话题性、深度、以及与目标受众的共鸣程度。

        # 输出格式
        请严格按照以下JSON格式输出，将所有构思的选题角度放在一个名为 'angles' 的列表中。不要添加任何额外的解释或说明文字：
        {{
            "angles": [
                {{
                    "angle_title": "[选题标题1]",
                    "hook": "[核心钩子1]",
                    "core_argument": "[核心论点1]",
                    "video_potential_score": [0-100的整数]
                }},
                {{
                    "angle_title": "[选题标题2]",
                    "hook": "[核心钩子2]",
                    "core_argument": "[核心论点2]",
                    "video_potential_score": [0-100的整数]
                }}
            ]
        }}
        """
        return prompt

if __name__ == '__main__':
    print("✓ TrendAnalyzerAgent 初始化，开始测试...")
    agent = TrendAnalyzerAgent()

    mock_trends = [
        {
            "event_id": "trend_001",
            "title": "某知名连锁咖啡品牌宣布开放加盟，加盟费低至5万元",
            "summary": "一直坚持直营的某咖啡品牌突然宣布开放加盟，试图通过下沉市场寻求新的增长点，引发行业热议。",
            "source": "TechCrunch",
            "heat_score": 92,
            "timestamp": "2026-03-01T10:00:00Z"
        },
        {
            "event_id": "trend_002",
            "title": "海外版拼多多Temu用户增长放缓，首次出现季度下滑",
            "summary": "依靠低价策略在海外迅速扩张的电商平台Temu，其最新财报显示用户增长出现瓶颈，引发对其商业模式可持续性的讨论。",
            "source": "Bloomberg",
            "heat_score": 85,
            "timestamp": "2026-03-01T09:00:00Z"
        }
    ]

    analyzed_angles = agent.analyze_trends(mock_trends)

    print("\n✓ 分析完成，生成选题角度如下:")
    print(json.dumps(analyzed_angles, ensure_ascii=False, indent=2))
