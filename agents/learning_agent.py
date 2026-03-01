#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LearningAgent - 爆款自动学习Agent (V4核心)
"""

import json
import os
from typing import List, Dict, Any

from openai import OpenAI

class LearningAgent:
    """从内容表现数据中学习，提取爆款结构模板。"""

    def __init__(self, asset_path: str):
        self.agent_name = "LearningAgent"
        self.version = "4.0"
        self.client = OpenAI()
        self.asset_path = asset_path
        self.structure_library_path = os.path.join(self.asset_path, "structure_library.json")
        self.score_threshold = 80 # 爆款分数阈值

    def learn_from_metrics(self, metrics_data: List[Dict[str, Any]], content_data: Dict[str, str]) -> bool:
        """
        分析指标，识别爆款，提取结构，并更新资产库。

        Args:
            metrics_data: 内容表现指标列表。
            content_data: 内容ID到内容的映射字典。

        Returns:
            如果成功学习到新模板，则返回True。
        """
        new_templates_learned = 0
        for metric in metrics_data:
            score = self._calculate_score(metric)
            metric["score"] = score # 在原数据上附加分数

            if score >= self.score_threshold:
                print(f"✓ 检测到爆款内容: {metric['content_id']} (分数: {score:.2f})，开始提取结构...")
                content_text = content_data.get(metric['content_id'])
                if not content_text:
                    print(f"✗ 警告: 找不到爆款内容ID {metric['content_id']} 的原文，跳过。")
                    continue
                
                structure_template = self._extract_structure(content_text)
                if structure_template:
                    self._update_structure_library(structure_template)
                    new_templates_learned += 1
        
        print(f"✓ 学习流程完成。共学习到 {new_templates_learned} 个新爆款模板。")
        return new_templates_learned > 0

    def _calculate_score(self, metric: Dict[str, Any]) -> float:
        """根据V4规格计算内容得分"""
        completion_rate = metric.get("completion_rate", 0) * 0.4
        forward_rate = metric.get("forward_rate", 0) * 0.3
        favorite_rate = metric.get("favorite_rate", 0) * 0.2
        comment_rate = metric.get("comment_rate", 0) * 0.1
        return (completion_rate + forward_rate + favorite_rate + comment_rate) * 100 # 转换为百分制

    def _extract_structure(self, content_text: str) -> Dict[str, Any]:
        """调用LLM逆向工程，提取内容的结构模板"""
        prompt = self._build_prompt(content_text)
        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "你是一个顶级的内内容策略分析师。你的任务是逆向工程一篇爆款视频脚本，提取其可复用的结构模板。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            if '```json' in raw_response:
                clean_response = raw_response.split('```json')[1].split('```')[0].strip()
            else:
                clean_response = raw_response.strip()
            
            return json.loads(clean_response)
        except Exception as e:
            print(f"✗ 提取结构失败: {e}")
            return {}

    def _build_prompt(self, content_text: str) -> str:
        return f"""
        # 任务
        分析以下这篇已被验证为“爆款”的视频脚本。你的目标是提炼出其内在的、可被复用的“结构模板”。不要总结内容，要总结结构！

        # 爆款脚本原文
        ---
        {content_text}
        ---

        # 提取要求
        1.  **template_name**: 为这个结构起一个言简意赅的名字，例如：“反常识钩子 + 3个平行论点 + 升华结尾”。
        2.  **hook_type**: 描述其钩子（开头）的类型，例如：“反常识提问”、“数据冲击”、“身份共鸣”。
        3.  **body_structure**: 描述其主体部分的论证结构，例如：“总分总结构”、“时间线叙事”、“问题-解决方案-效果展示”。
        4.  **conclusion_type**: 描述其结尾的类型，例如：“总结升华”、“开放式提问”、“强力行动号召”。
        5.  **applicable_scenario**: 描述这个结构模板最适用于哪类主题，例如：“商业模式分析”、“个人成长方法论”、“行业趋势解读”。

        # 输出格式
        请严格按照以下JSON格式输出，不要添加任何额外的解释或说明文字：
        {{
            "template_name": "[模板名称]",
            "hook_type": "[钩子类型]",
            "body_structure": "[主体结构]",
            "conclusion_type": "[结尾类型]",
            "applicable_scenario": "[适用场景]"
        }}
        """

    def _update_structure_library(self, template: Dict[str, Any]):
        """将新模板写入结构库，如果已存在则更新"""
        library = []
        if os.path.exists(self.structure_library_path):
            with open(self.structure_library_path, 'r', encoding='utf-8') as f:
                library = json.load(f)
        
        # 简单起见，这里用模板名称作为唯一标识，实际可使用更复杂的hash
        template_name = template.get("template_name")
        found = False
        for item in library:
            if item.get("template_name") == template_name:
                # 如果已存在，可以更新其数据，例如增加一个使用计数
                item["learned_count"] = item.get("learned_count", 1) + 1
                found = True
                break
        
        if not found:
            template["learned_count"] = 1
            library.append(template)

        with open(self.structure_library_path, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)
        print(f"✓ 结构库已更新。模板: '{template_name}'")

if __name__ == '__main__':
    print("✓ LearningAgent 初始化，开始测试...")
    agent = LearningAgent()

    # 模拟数据
    mock_metrics = [
        {
            "content_id": "video_001",
            "completion_rate": 0.95, # 95%
            "forward_rate": 0.80,    # 80%
            "favorite_rate": 0.90,   # 90%
            "comment_rate": 0.60     # 60%
        },
        {
            "content_id": "video_002",
            "completion_rate": 0.25,
            "forward_rate": 0.01,
            "favorite_rate": 0.05,
            "comment_rate": 0.02
        }
    ]
    
    mock_content = {
        "video_001": """都说AI要让一半人失业，但我认为，这反而是普通人拉开差距的最好机会。大家好，我是你们的增长与变现战略顾问。AI的到来，并非意味着普通人就没有机会了。恰恰相反，它为我们提供了一个重新定义职业、实现跃迁的黄金窗口期。关键在于，你是否具备与AI协作的元能力，是否拥有AI赋能的思维，以及是否能深耕人类独有的核心优势。那些能够主动拥抱AI、驾驭AI的人，将成为新时代的赢家。关于AI与职业发展，你还有哪些思考或困惑？欢迎在评论区留言，我们一起探讨。""",
        "video_002": """今天分享一个简单的效率工具，可以帮助你节省时间。"""
    }

    # 执行学习
    agent.learn_from_metrics(mock_metrics, mock_content)

    # 打印结果
    if os.path.exists(agent.structure_library_path):
        print("\n✓ 学习完成，当前结构库内容:")
        with open(agent.structure_library_path, 'r', encoding='utf-8') as f:
            print(f.read())
