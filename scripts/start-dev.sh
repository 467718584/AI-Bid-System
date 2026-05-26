#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  AI-Bid System - Development Start"
echo "========================================"

cd "$PROJECT_DIR"

# Check if .env file exists, create from template if not
if [ ! -f .env ]; then
    echo "[INFO] .env file not found, creating from template..."
    cat > .env << 'EOF'
# Database Configuration
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432

# Redis Configuration
REDIS_PORT=6379
REDIS_PASSWORD=

# Infrastructure Ports
CHROMA_PORT=8000
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001

# Application Ports
GATEWAY_PORT=8080
USER_PORT=8081
PROJECT_PORT=8082
MATERIAL_PORT=8083
DOCUMENT_PORT=8084
KNOWLEDGE_PORT=8086
AI_PORT=8087

# LLM Configuration
SPRING_PROFILES=docker
LLM_PROVIDER=minimax
MINIMAX_API_KEY=
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=abab6-chat
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1
QWEN_MODEL=qwen-turbo

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Embedding Configuration
EMBEDDING_MODEL=shibing624/text2vec-base-chinese
EMBEDDING_DEVICE=cpu

# AI Configuration
MAX_TOKENS=8192
TEMPERATURE=0.7
EOF
    echo "[INFO] .env file created. Please configure your API keys."
fi

# Pull base images
echo "[INFO] Pulling base images..."
docker-compose pull postgres redis chroma minio 2>/dev/null || true

# Build application services
echo "[INFO] Building application services..."
docker-compose build --parallel

# Start infrastructure services first
echo "[INFO] Starting infrastructure services..."
docker-compose up -d postgres redis chroma minio

# Wait for infrastructure to be healthy
echo "[INFO] Waiting for infrastructure services to be ready..."
sleep 5

for service in postgres redis chroma minio; do
    echo -n "[INFO] Checking $service..."
    for i in $(seq 1 30); do
        if docker inspect --format='{{.State.Health.Status}}' aidbid-$service 2>/dev/null | grep -q "healthy"; then
            echo " OK"
            break
        fi
        if [ $i -eq 30 ]; then
            echo " TIMEOUT (service may still be starting)"
        fi
        sleep 2
    done
done

# Start application services
echo "[INFO] Starting application services..."
docker-compose up -d

# Wait for application services to start
echo "[INFO] Waiting for application services to start..."
sleep 10

# Show status
echo ""
echo "========================================"
echo "  Service Status"
echo "========================================"
docker-compose ps

echo ""
echo "[INFO] Checking service health..."
for service in gateway user-service project-service material-service document-service knowledge ai; do
    port=""
    case $service in
        gateway) port=8080 ;;
        user-service) port=8081 ;;
        project-service) port=8082 ;;
        material-service) port=8083 ;;
        document-service) port=8084 ;;
        knowledge) port=8086 ;;
        ai) port=8087 ;;
    esac

    if curl -sf "http://localhost:$port/actuator/health" >/dev/null 2>&1 || \
       curl -sf "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "[OK] $service (port $port)"
    else
        echo "[--] $service (port $port) - not ready yet"
    fi
done

echo ""
echo "========================================"
echo "  Ports Summary"
echo "========================================"
echo "  Gateway:      ${GATEWAY_PORT:-8080}"
echo "  User Service: ${USER_PORT:-8081}"
echo "  Project Svc:  ${PROJECT_PORT:-8082}"
echo "  Material Svc: ${MATERIAL_PORT:-8083}"
echo "  Document Svc: ${DOCUMENT_PORT:-8084}"
echo "  Knowledge:    ${KNOWLEDGE_PORT:-8086}"
echo "  AI Service:   ${AI_PORT:-8087}"
echo "  PostgreSQL:   ${DB_PORT:-5432}"
echo "  Redis:        ${REDIS_PORT:-6379}"
echo "  Chroma:       ${CHROMA_PORT:-8000}"
echo "  MinIO:        ${MINIO_PORT:-9000} | Console: ${MINIO_CONSOLE_PORT:-9001}"
echo "========================================"
echo ""
echo "Done! Services are starting. Use './scripts/stop.sh' to stop."
echo "View logs with: docker-compose logs -f [service]"