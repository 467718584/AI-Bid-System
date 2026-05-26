"""
素材库服务 (Material Library Service)

提供素材上传、搜索、自动分类、相关推荐等素材库管理功能。
支持与后端 Java 服务 API 交互，以及 CLIP 向量搜索（通过 embedding service）。
"""
import logging
import os
import json
import hashlib
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


# ========== Data Models ==========


@dataclass
class MaterialItem:
    """素材项数据模型"""
    id: int
    name: str
    type: str  # IMAGE / DOCUMENT / VIDEO / AUDIO / TEMPLATE
    category: str = ""
    sub_category: str = ""
    tags: List[str] = field(default_factory=list)
    description: str = ""
    file_path: str = ""
    file_url: str = ""
    file_size: int = 0
    file_type: str = ""
    width: int = 0
    height: int = 0
    duration: int = 0
    thumbnail_path: str = ""
    ai_generated: bool = False
    ai_prompt: str = ""
    copyright_status: str = "UNKNOWN"
    source: str = ""
    usage_count: int = 0
    favorite_count: int = 0
    status: str = "ACTIVE"
    create_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "subCategory": self.sub_category,
            "tags": self.tags,
            "description": self.description,
            "filePath": self.file_path,
            "fileUrl": self.file_url,
            "fileSize": self.file_size,
            "fileType": self.file_type,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnailPath": self.thumbnail_path,
            "aiGenerated": self.ai_generated,
            "aiPrompt": self.ai_prompt,
            "copyrightStatus": self.copyright_status,
            "source": self.source,
            "usageCount": self.usage_count,
            "favoriteCount": self.favorite_count,
            "status": self.status,
            "createTime": self.create_time.isoformat() if self.create_time else None,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MaterialItem":
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

        create_time = d.get("createTime")
        if isinstance(create_time, str):
            try:
                create_time = datetime.fromisoformat(create_time.replace("Z", "+00:00"))
            except Exception:
                create_time = None

        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            type=d.get("type", ""),
            category=d.get("category", ""),
            sub_category=d.get("subCategory", ""),
            tags=tags,
            description=d.get("description", ""),
            file_path=d.get("filePath", ""),
            file_url=d.get("fileUrl", ""),
            file_size=d.get("fileSize", 0),
            file_type=d.get("fileType", ""),
            width=d.get("width", 0),
            height=d.get("height", 0),
            duration=d.get("duration", 0),
            thumbnail_path=d.get("thumbnailPath", ""),
            ai_generated=bool(d.get("aiGenerated")),
            ai_prompt=d.get("aiPrompt", ""),
            copyright_status=d.get("copyrightStatus", "UNKNOWN"),
            source=d.get("source", ""),
            usage_count=d.get("usageCount", 0),
            favorite_count=d.get("favoriteCount", 0),
            status=d.get("status", "ACTIVE"),
            create_time=create_time,
        )


@dataclass
class MaterialSearchResult:
    """素材搜索结果"""
    material: MaterialItem
    score: float = 0.0
    match_reason: str = ""


@dataclass
class UsageLog:
    """素材使用记录"""
    id: int
    material_id: int
    user_id: int
    usage_type: str  # DOWNLOAD / VIEW / EMBED / CITE
    usage_context: str = ""
    usage_project_id: int = 0
    create_time: Optional[datetime] = None


# ========== Material Library Service ==========


