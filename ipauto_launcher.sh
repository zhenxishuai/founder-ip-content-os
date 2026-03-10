#!/bin/bash

# IPAUTO Launcher Script for OpenClaw
# This script acts as a single entry point for OpenClaw to call IPAUTO.
# It dispatches to the appropriate IPAUTO script based on the 'action' parameter.

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Load environment variables from .env file
set -a
source .env
set +a

# Parse arguments
action=""
hub_article_path=""

for arg in "$@"; do
  case $arg in
    action:*) action="${arg#action:}";; # Extract value after 'action:'
    hub_article_path:*) hub_article_path="${arg#hub_article_path:}";; # Extract value after 'hub_article_path:'
  esac
done

# Execute the appropriate script based on action
case "$action" in
  "generate_content")
    echo "[IPAUTO Launcher] Executing generate_content action..."
    ./ipauto_generate_content.sh "$hub_article_path"
    ;;
  "push_daily_task")
    echo "[IPAUTO Launcher] Executing push_daily_task action..."
    ./ipauto_push_daily_task.sh
    ;;
  *)
    echo "[IPAUTO Launcher] Error: Unknown or missing action: $action"
    echo "Usage: ipauto_launcher.sh action:<generate_content|push_daily_task> [hub_article_path:<path>]"
    exit 1
    ;;
esac
