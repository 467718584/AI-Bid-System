FROM python:3.11-slim
WORKDIR /app

# Create volume for ChromaDB persistence
VOLUME ["/chroma/chroma_db"]

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "com.aidbid.knowledge.main:app", "--host", "0.0.0.0", "--port", "8086"]