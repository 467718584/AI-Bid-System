#!/bin/bash
# AI智能投标系统 - 一键启动脚本（无Docker原生启动）
# 使用systemd服务管理

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AI智能投标系统 - 启动所有服务"
echo "=========================================="

# 停止现有进程
echo "🛑 停止现有进程..."
pkill -f "java.*ai-bid" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

# 启动数据库
echo "📦 启动PostgreSQL..."
systemctl start postgresql 2>/dev/null || service postgresql start 2>/dev/null || echo "PostgreSQL可能已在运行"

echo "📦 启动Redis..."
systemctl start redis 2>/dev/null || service redis-server start 2>/dev/null || echo "Redis可能已在运行"

sleep 3

# 启动Python AI服务
echo "🐍 启动AI服务..."
cd "$SCRIPT_DIR/ai-bid-ai/src/main/python"
PYTHONPATH="$SCRIPT_DIR/ai-bid-ai/src/main/python" nohup python3 -m uvicorn com.aidbid.ai.main:app --host 0.0.0.0 --port 8087 > /tmp/ai-8087.log 2>&1 &
AI_PID=$!
echo "AI服务 PID: $AI_PID"

sleep 2

# 启动Knowledge服务
echo "📚 启动知识库服务..."
cd "$SCRIPT_DIR/ai-bid-knowledge/src/main/python"
PYTHONPATH="$SCRIPT_DIR/ai-bid-knowledge/src/main/python" nohup python3 -m uvicorn com.aidbid.knowledge.main:app --host 0.0.0.0 --port 8086 > /tmp/knowledge-8086.log 2>&1 &
KNOWLEDGE_PID=$!
echo "知识库服务 PID: $KNOWLEDGE_PID"

sleep 2

# 启动Java微服务
echo "☕ 启动Java微服务..."
for svc in user project material document bid enterprise; do
    echo "  启动 ai-bid-$svc..."
    cd "$SCRIPT_DIR/ai-bid-$svc"
    nohup mvn spring-boot:run > /tmp/$svc.log 2>&1 &
    echo "  ai-bid-$svc 已启动"
    sleep 3
done

# 启动Gateway
echo "🌉 启动Gateway..."
cd "$SCRIPT_DIR/ai-bid-gateway"
nohup mvn spring-boot:run > /tmp/gateway.log 2>&1 &
echo "Gateway 已启动"

sleep 5

echo ""
echo "📊 服务状态:"
netstat -tlnp 2>/dev/null | grep -E "808[0-9]|8090|3000" || ss -tlnp 2>/dev/null | grep -E "808[0-9]|8090|3000" || echo "请手动检查服务状态"

echo ""
echo "✅ 启动完成！"
echo "   访问地址: http://localhost:3000"