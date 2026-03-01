#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LongVideoScriptAgent - 3分钟视频脚本生成Agent (V4核心)
"""

import json
import os
from typing import Dict, Any, Union

# 假设我们有一个LLM客户端，这里用占位符表示
from openai import OpenAI

class LongVideoScriptAgent:
    """将结构化输入（Hub组件或热点选题）转化为3分钟视频脚本"""

    def __init__(self, asset_path: str):
        self.agent_name = "LongVideoScriptAgent"
        self.version = "4.0"
        self.client = OpenAI() # 假设API Key等已配置
        self.asset_path = asset_path

    def generate_script(self, input_data: Dict[str, Any], input_type: str) -> Dict[str, Any]:
        """
        生成一个3分钟（700-1000字）的视频脚本

        Args:
            input_data: 输入数据，可以是HubParser的组件或TrendAnalyzer的选题
            input_type: 'hub' 或 'trend'

        Returns:
            包含脚本的字典
        """
        prompt = self._build_prompt(input_data, input_type)
        
        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "你是一个顶级的视频脚本撰稿人，为创始人IP‘增长与变现战略顾问’撰写视频脚本。脚本必须理性、克制、专业，充满深度洞察，同时具备强大的传播力。严格按照用户提供的结构和字数要求输出。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            # 自动剥离Markdown代码块
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            script_json = json.loads(clean_response)
            
            # 基础校验
            if not all(k in script_json for k in ["title", "hook", "script", "cta"]):
                raise ValueError("LLM输出缺少必要的键")

            script_json["duration"] = "3min"
            script_json["generated_by"] = self.agent_name
            script_json["version"] = self.version

            return script_json

        except Exception as e:
            print(f"✗ {self.agent_name} 生成脚本失败: {e}")
            return {
                "error": str(e),
                "title": "脚本生成失败",
                "hook": "",
                "script": "",
                "cta": "",
                "duration": "3min"
            }

    def _build_prompt(self, data: Dict[str, Any], input_type: str) -> str:
        """构建用于生成脚本的Prompt"""
        
        if input_type == 'hub':
            viewpoints = data.get("components", {}).get("viewpoints", [])
            cases = data.get("components", {}).get("cases", [])
            frameworks = data.get("components", {}).get("frameworks", [])
            core_content = f"- 核心观点: {json.dumps(viewpoints, ensure_ascii=False)}\n- 案例: {json.dumps(cases, ensure_ascii=False)}\n- 核心框架: {json.dumps(frameworks, ensure_ascii=False)}"
            instruction = "请基于以上从一篇深度文章中提取的核心观点、案例和框架，创作一个3分钟视频脚本。"

        elif input_type == 'trend':
            core_content = f"- 选题标题: {data.get('angle_title')}\n- 核心钩子: {data.get('hook')}\n- 核心论点: {data.get('core_argument')}"
            instruction = "请基于以上热点选题，创作一个3分钟视频脚本，深入阐述核心论点。"
        else:
            return "无效的输入类型"

        prompt = f"""
        # 任务
        你是一个顶级的视频脚本撰稿人。你的任务是根据我提供的核心材料，创作一个结构完整的3分钟视频脚本，并以指定的JSON格式输出。

        # 核心材料
        {core_content}

        # 脚本要求
        1.  **目标受众**: 创始人、企业家、高级管理者。
        2.  **内容风格**: 理性、克制、专业、有深度，符合“增长与变现战略顾问”的IP定位。
        3.  **脚本结构**:
            - **钩子 (Hook)**: 视频开头3-5秒，必须用一个强有力的提问或反常识观点抓住用户，激发好奇心。
            - **展开 (Body)**: 对核心观点进行系统性阐述。如果材料中有框架，要清晰地拆解框架的步骤；如果材料中有案例，要生动地讲述案例，并提炼关键洞察。
            - **拔高与总结 (Conclusion)**: 在脚本结尾，对全文进行总结，并提供一个超越内容本身的、更高维度的思考或建议，巩固你的专家身份。
            - **行动号召 (CTA)**: 设计一个自然的、非营销感的CTA，例如“关于这个话题，你有什么想补充的，评论区聊聊”或“我把完整的思考框架放在了公众号，感兴趣可以去看”。
        4.  **字数**: 脚本原文（script字段）严格控制在700-1000字之间。

        # 输出格式
        你必须严格按照以下JSON格式输出，不要添加任何额外的解释或说明文字。确保所有字段都存在且内容完整：
        {{
            "title": "[一个引人注目的视频标题，20字以内]",
            "hook": "[视频开头的强力钩子，一句话]",
            "script": "[完整的口播脚本原文，700-1000字]",
            "cta": "[结尾的行动号召文案]"
        }}
        """
        return prompt

if __name__ == '__main__':
    # 这是一个用于测试的示例
    print("✓ LongVideoScriptAgent 初始化，开始测试...")
    agent = LongVideoScriptAgent()

    # 测试1: 基于Hub组件
    print("\n[测试1] 基于Hub组件生成脚本...")
    mock_hub_data = {
        "components": {
            "viewpoints": [{"content": "创始人最大的挑战是认知错配，而非资金匮乏。"}],
            "cases": [{"title": "某公司因认知错误导致失败", "key_insight": "资本无法弥补战略上的短视。"}],
            "frameworks": [{"name": "克制型增长模型", "components": ["认知-战略-执行"]}]
        }
    }
    hub_script = agent.generate_script(mock_hub_data, 'hub')
    print(json.dumps(hub_script, ensure_ascii=False, indent=2))

    # 测试2: 基于热点选题
    print("\n[测试2] 基于热点选题生成脚本...")
    mock_trend_data = {
        "angle_title": "AI全面接管打工人岗位，普通人还有机会吗？",
        "hook": "都说AI要让一半人失业，但我认为，这反而是普通人拉开差距的最好机会。",
        "core_argument": "AI是杠杆，它会放大强者的优势，但普通人可以通过掌握使用AI的元能力，实现非对称的职业跃迁。关键不在于你会不会被替代，而在于你能不能成为那个使用AI的人。"
    }
    trend_script = agent.generate_script(mock_trend_data, 'trend')
    print(json.dumps(trend_script, ensure_ascii=False, indent=2))
