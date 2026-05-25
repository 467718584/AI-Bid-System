from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json
import os

from .config import config
from .chroma_client import get_chroma_client, ChromaClient
from .models import (
    KnowledgeBase, KnowledgeChunk, RetrieveRequest, RetrieveResponse,
    ChunkCreateRequest, DocumentCreateRequest
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Bid Knowledge Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局向量存储（生产环境应使用ChromaDB）
_vector_store: Dict[str, List[Dict]] = {}
_knowledge_bases: Dict[str, KnowledgeBase] = {}

# 初始化ChromaDB
try:
    chroma_client = get_chroma_client()
    logger.info("ChromaDB client initialized")
except Exception as e:
    logger.warning(f"ChromaDB init warning: {e}")
    chroma_client = None

# ============== Models ==============

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    chunkStrategy: str = "recursive"
    chunkSize: int = 500
    embeddingModel: str = "m3e"

class DocumentCreate(BaseModel):
    kbId: str
    docName: str
    content: str
    metadata: Optional[Dict] = {}

class RetrieveRequest(BaseModel):
    kbId: str
    query: str
    topK: int = 5
    minSimilarity: float = 0.7

# ============== Knowledge Base CRUD ==============

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-bid-knowledge"}

@app.post("/api/knowledge/bases", response_model=Dict)
async def create_knowledge_base(req: KnowledgeBaseCreate):
    """创建知识库"""
    kb = KnowledgeBase(
        id=f"kb_{len(_knowledge_bases) + 1}",
        name=req.name,
        description=req.description,
        chunk_strategy=req.chunkStrategy,
        chunk_size=req.chunkSize,
        embedding_model=req.embeddingModel,
        status=1
    )
    _knowledge_bases[kb.id] = kb
    _vector_store[kb.id] = []
    return {"code": 200, "data": kb}

@app.get("/api/knowledge/bases")
async def list_knowledge_bases():
    """获取知识库列表"""
    return {"code": 200, "data": list(_knowledge_bases.values())}

@app.get("/api/knowledge/bases/{kb_id}")
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"code": 200, "data": kb}

@app.delete("/api/knowledge/bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    if kb_id in _knowledge_bases:
        del _knowledge_bases[kb_id]
        if kb_id in _vector_store:
            del _vector_store[kb_id]
    return {"code": 200, "message": "deleted"}

# ============== Document & Chunk Management ==============

@app.post("/api/knowledge/bases/{kb_id}/documents")
async def add_document(kb_id: str, req: DocumentCreate):
    """添加文档到知识库"""
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # 简单的文本分块
    content = req.content
    chunk_size = kb.chunk_size
    chunks = []

    # 按句子分块
    sentences = content.split("。")
    current_chunk = ""
    chunk_list = []

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + "。"
        else:
            if current_chunk:
                chunk_list.append(current_chunk)
            current_chunk = sentence + "。"

    if current_chunk:
        chunk_list.append(current_chunk)

    # 创建chunks
    for i, chunk_content in enumerate(chunk_list):
        chunk = KnowledgeChunk(
            id=f"{kb_id}_chunk_{len(_vector_store[kb_id]) + i + 1}",
            kb_id=kb_id,
            doc_id=req.docName,
            content=chunk_content,
            chunk_index=i,
            metadata=req.metadata or {}
        )
        _vector_store[kb_id].append({
            "id": chunk.id,
            "content": chunk.content,
            "metadata": chunk.metadata,
            # 模拟向量（实际应该用embedding模型）
            "vector": [0.0] * 1536
        })

    # 更新统计
    kb.document_count += 1
    kb.chunk_count += len(chunk_list)

    return {
        "code": 200,
        "data": {
            "docName": req.docName,
            "chunkCount": len(chunk_list)
        }
    }

@app.get("/api/knowledge/bases/{kb_id}/chunks")
async def list_chunks(kb_id: str, page: int = 1, pageSize: int = 20):
    """获取知识库切片列表"""
    if kb_id not in _vector_store:
        return {"code": 200, "data": [], "total": 0}

    chunks = _vector_store[kb_id]
    start = (page - 1) * pageSize
    end = start + pageSize

    return {
        "code": 200,
        "data": chunks[start:end],
        "total": len(chunks),
        "page": page,
        "pageSize": pageSize
    }

# ============== RAG Retrieval ==============

@app.post("/api/knowledge/bases/{kb_id}/retrieve")
async def retrieve(kb_id: str, req: RetrieveRequest):
    """RAG检索接口"""
    if kb_id not in _vector_store:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    chunks = _vector_store[kb_id]

    # 简单的关键词匹配（实际应该用向量检索）
    query_keywords = req.query.split()
    results = []

    for chunk in chunks:
        score = 0
        content_lower = chunk["content"].lower()
        for keyword in query_keywords:
            if keyword.lower() in content_lower:
                score += 1

        if score > 0:
            similarity = score / len(query_keywords)
            if similarity >= req.minSimilarity:
                results.append({
                    "chunkId": chunk["id"],
                    "content": chunk["content"],
                    "similarity": similarity,
                    "metadata": chunk["metadata"]
                })

    # 按相似度排序
    results.sort(key=lambda x: x["similarity"], reverse=True)

    # 取topK
    results = results[:req.topK]

    return {
        "code": 200,
        "data": {
            "results": results,
            "total": len(results),
            "query": req.query
        }
    }

@app.post("/api/knowledge/bases/{kb_id}/test")
async def test_retrieval(kb_id: str, req: RetrieveRequest):
    """命中测试"""
    return await retrieve(kb_id, req)

@app.post("/api/knowledge/bases/{kb_id}/vector-retrieve")
async def vector_retrieve(kb_id: str, req: RetrieveRequest):
    """基于向量的语义检索"""
    if chroma_client is None:
        raise HTTPException(status_code=503, detail="Vector store not available")

    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # 使用OpenAI的embedding API获取查询向量
    # 实际应该调用AI服务获取embedding
    query_embedding = [0.0] * 1536  # 占位符，实际需要调用embed接口

    results = chroma_client.search(
        collection_name=f"kb_{kb_id}",
        query_embedding=query_embedding,
        n_results=req.topK
    )

    return {
        "code": 200,
        "data": {
            "results": [
                {
                    "chunkId": rid,
                    "content": doc,
                    "similarity": 1.0 - dist if dist else 0.0,
                    "metadata": meta
                }
                for rid, doc, meta, dist in zip(
                    results.get("ids", []),
                    results.get("documents", []),
                    results.get("metadatas", []),
                    results.get("distances", [])
                )
            ],
            "total": len(results.get("ids", []))
        }
    }

# ============== Batch Operations ==============

@app.post("/api/knowledge/bases/{kb_id}/documents/batch")
async def batch_add_documents(kb_id: str, documents: List[DocumentCreate]):
    """批量添加文档"""
    results = []
    for doc in documents:
        result = await add_document(kb_id, doc)
        results.append(result)
    return {"code": 200, "data": results}

@app.delete("/api/knowledge/bases/{kb_id}/documents/{doc_name}")
async def delete_document(kb_id: str, doc_name: str):
    """删除文档及其chunks"""
    if kb_id in _vector_store:
        _vector_store[kb_id] = [
            c for c in _vector_store[kb_id]
            if c["metadata"].get("doc_name") != doc_name
        ]
    return {"code": 200, "message": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)