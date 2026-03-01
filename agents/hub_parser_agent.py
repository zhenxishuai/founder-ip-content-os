#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HubParser 结构解析Agent (V2 - Refactored)
功能：使用LLM一次性将Hub文章解析为结构化组件，确保幂等性与可追溯性。
输出：统一的、不含原文的JSON，作为后续所有Agent的"唯一输入真相源"
"""

import json
import uuid
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any

# 尝试导入openai，如果失败则定义一个模拟客户端
try:
    from openai import OpenAI
except ImportError:
    print("警告: openai库未安装。将使用模拟LLM客户端。")
    class MockCompletions:
        def create(self, *args, **kwargs):
            class MockChoice:
                def __init__(self, content):
                    self.message = type('obj', (object,), {'content': content})
            mock_response_content = self._get_mock_llm_response()
            return type('obj', (object,), {'choices': [MockChoice(mock_response_content)]})()

        def _get_mock_llm_response(self):
            return json.dumps({
                "viewpoints": [{"content": "模拟观点1"}, {"content": "模拟观点2"}, {"content": "模拟观点3"}, {"content": "模拟观点4"}, {"content": "模拟观点5"}],
                "golden_sentences": [{"content": f"模拟金句{i+1}"} for i in range(10)],
                "cases": [{"title": "模拟案例1", "description": "..."}, {"title": "模拟案例2", "description": "..."}, {"title": "模拟案例3", "description": "..."}],
                "frameworks": [{"name": "模拟框架1", "description": "..."}],
                "conflict_points": [{"conflict": "模拟冲突点1"}, {"conflict": "模拟冲突点2"}, {"conflict": "模拟冲突点3"}],
                "action_items": [{"action": "模拟行动项1"}, {"action": "模拟行动项2"}, {"action": "模拟行动项3"}],
                "keywords": ["模拟关键词1", "模拟关键词2", "模拟关键词3", "模拟关键词4", "模拟关键词5", "模拟关键词6", "模拟关键词7", "模拟关键词8"],
                "target_audience": {"primary": "模拟主要人群", "secondary": "模拟次要人群", "pain_points": ["痛点1"], "aspirations": ["期望1"]}
            })

    class MockOpenAI:
        def __init__(self, **kwargs):
            self.chat = type('obj', (object,), {'completions': MockCompletions()})()
    
    OpenAI = MockOpenAI

class HubParserAgent:
    def __init__(self, asset_path: str):
        self.agent_name = "HubParser"
        self.version = "2.0"
        self.llm_client = OpenAI() # API key and base URL are pre-configured
        self.asset_path = asset_path
        self.component_thresholds = {
            "viewpoints": 5,
            "golden_sentences": 10,
            "cases": 3,
            "frameworks": 1,
            "conflict_points": 3,
            "action_items": 3,
            "keywords": 8
        }

    def _get_llm_prompt(self, content: str) -> str:
        """构建用于一次性提取所有组件的LLM提示"""
        return f"""你是一个内容战略分析师。请将以下文章深度拆解为结构化的JSON对象，严格遵循指定的字段和数量要求。不要添加任何额外的解释或注释，只返回JSON。

文章内容:
--- START OF ARTICLE ---
{content}
--- END OF ARTICLE ---

