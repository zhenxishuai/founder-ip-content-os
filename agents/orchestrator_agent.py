#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - 总控Agent (V4.2 - 大纲驱动版)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

# 显式导入所有新版Agent
from .outline_agent import OutlineAgent
from .short_video_agent import ShortVideoAgent
from .xiaohongshu_agent import XiaohongshuAgent
from .wechat_agent import WeChatAgent
from .moments_agent import MomentsAgent

class OrchestratorAgent:
    """V4.2总控Agent，负责调度所有子Agent，执行大纲驱动的内容生成工作流。"""

    def __init__(self, root_path="/home/ubuntu/founder-ip-content-os-full/"):
        self.agent_name = "OrchestratorAgent"
        self.version = "4.2"
        self.root_path = root_path
        self.setup_directories()

        # 实例化所有Agent
        self.outline_agent = OutlineAgent(root_path=self.root_path)
        self.platform_agents = {
            "短视频": ShortVideoAgent(),
            "小红书": XiaohongshuAgent(),
            "公众号": WeChatAgent(),
            "朋友圈": MomentsAgent(),
        }

    def setup_directories(self):
        """创建所有必需的目录。"""
        self.hub_path = os.path.join(self.root_path, "01_Hub文章")
        self.processed_hub_path = os.path.join(self.hub_path, "processed")
        self.delivery_path = os.path.join(self.root_path, "13_交付包")
        os.makedirs(self.processed_hub_path, exist_ok=True)
        os.makedirs(self.delivery_path, exist_ok=True)

    def execute_workflow(self, hub_filename: str):
        """为指定的Hub文章执行完整的大纲驱动工作流。"""
        print(f"🚀 OrchestratorAgent V{self.version} 开始为 {hub_filename} 执行工作流...")

        # 1. 读取Hub文章内容
        hub_content = self._read_hub_file(hub_filename)
        if not hub_content:
            print(f"✗ 无法读取Hub文章: {hub_filename}，工作流终止。")
            return

        # 2. 生成内容大纲
        print("  → 正在调用 OutlineAgent 生成内容大纲...")
        outline_data = self.outline_agent.generate_outline(hub_content)
        if "error" in outline_data:
            print(f"✗ 生成大纲失败: {outline_data['error']}，工作流终止。")
            return
        
        # 保存大纲文档
        outline_filename = self._save_outline(outline_data, hub_filename)
        print(f"  ✓ 内容大纲已生成并保存到: {outline_filename}")

        # 3. 生成第一天的内容
        print("\n  → 正在为第一天生成各平台内容...")
        day_1_outline = next((item for item in outline_data.get("weekly_content_outline", []) if item.get("day") == 1), None)
        
        if not day_1_outline:
            print("✗ 在大纲中未找到第一天的内容，无法继续生成。")
            return

        # 根据用户要求，每天生成 小红书、短视频、朋友圈，第1天额外生成公众号长文
        platforms_to_generate = ["公众号", "小红书", "短视频", "朋友圈"]
        day_1_content = {}

        for platform_name in platforms_to_generate:
            # 从大纲中找到第1天对应平台的条目
            platform_outline_part = next(
                (item for item in outline_data.get("weekly_content_outline", [])
                 if item.get("day") == 1 and item.get("platform") == platform_name),
                None
            )
            if not platform_outline_part:
                print(f"  - 未在大纲中找到第1天平台 '{platform_name}' 的计划，跳过。")
                continue

            agent = self.platform_agents.get(platform_name)
            if agent:
                print(f"    - 调用 {agent.agent_name} 生成 [{platform_name}] 内容...")
                content = agent.generate_content(platform_outline_part, hub_content)
                day_1_content[platform_name] = content
                if "error" in content:
                    print(f"    ✗ {agent.agent_name} 生成失败: {content['error']}")
                else:
                    print(f"    ✓ {agent.agent_name} 内容生成成功。")
            else:
                print(f"    - 未找到平台 '{platform_name}' 对应的Agent，跳过。")

        # 4. 保存第一天的内容
        day_1_filename = self._save_day_1_content(day_1_content, hub_filename)
        print(f"  ✓ 第一天内容已生成并保存到: {day_1_filename}")

        # 5. 标记Hub为已处理
        self._mark_hub_processed(hub_filename)

        print(f"\n✅ V{self.version} 工作流执行完毕。")
        print(f"请查看交付目录: {self.delivery_path}")

    def _read_hub_file(self, filename: str) -> str:
        """读取Hub文章内容。"""
        filepath = os.path.join(self.hub_path, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _save_outline(self, outline_data: Dict[str, Any], hub_filename: str) -> str:
        """将JSON大纲格式化为Markdown并保存。"""
        base_name = os.path.splitext(hub_filename)[0]
        filename = os.path.join(self.delivery_path, f"{base_name}_一周内容大纲.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 《{base_name}》一周内容大纲\n\n")
            for day_plan in outline_data.get("weekly_content_outline", []):
                f.write(f"## Day {day_plan['day']}: {day_plan['platform']} - {day_plan['theme']}\n\n")
                if 'title_suggestion' in day_plan:
                    f.write(f"**标题建议:** {day_plan['title_suggestion']}\n\n")
                if 'content_structure' in day_plan:
                    for section in day_plan['content_structure']:
                        f.write(f"- **{section['section'].capitalize()}:** {section['key_point'] if 'key_point' in section else ', '.join(section.get('key_points', []))}\n")
                if 'methods' in day_plan:
                    for method in day_plan['methods']:
                        f.write(f"- **方法{method['method_index']} ({method['method_name']}):** {method['key_point']}\n")
                if 'key_points_by_section' in day_plan:
                    for section, point in day_plan['key_points_by_section'].items():
                        f.write(f"- **{section.capitalize()}:** {point}\n")
                if 'key_point' in day_plan and 'platform' in day_plan and day_plan['platform'] == '朋友圈':
                     f.write(f"- **核心文案:** {day_plan['key_point']}\n")
                f.write("\n---\n\n")
        return filename

    def _save_day_1_content(self, day_1_content: Dict[str, Any], hub_filename: str) -> str:
        """将第一天的所有生成内容保存到一个Markdown文件。"""
        base_name = os.path.splitext(hub_filename)[0]
        filename = os.path.join(self.delivery_path, f"{base_name}_第一天发布内容.md")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 《{base_name}》第一天发布内容\n\n")
            for platform, content in day_1_content.items():
                f.write(f"## 平台: {platform}\n\n")
                if "error" in content:
                    f.write(f"**生成失败:** {content['error']}\n\n")
                else:
                    f.write(f"**标题:** {content.get('title', 'N/A')}\n\n")
                    if 'body' in content:
                        f.write(f"**正文:**\n{content['body']}\n\n")
                    if 'script_body' in content:
                        f.write(f"**脚本:**\n{content['script_body']}\n\n")
                    if 'article_body' in content:
                        f.write(f"**文章:**\n{content['article_body']}\n\n")
                    if 'post_text' in content:
                        f.write(f"**文案:**\n{content['post_text']}\n\n")
                    if 'tags' in content:
                        f.write(f"**标签:** {' '.join(content['tags'])}\n\n")
                f.write("\n---\n\n")
        return filename

    def _mark_hub_processed(self, filename: str):
        """将处理过的Hub文章移动到processed目录。"""
        src = os.path.join(self.hub_path, filename)
        dst = os.path.join(self.processed_hub_path, filename)
        if os.path.exists(src):
            os.rename(src, dst)
            print(f"  ✓ Hub文章已标记为已处理: {filename}")

if __name__ == '__main__':
    # 这是一个用于测试的示例
    # 实际使用时，应该从外部传入hub_filename
    orchestrator = OrchestratorAgent()
    
    # 创建一个模拟的Hub文章用于测试
    mock_hub_filename = "mock_hub_article.txt"
    mock_hub_content = """
    # 网感不是天赋，是训练出来的
    很多人觉得网感是天生的，但MCN的经验告诉我们，网感完全是一套可以被刻意练习的方法论。我们总结了4个核心方法：
    第一，分析选题。不要自己瞎想，去搜索，看同类爆款，爆款选题自带流量。
    第二，训练开头。一个好的开头价值千金。你必须用3秒抓住用户，否则就会被划走。
    第三，分析框架。把爆款视频一帧一帧拆解，你会发现它们的结构惊人地相似。
    第四，建立素材库。高手从不临时找灵感，他们有一个自己的“弹药库”。
    """
    with open(os.path.join(orchestrator.hub_path, mock_hub_filename), 'w', encoding='utf-8') as f:
        f.write(mock_hub_content)
    
    orchestrator.execute_workflow(hub_filename=mock_hub_filename)
