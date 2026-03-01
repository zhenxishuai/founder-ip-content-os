#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AssetStore - 中央资产库管理模块 (V4.1核心)
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

class AssetStore:
    """负责所有资产的中央读写，实现复利机制。"""

    def __init__(self, asset_path: str):
        self.asset_path = asset_path
        self.asset_library_path = os.path.join(self.asset_path, "asset_library.json")
        self.library = self._load_library()

    def _load_library(self) -> Dict[str, Dict[str, Any]]:
        """加载资产库文件。"""
        if not os.path.exists(self.asset_library_path):
            return {}
        with open(self.asset_library_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_library(self):
        """保存资产库文件。"""
        with open(self.asset_library_path, 'w', encoding='utf-8') as f:
            json.dump(self.library, f, ensure_ascii=False, indent=2)

    def upsert(self, asset: Dict[str, Any], asset_type: str) -> str:
        """
        更新或插入一个资产到库中。
        如果资产已存在（通过ID判断），则增加其usage_count。
        如果不存在，则创建新条目。

        Args:
            asset: 要插入的资产字典，必须包含'id'和'content'。
            asset_type: 资产类型 (e.g., 'viewpoint', 'golden_sentence', 'hook').

        Returns:
            资产的ID。
        """
        asset_id = asset.get('id')
        if not asset_id:
            raise ValueError("资产必须包含一个'id'")

        if asset_id in self.library:
            # 更新现有资产
            self.library[asset_id]['usage_count'] += 1
            self.library[asset_id]['last_used_at'] = datetime.now().isoformat()
        else:
            # 插入新资产
            new_asset = {
                'id': asset_id,
                'type': asset_type,
                'content': asset.get('content'),
                'usage_count': 1,
                'score': asset.get('score', 50), # 初始默认分
                'risk_level': asset.get('risk_level', 'low'),
                'platform_tags': asset.get('platform_tags', ['general']),
                'created_at': datetime.now().isoformat(),
                'last_used_at': datetime.now().isoformat(),
                'source_hub_id': asset.get('source_hub_id')
            }
            self.library[asset_id] = new_asset
        
        self._save_library()
        return asset_id

    def get(self, asset_id: str) -> Dict[str, Any]:
        """根据ID获取资产。"""
        return self.library.get(asset_id)

    def get_all_by_type(self, asset_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有资产。"""
        return [asset for asset in self.library.values() if asset['type'] == asset_type]
