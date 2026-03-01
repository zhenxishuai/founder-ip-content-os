#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonetizationAgent - 变现优化Agent (V4核心)
"""

import json
import os
from typing import Dict, Any

class MonetizationAgent:
    """分析内容并匹配最佳变现产品。"""

    def __init__(self, asset_path: str):
        self.agent_name = "MonetizationAgent"
        self.version = "4.0"
        self.asset_path = asset_path
        self.products_path = os.path.join(self.asset_path, "monetization_products.json")
        self.products = self._load_products()

    def _load_products(self) -> Dict[str, Any]:
        """加载变现产品库。""" 
        try:
            with open(self.products_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到变现产品库 {self.products_path}。将使用空产品列表。")
            # 创建一个空的示例文件
            default_products = {
                "products": [
                    {
                        "product_id": "course_ai_writing",
                        "name": "AI写作大师课",
                        "keywords": ["AI写作", "内容创作", "效率"],
                        "target_audience": ["自媒体人", "内容创作者"],
                        "cta_suggestion": "想学习如何用AI每天生产10篇高质量文章吗？点击链接，了解我的《AI写作大师课》。"
                    },
                    {
                        "product_id": "consult_startup_growth",
                        "name": "初创公司增长咨询",
                        "keywords": ["增长", "创业", "融资", "商业模式"],
                        "target_audience": ["创始人", "创业者"],
                        "cta_suggestion": "正在为你的项目增长发愁吗？预约我的1对1咨询，帮你梳理增长策略。"
                    }
                ]
            }
            with open(self.products_path, 'w', encoding='utf-8') as f:
                json.dump(default_products, f, ensure_ascii=False, indent=4)
            return default_products

    def analyze_and_suggest(self, content_script: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容脚本并提出变现建议。"""
        script_text = content_script.get("script", "")
        best_match = None
        max_score = 0

        for product in self.products.get("products", []):
            score = 0
            for keyword in product.get("keywords", []):
                if keyword.lower() in script_text.lower():
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = product

        if best_match:
            return {
                "product_id": best_match["product_id"],
                "suggestion": best_match["cta_suggestion"],
                "confidence": max_score / len(best_match.get("keywords", [1])) # 归一化得分
            }
        else:
            return {
                "product_id": None,
                "suggestion": "未找到合适的变现产品，建议使用通用引流CTA。",
                "confidence": 0
            }

if __name__ == '__main__':
    print("✓ MonetizationAgent 初始化...")
    agent = MonetizationAgent()
    
    # 模拟一个视频脚本输入
    mock_script = {
        "title": "AI如何重塑内容创作",
        "hook": "你还在为每天写不出东西而焦虑吗？",
        "script": "...在这个时代，AI写作已经成为内容创作者的必备技能。它极大地提升了我们的生产效率...",
        "duration": "3min",
        "cta": ""
    }
    
    suggestion = agent.analyze_and_suggest(mock_script)
    print("\n模拟脚本输入:")
    print(json.dumps(mock_script, ensure_ascii=False, indent=2))
    print("\n变现建议输出:")
    print(json.dumps(suggestion, ensure_ascii=False, indent=2))
    
    if suggestion["product_id"] == "course_ai_writing":
        print("\n✓ 测试成功：成功为AI写作脚本匹配到《AI写作大师课》。")
    else:
        print("\n✗ 测试失败：未能正确匹配变现产品。")
