#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OutlineAgent - 大纲生成 Agent (V4.3)
根据Hub文章，生成结构化的一周内容大纲（7天 × 3平台 + 公众号长文）。
"""

import json
import os
from typing import Dict, Any
from openai import OpenAI

class OutlineAgent:
    """读取Hub文章，生成结构化内容大纲。"""

    def __init__(self, root_path: str):
        self.agent_name = "OutlineAgent"
        self.version = "1.1"
        self.client = OpenAI()
        self.root_path = root_path

    def generate_outline(self, hub_content: str) -> Dict[str, Any]:
        """
        根据Hub文章内容生成结构化大纲。

        Args:
            hub_content: Hub文章的完整内容。

        Returns:
            包含内容大纲的字典。
        """
        prompt = self._build_prompt(hub_content)
        
        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": (
                        "你是一位顶级的内容策略总监。你的任务是根据一篇核心文章，"
                        "规划出一整周（7天）、跨平台的内容发布大纲。"
                        "每天必须包含3个平台：小红书、短视频、朋友圈。"
                        "第1天额外增加一篇公众号长文。"
                        "你必须确保大纲的结构清晰、逻辑严谨、顺序正确，"
                        "并严格按照指定的JSON格式输出。"
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=6000,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
            # 处理可能的 markdown 代码块包裹
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            elif raw_response.strip().startswith('{'):
                clean_response = raw_response.strip()
            else:
                # 尝试找到第一个 { 和最后一个 }
                start = raw_response.find('{')
                end = raw_response.rfind('}') + 1
                clean_response = raw_response[start:end]
            
            outline_json = json.loads(clean_response)
            
            # 基础校验
            if "weekly_content_outline" not in outline_json:
                raise ValueError("LLM输出缺少根键 'weekly_content_outline'")

            return outline_json

        except Exception as e:
            print(f"✗ {self.agent_name} 生成大纲失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, hub_content: str) -> str:
        """构建用于生成大纲的Prompt"""
        
        prompt = f"""
# 任务
根据我提供的【核心文章】，为创始人IP"增长与变现战略顾问"创作一个为期7天的跨平台内容大纲。

# 核心文章
{hub_content}

# 大纲要求
1. 必须生成7天的内容计划（day: 1 到 day: 7）。
2. 每天必须包含3个平台的条目：小红书、短视频、朋友圈。
3. 第1天（day: 1）额外增加一篇公众号长文条目。
4. 每天的3个平台内容，主题要相互呼应，但角度不同（小红书偏干货列表，短视频偏口播脚本，朋友圈偏金句感悟）。
5. 7天的内容要覆盖核心文章的不同角度，不要7天都讲同一件事。
6. 所有要点必须从核心文章中提炼，不要编造。

# 输出格式
严格按照以下JSON格式输出。每天有多个条目（每个平台一个条目），所有条目都放在 weekly_content_outline 数组中。

{{
    "weekly_content_outline": [
        {{
            "day": 1,
            "platform": "公众号",
            "theme": "本周公众号长文的核心主题",
            "structure": "开头 -> 发展 -> 转折 -> 收尾",
            "key_points_by_section": {{
                "opening": "开头部分的核心观点",
                "development": "发展部分的核心论述",
                "turning_point": "转折部分的反思或新视角",
                "ending": "收尾部分的总结和升华"
            }}
        }},
        {{
            "day": 1,
            "platform": "小红书",
            "theme": "第1天小红书的核心主题",
            "title_suggestion": "爆款标题建议",
            "methods": [
                {{"method_index": 1, "method_name": "方法1名称", "key_point": "方法1要点"}},
                {{"method_index": 2, "method_name": "方法2名称", "key_point": "方法2要点"}},
                {{"method_index": 3, "method_name": "方法3名称", "key_point": "方法3要点"}}
            ]
        }},
        {{
            "day": 1,
            "platform": "短视频",
            "theme": "第1天短视频的核心主题",
            "content_structure": [
                {{"section": "hook", "key_point": "3秒钩子"}},
                {{"section": "body", "key_points": ["要点1", "要点2", "要点3"]}},
                {{"section": "ending", "key_point": "结尾引导"}}
            ]
        }},
        {{
            "day": 1,
            "platform": "朋友圈",
            "theme": "第1天朋友圈主题",
            "key_point": "一句金句或核心洞察（不超过50字）"
        }},
        {{
            "day": 2,
            "platform": "小红书",
            "theme": "第2天小红书主题",
            "title_suggestion": "爆款标题",
            "methods": [
                {{"method_index": 1, "method_name": "方法1", "key_point": "要点"}},
                {{"method_index": 2, "method_name": "方法2", "key_point": "要点"}}
            ]
        }},
        {{
            "day": 2,
            "platform": "短视频",
            "theme": "第2天短视频主题",
            "content_structure": [
                {{"section": "hook", "key_point": "3秒钩子"}},
                {{"section": "body", "key_points": ["要点1", "要点2"]}},
                {{"section": "ending", "key_point": "结尾"}}
            ]
        }},
        {{
            "day": 2,
            "platform": "朋友圈",
            "theme": "第2天朋友圈主题",
            "key_point": "金句"
        }}
    ]
}}

注意：上面只是前2天的示例结构。你必须按照同样的结构，生成完整的7天内容（day 1 到 day 7），每天包含小红书、短视频、朋友圈3个条目，第1天额外包含公众号条目。
        """
        return prompt


if __name__ == '__main__':
    print("✓ OutlineAgent V1.1 初始化，开始测试...")
    agent = OutlineAgent(root_path=os.path.dirname(os.path.dirname(__file__)))
    
    mock_hub_content = """
    短视频赚钱的核心公式：收入=有效曝光×点击率×转化率×客单价×复购率×毛利率。
    五个关键要素：人群定位、供给选品、内容三件套（钩子+证据+行动）、承接路径、数据放大。
    """
    
    print("\n[测试] 基于模拟Hub文章生成大纲...")
    outline = agent.generate_outline(mock_hub_content)
    print(json.dumps(outline, ensure_ascii=False, indent=2))
