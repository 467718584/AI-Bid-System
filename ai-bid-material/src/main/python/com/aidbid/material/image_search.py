"""
Image Search & Private Image Library

提供图片搜索（关键词 + CLIP 向量语义）、AI 图片生成、私人图库管理、
图片版权检测等完整图片素材管理功能。
"""
import logging
import os
import json
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


# ========== Data Models ==========


@dataclass
class ImageSearchResult:
    """图片搜索结果"""
    image_id: int
    path: str = ""
    url: str = ""
    caption: str = ""
    tags: List[str] = field(default_factory=list)
    score: float = 0.0
    material_id: int = 0
    width: int = 0
    height: int = 0
    ai_generated: bool = False
    copyright_status: str = "UNKNOWN"
    detection_result: str = ""


@dataclass
class PrivateImage:
    """私人图片数据模型"""
    id: int
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    file_path: str = ""
    file_url: str = ""
    file_size: int = 0
    width: int = 0
    height: int = 0
    thumbnail_path: str = ""
    ai_generated: bool = False
    ai_model: str = ""
    ai_prompt: str = ""
    ai_negative_prompt: str = ""
    copyright_status: str = "OWNED"
    copyright_remark: str = ""
    source_url: str = ""
    detected_sources: List[Dict[str, Any]] = field(default_factory=list)
    detection_score: float = 0.0
    detection_result: str = ""  # CLEAN / SUSPICIOUS / COPYRIGHTED
    usage_count: int = 0
    upload_user_id: int = 0
    album_id: int = 0
    status: str = "ACTIVE"
    create_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "filePath": self.file_path,
            "fileUrl": self.file_url,
            "fileSize": self.file_size,
            "width": self.width,
            "height": self.height,
            "thumbnailPath": self.thumbnail_path,
            "aiGenerated": self.ai_generated,
            "aiModel": self.ai_model,
            "aiPrompt": self.ai_prompt,
            "aiNegativePrompt": self.ai_negative_prompt,
            "copyrightStatus": self.copyright_status,
            "copyrightRemark": self.copyright_remark,
            "sourceUrl": self.source_url,
            "detectedSources": self.detected_sources,
            "detectionScore": self.detection_score,
            "detectionResult": self.detection_result,
            "usageCount": self.usage_count,
            "uploadUserId": self.upload_user_id,
            "albumId": self.album_id,
            "status": self.status,
            "createTime": self.create_time.isoformat() if self.create_time else None,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PrivateImage":
        tags_raw = d.get("tags", "")
        if isinstance(tags_raw, str):
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        elif isinstance(tags_raw, list):
            tags = tags_raw
        else:
            tags = []

        detected_raw = d.get("detectedSources", [])
        if isinstance(detected_raw, str):
            try:
                detected = json.loads(detected_raw)
            except Exception:
                detected = []
        else:
            detected = detected_raw

        ct = d.get("createTime")
        if isinstance(ct, str):
            try:
                ct = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            except Exception:
                ct = None
        else:
            ct = None

        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            description=d.get("description", ""),
            tags=tags,
            file_path=d.get("filePath", ""),
            file_url=d.get("fileUrl", ""),
            file_size=d.get("fileSize", 0),
            width=d.get("width", 0),
            height=d.get("height", 0),
            thumbnail_path=d.get("thumbnailPath", ""),
            ai_generated=bool(d.get("aiGenerated")),
            ai_model=d.get("aiModel", ""),
            ai_prompt=d.get("aiPrompt", ""),
            ai_negative_prompt=d.get("aiNegativePrompt", ""),
            copyright_status=d.get("copyrightStatus", "OWNED"),
            copyright_remark=d.get("copyrightRemark", ""),
            source_url=d.get("sourceUrl", ""),
            detected_sources=detected,
            detection_score=float(d.get("detectionScore") or 0),
            detection_result=d.get("detectionResult", ""),
            usage_count=d.get("usageCount", 0),
            upload_user_id=d.get("uploadUserId", 0),
            album_id=d.get("albumId", 0),
            status=d.get("status", "ACTIVE"),
            create_time=ct,
        )


@dataclass
class ImageAlbum:
    """私人图库相册"""
    id: int
    name: str
    description: str = ""
    cover_image_id: int = 0
    image_count: int = 0
    upload_user_id: int = 0
    sort: int = 0
    status: int = 1
    create_time: Optional[datetime] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ImageAlbum":
        ct = d.get("createTime")
        if isinstance(ct, str):
            try:
                ct = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            except Exception:
                ct = None
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            description=d.get("description", ""),
            cover_image_id=d.get("coverImageId", 0),
            image_count=d.get("imageCount", 0),
            upload_user_id=d.get("uploadUserId", 0),
            sort=d.get("sort", 0),
            status=d.get("status", 1),
            create_time=ct,
        )


