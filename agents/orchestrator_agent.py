#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - 总控Agent (V4.1 - 增长与变现操作系统)
修复：显式导入、统一构造参数、QA回炉机制、真实排期CSV、TrendCrawler解耦
"""

import os
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 显式导入所有Agent
from .hub_parser_agent import HubParserAgent
from .long_video_script_agent import LongVideoScriptAgent
from .trend_crawler_agent import TrendCrawlerAgent
from .trend_analyzer_agent import TrendAnalyzerAgent
from .learning_agent import LearningAgent
from .monetization_agent import MonetizationAgent
from .asset_store import AssetStore
from .qa_agent import QAAgent


class OrchestratorAgent:
    """V4.1总控Agent，负责调度所有子Agent，执行增长与变现工作流。"""

    def __init__(self, root_path="/home/ubuntu/创始人IP系统/"):
        self.agent_name = "OrchestratorAgent"
        self.version = "4.1"
        self.root_path = root_path
        self.setup_directories()

        # 实例化所有Agent，统一传入asset_path
        self.hub_parser = HubParserAgent(asset_path=self.asset_path)
        self.long_video_script_agent = LongVideoScriptAgent(asset_path=self.asset_path)
        self.trend_crawler = TrendCrawlerAgent(asset_path=self.asset_path)
        self.trend_analyzer = TrendAnalyzerAgent(asset_path=self.asset_path)
        self.learning_agent = LearningAgent(asset_path=self.asset_path)
        self.monetization_agent = MonetizationAgent(asset_path=self.asset_path)
        self.asset_store = AssetStore(asset_path=self.asset_path)
        self.qa_agent = QAAgent(asset_path=self.asset_path)

    def setup_directories(self):
        """创建所有必需的目录。"""
        self.hub_path = os.path.join(self.root_path, "01_Hub文章")
        self.processed_hub_path = os.path.join(self.hub_path, "processed")
        self.asset_path = os.path.join(self.root_path, "10_资产库")
        self.delivery_path = os.path.join(self.root_path, "13_交付包")
        self.schedule_path = os.path.join(self.root_path, "09_排期表")
        self.review_path = os.path.join(self.root_path, "14_需人工审核")
        os.makedirs(self.processed_hub_path, exist_ok=True)
        os.makedirs(self.asset_path, exist_ok=True)
        os.makedirs(self.delivery_path, exist_ok=True)
        os.makedirs(self.schedule_path, exist_ok=True)
        os.makedirs(self.review_path, exist_ok=True)

    def execute_full_workflow(self):
        """执行完整的V4.1工作流。"""
        print(f"🚀 OrchestratorAgent V{self.version} 开始执行增长与变现工作流...")

        # --- 1. 热点驱动工作流 ---
        print("\n--- 1. 热点驱动工作流 ---")
        # TrendCrawlerAgent只读取外部已写入的raw_trend_events.json，不再安装依赖
        trend_processed = self.trend_crawler.process_raw_trends()
        if trend_processed:
            trend_events_path = os.path.join(self.asset_path, "trend_events.json")
            trend_events = []
            if os.path.exists(trend_events_path):
                with open(trend_events_path, 'r', encoding='utf-8') as f:
                    trend_events = json.load(f)
            analyzed_angles = self.trend_analyzer.analyze_trends(trend_events) if trend_events else []
            if analyzed_angles:
                latest_angle = analyzed_angles[-1]
                video_script = self.long_video_script_agent.generate_script(latest_angle, input_type="trend")
                self._qa_and_save(video_script, source="trend_driven")
        else:
            print("  → 未检测到新热点，跳过热点驱动工作流。")

        # --- 2. Hub驱动工作流 ---
        print("\n--- 2. Hub驱动工作流 ---")
        new_hubs = self._detect_new_hubs()
        if not new_hubs:
            print("  → 未检测到新Hub文章，跳过Hub驱动工作流。")
        for hub_file in new_hubs:
            print(f"  处理Hub文章: {hub_file}")
            hub_content = self._read_hub_file(hub_file)
            parsed_data = self.hub_parser.parse_hub(hub_content, hub_file)
            if parsed_data:
                # 将解析出的组件写入中央资产库（幂等upsert）
                import hashlib
                for comp_type, comp_list in parsed_data.get("components", {}).items():
                    if isinstance(comp_list, list):
                        for item in comp_list:
                            if isinstance(item, dict):
                                # 确保每个组件有唯一ID（基于内容哈希）
                                content_str = json.dumps(item, ensure_ascii=False, sort_keys=True)
                                item["id"] = hashlib.md5(content_str.encode()).hexdigest()[:16]
                                item["source_hub_id"] = parsed_data["metadata"]["hub_id"]
                                self.asset_store.upsert(item, comp_type)
                # 生成视频脚本并走QA
                video_script = self.long_video_script_agent.generate_script(parsed_data, input_type="hub")
                self._qa_and_save(video_script, source="hub_driven", hub_file=hub_file)
                # 标记Hub已处理（移动到processed目录）
                self._mark_hub_processed(hub_file)

        # --- 3. 学习回路 ---
        print("\n--- 3. 学习回路 ---")
        # LearningAgent需要metrics数据，此处为空跑（无metrics时跳过）
        metrics_path = os.path.join(self.asset_path, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            self.learning_agent.learn_from_metrics(metrics_data, {})
            print("  ✓ 学习回路执行完毕")
        else:
            print("  → 未找到metrics数据，跳过学习回路。")

        # --- 4. 生成排期表 ---
        print("\n--- 4. 生成排期表 ---")
        self._generate_schedule()

        print("\n✅ V4.1工作流执行完毕。")

    def _qa_and_save(self, video_script: Dict[str, Any], source: str, hub_file: str = None):
        """对脚本进行QA检查，最多回炉一次，不通过则进入人工审核队列。"""
        if not video_script or video_script.get("error"):
            print(f"  ✗ 脚本生成失败，跳过QA。")
            return

        qa_result = self.qa_agent.quality_check(video_script, "video_long_script")
        if not qa_result.get("rewrite_required"):
            print(f"  ✓ QA通过")
            self._process_and_save_script(video_script, source)
        else:
            print(f"  ✗ QA失败（问题: {qa_result.get('issues')}），触发回炉重写...")
            # 回炉重写一次
            video_script_retry = self.long_video_script_agent.generate_script(
                {"qa_feedback": qa_result.get("issues")}, input_type="hub" if hub_file else "trend"
            )
            if video_script_retry and not video_script_retry.get("error"):
                qa_result_retry = self.qa_agent.quality_check(video_script_retry, "video_long_script")
                if not qa_result_retry.get("rewrite_required"):
                    print(f"  ✓ 回炉重写成功，QA通过")
                    self._process_and_save_script(video_script_retry, source)
                    return
            # 两次均不通过，进入人工审核
            print(f"  ✗ 回炉重写失败，标记为需人工审核")
            review_path = os.path.join(self.review_path, f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(review_path, 'w', encoding='utf-8') as f:
                json.dump({"script": video_script, "qa_issues": qa_result.get("issues")}, f, ensure_ascii=False, indent=2)

    def _process_and_save_script(self, script: Dict[str, Any], source: str):
        """调用MonetizationAgent优化CTA，然后保存脚本到交付包。"""
        print(f"  正在处理脚本: {script.get('title', '无标题')}")
        monetization_suggestion = self.monetization_agent.analyze_and_suggest(script)
        script['monetization_cta'] = monetization_suggestion.get('suggestion', '')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_id = f"{source}_{timestamp}_3min"
        delivery_folder = os.path.join(self.delivery_path, script_id)
        os.makedirs(delivery_folder, exist_ok=True)
        script_path = os.path.join(delivery_folder, "video_script.json")
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=4)
        print(f"  ✓ 脚本已保存到: {script_path}")

    def _detect_new_hubs(self) -> List[str]:
        """检测01_Hub文章/目录下的新文章（排除processed子目录）。"""
        return [
            f for f in os.listdir(self.hub_path)
            if os.path.isfile(os.path.join(self.hub_path, f))
        ]

    def _read_hub_file(self, filename: str) -> str:
        """读取Hub文章内容。"""
        with open(os.path.join(self.hub_path, filename), 'r', encoding='utf-8') as f:
            return f.read()

    def _mark_hub_processed(self, filename: str):
        """将处理过的Hub文章移动到processed目录，实现幂等性。"""
        src = os.path.join(self.hub_path, filename)
        dst = os.path.join(self.processed_hub_path, filename)
        os.rename(src, dst)
        print(f"  ✓ Hub文章已标记为已处理: {filename}")

    def _generate_schedule(self):
        """根据V4.1策略（长视频优先）生成真实的排期CSV。"""
        schedule_path = os.path.join(self.schedule_path, "schedule.csv")

        # 1. 收集所有已生成的内容文件
        content_files = []
        for root, _, files in os.walk(self.delivery_path):
            for file in files:
                if file.endswith(".json"):
                    content_files.append(os.path.join(root, file))

        # 2. 按长短视频分类（文件夹名包含"3min"为长视频）
        long_videos = [f for f in content_files if "3min" in f]
        short_content = [f for f in content_files if "3min" not in f]

        # 3. 生成排期（V4规则：周一/三/五/日=长视频，周二/四/六=短内容）
        schedule = []
        start_date = datetime.now().date()
        long_video_days = {0, 2, 4, 6}  # Mon, Wed, Fri, Sun

        for i in range(14):  # 排两周
            current_date = start_date + timedelta(days=i)
            weekday = current_date.weekday()

            if weekday in long_video_days:
                pool = long_videos if long_videos else short_content
                content_type = "long_video"
            else:
                pool = short_content if short_content else long_videos
                content_type = "short_content"

            if not pool:
                continue

            file_path = pool.pop(0)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                title = content_data.get("title", "无标题")
            except Exception:
                title = "无标题"

            schedule.append({
                "publish_date": current_date.isoformat(),
                "content_type": content_type,
                "title": title,
                "file_path": file_path
            })

        # 4. 写入CSV
        if schedule:
            with open(schedule_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["publish_date", "content_type", "title", "file_path"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(schedule)
            print(f"  ✓ 排期表已生成: {schedule_path}（共{len(schedule)}条）")
        else:
            print("  → 无内容可排期。")


if __name__ == '__main__':
    orchestrator = OrchestratorAgent()
    orchestrator.execute_full_workflow()
