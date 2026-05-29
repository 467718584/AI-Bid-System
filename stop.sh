#!/bin/bash
# AI智能投标系统 - 停止脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AI智能投标系统 - 停止所有服务"
echo "=========================================="

echo "🛑 停止所有服务..."
docker-compose down

echo ""
echo "✅ 服务已停止"
echo ""
echo "💡 提示: 如需完全清理（包括数据卷）:"
echo "   docker-compose down -v"