# ========== Image Search Engine ==========


class ImageSearch:
    """
    CLIP-based Image Search Engine

    支持：
    - 关键词/标签搜索（通过素材库 API）
    - CLIP 向量语义搜索（通过 embedding service）
    - 混合搜索（关键词 + 内容相似度）
    - 私人图库管理
    - AI 图片生成（调用 Stable Diffusion / DALL-E / Midjourney）
    - 图片版权检测（反向图片搜索）
    """

    def __init__(self, material_service_url: str = "http://localhost:8083"):
        self.material_service_url = material_service_url.rstrip("/")
        self._http_client: Optional[httpx.AsyncClient] = None
        self._embedding_service = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def close(self):
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    # ========== Keyword Search ==========

    async def search_by_keywords(
        self, keyword: str, limit: int = 20
    ) -> List[ImageSearchResult]:
        """通过关键词搜索图片（调用素材库 API）"""
        try:
            resp = await self.http_client.get(
                f"{self.material_service_url}/api/material/search",
                params={"keyword": keyword},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    results: List[ImageSearchResult] = []
                    for item in data.get("data") or []:
                        if item.get("type") == "IMAGE":
                            results.append(ImageSearchResult(
                                image_id=item.get("id", 0),
                                path=item.get("filePath", ""),
                                url=item.get("fileUrl", ""),
                                caption=item.get("name", ""),
                                tags=self._parse_tags(item.get("tags", "")),
                                score=1.0,
                                material_id=item.get("id", 0),
                                width=item.get("width", 0),
                                height=item.get("height", 0),
                                ai_generated=bool(item.get("aiGenerated")),
                                copyright_status=item.get("copyrightStatus", "UNKNOWN"),
                            ))
                    return results
        except httpx.HTTPError as e:
            logger.warning(f"关键词图片搜索失败 keyword={keyword}: {e}")
        return []

    # ========== CLIP Semantic Search ==========

    async def search_by_content(
        self,
        query: str,
        top_k: int = 20,
        collection: str = "material_images",
    ) -> List[ImageSearchResult]:
        """通过 CLIP embedding 搜索图片内容"""
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from embedding_service import get_embedding_service
            svc = await get_embedding_service()
            query_embedding = await svc.get_embedding(query)
            if query_embedding is None:
                logger.warning("无法获取 CLIP embedding，降至关键词搜索")
                return await self.search_by_keywords(query, top_k)

            # Search ChromaDB via knowledge service
            kb_resp = await self.http_client.post(
                "http://localhost:8084/api/knowledge/search",
                json={"query": query, "top_k": top_k, "collection": collection},
                timeout=30.0,
            )
            if kb_resp.status_code == 200:
                kb_data = kb_resp.json()
                results: List[ImageSearchResult] = []
                for item in kb_data.get("data", {}).get("results", []):
                    results.append(ImageSearchResult(
                        image_id=item.get("id", 0),
                        path=item.get("filePath", ""),
                        url=item.get("fileUrl", ""),
                        caption=item.get("content", item.get("name", "")),
                        score=item.get("score", 0.0),
                    ))
                return results
        except ImportError as e:
            logger.warning(f"embedding_service 未加载: {e}，使用关键词搜索")
            return await self.search_by_keywords(query, top_k)
        except httpx.HTTPError as e:
            logger.warning(f"CLIP 搜索失败 query={query}: {e}")
        return []

    # ========== Hybrid Search ==========

    async def search_hybrid(
        self,
        query: str,
        keyword_weight: float = 0.4,
        content_weight: float = 0.6,
        top_k: int = 20,
    ) -> List[ImageSearchResult]:
        """
        混合搜索：关键词 + CLIP 内容相似度融合

        Args:
            query: 搜索查询
            keyword_weight: 关键词搜索权重
            content_weight: 内容搜索权重
            top_k: 返回数量
        """
        kw_results = await self.search_by_keywords(query, top_k * 2)
        content_results = await self.search_by_content(query, top_k * 2)

        # Merge and score
        score_map: Dict[int, ImageSearchResult] = {}
        for r in kw_results:
            r.score *= keyword_weight
            score_map[r.image_id] = r
        for r in content_results:
            if r.image_id in score_map:
                score_map[r.image_id].score += r.score * content_weight
            else:
                r.score *= content_weight
                score_map[r.image_id] = r

        sorted_results = sorted(score_map.values(), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k]

    # ========== Private Image Library ==========

    async def upload_private_image(
        self,
        file_path: str,
        name: Optional[str] = None,
        description: Optional[str] = "",
        tags: Optional[List[str]] = None,
        user_id: int = 0,
        album_id: Optional[int] = None,
    ) -> PrivateImage:
        """上传私人图片"""
        import os as _os

        if not _os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        mime_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"
        files = {
            "file": (_os.path.basename(file_path), open(file_path, "rb"), mime_type),
        }
        data: Dict[str, Any] = {
            "name": name or _os.path.basename(file_path),
            "description": description or "",
            "userId": str(user_id),
        }
        if tags:
            data["tags"] = ",".join(tags)
        if album_id:
            data["albumId"] = str(album_id)

        try:
            resp = await self.http_client.post(
                f"{self.material_service_url}/api/material/image/upload",
                files=files,
                data=data,
                timeout=60.0,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 200:
                return PrivateImage.from_dict(result.get("data", {}))
            else:
                raise RuntimeError(f"图片上传失败: {result.get('message', '未知错误')}")
        finally:
            files["file"][1].close()

    async def search_private_images(
        self, user_id: int, keyword: str, limit: int = 50
    ) -> List[PrivateImage]:
        """搜索私人图片"""
        try:
            resp = await self.http_client.get(
                f"{self.material_service_url}/api/material/image/search",
                params={"userId": user_id, "keyword": keyword, "limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [PrivateImage.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"搜索私人图片失败 user_id={user_id}: {e}")
        return []

    async def list_private_images(
        self, user_id: int, album_id: Optional[int] = None, limit: int = 100
    ) -> List[PrivateImage]:
        """列出私人图片"""
        try:
            url = f"{self.material_service_url}/api/material/image/list"
            params: Dict[str, Any] = {"userId": user_id, "limit": limit}
            if album_id:
                url = f"{self.material_service_url}/api/material/image/list/album/{album_id}"
                params = {"limit": limit}

            resp = await self.http_client.get(url, params=params, timeout=30.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [PrivateImage.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"获取私人图片列表失败 user_id={user_id}: {e}")
        return []

    # ========== AI Image Generation ==========

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "stable-diffusion",
        user_id: Optional[int] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.5,
    ) -> PrivateImage:
        """
        AI 图片生成（方案配图）

        支持模型：stable-diffusion / dall-e-3 / midjourney

        Args:
            prompt: 生成提示词
            negative_prompt: 负面提示词
            model: AI 模型名称
            user_id: 用户ID
            width: 图片宽度
            height: 图片高度
            steps: 采样步数
            cfg_scale: CFG 强度
        """
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "userId": user_id,
            "width": width,
            "height": height,
            "steps": steps,
            "cfgScale": cfg_scale,
        }
        if negative_prompt:
            payload["negativePrompt"] = negative_prompt

        try:
            resp = await self.http_client.post(
                f"{self.material_service_url}/api/material/image/generate",
                json=payload,
                timeout=120.0,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 200:
                return PrivateImage.from_dict(result.get("data", {}))
            else:
                raise RuntimeError(f"AI图片生成失败: {result.get('message', '未知错误')}")
        except httpx.HTTPError as e:
            logger.error(f"AI图片生成请求失败: {e}")
            raise RuntimeError(f"AI图片生成请求失败: {e}")

    # ========== Copyright Detection ==========

    async def detect_copyright(
        self,
        image_id: int,
        method: str = "reverse_search",
    ) -> PrivateImage:
        """
        图片版权检测

        Args:
            image_id: 图片ID
            method: 检测方法（reverse_search / ai_classify）

        Returns:
            更新了检测结果的图片对象
        """
        try:
            resp = await self.http_client.post(
                f"{self.material_service_url}/api/material/image/detect-copyright",
                json={"imageId": image_id, "method": method},
                timeout=60.0,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 200:
                return PrivateImage.from_dict(result.get("data", {}))
            else:
                raise RuntimeError(f"版权检测失败: {result.get('message', '未知错误')}")
        except httpx.HTTPError as e:
            logger.error(f"版权检测请求失败 image_id={image_id}: {e}")
            raise RuntimeError(f"版权检测请求失败: {e}")

    async def detect_copyright_by_url(
        self,
        image_url: str,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        通过 URL 检测图片版权（上传后检测）

        Args:
            image_url: 图片 URL
            user_id: 用户ID

        Returns:
            版权检测结果
        """
        # Placeholder: in production, would call reverse image search API
        # (e.g., Google Reverse Image Search, TinEye, or custom model)
        return {
            "imageUrl": image_url,
            "detectionResult": "CLEAN",
            "detectionScore": 0.0,
            "detectedSources": [],
            "warning": "此功能需要配置版权检测服务（如反向图片搜索 API）",
        }

    # ========== Albums ==========

    async def list_albums(self, user_id: int) -> List[ImageAlbum]:
        """获取相册列表"""
        try:
            resp = await self.http_client.get(
                f"{self.material_service_url}/api/material/image/album/list",
                params={"userId": user_id},
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [ImageAlbum.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"获取相册列表失败 user_id={user_id}: {e}")
        return []

    async def create_album(
        self, name: str, user_id: int, description: str = "", sort: int = 0
    ) -> ImageAlbum:
        """创建相册"""
        payload = {"name": name, "description": description, "userId": user_id, "sort": sort}
        resp = await self.http_client.post(
            f"{self.material_service_url}/api/material/image/album",
            json=payload,
            timeout=15.0,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 200:
            return ImageAlbum.from_dict(result.get("data", {}))
        raise RuntimeError(f"创建相册失败: {result.get('message', '未知错误')}")

    # ========== Helpers ==========

    def _parse_tags(self, tags_raw: Any) -> List[str]:
        if isinstance(tags_raw, str):
            try:
                return json.loads(tags_raw)
            except Exception:
                return [t.strip() for t in tags_raw.split(",") if t.strip()]
        if isinstance(tags_raw, list):
            return tags_raw
        return []

    async def get_image_by_id(self, image_id: int) -> Optional[ImageSearchResult]:
        """根据ID获取图片"""
        try:
            resp = await self.http_client.get(
                f"{self.material_service_url}/api/material/{image_id}",
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    item = data.get("data", {})
                    return ImageSearchResult(
                        image_id=item.get("id", 0),
                        path=item.get("filePath", ""),
                        url=item.get("fileUrl", ""),
                        caption=item.get("name", ""),
                        tags=self._parse_tags(item.get("tags", "")),
                        score=1.0,
                        material_id=item.get("id", 0),
                        width=item.get("width", 0),
                        height=item.get("height", 0),
                        ai_generated=bool(item.get("aiGenerated")),
                        copyright_status=item.get("copyrightStatus", "UNKNOWN"),
                    )
        except httpx.HTTPError:
            pass
        return None

    async def get_related_images(
        self, image_id: int, limit: int = 10
    ) -> List[ImageSearchResult]:
        """获取相关图片（基于 CLIP embedding）"""
        try:
            resp = await self.http_client.get(
                f"{self.material_service_url}/api/material/{image_id}/related",
                params={"limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    results: List[ImageSearchResult] = []
                    for item in data.get("data", []):
                        results.append(ImageSearchResult(
                            image_id=item.get("id", 0),
                            path=item.get("filePath", ""),
                            url=item.get("fileUrl", ""),
                            caption=item.get("name", ""),
                            score=item.get("score", 0.0),
                        ))
                    return results
        except httpx.HTTPError as e:
            logger.warning(f"获取相关图片失败 image_id={image_id}: {e}")
        return []


# ========== Sync Wrapper ==========


class SyncImageSearch:
    """同步包装器"""

    def __init__(self, material_service_url: str = "http://localhost:8083"):
        self._engine = ImageSearch(material_service_url=material_service_url)

    def search_by_keywords(self, keyword: str, limit: int = 20) -> List[ImageSearchResult]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.search_by_keywords(keyword, limit))

    def search_hybrid(self, query: str, limit: int = 20) -> List[ImageSearchResult]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.search_hybrid(query, limit))

    def search_by_content(self, query: str, top_k: int = 20) -> List[ImageSearchResult]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.search_by_content(query, top_k))

    def upload_private_image(self, file_path: str, **kwargs) -> PrivateImage:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.upload_private_image(file_path, **kwargs))

    def generate_image(self, prompt: str, **kwargs) -> PrivateImage:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.generate_image(prompt, **kwargs))

    def detect_copyright(self, image_id: int) -> PrivateImage:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.detect_copyright(image_id))

    def list_private_images(self, user_id: int, **kwargs) -> List[PrivateImage]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._engine.list_private_images(user_id, **kwargs))

    def close(self):
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._engine.close())


# ========== Global Singleton ==========

_image_search: Optional[ImageSearch] = None


def get_image_search() -> ImageSearch:
    """获取全局图片搜索引擎单例"""
    global _image_search
    if _image_search is None:
        _image_search = ImageSearch(
            material_service_url=os.getenv(
                "MATERIAL_SERVICE_URL", "http://localhost:8083"
            )
        )
    return _image_search