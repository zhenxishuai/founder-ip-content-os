#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MomentsAgent - 朋友圈文案生成 Agent (V4.2)
根据大纲填充内容，生成一条朋友圈文案。
"""

import json
from typing import Dict, Any
from openai import OpenAI

class MomentsAgent:
    """接收大纲的一部分，生成一条朋友圈文案。"""

    def __init__(self):
        self.agent_name = "MomentsAgent"
        self.version = "1.0"
        self.client = OpenAI()

    def generate_content(self, outline_part: Dict[str, Any], hub_content: str) -> Dict[str, Any]:
        """
        根据大纲部分和原始Hub文章，生成朋友圈文案。

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
                    {"role": "system", "content": "你是一位精通社交文案的专家，为创始人IP撰写朋友圈。你是一位顶级的社交媒体文案专家，为创始人IP撰写朋友圈“短文章”。你的任务是根据给定的【大纲要点】，将其扩展成一篇300字左右、有场景感、有个人思考、能引发共鸣的朋友圈文案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            
            content_json = json.loads(clean_response)
            
            if "post_text" not in content_json:
                raise ValueError("LLM输出缺少必要的键: post_text")

            return content_json

        except Exception as e:
            print(f"✗ {self.agent_name} 生成内容失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, outline_part: Dict[str, Any], hub_content: str) -> str:
        """构建用于生成内容的Prompt"""
        
        outline_str = json.dumps(outline_part, ensure_ascii=False, indent=2)

        prompt = f"""
        # 任务
        你的任务是将以下【大纲要点】提炼成一条精悍、有洞察、适合发布在朋友圈的文案。你可以参考【原始文章】来理解上下文，但最终文案必须简洁有力。

        # 大纲要点
        ```json
        {outline_str}
        ```

        # 原始文章 (供参考)
        ```markdown
        {hub_content}
        ```

        # 文案要求
        1.  **短文章风格**: 全文约300字，不能是干巴巴的几句话，要有场景、有故事、有思考、有金句。
        2.  **真人感**: 必须用第一人称“我”来写，语气要像一个真实的人在分享自己的观察和感悟，可以带一点口语化的表达。
        3.  **有价值**: 不能是无病呻吟，必须包含至少一个来自【大纲要点】的核心洞察或方法论，给读者带来启发。
        4.  **引导互动**: 结尾可以提出一个开放性问题，或者邀请大家在评论区讨论，增加互动。

        # 输出格式
        你必须严格按照以下JSON格式输出，不要有任何多余的解释。

        ```json
        {{
            "post_text": "[这里是最终的朋友圈“短文章”文案，约300字，有场景、有思考、有金句]"
        }}
        ```
        """
        return prompt