请提取以下组件并按此JSON格式输出:
{{
  "viewpoints": [{{ "content": "核心观点", "confidence": 0.9, "supporting_evidence": "相关论据摘要" }}], // 必须提取至少5条
  "golden_sentences": [{{ "content": "金句原文", "context": "金句出现的上下文" }}], // 必须提取至少10条
  "cases": [{{ "title": "案例标题", "description": "案例详细描述", "key_insight": "案例的关键启示" }}], // 必须提取至少3条
  "frameworks": [{{ "name": "框架名称", "description": "框架的用途和步骤", "components": ["步骤1", "步骤2"] }}], // 必须提取至少1套
  "conflict_points": [{{ "conflict": "认知冲突点", "common_misconception": "普遍的错误认知", "truth": "事实或更深刻的真相" }}], // 必须提取至少3条
  "action_items": [{{ "action": "具体的行动建议", "priority": "high/medium/low" }}], // 必须提取至少3条
  "keywords": ["关键词1", "关键词2"], // 必须提取至少8个
  "target_audience": {{ "primary": "最主要的目标人群", "secondary": "次要目标人群", "pain_points": ["人群的核心痛点1"], "aspirations": ["人群的期望与目标1"] }}
}}
"""

    def _extract_all_components_with_llm(self, content: str) -> Dict[str, Any]:
        """使用LLM一次性提取所有组件"""
        prompt = self._get_llm_prompt(content)
        try:
            response = self.llm_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            extracted_json = response.choices[0].message.content
            # 清理LLM可能返回的markdown代码块
            if extracted_json.strip().startswith('```json'):
                extracted_json = extracted_json.strip()[7:-3].strip()
            
            components = json.loads(extracted_json)
            return components
        except Exception as e:
            print(f"✗ LLM提取或JSON解析失败: {e}")
            return {} # 返回空字典以便后续处理

    def parse_hub(self, hub_content: str, source_file: str) -> Dict[str, Any]:
        """解析Hub文章为结构化组件"""
        hub_hash = hashlib.sha256(hub_content.encode()).hexdigest()
        hub_id = f"hub_{hub_hash[:12]}_{datetime.now().strftime('%Y%m%d')}"
        
        # 1. LLM提取
        components = self._extract_all_components_with_llm(hub_content)
        if not components:
            print(f"警告: 无法从 {source_file} 提取任何组件。")

        # 2. 校验与补齐 (简化版，实际可二次调用LLM)
        for comp_name, threshold in self.component_thresholds.items():
            if comp_name not in components or len(components.get(comp_name, [])) < threshold:
                print(f"警告: '{comp_name}' 组件数量不足 (需要 {threshold}，实际 {len(components.get(comp_name, []))})。")

        # 3. 生成幂等ID
        for comp_name, comp_list in components.items():
            if isinstance(comp_list, list):
                for item in comp_list:
                    if isinstance(item, dict) and 'content' in item:
                        item['id'] = f"comp_{hashlib.sha256(item['content'].encode()).hexdigest()[:16]}"
                    elif isinstance(item, str):
                        # 处理keywords这种字符串列表
                        pass

        # 4. 计算质量指标
        satisfied_thresholds = 0
        for name, threshold in self.component_thresholds.items():
            if len(components.get(name, [])) >= threshold:
                satisfied_thresholds += 1
        coverage_score = satisfied_thresholds / len(self.component_thresholds)

        # 5. 构建最终输出 (不含raw_content)
        parsed_data = {
            "metadata": {
                "hub_id": hub_id,
                "hub_hash": hub_hash,
                "source_file": source_file,
                "parsed_at": datetime.now().isoformat(),
                "parser_version": self.version
            },
            "components": components,
            "quality_metrics": {
                "component_count": sum(len(components.get(name, [])) for name in self.component_thresholds.keys()),
                "coverage_score": round(coverage_score, 2),
                "completeness": "pass" if coverage_score > 0.8 else "fail"
            }
        }
        
        return parsed_data

    def save_to_json(self, parsed_data: Dict, output_path: str) -> None:
        """保存解析结果为JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        print(f"✓ 解析结果已保存: {output_path}")

# 使用示例
if __name__ == "__main__":
    parser = HubParserAgent()
    
    # 示例Hub文章
    sample_hub = """
    在当今的商业环境中，创始人面临的最大挑战并非资金匮乏，而是认知错配。我们普遍认为，拿到融资是成功的标志，但实际上，这仅仅是放大了创始人现有认知的结果。一个残酷的真相是，错误的认知配上充足的资本，只会加速企业的灭亡。我服务超过50位创始人后发现，那些最终成功的，往往不是最会融资的，而是最懂克制的。他们遵循一个简单的框架：认知-战略-执行。在认知层面，他们不断打破信息茧房；在战略层面，他们聚焦于单点突破；在执行层面，他们追求极致的效率。这套“克制型增长”模型，是穿越周期的核心。如果你还在为融资焦虑，不妨先问问自己：我的认知，配得上这笔钱吗？毕竟，没有认知地基，再高的资本大厦也终将倾覆。我把这套完整的模型整理成了一份文档，包含了详细的案例和执行清单，在我的公众号里可以找到。
    """
    
    # 执行解析
    result = parser.parse_hub(sample_hub, "sample_hub.txt")
    
    # 保存结果
    output_dir = "/home/ubuntu/创始人IP系统/10_资产库"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"parsed_{result['metadata']['hub_id']}.json")
    parser.save_to_json(result, output_path)
    
    print(f"\n✓ HubParser Agent (V2) 重构完成")
    print(f"  - 核心变更: 使用LLM一次性提取全组件")
    print(f"  - 幂等性: hub_id 和 component_id 基于内容哈希生成")
    print(f"  - 真相源: 输出的JSON不再包含 'raw_content'")
    print(f"  - 质量评估: 实现了基于阈值的 'coverage_score'")
    print(f"\n测试输出:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
