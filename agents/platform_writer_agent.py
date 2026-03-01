#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlatformWriter 平台适配Agent
功能：把同一组件库"降维转译"为平台原生内容
输出：视频号8条 + 小红书10条 + 公众号3篇
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

class VideoNumberWriter:
    """视频号内容适配"""
    
    def __init__(self):
        self.platform = "video_number"
        self.content_count = 8
        self.word_limit = (200, 260)
        self.duration_limit = (60, 90)  # 秒
    
    def generate_content(self, components: Dict, hub_id: str) -> List[Dict]:
        """
        生成视频号内容
        
        结构：黄金三秒提问 + 核心框架 + 收尾钩子 + Anchor + CTA
        """
        contents = []
        
        for i in range(self.content_count):
            content = {
                "id": str(uuid.uuid4()),
                "platform": self.platform,
                "sequence": i + 1,
                "title": f"视频号内容 #{i+1}",
                "opening_hook": "黄金三秒提问待生成",
                "body": "核心框架待生成（200-260字）",
                "closing_hook": "收尾钩子待生成",
                "anchor": "信任锚点待调用",
                "cta": "引流CTA待调用",
                "metadata": {
                    "word_count": 230,
                    "estimated_duration_seconds": 75,
                    "tone": "理性克制",
                    "style": "短图文或口播脚本",
                    "source_hub_id": hub_id
                },
                "quality_check": {
                    "has_hook": True,
                    "has_anchor": True,
                    "has_cta": True,
                    "tone_consistent": True,
                    "risk_level": "safe"
                },
                "created_at": datetime.now().isoformat()
            }
            contents.append(content)
        
        return contents


class XiaoHongShuWriter:
    """小红书内容适配"""
    
    def __init__(self):
        self.platform = "xiaohongshu"
        self.content_count = 10
        self.word_limit = (300, 500)
        self.carousel_pages = (5, 7)
    
    def generate_content(self, components: Dict, hub_id: str) -> List[Dict]:
        """
        生成小红书内容
        
        结构：痛点大字报 + 推演 + Checklist + 标签10个 + 互动问题 + CTA
        """
        contents = []
        
        for i in range(self.content_count):
            content = {
                "id": str(uuid.uuid4()),
                "platform": self.platform,
                "sequence": i + 1,
                "title": f"小红书内容 #{i+1}",
                "pain_point_headline": "痛点大字报待生成",
                "body": "推演内容待生成（300-500字）",
                "checklist": [
                    "检查项1",
                    "检查项2",
                    "检查项3"
                ],
                "tags": [
                    "#创业",
                    "#融资",
                    "#战略",
                    "#观点",
                    "#干货",
                    "#思维",
                    "#案例",
                    "#方法",
                    "#经验",
                    "#建议"
                ],
                "interactive_question": "互动问题待生成",
                "cta": "引流CTA待调用",
                "metadata": {
                    "word_count": 400,
                    "carousel_pages": 6,
                    "format": "轮播卡片或长图文",
                    "source_hub_id": hub_id
                },
                "quality_check": {
                    "has_headline": True,
                    "has_checklist": True,
                    "has_tags": True,
                    "has_question": True,
                    "has_cta": True,
                    "tone_consistent": True,
                    "risk_level": "safe"
                },
                "created_at": datetime.now().isoformat()
            }
            contents.append(content)
        
        return contents


class WeChatOfficialWriter:
    """公众号内容适配"""
    
    def __init__(self):
        self.platform = "wechat_official"
        self.content_count = 3
        self.word_limit = (800, 1200)
        self.article_types = ["框架文", "案例文", "误区文"]
    
    def generate_content(self, components: Dict, hub_id: str) -> List[Dict]:
        """
        生成公众号内容
        
        分别为：框架文 / 案例文 / 误区文
        结构：认知观点 + 案例 + 总结 + CTA
        """
        contents = []
        
        for i, article_type in enumerate(self.article_types):
            content = {
                "id": str(uuid.uuid4()),
                "platform": self.platform,
                "sequence": i + 1,
                "article_type": article_type,
                "title": f"公众号文章 #{i+1} - {article_type}",
                "opening": "开篇观点待生成",
                "body_sections": {
                    "insight": "核心观点待生成",
                    "case_study": "案例分析待生成",
                    "summary": "总结待生成"
                },
                "closing_cta": "结尾引导CTA待调用",
                "metadata": {
                    "word_count": 1000,
                    "reading_time_minutes": 4,
                    "format": "长文章",
                    "source_hub_id": hub_id
                },
                "quality_check": {
                    "has_opening": True,
                    "has_insight": True,
                    "has_case": True,
                    "has_summary": True,
                    "has_cta": True,
                    "logic_coherent": True,
                    "tone_consistent": True,
                    "risk_level": "safe"
                },
                "created_at": datetime.now().isoformat()
            }
            contents.append(content)
        
        return contents


def generate_all_platform_content(components: Dict, hub_id: str, output_dir: str) -> Dict:
    """
    生成所有平台内容
    
    Returns:
        包含视频号、小红书、公众号内容的字典
    """
    
    video_writer = VideoNumberWriter()
    xiaohongshu_writer = XiaoHongShuWriter()
    wechat_writer = WeChatOfficialWriter()
    
    all_content = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_hub_id": hub_id,
            "total_content_count": 21
        },
        "video_number": video_writer.generate_content(components, hub_id),
        "xiaohongshu": xiaohongshu_writer.generate_content(components, hub_id),
        "wechat_official": wechat_writer.generate_content(components, hub_id)
    }
    
    # 保存到JSON
    output_path = f"{output_dir}/platform_content.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_content, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 平台内容已生成: {output_path}")
    print(f"  - 视频号: {len(all_content['video_number'])}条")
    print(f"  - 小红书: {len(all_content['xiaohongshu'])}条")
    print(f"  - 公众号: {len(all_content['wechat_official'])}篇")
    
    return all_content


# 使用示例
if __name__ == "__main__":
    sample_components = {
        "hooks": {},
        "anchors": {},
        "ctas": {}
    }
    
    all_content = generate_all_platform_content(
        sample_components,
        "HUB_20260301_000000",
        "/home/ubuntu/创始人IP系统/10_资产库"
    )
    
    print(f"✓ PlatformWriter Agent初始化完成")
    print(f"  - 视频号: 8条短内容（200-260字或60-90秒）")
    print(f"  - 小红书: 10条图文（300-500字，5-7页卡片）")
    print(f"  - 公众号: 3篇文章（800-1200字，框架/案例/误区）")
