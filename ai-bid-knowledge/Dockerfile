FROM python:3.11-slim
WORKDIR /app
COPY src/main/python /app
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir fastapi uvicorn langchain langchain-community \
        chromadb psycopg2-binary python-multipart aiofiles pydantic-settings
EXPOSE 8086
CMD ["python", "-m", "com.aidbid.knowledge.main"]
