#!/usr/bin/env bash
#
# runner.sh - Unified script runner with automatic PYTHONPATH setup
#
# Usage:
#   ./runner.sh <command> [args...]
#
# Examples:
#   ./runner.sh python tools/events2guards.py data/runs/r42
#   ./runner.sh python tools/chat2events.py data/runs/r42
#   ./runner.sh python tools/process_long_conversation.py cursor.md
#   ./runner.sh pytest tests/
#
# This script automatically sets PYTHONPATH to the project root directory,
# eliminating ModuleNotFoundError when importing 'tools' package.

set -euo pipefail

# Get the directory where this script is located (project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to project root
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

# Run the command with all arguments
exec "$@"
