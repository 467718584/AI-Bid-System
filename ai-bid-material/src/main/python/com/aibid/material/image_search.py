"""素材图片搜索模块 - 基于标签/关键词和内容相似度搜索"""
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)


class ImageSearchResult:
    """图片搜索结果"""

    def __init__(
        self,
        image_id: str,
        path: str,
        url: Optional[str] = None,
        caption: str = "",
        tags: Optional[List[str]] = None,
        score: float = 0.0,
        material_id: Optional[int] = None
    ):
        self.image_id = image_id
        self.path = path
        self.url = url
        self.caption = caption
        self.tags = tags or []
        self.score = score
        self.material_id = material_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.image_id,
            "path": self.path,
            "url": self.url,
            "caption": self.caption,
            "tags": self.tags,
            "score": self.score
        }


class ImageSearch:
    """素材图片搜索引擎

    支持两种搜索模式：
    1. 关键词搜索：基于标签和描述文本匹配
    2. 内容相似度搜索：基于CLIP embedding计算语义相似度
    """

    def __init__(self, base_url: str = "http://localhost:8083"):
        self.base_url = base_url
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def search_by_keywords(
        self,
        query: str,
        count: int = 5,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ImageSearchResult]:
        """基于关键词/标签搜索图片

        Args:
            query: 搜索关键词
            count: 返回数量
            project_id: 项目ID（可选，用于限定搜索范围）
            tags: 额外标签过滤（可选）

        Returns:
            匹配的图片列表，按相关度排序
        """
        try:
            # 调用素材服务API
            url = f"{self.base_url}/api/material/search"
            params = {
                "keyword": query,
                "limit": count,
                "type": "image"
            }
            if project_id:
                params["projectId"] = project_id

            response = await self.http_client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return self._parse_material_response(data)

        except Exception as e:
            logger.warning(f"Keyword search failed: {e}")

        # 降级：返回空列表
        return []

    async def search_by_content(
        self,
        query_text: str,
        image_paths: List[str],
        count: int = 5,
        threshold: float = 0.5
    ) -> List[ImageSearchResult]:
        """基于内容相似度搜索图片

        使用CLIP embedding计算文本与图片的语义相似度。

        Args:
            query_text: 查询文本
            image_paths: 候选图片路径列表
            count: 返回数量
            threshold: 相似度阈值（0-1）

        Returns:
            相似图片列表，按相似度排序
        """
        try:
            from ...knowledge.embedding_service import get_embedding_service
            import numpy as np

            # 获取嵌入服务（需要配置API Key）
            try:
                embedding_service = get_embedding_service()
            except RuntimeError as e:
                logger.warning(f"Embedding service not available: {e}")
                return []

            # 1. 获取查询文本的embedding
            query_embedding = await embedding_service.embed_text(query_text)

            # 2. 获取候选图片的embedding
            results = []
            for path in image_paths:
                try:
                    img_embedding = await embedding_service.embed_image(path)
                    similarity = embedding_service.compute_similarity(
                        query_embedding, img_embedding
                    )

                    if similarity >= threshold:
                        results.append(ImageSearchResult(
                            image_id=os.path.basename(path),
                            path=path,
                            caption=query_text,
                            score=similarity
                        ))
                except Exception as e:
                    logger.warning(f"Failed to compute embedding for {path}: {e}")

            # 3. 按相似度排序并返回top_k
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:count]

        except ImportError as e:
            logger.warning(f"Content search dependency not available: {e}")
            return []
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return []

    async def search_hybrid(
        self,
        query: str,
        count: int = 5,
        project_id: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        alpha: float = 0.5
    ) -> List[ImageSearchResult]:
        """混合搜索：关键词 + 内容相似度

        Args:
            query: 搜索查询
            count: 返回数量
            project_id: 项目ID
            image_paths: 本地图片路径列表（用于内容相似度）
            alpha: 关键词权重（1-alpha为内容相似度权重）

        Returns:
            混合评分最高的图片列表
        """
        # 1. 关键词搜索
        keyword_results = await self.search_by_keywords(query, count * 2, project_id)

        # 2. 内容相似度搜索（如果有本地图片）
        content_results = []
        if image_paths:
            content_results = await self.search_by_content(
                query, image_paths, count * 2
            )

        # 3. 合并结果
        combined = self._merge_search_results(keyword_results, content_results, alpha)

        return combined[:count]

    def _parse_material_response(self, data: Dict) -> List[ImageSearchResult]:
        """解析素材服务响应"""
        results = []

        items = data.get("data", {}).get("items", data.get("data", []))
        if not isinstance(items, list):
            items = []

        for item in items:
            # 检查是否是图片类型的素材
            material_type = item.get("type", item.get("fileType", ""))
            if material_type.lower() not in ("image", "img", "jpg", "png", "svg"):
                continue

            results.append(ImageSearchResult(
                image_id=str(item.get("id", "")),
                path=item.get("path", item.get("url", "")),
                url=item.get("url", item.get("path", "")),
                caption=item.get("description", item.get("name", "")),
                tags=item.get("tags", []),
                score=item.get("score", 0.0),
                material_id=item.get("materialId", item.get("id"))
            ))

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def _merge_search_results(
        self,
        keyword_results: List[ImageSearchResult],
        content_results: List[ImageSearchResult],
        alpha: float
    ) -> List[ImageSearchResult]:
        """合并关键词搜索和内容搜索结果"""
        # 使用字典按image_id合并
        merged: Dict[str, ImageSearchResult] = {}

        for r in keyword_results:
            r.score = alpha * r.score  # 应用关键词权重
            merged[r.image_id] = r

        for r in content_results:
            beta = 1 - alpha
            if r.image_id in merged:
                merged[r.image_id].score += beta * r.score
            else:
                r.score = beta * r.score
                merged[r.image_id] = r

        # 转换为列表并排序
        result_list = list(merged.values())
        result_list.sort(key=lambda x: x.score, reverse=True)
        return result_list

    async def get_image_by_id(self, image_id: str) -> Optional[ImageSearchResult]:
        """根据ID获取图片信息"""
        try:
            url = f"{self.base_url}/api/material/{image_id}"
            response = await self.http_client.get(url)

            if response.status_code == 200:
                data = response.json()
                item = data.get("data", {})
                return ImageSearchResult(
                    image_id=str(item.get("id", "")),
                    path=item.get("path", ""),
                    url=item.get("url", ""),
                    caption=item.get("description", ""),
                    tags=item.get("tags", [])
                )

        except Exception as e:
            logger.warning(f"Failed to get image by ID: {e}")

        return None

    async def get_related_images(
        self,
        seed_image_path: str,
        count: int = 5
    ) -> List[ImageSearchResult]:
        """获取与指定图片相似的其他图片

        Args:
            seed_image_path: 种子图片路径
            count: 返回数量

        Returns:
            相似图片列表
        """
        try:
            from ...knowledge.embedding_service import get_embedding_service

            embedding_service = get_embedding_service()

            # 获取种子图片的embedding
            seed_embedding = await embedding_service.embed_image(seed_image_path)

            # TODO: 在素材库中搜索相似embedding
            # 暂时返回空列表
            logger.info("Related image search requires material library integration")

            return []

        except Exception as e:
            logger.warning(f"Failed to get related images: {e}")
            return []


