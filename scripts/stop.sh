#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  AI-Bid System - Stopping Services"
echo "========================================"

cd "$PROJECT_DIR"

# Stop all services
echo "[INFO] Stopping all services..."
docker-compose down

echo "[INFO] Checking for remaining containers..."
remaining=$(docker ps -a --filter "name=aidbid-" --format "{{.Names}}" 2>/dev/null)
if [ -n "$remaining" ]; then
    echo "[WARN] Remaining containers found:"
    echo "$remaining"
    echo ""
    read -p "Remove remaining containers? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "$remaining" | xargs docker rm -f 2>/dev/null
        echo "[INFO] Remaining containers removed."
    fi
else
    echo "[OK] No remaining containers."
fi

# Ask about volumes
read -p "Remove data volumes (postgres, redis, chroma, minio)? (y/N): " confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo "[INFO] Removing data volumes..."
    docker volume rm $(docker volume ls --filter "name=aidbid" --format "{{.Name}}" 2>/dev/null) 2>/dev/null || true
    docker volume rm ai-bid_postgres_data ai-bid_redis_data ai-bid_chroma_data ai-bid_minio_data 2>/dev/null || true
    echo "[INFO] Data volumes removed."
fi

echo ""
echo "========================================"
echo "  All Services Stopped"
echo "========================================"
echo ""
echo "Use './scripts/start-dev.sh' to start again."