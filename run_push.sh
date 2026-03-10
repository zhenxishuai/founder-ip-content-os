#!/bin/bash
cd /home/ubuntu/founder-ip-content-os-full
# Load env vars from .env file
set -a
source .env
set +a
python3 -c "
import sys
sys.path.insert(0, '/home/ubuntu/founder-ip-content-os-full')
from agents.push_agent import PushAgent
agent = PushAgent(root_path='/home/ubuntu/founder-ip-content-os-full/')
agent.execute()
" >> /home/ubuntu/founder-ip-content-os-full/logs/cron.log 2>&1
