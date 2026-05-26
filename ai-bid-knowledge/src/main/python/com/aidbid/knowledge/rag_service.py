"""RAG服务 - 检索增强生成"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

# 全局配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "abab6-chat")


class RAGService:
    """RAG检索增强生成服务"""

    def __init__(
        self,
        chroma_client,  # ChromaDB客户端
        embedding_service  # 嵌入服务
    ):
        self.chroma_client = chroma_client
        self.embedding_service = embedding_service
        self._http_client = None

    @property
    def http_client(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=120.0)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def rag_retrieve(
        self,
        query: str,
        kb_id: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
        use_hybrid: bool = True,
        alpha: float = 0.7
    ) -> List[Dict[str, Any]]:
        """RAG检索 - 从知识库获取相关上下文"""
        try:
            collection_name = f"kb_{kb_id}"

            # 获取查询向量
            query_embedding = await self.embedding_service.embed_text(query)

            if use_hybrid:
                # 混合检索
                results = self.chroma_client.hybrid_search(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    query_text=query,
                    n_results=top_k * 2,
                    alpha=alpha
                )
            else:
                # 纯向量检索
                raw_results = self.chroma_client.query(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    n_results=top_k * 2
                )
                results = [
                    {
                        "id": raw_results["ids"][i],
                        "content": raw_results["documents"][i],
                        "metadata": raw_results["metadatas"][i],
                        "distance": raw_results["distances"][i],
                        "similarity": 1.0 - (raw_results["distances"][i] / 2.0) if raw_results["distances"][i] else 0.5
                    }
                    for i in range(len(raw_results["ids"]))
                ]

            # 过滤低相似度结果
            filtered_results = [
                r for r in results
                if r.get("similarity", 0) >= min_similarity
            ][:top_k]

            return filtered_results

        except Exception as e:
            logger.error(f"RAG retrieve failed: {e}")
            return []

    async def rag_retrieve_with_sources(
        self,
        query: str,
        kb_id: str,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> Tuple[List[Dict[str, Any]], str]:
        """RAG检索 - 返回带来源的上下文"""
        results = await self.rag_retrieve(query, kb_id, top_k, min_similarity)

        # 构建上下文
        context_parts = []
        sources = []

        for i, r in enumerate(results):
            context_parts.append(f"[{i + 1}] {r['content']}")
            sources.append({
                "id": r.get("id", ""),
                "content": r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"],
                "similarity": r.get("similarity", 0)
            })

        context = "\n\n".join(context_parts)

        return results, context, sources

    async def rag_generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """RAG生成 - 结合上下文生成回答"""
        try:
            # 构建prompt
            if use_rag and context:
                user_prompt = f"""基于以下参考资料回答问题。如果参考资料中没有相关信息，请说明"根据已有资料无法回答"。

参考资料：
{context}

问题：{query}

回答："""
            else:
                user_prompt = query

            # 调用LLM
            response = await self._call_llm(user_prompt, system_prompt)

            return {
                "answer": response.get("content", ""),
                "model": response.get("model", MINIMAX_MODEL),
                "usage": response.get("usage", {}),
                "finish_reason": response.get("finish_reason", "")
            }

        except Exception as e:
            logger.error(f"RAG generate failed: {e}")
            return {
                "answer": f"生成失败: {str(e)}",
                "model": MINIMAX_MODEL,
                "usage": {},
                "error": str(e)
            }

    async def rag_full(
        self,
        query: str,
        kb_id: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
        system_prompt: Optional[str] = None,
        use_hybrid: bool = True
    ) -> Dict[str, Any]:
        """完整的RAG流程：检索 + 生成"""
        try:
            # 1. 检索相关上下文
            results, context, sources = await self.rag_retrieve_with_sources(
                query, kb_id, top_k, min_similarity
            )

            # 2. 生成回答
            generation = await self.rag_generate(
                query, context, system_prompt, use_rag=bool(context)
            )

            return {
                "query": query,
                "answer": generation.get("answer", ""),
                "sources": sources,
                "retrieved_count": len(results),
                "model": generation.get("model", ""),
                "usage": generation.get("usage", {}),
                "context_used": bool(context)
            }

        except Exception as e:
            logger.error(f"RAG full pipeline failed: {e}")
            return {
                "query": query,
                "answer": f"RAG流程失败: {str(e)}",
                "sources": [],
                "retrieved_count": 0,
                "error": str(e)
            }

    async def _call_llm(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用LLM API"""
        if not MINIMAX_API_KEY:
            raise RuntimeError("MINIMAX_API_KEY not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        url = f"{MINIMAX_BASE_URL}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": MINIMAX_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }

        response = await self.http_client.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        return {
            "content": result["choices"][0]["message"]["content"],
            "model": result.get("model", MINIMAX_MODEL),
            "usage": result.get("usage", {}),
            "finish_reason": result["choices"][0].get("finish_reason", "")
        }


# 全局单例
_rag_service: Optional[RAGService] = None


def get_rag_service(
    chroma_client,
    embedding_service
) -> RAGService:
    """获取RAG服务实例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(chroma_client, embedding_service)
    return _rag_service


async def close_rag_service():
    """关闭RAG服务"""
    global _rag_service
    if _rag_service:
        await _rag_service.close()
        _rag_service = None