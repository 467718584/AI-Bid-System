"""ChromaDB向量数据库客户端 - 真实向量存储与检索"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger(__name__)

# 向量维度常量
# 注意：1536用于MiniMax embo01，简单模型使用384
DEFAULT_EMBEDDING_DIMENSION = 384


class ChromaClient:
    """ChromaDB向量数据库客户端 - 真实向量存储"""

    def __init__(self, persist_directory: str = "/chroma/chroma_db"):
        self.persist_directory = persist_directory
        self._client = None
        self._initialized = False

    def _initialize(self):
        """初始化ChromaDB客户端"""
        if self._initialized:
            return

        try:
            # 确保目录存在
            os.makedirs(self.persist_directory, exist_ok=True)

            # 使用PersistentClient进行持久化存储
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            self._initialized = True
            logger.info(f"ChromaDB initialized with persistence at {self.persist_directory}")
        except Exception as e:
            logger.warning(f"ChromaDB persistent mode failed: {e}, trying in-memory mode")
            try:
                self._client = chromadb.Client()
                self._initialized = True
                logger.info("ChromaDB initialized in-memory mode")
            except Exception as e2:
                logger.error(f"ChromaDB initialization completely failed: {e2}")
                raise

    @property
    def client(self):
        if not self._initialized:
            self._initialize()
        return self._client

    def get_or_create_collection(self, name: str) -> Any:
        """获取或创建Collection"""
        return self.client.get_or_create_collection(name=name)

    def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """添加文档到Collection（真实向量存储）"""
        try:
            collection = self.get_or_create_collection(collection_name)

            # 验证向量维度
            for i, emb in enumerate(embeddings):
                if len(emb) != len(embeddings[0]) if embeddings else True:
                    embeddings[i] = self._pad_embedding(emb, len(embeddings[0]) if embeddings else DEFAULT_EMBEDDING_DIMENSION)

            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} documents to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def add_vectors(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """添加向量到Collection（别名）"""
        return self.add_documents(collection_name, ids, embeddings, documents, metadatas)

    def _pad_embedding(self, emb: List[float], target_dim: int = DEFAULT_EMBEDDING_DIMENSION) -> List[float]:
        """填充或截断向量到标准维度"""
        if len(emb) < target_dim:
            return emb + [0.0] * (target_dim - len(emb))
        elif len(emb) > target_dim:
            return emb[:target_dim]
        return emb

    def query(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5,
        where_filter: Optional[Dict] = None,
        where_document_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """向量检索（真实语义检索）"""
        try:
            collection = self.get_or_create_collection(collection_name)

            # 调试日志
            logger.info(f"[DEBUG] Query collection={collection_name}, query_embedding_dim={len(query_embedding)}, collection_count={collection.count()}")

            # 验证查询向量维度
            target_dim = DEFAULT_EMBEDDING_DIMENSION
            if collection.count() > 0:
                existing = collection.get(limit=1, include=["embeddings"])
                existing_embs = existing.get("embeddings", [])
                # 处理ChromaDB返回的numpy数组
                if existing_embs is not None and len(existing_embs) > 0:
                    first_emb = existing_embs[0]
                    if hasattr(first_emb, '__len__'):
                        target_dim = len(first_emb)
                    elif hasattr(first_emb, 'tolist'):
                        target_dim = len(first_emb.tolist())
                    logger.info(f"[DEBUG] Using existing collection dimension: {target_dim}")

            if len(query_embedding) != target_dim:
                logger.warning(f"[DEBUG] Padding query embedding: {len(query_embedding)} -> {target_dim}")
                query_embedding = self._pad_embedding(query_embedding, target_dim)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                where_document=where_document_filter
            )

            return self._format_results(results)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": [], "embeddings": []}

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """向量检索（别名）"""
        return self.query(collection_name, query_embedding, n_results, where_filter, None)

    def _format_results(self, results: Dict) -> Dict[str, Any]:
        """格式化查询结果"""
        return {
            "ids": results.get("ids", [[]])[0] if results.get("ids") else [],
            "documents": results.get("documents", [[]])[0] if results.get("documents") else [],
            "metadatas": results.get("metadatas", [[]])[0] if results.get("metadatas") else [],
            "distances": results.get("distances", [[]])[0] if results.get("distances") else [],
            "embeddings": results.get("embeddings", [[]])[0] if results.get("embeddings") else []
        }

    def hybrid_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        query_text: str,
        n_results: int = 10,
        alpha: float = 0.7
    ) -> List[Dict[str, Any]]:
        """混合检索：向量检索 + 关键词检索"""
        try:
            collection = self.get_or_create_collection(collection_name)

            # 1. 向量检索
            vector_results = self.query(
                collection_name,
                query_embedding,
                n_results=n_results * 2  # 获取更多结果用于混合
            )

            # 2. 关键词检索（从向量结果中筛选）
            keyword_results = self._keyword_search(
                vector_results.get("documents", []),
                query_text
            )

            # 3. 混合打分
            scored_results = self._mix_scores(
                vector_results,
                keyword_results,
                alpha
            )

            # 4. 取top_k
            return scored_results[:n_results]
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    def _keyword_search(self, documents: List[str], query: str) -> Dict[str, float]:
        """关键词匹配评分"""
        query_keywords = self._extract_keywords(query)
        scores = {}

        for i, doc in enumerate(documents):
            doc_lower = doc.lower()
            score = 0
            for keyword in query_keywords:
                if keyword in doc_lower:
                    score += 1
            if score > 0:
                scores[str(i)] = score / len(query_keywords)

        return scores

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现）"""
        # 去除停用词
        stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        words = text.replace(",", " ").replace("。", " ").replace("，", " ").split()
        return [w for w in words if w not in stopwords and len(w) > 1]

    def _mix_scores(
        self,
        vector_results: Dict,
        keyword_scores: Dict[str, float],
        alpha: float = 0.7
    ) -> List[Dict[str, Any]]:
        """混合向量相似度和关键词得分"""
        results = []

        for i in range(len(vector_results.get("ids", []))):
            vector_dist = vector_results["distances"][i] if i < len(vector_results.get("distances", [])) else 1.0
            vector_score = 1.0 - (vector_dist / 2.0) if vector_dist else 0.5  # 转换为0-1分数

            keyword_score = keyword_scores.get(str(i), 0.0)

            # 混合分数：alpha * 向量分数 + (1-alpha) * 关键词分数
            mixed_score = alpha * vector_score + (1 - alpha) * keyword_score

            results.append({
                "id": vector_results["ids"][i] if i < len(vector_results.get("ids", [])) else "",
                "content": vector_results["documents"][i] if i < len(vector_results.get("documents", [])) else "",
                "metadata": vector_results["metadatas"][i] if i < len(vector_results.get("metadatas", [])) else {},
                "distance": vector_dist,
                "similarity": mixed_score,
                "vector_score": vector_score,
                "keyword_score": keyword_score
            })

        # 按混合分数排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

    def rerank_results(
        self,
        results: List[Dict],
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """重排序结果"""
        if not results:
            return []

        # 基于关键词匹配重排序
        query_keywords = set(self._extract_keywords(query))

        reranked = []
        for r in results:
            content = r.get("content", "").lower()
            keyword_hits = sum(1 for kw in query_keywords if kw in content)

            # 位置得分：匹配的关键词越靠前越好
            position_score = 0
            for kw in query_keywords:
                pos = content.find(kw)
                if pos >= 0:
                    position_score += 1.0 / (pos + 1)

            # 综合分数
            final_score = r.get("similarity", 0.5) * 0.6 + (keyword_hits / max(len(query_keywords), 1)) * 0.3 + position_score * 0.1

            reranked.append({
                **r,
                "keyword_hits": keyword_hits,
                "final_score": final_score
            })

        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked[:top_k]

    def delete_collection(self, name: str) -> bool:
        """删除Collection"""
        try:
            self.client.delete_collection(name=name)
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    def reset(self) -> bool:
        """重置数据库"""
        try:
            self.client.reset()
            logger.info("ChromaDB reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset: {e}")
            return False

    def list_collections(self) -> List[str]:
        """列出所有Collection"""
        try:
            return [c.name for c in self.client.list_collections()]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def get_collection_info(self, name: str) -> Optional[Dict]:
        """获取Collection信息"""
        try:
            collection = self.get_or_create_collection(name)
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None


# 全局单例
_chroma_client: Optional[ChromaClient] = None


def get_chroma_client() -> ChromaClient:
    """获取ChromaDB客户端实例"""
    global _chroma_client
    if _chroma_client is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "/chroma/chroma_db")
        _chroma_client = ChromaClient(persist_directory=persist_dir)
    return _chroma_client