FROM python:3.11-slim
WORKDIR /app
COPY src/main/python /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir fastapi uvicorn langchain langchain-community \
        httpx aiofiles python-multipart pydantic-settings
EXPOSE 8087
CMD ["python", "-m", "com.aidbid.ai.main"]
