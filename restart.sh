#!/bin/bash
# AI智能投标系统 - 重启脚本（先停再启）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AI智能投标系统 - 重启所有服务"
echo "=========================================="

echo "🛑 停止服务..."
docker-compose down

echo ""
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "✅ 重启完成！"