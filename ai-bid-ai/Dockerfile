# Python AI Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制代码
COPY ai-bid-ai/src/main/python /app

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

# 暴露端口
EXPOSE 8087

# 启动服务
CMD ["python", "-m", "uvicorn", "com.aidbid.ai.main:app", "--host", "0.0.0.0", "--port", "8087"]