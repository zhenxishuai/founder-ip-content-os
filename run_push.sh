#!/bin/bash

# 设置项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# 确保在项目根目录下执行
cd "$PROJECT_DIR"

# 检查虚拟环境（如果存在）
# if [ -d "venv" ]; then
#   source venv/bin/activate
# fi

# 执行Push Agent
# 使用 python3 -m agents.push_agent 来确保模块能被正确找到
python3 -m agents.push_agent
