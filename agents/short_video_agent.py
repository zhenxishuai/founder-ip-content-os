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
                    {"role": "system", "content": "你是一个顶级的短视频脚本撰稿人。你的任务是严格按照给定的【大纲要点】和【原始文章】，将要点扩写成一段流畅、完整、口语化的视频脚本。你必须忠于大纲的结构和核心思想。"},
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
        1.  **口语化**: 想象你正在对镜头说话，使用自然、流畅的语言。
        2.  **内容完整**: 将大纲中的每一个`key_point`都充分展开，形成一段有逻辑、有血有肉的脚本。
        3.  **忠于大纲**: 严格保持“钩子-主体-结尾”的结构，不要改变要点的顺序或核心思想。
        4.  **字数**: 脚本全文（script_body字段）建议在400-600字之间。

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
