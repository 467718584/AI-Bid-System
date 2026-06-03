from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json
import os
import asyncio
import numpy as np

# CORS配置 - 生产环境应通过环境变量配置具体域名
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")

from .config import config, embed_text, embed_texts
from .chroma_client import get_chroma_client, ChromaClient
from .embedding_service import get_embedding_service, EMBEDDING_DIMENSION
from .rag_service import get_rag_service
from .models import (
    KnowledgeBase, KnowledgeChunk, RetrieveRequest, RetrieveResponse,
    ChunkCreateRequest, DocumentCreateRequest
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Bid Knowledge Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


# 全局存储
_vector_store: Dict[str, List[Dict]] = {}
_knowledge_bases: Dict[str, KnowledgeBase] = {}
_categories: List[Dict] = [
    {"id": "cat_1", "name": "招标文件", "description": "招标文件范本"},
    {"id": "cat_2", "name": "技术方案", "description": "技术方案文档"},
    {"id": "cat_3", "name": "商务标", "description": "商务标文档"},
    {"id": "cat_4", "name": "资质证明", "description": "资质证明材料"},
]

# 文档存储 (模拟)
_documents: List[Dict] = []
_document_id_counter = 1

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

class HybridSearchRequest(BaseModel):
    query: str
    topK: int = 5
    minSimilarity: float = 0.5
    alpha: float = 0.7

class RAGGenerateRequest(BaseModel):
    query: str
    topK: int = 5
    minSimilarity: float = 0.5
    systemPrompt: Optional[str] = None
    useHybrid: bool = True
    alpha: float = 0.7

# ============== 兼容前端API的新路由 ==============

@app.get("/api/knowledge/categories")
async def get_categories():
    """获取知识分类列表 - 兼容前端"""
    return {"code": 200, "data": _categories}

@app.get("/api/knowledge/search")
async def search_knowledge(keyword: Optional[str] = None, category: Optional[str] = None):
    """搜索知识库 - 兼容前端"""
    results = []
    for doc in _documents:
        if keyword and keyword.lower() not in doc.get("content", "").lower():
            continue
        if category and doc.get("category") != category:
            continue
        results.append({
            "id": doc.get("id"),
            "title": doc.get("title"),
            "snippet": doc.get("content", "")[:200],
            "content": doc.get("content", ""),
            "category": doc.get("category"),
            "updatedAt": doc.get("updatedAt")
        })
    return {"code": 200, "data": results, "total": len(results)}

@app.get("/api/knowledge/documents")
async def list_documents(page: int = 1, pageSize: int = 20, category: Optional[str] = None):
    """获取文档列表 - 兼容前端"""
    docs = _documents
    if category:
        docs = [d for d in docs if d.get("category") == category]
    
    start = (page - 1) * pageSize
    end = start + pageSize
    return {"code": 200, "data": docs[start:end], "total": len(docs), "page": page, "pageSize": pageSize}

@app.get("/api/knowledge/documents/{doc_id}")
async def get_document(doc_id: str):
    """获取文档详情"""
    for doc in _documents:
        if str(doc.get("id")) == str(doc_id):
            return {"code": 200, "data": doc}
    raise HTTPException(status_code=404, detail="Document not found")

@app.post("/api/knowledge/documents")
async def add_document(data: Dict):
    """添加文档"""
    global _document_id_counter
    doc = {
        "id": _document_id_counter,
        "title": data.get("title", "未命名文档"),
        "content": data.get("content", ""),
        "category": data.get("category", "未分类"),
        "fileType": data.get("fileType", "txt"),
        "updatedAt": data.get("updatedAt", ""),
        "createdAt": data.get("createdAt", "")
    }
    _documents.append(doc)
    _document_id_counter += 1
    return {"code": 200, "data": doc}

@app.put("/api/knowledge/documents/{doc_id}")
async def update_document(doc_id: str, data: Dict):
    """更新文档"""
    for doc in _documents:
        if str(doc.get("id")) == str(doc_id):
            doc.update(data)
            return {"code": 200, "data": doc}
    raise HTTPException(status_code=404, detail="Document not found")

@app.delete("/api/knowledge/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    global _documents
    _documents = [d for d in _documents if str(d.get("id")) != str(doc_id)]
    return {"code": 200, "message": "deleted"}

@app.post("/api/knowledge/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档"""
    global _document_id_counter
    content = await file.read()
    doc = {
        "id": _document_id_counter,
        "title": file.filename,
        "content": content.decode("utf-8", errors="ignore"),
        "category": "未分类",
        "fileType": file.filename.split(".")[-1] if "." in file.filename else "txt",
        "updatedAt": "",
        "createdAt": ""
    }
    _documents.append(doc)
    _document_id_counter += 1
    return {"code": 200, "data": {"id": doc["id"], "filename": file.filename}}

@app.get("/api/knowledge/stats")
async def get_stats():
    """获取知识库统计"""
    return {"code": 200, "data": {
        "totalDocuments": len(_documents),
        "totalCategories": len(_categories),
        "totalChunks": sum(len(v) for v in _vector_store.values())
    }}

@app.post("/api/knowledge/rebuild-index")
async def rebuild_index():
    """重建向量索引"""
    return {"code": 200, "message": "Index rebuild triggered"}

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
async def add_document_to_kb(kb_id: str, req: DocumentCreate):
    """添加文档到知识库"""
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    content = req.content
    chunk_size = kb.chunk_size
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

    embeddings = await embed_texts(chunk_list)

    for i, chunk_content in enumerate(chunk_list):
        chunk_id = f"{kb_id}_chunk_{len(_vector_store[kb_id]) + i + 1}"
        _vector_store[kb_id].append({
            "id": chunk_id,
            "content": chunk_content,
            "metadata": {"doc_name": req.docName, "chunk_index": i},
            "vector": embeddings[i] if i < len(embeddings) else [0.0] * 1536
        })

    kb.document_count += 1
    kb.chunk_count += len(chunk_list)

    return {"code": 200, "data": {"docName": req.docName, "chunkCount": len(chunk_list)}}

@app.get("/api/knowledge/bases/{kb_id}/chunks")
async def list_chunks(kb_id: str, page: int = 1, pageSize: int = 20):
    """获取知识库切片列表"""
    if kb_id not in _vector_store:
        return {"code": 200, "data": [], "total": 0}

    chunks = _vector_store[kb_id]
    start = (page - 1) * pageSize
    end = start + pageSize

    return {"code": 200, "data": chunks[start:end], "total": len(chunks), "page": page, "pageSize": pageSize}

# ============== RAG Retrieval ==============

@app.post("/api/knowledge/bases/{kb_id}/retrieve")
async def retrieve(kb_id: str, req: RetrieveRequest):
    """RAG检索接口"""
    if kb_id not in _vector_store:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    chunks = _vector_store[kb_id]
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

    results.sort(key=lambda x: x["similarity"], reverse=True)
    results = results[:req.topK]

    return {"code": 200, "data": {"results": results, "total": len(results), "query": req.query}}

@app.post("/api/knowledge/bases/{kb_id}/test")
async def test_retrieval(kb_id: str, req: RetrieveRequest):
    """命中测试"""
    return await retrieve(kb_id, req)

@app.post("/api/knowledge/bases/{kb_id}/vector-retrieve")
async def vector_retrieve(kb_id: str, req: RetrieveRequest):
    """基于向量的语义检索"""
    kb = _vector_store.get(kb_id)

    query_embedding = await embed_text(req.query)

    if chroma_client is not None:
        try:
            results = chroma_client.search(
                collection_name=f"kb_{kb_id}",
                query_embedding=query_embedding,
                n_results=req.topK
            )

            if results.get("ids"):
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
        except Exception as e:
            logger.warning(f"ChromaDB query failed: {e}, falling back to memory")

    chunks = _vector_store.get(kb_id, [])

    if not chunks:
        return {"code": 200, "data": {"results": [], "total": 0}}

    scored = []
    for chunk in chunks:
        vector = chunk.get("vector", [])
        if vector and len(vector) == len(query_embedding):
            similarity = _cosine_similarity(query_embedding, vector)
            if similarity >= req.minSimilarity:
                scored.append({
                    "chunkId": chunk["id"],
                    "content": chunk["content"],
                    "similarity": similarity,
                    "metadata": chunk.get("metadata", {})
                })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    scored = scored[:req.topK]

    return {"code": 200, "data": {"results": scored, "total": len(scored)}}

@app.post("/api/knowledge/bases/{kb_id}/hybrid-search")
async def hybrid_search(kb_id: str, req: HybridSearchRequest):
    """混合检索：向量 + 关键词"""
    if chroma_client is None:
        raise HTTPException(status_code=503, detail="Vector store not available")

    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    query_embedding = await embed_text(req.query)

    results = chroma_client.hybrid_search(
        collection_name=f"kb_{kb_id}",
        query_embedding=query_embedding,
        query_text=req.query,
        n_results=req.topK,
        alpha=req.alpha
    )

    filtered = [r for r in results if r.get("similarity", 0) >= req.minSimilarity]

    return {"code": 200, "data": {"results": filtered, "total": len(filtered), "query": req.query, "method": "hybrid"}}

@app.post("/api/knowledge/bases/{kb_id}/rag-retrieve")
async def rag_retrieve(kb_id: str, req: RetrieveRequest):
    """RAG检索接口（增强版）"""
    from .rag_service import get_rag_service
    from .embedding_service import get_embedding_service

    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    embedding_svc = get_embedding_service()
    rag_svc = get_rag_service(chroma_client, embedding_svc)

    results = await rag_svc.rag_retrieve(
        query=req.query,
        kb_id=kb_id,
        top_k=req.topK,
        min_similarity=req.minSimilarity
    )

    return {"code": 200, "data": {"results": results, "total": len(results), "query": req.query}}

@app.post("/api/knowledge/bases/{kb_id}/rag-generate")
async def rag_generate(kb_id: str, req: RAGGenerateRequest):
    """RAG生成：检索 + 生成"""
    from .rag_service import get_rag_service
    from .embedding_service import get_embedding_service

    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    if not chroma_client:
        raise HTTPException(status_code=503, detail="Vector store not available")

    embedding_svc = get_embedding_service()
    rag_svc = get_rag_service(chroma_client, embedding_svc)

    result = await rag_svc.rag_full(
        query=req.query,
        kb_id=kb_id,
        top_k=req.topK,
        min_similarity=req.minSimilarity,
        system_prompt=req.systemPrompt,
        use_hybrid=req.useHybrid
    )

    return {"code": 200, "data": result}

@app.post("/api/knowledge/bases/{kb_id}/documents/batch")
async def batch_add_documents(kb_id: str, documents: List[DocumentCreate]):
    """批量添加文档"""
    results = []
    for doc in documents:
        result = await add_document_to_kb(kb_id, doc)
        results.append(result)
    return {"code": 200, "data": results}

@app.delete("/api/knowledge/bases/{kb_id}/documents/{doc_name}")
async def delete_doc_from_kb(kb_id: str, doc_name: str):
    """删除文档及其chunks"""
    if kb_id in _vector_store:
        _vector_store[kb_id] = [
            c for c in _vector_store[kb_id]
            if c["metadata"].get("doc_name") != doc_name
        ]
    return {"code": 200, "message": "deleted"}

# 兼容前端批量导入路由
@app.post("/api/knowledge/batch-import")
async def batch_import(file: UploadFile = File(...)):
    """批量导入知识文档"""
    global _document_id_counter
    content = await file.read()
    doc = {
        "id": _document_id_counter,
        "title": file.filename,
        "content": content.decode("utf-8", errors="ignore"),
        "category": "批量导入",
        "fileType": file.filename.split(".")[-1] if "." in file.filename else "txt",
        "updatedAt": "",
        "createdAt": ""
    }
    _documents.append(doc)
    _document_id_counter += 1
    return {"code": 200, "data": {"id": doc["id"], "filename": file.filename}}

# 兼容导出路由
@app.get("/api/knowledge/export")
async def export_knowledge(format: str = "json"):
    """导出知识"""
    return {"code": 200, "data": {"documents": _documents, "categories": _categories, "format": format}}

# 向量检索兼容路由
@app.post("/api/knowledge/vector/search")
async def vector_search(req: Dict):
    """向量检索"""
    query = req.get("query", "")
    kb_id = req.get("kbId", "kb_1")
    top_k = req.get("topK", 5)
    
    query_embedding = await embed_text(query)
    chunks = _vector_store.get(kb_id, [])
    
    scored = []
    for chunk in chunks:
        vector = chunk.get("vector", [])
        if vector and len(vector) == len(query_embedding):
            similarity = _cosine_similarity(query_embedding, vector)
            scored.append({
                "chunkId": chunk["id"],
                "content": chunk["content"],
                "similarity": similarity,
                "metadata": chunk.get("metadata", {})
            })
    
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return {"code": 200, "data": {"results": scored[:top_k], "total": len(scored)}}

# 混合搜索兼容路由
@app.post("/api/knowledge/hybrid/search")
async def hybrid_search_compat(req: Dict):
    """混合搜索"""
    query = req.get("query", "")
    kb_id = req.get("kbId", "kb_1")
    top_k = req.get("topK", 5)
    
    query_embedding = await embed_text(query)
    chunks = _vector_store.get(kb_id, [])
    
    scored = []
    for chunk in chunks:
        vector = chunk.get("vector", [])
        if vector and len(vector) == len(query_embedding):
            similarity = _cosine_similarity(query_embedding, vector)
            scored.append({
                "chunkId": chunk["id"],
                "content": chunk["content"],
                "similarity": similarity,
                "metadata": chunk.get("metadata", {})
            })
    
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return {"code": 200, "data": {"results": scored[:top_k], "total": len(scored), "query": query}}

# 相关片段路由
@app.post("/api/knowledge/chunks/related")
async def get_related_chunks(req: Dict):
    """获取相关片段"""
    chunk_id = req.get("chunkId", "")
    kb_id = req.get("kbId", "kb_1")
    top_k = req.get("topK", 5)
    
    chunks = _vector_store.get(kb_id, [])
    target_chunk = None
    for c in chunks:
        if c["id"] == chunk_id:
            target_chunk = c
            break
    
    if not target_chunk:
        return {"code": 200, "data": {"results": [], "total": 0}}
    
    query_embedding = target_chunk.get("vector", [])
    if not query_embedding:
        return {"code": 200, "data": {"results": [], "total": 0}}
    
    scored = []
    for chunk in chunks:
        if chunk["id"] == chunk_id:
            continue
        vector = chunk.get("vector", [])
        if vector and len(vector) == len(query_embedding):
            similarity = _cosine_similarity(query_embedding, vector)
            scored.append({
                "chunkId": chunk["id"],
                "content": chunk["content"],
                "similarity": similarity,
                "metadata": chunk.get("metadata", {})
            })
    
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return {"code": 200, "data": {"results": scored[:top_k], "total": len(scored)}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)
