#!/bin/bash
# AI智能投标系统 - 一键启动脚本
# 使用Docker Compose启动所有微服务

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AI智能投标系统 - Docker微服务启动"
echo "=========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境配置文件..."
    cat > .env << 'EOF'
# AI智能投标系统环境配置
MINIMAX_API_KEY=sk-cp-ZpS3_cdjkZ282Ux41yYKpAT6uOmYqQ6L3f7rqJ81HFLsVcLC1xeJ5UaUgu5p3BzRqdDVYtTLDxtMuLKZfyiqd_eYuPrHaJzPMRA_BIevVROCws1zs0JsAH4

# PostgreSQL
POSTGRES_DB=ai_bid
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Java服务配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ai_bid
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
EOF
    echo "✅ 环境配置文件已创建: .env"
fi

echo ""
echo "🐳 构建Docker镜像..."
docker-compose build --parallel

echo ""
echo "🚀 启动所有服务..."
docker-compose up -d

echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "🌐 访问地址:"
echo "   前端: http://localhost:3000"
echo "   Gateway: http://localhost:8090"
echo "   API文档: http://localhost:8090/swagger-ui.html"

echo ""
echo "📝 常用命令:"
echo "   查看日志: docker-compose logs -f [service_name]"
echo "   停止服务: ./stop.sh"
echo "   重启服务: docker-compose restart [service_name]"

echo ""
echo "=========================================="
echo "✅ 启动完成！"
echo "=========================================="