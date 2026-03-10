#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChatAgent - 公众号文章生成 Agent (V4.2)
根据大纲填充内容，生成完整的公众号文章。
"""

import json
from typing import Dict, Any
from openai import OpenAI

class WeChatAgent:
    """接收大纲的一部分，生成完整的公众号文章。"""

    def __init__(self):
        self.agent_name = "WeChatAgent"
        self.version = "1.0"
        self.client = OpenAI()

    def generate_content(self, outline_part: Dict[str, Any], hub_content: str) -> Dict[str, Any]:
        """
        根据大纲部分和原始Hub文章，生成公众号文章。

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
                    {"role": "system", "content": "你是一位资深的商业内容撰稿人，为创始人IP撰写深度公众号文章。你的任务是严格按照给定的【大纲要点】和【原始文章】，将要点扩写成一篇逻辑严谨、论证充分、有深度的文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            
            content_json = json.loads(clean_response)
            
            if not all(k in content_json for k in ["title", "article_body"]):
                raise ValueError("LLM输出缺少必要的键: title, article_body")

            return content_json

        except Exception as e:
            print(f"✗ {self.agent_name} 生成内容失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, outline_part: Dict[str, Any], hub_content: str) -> str:
        """构建用于生成内容的Prompt"""
        
        outline_str = json.dumps(outline_part, ensure_ascii=False, indent=2)

        prompt = f"""
        # 任务
        你的任务是将以下【大纲要点】扩写成一篇完整的、有深度的公众号文章。你必须严格遵循大纲的“开头-发展-转折-收尾”结构，并从【原始文章】中汲取论据、案例和细节，确保文章内容丰富、逻辑严谨。

        # 大纲要点
        ```json
        {outline_str}
        ```

        # 原始文章 (供参考)
        ```markdown
        {hub_content}
        ```

        # 文章要求
        1.  **深度分析**: 不仅仅是复述要点，而是要深入阐述每个部分的“是什么”、“为什么”、“怎么做”。
        2.  **逻辑严谨**: 确保文章的起承转合自然流畅，论证过程有说服力。
        3.  **内容丰富**: 充分利用【原始文章】中的信息，用具体的例子、数据或引言来支撑你的观点。
        4.  **专业风格**: 保持“增长与变现战略顾问”的专业、理性的风格。
        5.  **字数**: 全文建议在1500-2000字之间。

        # 输出格式
        你必须严格按照以下JSON格式输出，不要有任何多余的解释。

        ```json
        {{
            "title": "{outline_part.get('theme', '未命名文章')}",
            "article_body": "[这里是完整的公众号文章正文，段落清晰，逻辑严谨，严格按照“开头-发展-转折-收尾”的结构组织]"
        }}
        ```
        """
        return prompt