# ============================================================
# 同步搜索包装器（供同步上下文使用）
# ============================================================

class SyncImageSearch:
    """同步图片搜索（包装异步版本）"""

    def __init__(self, base_url: str = "http://localhost:8083"):
        self.base_url = base_url

    def search_by_keywords(
        self,
        query: str,
        count: int = 5,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """同步关键词搜索"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        search = ImageSearch(self.base_url)
        try:
            results = loop.run_until_complete(
                search.search_by_keywords(query, count, project_id)
            )
            return [r.to_dict() for r in results]
        finally:
            loop.run_until_complete(search.close())

    def search_hybrid(
        self,
        query: str,
        count: int = 5,
        image_paths: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """同步混合搜索"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        search = ImageSearch(self.base_url)
        try:
            results = loop.run_until_complete(
                search.search_hybrid(query, count, image_paths=image_paths)
            )
            return [r.to_dict() for r in results]
        finally:
            loop.run_until_complete(search.close())


# ============================================================
# 全局单例
# ============================================================

_image_search: Optional[ImageSearch] = None


def get_image_search() -> ImageSearch:
    """获取图片搜索实例"""
    global _image_search
    if _image_search is None:
        material_url = os.getenv("MATERIAL_SERVICE_URL", "http://localhost:8083")
        _image_search = ImageSearch(base_url=material_url)
    return _image_search