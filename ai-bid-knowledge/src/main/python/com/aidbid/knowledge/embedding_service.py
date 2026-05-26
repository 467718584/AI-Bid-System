"""向量嵌入服务 - 支持文本和图片嵌入"""
import os
import io
import httpx
import logging
import asyncio
from typing import List, Optional

logger = logging.getLogger(__name__)

# 向量维度常量
EMBEDDING_DIMENSION = 1536


class EmbeddingService:
    """向量嵌入服务"""

    def __init__(self, api_key: str, base_url: str = "https://api.minimax.chat/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self._http_client = None
        self._simple_model = None

    @property
    def http_client(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _get_simple_model(self):
        """获取简单嵌入模型"""
        if self._simple_model is None:
            from .config import SimpleEmbeddingModel
            self._simple_model = SimpleEmbeddingModel()
        return self._simple_model

    async def embed_text(self, text: str) -> List[float]:
        """单文本嵌入"""
        results = await self.embed_texts([text])
        return results[0]

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文本嵌入（最多100条）"""
        if not texts:
            return []

        if len(texts) > 100:
            results = []
            for i in range(0, len(texts), 100):
                batch = texts[i:i + 100]
                results.extend(await self._embed_batch(batch))
            return results

        return await self._embed_batch(texts)

    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入（内部方法）"""
        # 尝试使用MiniMax API
        if self.api_key:
            url = f"{self.base_url}/embeddings"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "embo01",
                "texts": texts,
                "type": "dbqa"
            }

            try:
                response = await self.http_client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                vectors = result.get("vectors", [])
                if vectors:
                    return [v.get("embedding", v) if isinstance(v, dict) else v for v in vectors]

                error_msg = result.get("base_resp", {}).get("status_msg", "")
                if "insufficient" in error_msg.lower():
                    logger.warning(f"MiniMax API insufficient balance, using simple fallback")
                else:
                    logger.warning(f"MiniMax API error: {error_msg}")

            except Exception as e:
                logger.warning(f"MiniMax embedding failed: {e}, using simple fallback")

        # 使用简单模型
        model = self._get_simple_model()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, model.encode, texts)

    async def embed_image(self, image_path: str) -> List[float]:
        """图片嵌入（使用文本描述作为备选）"""
        try:
            from PIL import Image
            import base64
            import io

            img = Image.open(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            if self.api_key:
                url = f"{self.base_url}/embeddings"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "CLIP",
                    "input": [{"type": "image", "image": img_base64}]
                }

                response = await self.http_client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                vectors = result.get("vectors", [])
                if vectors and len(vectors) > 0:
                    v = vectors[0]
                    return v.get("embedding", v) if isinstance(v, dict) else v

        except Exception as e:
            logger.warning(f"Image embedding failed: {e}")

        return await self.embed_text(f"image: {image_path}")

    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        import numpy as np

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


# 全局单例
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(api_key: Optional[str] = None) -> EmbeddingService:
    """获取嵌入服务实例"""
    global _embedding_service

    if _embedding_service is None:
        api_key = api_key or os.getenv("MINIMAX_API_KEY")
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        _embedding_service = EmbeddingService(api_key, base_url)

    return _embedding_service


async def close_embedding_service():
    """关闭嵌入服务"""
    global _embedding_service
    if _embedding_service:
        await _embedding_service.close()
        _embedding_service = None