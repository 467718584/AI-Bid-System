"""FastAPI主应用 - AI投标知识库服务"""
import logging
import hashlib
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .models import (
    KnowledgeBase, KnowledgeChunk, RetrieveRequest, RetrieveResponse,
    KnowledgeBaseCreateRequest, KnowledgeBaseUpdateRequest,
    ChunkCreateRequest, ChunkBatchCreateRequest, ChunkStatus
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# LLM网关类
# ============================================================

class LLMGateway:
    """LLM统一网关，支持多后端切换"""

    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if self.provider == "minimax":
                from langchain_community.chat_models import MiniMaxChat
                self._client = MiniMaxChat(
                    model_name=config.MINIMAX_MODEL,
                    api_key=config.MINIMAX_API_KEY,
                    base_url=config.MINIMAX_BASE_URL
                )
            elif self.provider == "deepseek":
                from langchain_community.chat_models import ChatOpenAI
                self._client = ChatOpenAI(
                    model=config.DEEPSEEK_MODEL,
                    openai_api_key=config.DEEPSEEK_API_KEY,
                    openai_api_base=config.DEEPSEEK_BASE_URL
                )
            elif self.provider == "qwen":
                from langchain_community.chat_models import ChatOpenAI
                self._client = ChatOpenAI(
                    model=config.QWEN_MODEL,
                    openai_api_key=config.QWEN_API_KEY,
                    openai_api_base=config.QWEN_BASE_URL
                )
        return self._client

    def chat(self, prompt: str, **kwargs) -> str:
        """通用对话接口"""
        try:
            response = self.client.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise HTTPException(status_code=500, detail=f"LLM调用失败: {str(e)}")


# ============================================================
# RAG服务类
# ============================================================

class RAGService:
    """RAG检索增强生成服务"""

    def __init__(self):
        self.llm_gateway = LLMGateway()
        self._vector_store = None
        self._embedding_model = None
        self._initialize()

    def _initialize(self):
        """初始化向量数据库和Embedding模型"""
        try:
            import chromadb
            from langchain_community.embeddings import HuggingFaceEmbeddings

            # 初始化Chroma客户端
            chroma_client = chromadb.HttpClient(
                host=config.CHROMA_HOST,
                port=config.CHROMA_PORT
            )
            self._vector_store = chroma_client

            # 初始化Embedding模型
            self._embedding_model = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs={'device': config.EMBEDDING_DEVICE}
            )
            logger.info("RAG服务初始化成功")
        except Exception as e:
            logger.warning(f"RAG服务初始化警告: {e}")

    def get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        if self._embedding_model is None:
            self._initialize()
        return self._embedding_model.embed_query(text)

    def retrieve(self, request: RetrieveRequest) -> RetrieveResponse:
        """向量检索"""
        import time
        start_time = time.time()

        if self._vector_store is None:
            self._initialize()

        try:
            query_vector = self.get_embedding(request.query)

            # 构建查询条件
            where_filter = {}
            if request.knowledge_base_id:
                where_filter["knowledge_base_id"] = request.knowledge_base_id
            if request.filter:
                where_filter.update(request.filter)

            # 查询向量数据库
            collection_name = "knowledge_chunks"
            results = []

            try:
                collection = self._vector_store.get_collection(collection_name)
                query_results = collection.query(
                    query_embeddings=[query_vector],
                    n_results=request.top_k,
                    where=where_filter if where_filter else None
                )

                # 解析结果
                if query_results and query_results.get('documents'):
                    for i, doc in enumerate(query_results['documents'][0]):
                        distance = query_results['distances'][0][i] if 'distances' in query_results else 0
                        score = 1 - distance if distance <= 1 else 0

                        if score >= request.score_threshold:
                            metadata = query_results['metadatas'][0][i] if 'metadatas' in query_results else {}
                            results.append({
                                "content": doc,
                                "score": score,
                                "metadata": metadata
                            })
            except Exception as e:
                logger.warning(f"向量检索查询失败: {e}")

            duration_ms = (time.time() - start_time) * 1000

            return RetrieveResponse(
                query=request.query,
                results=results,
                total=len(results),
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.error(f"检索失败: {e}")
            raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


# ============================================================
# 知识库存储（内存模拟，生产应使用数据库）
# ============================================================

class KnowledgeStore:
    """知识库内存存储（生产环境应使用数据库）"""

    def __init__(self):
        self.bases: Dict[str, KnowledgeBase] = {}
        self.chunks: Dict[str, KnowledgeChunk] = {}

    def create_base(self, request: KnowledgeBaseCreateRequest) -> KnowledgeBase:
        """创建知识库"""
        kb_id = str(uuid.uuid4())
        now = datetime.now()
        kb = KnowledgeBase(
            id=kb_id,
            name=request.name,
            description=request.description,
            kb_type=request.kb_type or "general",
            metadata=request.metadata or {},
            created_at=now,
            updated_at=now
        )
        self.bases[kb_id] = kb
        return kb

    def get_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        return self.bases.get(kb_id)

    def list_bases(self) -> List[KnowledgeBase]:
        return list(self.bases.values())

    def update_base(self, kb_id: str, request: KnowledgeBaseUpdateRequest) -> Optional[KnowledgeBase]:
        kb = self.bases.get(kb_id)
        if not kb:
            return None
        if request.name is not None:
            kb.name = request.name
        if request.description is not None:
            kb.description = request.description
        if request.metadata is not None:
            kb.metadata = request.metadata
        kb.updated_at = datetime.now()
        return kb

    def delete_base(self, kb_id: str) -> bool:
        if kb_id in self.bases:
            del self.bases[kb_id]
            # 删除关联的知识块
            to_delete = [cid for cid, c in self.chunks.items() if c.knowledge_base_id == kb_id]
            for cid in to_delete:
                del self.chunks[cid]
            return True
        return False

    def create_chunk(self, request: ChunkCreateRequest) -> KnowledgeChunk:
        """创建知识块"""
        chunk_id = str(uuid.uuid4())
        now = datetime.now()
        content_hash = hashlib.md5(request.content.encode()).hexdigest()

        chunk = KnowledgeChunk(
            id=chunk_id,
            knowledge_base_id=request.knowledge_base_id,
            content=request.content,
            content_hash=content_hash,
            metadata=request.metadata or {},
            chunk_order=request.chunk_order or 0,
            created_at=now,
            updated_at=now
        )
        self.chunks[chunk_id] = chunk

        # 更新知识库统计
        kb = self.bases.get(request.knowledge_base_id)
        if kb:
            kb.chunk_count = len([c for c in self.chunks.values() if c.knowledge_base_id == request.knowledge_base_id])
            kb.updated_at = now

        return chunk

    def get_chunk(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        return self.chunks.get(chunk_id)

    def list_chunks(self, kb_id: str) -> List[KnowledgeChunk]:
        return [c for c in self.chunks.values() if c.knowledge_base_id == kb_id and c.status == ChunkStatus.ACTIVE]

    def delete_chunk(self, chunk_id: str) -> bool:
        chunk = self.chunks.get(chunk_id)
        if chunk:
            chunk.status = ChunkStatus.DELETED
            return True
        return False


# ============================================================
# FastAPI应用
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("AI投标知识库服务启动中...")
    yield
    logger.info("AI投标知识库服务关闭...")


app = FastAPI(
    title="AI投标知识库服务",
    description="提供RAG知识库检索能力，支持投标文档智能问答",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
rag_service = RAGService()
knowledge_store = KnowledgeStore()
llm_gateway = LLMGateway()


# ============================================================
# 知识库CRUD接口
# ============================================================

@app.post("/api/v1/knowledge-bases", response_model=KnowledgeBase, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(request: KnowledgeBaseCreateRequest):
    """创建知识库"""
    return knowledge_store.create_base(request)


@app.get("/api/v1/knowledge-bases", response_model=List[KnowledgeBase])
async def list_knowledge_bases():
    """获取知识库列表"""
    return knowledge_store.list_bases()


@app.get("/api/v1/knowledge-bases/{kb_id}", response_model=KnowledgeBase)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    kb = knowledge_store.get_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb


@app.put("/api/v1/knowledge-bases/{kb_id}", response_model=KnowledgeBase)
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdateRequest):
    """更新知识库"""
    kb = knowledge_store.update_base(kb_id, request)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb


@app.delete("/api/v1/knowledge-bases/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    if not knowledge_store.delete_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")


# ============================================================
# 知识块CRUD接口
# ============================================================

@app.post("/api/v1/chunks", response_model=KnowledgeChunk, status_code=status.HTTP_201_CREATED)
async def create_chunk(request: ChunkCreateRequest):
    """创建知识块"""
    # 验证知识库存在
    if not knowledge_store.get_base(request.knowledge_base_id):
        raise HTTPException(status_code=404, detail="知识库不存在")
    return knowledge_store.create_chunk(request)


@app.post("/api/v1/chunks/batch", response_model=List[KnowledgeChunk], status_code=status.HTTP_201_CREATED)
async def create_chunks_batch(request: ChunkBatchCreateRequest):
    """批量创建知识块"""
    if not knowledge_store.get_base(request.knowledge_base_id):
        raise HTTPException(status_code=404, detail="知识库不存在")
    return [knowledge_store.create_chunk(c) for c in request.chunks]


@app.get("/api/v1/knowledge-bases/{kb_id}/chunks", response_model=List[KnowledgeChunk])
async def list_chunks(kb_id: str):
    """获取知识库下的知识块列表"""
    if not knowledge_store.get_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")
    return knowledge_store.list_chunks(kb_id)


@app.delete("/api/v1/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(chunk_id: str):
    """删除知识块"""
    if not knowledge_store.delete_chunk(chunk_id):
        raise HTTPException(status_code=404, detail="知识块不存在")


# ============================================================
# 向量检索接口
# ============================================================

@app.post("/api/v1/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    """向量检索接口"""
    return rag_service.retrieve(request)


@app.post("/api/v1/retrieve/chat", status_code=status.HTTP_200_OK)
async def retrieve_with_chat(request: RetrieveRequest):
    """带LLM生成的检索问答"""
    # 1. 检索相关知识
    retrieve_result = rag_service.retrieve(request)

    if not retrieve_result.results:
        return {"answer": "抱歉，未找到相关信息", "sources": []}

    # 2. 构建上下文
    context_parts = []
    for idx, result in enumerate(retrieve_result.results[:3], 1):
        context_parts.append(f"[{idx}] {result['content']}")

    context = "\n\n".join(context_parts)

    # 3. 调用LLM生成答案
    prompt = f"""基于以下参考信息，回答用户问题。如果参考信息不足，请明确说明。

参考信息：
{context}

用户问题：{request.query}

请给出准确、简洁的回答，并适当引用参考信息。"""

    try:
        answer = llm_gateway.chat(prompt)
        return {
            "answer": answer,
            "sources": retrieve_result.results[:3]
        }
    except Exception as e:
        logger.error(f"LLM生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"LLM生成失败: {str(e)}")


# ============================================================
# 健康检查接口
# ============================================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-bid-knowledge",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "com.aidbid.knowledge.main:app",
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
        reload=True
    )