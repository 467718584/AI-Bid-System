#!/bin/bash
# AI智能投标系统 - 查看服务状态

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AI智能投标系统 - 服务状态"
echo "=========================================="
echo ""

echo "📊 Docker容器状态:"
docker-compose ps
echo ""

echo "🌐 服务健康检查:"
for service in gateway user project material document bid knowledge ai enterprise frontend; do
    port=$(grep -E "^.*ports:" -A1 docker-compose.yml 2>/dev/null | grep -E "808[0-9]|8090|3000" | head -1 | grep -oE "[0-9]+" | head -1 || echo "N/A")
done

echo ""
echo "💻 服务响应测试:"
echo -n "  Gateway: "
curl -s --max-time 3 http://localhost:8090/actuator/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','ERR'))" 2>/dev/null || echo "OFFLINE"

echo -n "  AI服务: "
curl -s --max-time 3 -X POST http://localhost:8090/api/ai/bid/polish -H "Content-Type: application/json" -d '{"content":"test"}' 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('UP' if d.get('code')==200 else 'ERR')" 2>/dev/null || echo "OFFLINE"

echo -n "  标书API: "
curl -s --max-time 3 http://localhost:8090/api/bid/list 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('UP' if d.get('code')==200 else 'ERR')" 2>/dev/null || echo "OFFLINE"

echo ""
echo "=========================================="