#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShortVideoAgent - 短视频脚本生成 Agent (V4.2)
根据大纲填充内容，生成完整的短视频脚本。
"""

import json
from typing import Dict, Any
from openai import OpenAI

class ShortVideoAgent:
    """接收大纲的一部分，生成完整的短视频脚本。"""

    def __init__(self):
        self.agent_name = "ShortVideoAgent"
        self.version = "1.0"
        self.client = OpenAI()

    def generate_content(self, outline_part: Dict[str, Any], hub_content: str) -> Dict[str, Any]:
        """
        根据大纲部分和原始Hub文章，生成短视频内容。

        Args:
            outline_part: 从大纲中提取的、与本平台相关的部分。
            hub_content: 原始的Hub文章全文，用于上下文参考。

        Returns:
            包含生成内容的字典。
        """
        prompt = self._build_prompt(outline_part, hub_content)
        
        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "你现在就是我本人，一个在商业圈摸爬滚打多年的创始人。你要用我（创始人）的口吻，对着镜头跟朋友聊天。不要端着，不要说教，就像在跟一个好朋友分享你最近的思考。你的任务是把【大纲要点】变成一段“人话”，一段能让人听进去、听完有启发的口播稿。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            
            content_json = json.loads(clean_response)
            
            if not all(k in content_json for k in ["title", "script_body"]):
                raise ValueError("LLM输出缺少必要的键: title, script_body")

            return content_json

        except Exception as e:
            print(f"✗ {self.agent_name} 生成内容失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, outline_part: Dict[str, Any], hub_content: str) -> str:
        """构建用于生成内容的Prompt"""
        
        outline_str = json.dumps(outline_part, ensure_ascii=False, indent=2)

        prompt = f"""
        # 任务
        你的任务是将以下【大纲要点】扩写成一段完整的、口语化的短视频脚本。你必须严格遵循大纲的结构（钩子、主体、结尾），并从【原始文章】中汲取细节和语气，确保内容丰富且忠于原文。

        # 大纲要点
        ```json
        {outline_str}
        ```

        # 原始文章 (供参考)
        ```markdown
        {hub_content}
        ```

        # 脚本要求
        1.  **说人话**: 忘掉书面语，用最简单、最直接的口语。多用短句，多用“你发现没”、“我跟你说”、“其实就是”这样的词。
        2.  **有节奏**: 稿子要有起伏，开头用一个反常识的观点或者一个故事勾住人，中间把道理一二三讲清楚，结尾给人一个明确的行动点。
        3.  **有干货**: 虽然是聊天，但得有价值。把【大纲要点】里的干货揉碎了，用自己的话讲出来，最好能带点我自己的例子或者故事。
        4.  **真人感**: 稿子里要有“我”的存在，有我的情绪、我的判断、我的经历。比如“我前两天就碰到个事儿...”、“这事儿吧，我琢磨了半天...”。

        # 输出格式
        你必须严格按照以下JSON格式输出，不要有任何多余的解释。

        ```json
        {{
            "title": "{outline_part.get('theme', '未命名视频')}",
            "script_body": "[这里是完整的、口语化的视频脚本，将钩子、主体、结尾无缝衔接成一篇完整的文章]"
        }}
        ```
        """
        return prompt
