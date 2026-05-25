"""ChromaDB向量数据库客户端"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger(__name__)

class ChromaClient:
    """ChromaDB向量数据库客户端"""

    def __init__(self, persist_directory: str = "/chroma/chroma_db"):
        self.persist_directory = persist_directory
        self._client = None
        self._initialized = False

    def _initialize(self):
        """初始化ChromaDB客户端"""
        if self._initialized:
            return

        try:
            self._client = chromadb.Client(
                Settings(
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                )
            )
            self._initialized = True
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}, using in-memory mode")
            self._client = chromadb.Client()
            self._initialized = True

    @property
    def client(self):
        if not self._initialized:
            self._initialize()
        return self._client

    def get_or_create_collection(self, name: str) -> Any:
        """获取或创建Collection"""
        return self.client.get_or_create_collection(name=name)

    def add_vectors(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """添加向量到Collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} vectors to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """向量检索"""
        try:
            collection = self.get_or_create_collection(collection_name)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )

            return {
                "ids": results.get("ids", [[]])[0],
                "documents": results.get("documents", [[]])[0],
                "metadatas": results.get("metadatas", [[]])[0],
                "distances": results.get("distances", [[]])[0]
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

    def delete_collection(self, name: str) -> bool:
        """删除Collection"""
        try:
            self.client.delete_collection(name=name)
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
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
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaClient()
    return _chroma_client