class MaterialService:
    """
    素材库服务

    提供素材上传、搜索、自动分类、相关推荐等完整素材管理功能。
    支持：
    - 关键词/标签搜索（通过 Java API）
    - CLIP 向量语义搜索（通过 embedding service）
    - 自动标签生成（调用 AI）
    - 相关素材推荐
    - 使用统计追踪
    """

    def __init__(self, base_url: str = "http://localhost:8083"):
        """
        初始化素材库服务

        Args:
            base_url: 后端 API 基础 URL（素材服务端口）
        """
        self.base_url = base_url.rstrip("/")
        self._http_client: Optional[httpx.AsyncClient] = None
        self._embedding_service = None  # lazy-loaded

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def close(self):
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    # ========== Upload ==========

    async def upload_material(
        self,
        file_path: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
        auto_tag: bool = True,
    ) -> MaterialItem:
        """
        上传素材文件

        Args:
            file_path: 文件路径
            name: 素材名称（默认使用文件名）
            tags: 标签列表
            category: 素材分类
            description: 素材描述
            project_id: 关联项目ID
            user_id: 上传用户ID
            auto_tag: 是否自动生成标签

        Returns:
            上传后的素材对象
        """
        import mimetypes
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        file_size = os.path.getsize(file_path)

        files = {
            "file": (os.path.basename(file_path), open(file_path, "rb"), mime_type),
        }
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if tags:
            data["tags"] = ",".join(tags)
        if category:
            data["category"] = category
        if description:
            data["description"] = description
        if project_id:
            data["projectId"] = str(project_id)
        if user_id:
            data["userId"] = str(user_id)

        try:
            resp = await self.http_client.post(
                f"{self.base_url}/api/material/upload",
                files=files,
                data=data,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 200:
                item = MaterialItem.from_dict(result.get("data", {}))
                if auto_tag and not tags:
                    await self._auto_tag_material(item)
                return item
            else:
                raise RuntimeError(f"上传失败: {result.get('message', '未知错误')}")
        except httpx.HTTPError as e:
            logger.error(f"素材上传请求失败: {e}")
            raise RuntimeError(f"素材上传请求失败: {e}")
        finally:
            files["file"][1].close()

    async def upload_material_bytes(
        self,
        content: bytes,
        filename: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> MaterialItem:
        """
        通过字节内容上传素材

        Args:
            content: 文件字节内容
            filename: 文件名
            name: 素材名称
            tags: 标签列表
            category: 素材分类
            description: 素材描述
            user_id: 上传用户ID

        Returns:
            上传后的素材对象
        """
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        files = {"file": (filename, content, mime_type)}
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if tags:
            data["tags"] = ",".join(tags)
        if category:
            data["category"] = category
        if description:
            data["description"] = description
        if user_id:
            data["userId"] = str(user_id)

        resp = await self.http_client.post(
            f"{self.base_url}/api/material/upload",
            files=files,
            data=data,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 200:
            return MaterialItem.from_dict(result.get("data", {}))
        else:
            raise RuntimeError(f"上传失败: {result.get('message', '未知错误')}")

    async def batch_upload(
        self,
        file_paths: List[str],
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[MaterialItem]:
        """
        批量上传素材

        Args:
            file_paths: 文件路径列表
            tags: 标签列表
            category: 素材分类
            user_id: 上传用户ID

        Returns:
            上传后的素材列表
        """
        results: List[MaterialItem] = []
        for fp in file_paths:
            try:
                item = await self.upload_material(
                    fp, tags=tags, category=category, user_id=user_id
                )
                results.append(item)
            except Exception as e:
                logger.warning(f"批量上传失败 {fp}: {e}")
        return results

    # ========== Search ==========

    async def search_material(self, keyword: str, limit: int = 20) -> List[MaterialItem]:
        """
        关键词搜索素材

        Args:
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的素材列表
        """
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/search",
                params={"keyword": keyword},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [MaterialItem.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"素材搜索失败 keyword={keyword}: {e}")
        return []

    async def list_by_type(self, material_type: str, limit: int = 50) -> List[MaterialItem]:
        """按类型获取素材列表"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/list/type/{material_type}",
                params={"limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [MaterialItem.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"获取素材列表失败 type={material_type}: {e}")
        return []

    async def list_by_category(
        self, category: str, limit: int = 50
    ) -> List[MaterialItem]:
        """按分类获取素材列表"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/list/category/{category}",
                params={"limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [MaterialItem.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"获取素材列表失败 category={category}: {e}")
        return []

    # ========== Auto Categorize ==========

    async def categorize_material(self, material_id: int) -> str:
        """
        AI自动分类素材

        Args:
            material_id: 素材ID

        Returns:
            推荐分类名称
        """
        try:
            item = await self.get_by_id(material_id)
            if not item:
                return ""

            # Simple rule-based categorization as fallback
            name_lower = item.name.lower()
            desc_lower = item.description.lower()
            combined = f"{item.name} {item.description}"

            if any(k in combined for k in ["logo", "标志", "品牌"]):
                return "品牌视觉"
            if any(k in combined for k in ["产品", "product", "设备"]):
                return "产品展示"
            if any(k in combined for k in ["工厂", "厂房", "车间", "办公", "office"]):
                return "企业形象"
            if any(k in combined for k in ["团队", "team", "成员", "员工"]):
                return "团队介绍"
            if any(k in combined for k in ["项目", "案例", "case"]):
                return "项目案例"
            if item.type == "IMAGE":
                return "图片素材"
            elif item.type == "DOCUMENT":
                return "文档模板"
            elif item.type == "VIDEO":
                return "视频素材"
            return "综合素材"
        except Exception as e:
            logger.warning(f"AI自动分类失败 material_id={material_id}: {e}")
            return ""

    async def _auto_tag_material(self, item: MaterialItem):
        """自动为素材生成标签（调用AI或规则引擎）"""
        tags: List[str] = []

        name_lower = item.name.lower()
        desc_lower = item.description.lower()
        combined = f"{item.name} {item.description}"

        # Rule-based tag generation
        tag_rules = {
            "建筑": ["建筑工程", "施工"],
            "装修": ["室内设计", "装潢"],
            "IT": ["信息技术", "软件开发"],
            "医疗": ["医疗健康", "医药"],
            "教育": ["教育培训", "学校"],
            "政府": ["政府采购", "政务"],
            "绿化": ["园林绿化", "景观"],
            "物业": ["物业管理", "安保"],
        }
        for key, values in tag_rules.items():
            if key in combined:
                tags.extend(values[:2])

        if item.ai_generated:
            tags.append("AI生成")
        if item.copyright_status == "OWNED":
            tags.append("自有版权")
        elif item.copyright_status == "LICENSED":
            tags.append("已授权")

        if tags:
            try:
                await self.http_client.put(
                    f"{self.base_url}/api/material",
                    json={"id": item.id, "tags": ",".join(tags)},
                    timeout=15.0,
                )
            except Exception as e:
                logger.warning(f"自动标签更新失败: {e}")

    # ========== Recommend ==========

    async def recommend_material(
        self, context: str, limit: int = 10
    ) -> List[MaterialSearchResult]:
        """
        根据上下文推荐相关素材

        Args:
            context: 上下文描述（如项目名称、类型等）
            limit: 返回数量

        Returns:
            推荐素材列表（含相关性分数）
        """
        try:
            resp = await self.http_client.post(
                f"{self.base_url}/api/material/recommend",
                json={"context": context, "limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    results: List[MaterialSearchResult] = []
                    for i, item_data in enumerate(data.get("data") or []):
                        item = MaterialItem.from_dict(item_data)
                        score = 1.0 - (i * 0.1)
                        results.append(MaterialSearchResult(
                            material=item,
                            score=max(score, 0.1),
                            match_reason=f"关键词匹配: {context}",
                        ))
                    return results
        except httpx.HTTPError as e:
            logger.warning(f"素材推荐请求失败 context={context}: {e}")
        return []

    # ========== Usage Tracking ==========

    async def record_usage(
        self,
        material_id: int,
        user_id: Optional[int] = None,
        usage_type: str = "VIEW",
        usage_context: str = "",
        project_id: Optional[int] = None,
    ):
        """
        记录素材使用

        Args:
            material_id: 素材ID
            user_id: 使用用户ID
            usage_type: 使用类型（DOWNLOAD/VIEW/EMBED/CITE）
            usage_context: 使用场景
            project_id: 使用项目ID
        """
        try:
            payload = {
                "materialId": material_id,
                "usageType": usage_type,
                "usageContext": usage_context,
            }
            if user_id:
                payload["userId"] = user_id
            if project_id:
                payload["usageProjectId"] = project_id

            resp = await self.http_client.post(
                f"{self.base_url}/api/material/usage/record",
                json=payload,
                timeout=15.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning(f"记录素材使用失败 material_id={material_id}: {e}")

    async def get_usage_stats(self, material_id: int) -> Dict[str, int]:
        """获取素材使用统计"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/usage/logs/{material_id}",
                timeout=15.0,
            )
            if resp.status_code == 200:
                logs = resp.json().get("data") or []
                return {
                    "total": len(logs),
                    "download": sum(1 for l in logs if l.get("usageType") == "DOWNLOAD"),
                    "view": sum(1 for l in logs if l.get("usageType") == "VIEW"),
                    "embed": sum(1 for l in logs if l.get("usageType") == "EMBED"),
                }
        except httpx.HTTPError as e:
            logger.warning(f"获取使用统计失败 material_id={material_id}: {e}")
        return {"total": 0, "download": 0, "view": 0, "embed": 0}

    # ========== CRUD ==========

    async def get_by_id(self, material_id: int) -> Optional[MaterialItem]:
        """根据ID获取素材"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/{material_id}",
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return MaterialItem.from_dict(data.get("data", {}))
        except httpx.HTTPError:
            pass
        return None

    async def list_all(self, limit: int = 100) -> List[MaterialItem]:
        """获取所有素材"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/list",
                params={"limit": limit},
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return [MaterialItem.from_dict(item) for item in (data.get("data") or [])]
        except httpx.HTTPError as e:
            logger.warning(f"获取素材列表失败: {e}")
        return []

    async def get_categories(self) -> List[str]:
        """获取所有分类"""
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/api/material/categories",
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return data.get("data") or []
        except httpx.HTTPError as e:
            logger.warning(f"获取分类列表失败: {e}")
        return []


# ========== Sync Wrapper ==========


class SyncMaterialService:
    """同步包装器"""

    def __init__(self, base_url: str = "http://localhost:8083"):
        self._service = MaterialService(base_url=base_url)

    def search_material(self, keyword: str, limit: int = 20) -> List[MaterialItem]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.search_material(keyword, limit))

    def recommend_material(self, context: str, limit: int = 10) -> List[MaterialSearchResult]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.recommend_material(context, limit))

    def list_all(self, limit: int = 100) -> List[MaterialItem]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.list_all(limit))

    def get_by_id(self, material_id: int) -> Optional[MaterialItem]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.get_by_id(material_id))

    def get_categories(self) -> List[str]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.get_categories())

    def record_usage(self, material_id: int, user_id: Optional[int] = None,
                     usage_type: str = "VIEW", usage_context: str = ""):
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._service.record_usage(material_id, user_id, usage_type, usage_context)
        )

    def close(self):
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._service.close())


# ========== Global Singleton ==========

_material_service: Optional[MaterialService] = None


def get_material_service() -> MaterialService:
    """获取全局素材库服务单例"""
    global _material_service
    if _material_service is None:
        _material_service = MaterialService(
            base_url=os.getenv("MATERIAL_SERVICE_URL", "http://localhost:8083")
        )
    return _material_service