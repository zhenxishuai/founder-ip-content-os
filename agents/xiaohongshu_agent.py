#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaohongshuAgent - 小红书图文生成 Agent (V4.2)
根据大纲填充内容，生成完整的小红书图文笔记。
"""

import json
from typing import Dict, Any
from openai import OpenAI

class XiaohongshuAgent:
    """接收大纲的一部分，生成完整的小红书图文笔记。"""

    def __init__(self):
        self.agent_name = "XiaohongshuAgent"
        self.version = "1.0"
        self.client = OpenAI()

    def generate_content(self, outline_part: Dict[str, Any], hub_content: str) -> Dict[str, Any]:
        """
        根据大纲部分和原始Hub文章，生成小红书内容。

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
                    {"role": "system", "content": "你是一位顶级的社交媒体内容创作者，尤其擅长小红书平台。你的任务是严格按照给定的【大纲要点】和【原始文章】，将要点扩写成一篇吸引人的、结构清晰的小红书图文笔记。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            
            content_json = json.loads(clean_response)
            
            # 兼容LLM可能使用的不同键名
            normalized = {}
            # 标题字段
            for key in ["title", "标题", "note_title"]:
                if key in content_json:
                    normalized["title"] = content_json[key]
                    break
            # 正文字段
            for key in ["body", "正文", "content", "note_body", "text"]:
                if key in content_json:
                    normalized["body"] = content_json[key]
                    break
            # 标签字段
            for key in ["tags", "标签", "hashtags"]:
                if key in content_json:
                    normalized["tags"] = content_json[key]
                    break
            
            if not all(k in normalized for k in ["title", "body"]):
                # 如果还是找不到，把整个JSON当body
                normalized["title"] = content_json.get("title", "未命名")
                normalized["body"] = json.dumps(content_json, ensure_ascii=False)
                normalized["tags"] = []
            
            if "tags" not in normalized:
                normalized["tags"] = []

            return normalized

        except Exception as e:
            print(f"✗ {self.agent_name} 生成内容失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, outline_part: Dict[str, Any], hub_content: str) -> str:
        """构建用于生成内容的Prompt"""
        
        outline_str = json.dumps(outline_part, ensure_ascii=False, indent=2)

        prompt = f"""
        # 任务
        你的任务是将以下【大纲要点】扩写成一篇完整的小红书图文笔记。你必须严格遵循大纲的结构和方法顺序，并从【原始文章】中汲取细节和语气，确保内容有价值、易读、符合小红书风格。

        # 大纲要点
        ```json
        {outline_str}
        ```

        # 原始文章 (供参考)
        ```markdown
        {hub_content}
        ```

        # 笔记要求
        1.  **小红书风格**: 使用表情符号（emoji）来增加可读性，段落之间空一行，多用短句。
        2.  **结构清晰**: 严格按照大纲中`methods`的顺序（1, 2, 3, 4...）来组织正文，每一段对应一个方法。
        3.  **内容完整**: 将大纲中的每一个`key_point`都充分展开，解释清楚每个方法是什么、为什么、怎么做。
        4.  **标题吸引人**: 使用大纲中建议的`title_suggestion`作为标题，或者在其基础上进行微调，使其更具吸引力。
        5.  **包含标签**: 在笔记末尾，生成5-7个相关的小红书标签（tags）。

        # 输出格式
        你必须严格按照以下JSON格式输出，不要有任何多余的解释。

        ```json
        {{
            "title": "[这里是最终的小红书标题]",
            "body": "[这里是完整的小红书正文，包含emoji，段落分明，严格按方法顺序组织]",
            "tags": [
                "#[标签1]",
                "#[标签2]",
                "#[标签3]",
                "#[标签4]",
                "#[标签5]"
            ]
        }}
        ```
        """
        return prompt
