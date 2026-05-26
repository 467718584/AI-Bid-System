#!/bin/bash
# AI智能投标系统 - 前端依赖安装与启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================"
echo "AI智能投标系统 - 前端启动"
echo "========================================"

# 检查 node 版本
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js 18+ is required. Current version: $(node -v)"
    exit 1
fi

# 检查 npm 版本
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed."
    exit 1
fi

echo ""
echo "[1/3] 检查环境..."
echo "  Node.js: $(node -v)"
echo "  npm: $(npm -v)"
echo "  项目目录: $PROJECT_DIR"

# 复制环境变量文件（如需）
if [ ! -f .env ]; then
    echo ""
    echo "[2/3] 创建 .env 文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "  已从 .env.example 创建 .env"
    else
        echo "  Warning: .env.example 不存在，跳过"
    fi
fi

# 安装依赖
echo ""
echo "[3/3] 安装依赖..."
if [ -d node_modules ]; then
    echo "  检测到已安装依赖，跳过 npm install"
else
    npm install
fi

# 启动开发服务器
echo ""
echo "========================================"
echo "启动开发服务器 (http://localhost:3000)"
echo "========================================"
npm run dev
