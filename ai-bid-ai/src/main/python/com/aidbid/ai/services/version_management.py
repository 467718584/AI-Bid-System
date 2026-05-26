"""标书版本管理服务 - 管理改写历史和版本对比"""
import logging
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class VersionRecord:
    """版本记录"""
    version_id: str
    content_id: str
    version_number: str
    content: str
    content_hash: str       # 内容哈希，用于快速比较
    change_summary: str     # 变更摘要
    rewrite_strategy: str   # 使用的改写策略
    rewrite_style: Optional[str] = None
    created_at: str = ""
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentRecord:
    """内容记录（一个可改写内容的完整记录）"""
    content_id: str
    original_content: str
    title: str = ""
    description: str = ""
    current_version_id: str = ""
    versions: List[VersionRecord] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["version_count"] = len(self.versions)
        return result


@dataclass
class VersionDiff:
    """版本差异"""
    from_version: str
    to_version: str
    length_change: int
    change_ratio: float
    added_lines: int
    removed_lines: int
    similarity: float  # 相似度 0-1
    diff_segments: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================
# 版本管理服务
# ============================================================

class VersionManagementService:
    """标书版本管理服务"""

    def __init__(self):
        """初始化版本管理服务"""
        # content_id -> ContentRecord
        self._contents: Dict[str, ContentRecord] = {}
        # version_id -> VersionRecord
        self._versions: Dict[str, VersionRecord] = {}

    def _compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _compute_diff(self, old: str, new: str) -> Dict[str, Any]:
        """计算两个版本的差异"""
        old_lines = old.split('\n')
        new_lines = new.split('\n')

        # 简单行级差异计算
        old_set = set(old_lines)
        new_set = set(new_lines)

        added = len(new_set - old_set)
        removed = len(old_set - new_set)

        return {
            "added_lines": added,
            "removed_lines": removed,
            "similarity": len(set(old_lines) & set(new_lines)) / max(len(set(old_lines) | set(new_lines)), 1)
        }

    def create_content(
        self,
        content: str,
        title: str = "",
        description: str = "",
        tags: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> ContentRecord:
        """
        创建新内容记录

        Args:
            content: 内容文本
            title: 标题
            description: 描述
            tags: 标签
            created_by: 创建人

        Returns:
            创建的内容记录
        """
        content_id = f"cnt_{uuid.uuid4().hex[:12]}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 创建初始版本
        version_id = f"ver_{uuid.uuid4().hex[:12]}"
        version = VersionRecord(
            version_id=version_id,
            content_id=content_id,
            version_number="1.0.0",
            content=content,
            content_hash=self._compute_hash(content),
            change_summary="初始版本",
            rewrite_strategy="initial",
            created_at=now,
            created_by=created_by
        )

        record = ContentRecord(
            content_id=content_id,
            original_content=content,
            title=title,
            description=description,
            current_version_id=version_id,
            versions=[version],
            created_at=now,
            updated_at=now,
            tags=tags or []
        )

        self._contents[content_id] = record
        self._versions[version_id] = version

        logger.info(f"Created content record: {content_id}")
        return record

    def get_content(self, content_id: str) -> Optional[ContentRecord]:
        """获取内容记录"""
        return self._contents.get(content_id)

    def get_version(self, version_id: str) -> Optional[VersionRecord]:
        """获取特定版本"""
        return self._versions.get(version_id)

    def add_version(
        self,
        content_id: str,
        content: str,
        rewrite_strategy: str,
        change_summary: str = "",
        rewrite_style: Optional[str] = None,
        created_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[VersionRecord]:
        """
        为内容添加新版本

        Args:
            content_id: 内容ID
            content: 新版本内容
            rewrite_strategy: 使用的改写策略
            change_summary: 变更摘要
            rewrite_style: 改写风格
            created_by: 创建人
            metadata: 附加元数据

        Returns:
            新版本记录，未找到内容返回None
        """
        record = self._contents.get(content_id)
        if not record:
            return None

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算新版本号
        current = record.versions[-1].version_number if record.versions else "0.0.0"
        parts = current.split(".")
        if len(parts) >= 2:
            major, minor = int(parts[0]), int(parts[1])
            new_version = f"{major}.{minor + 1}"
        else:
            new_version = "1.1"

        version_id = f"ver_{uuid.uuid4().hex[:12]}"

        version = VersionRecord(
            version_id=version_id,
            content_id=content_id,
            version_number=new_version,
            content=content,
            content_hash=self._compute_hash(content),
            change_summary=change_summary,
            rewrite_strategy=rewrite_strategy,
            rewrite_style=rewrite_style,
            created_at=now,
            created_by=created_by,
            metadata=metadata or {}
        )

        record.versions.append(version)
        record.current_version_id = version_id
        record.updated_at = now

        self._versions[version_id] = version

        logger.info(f"Added version {new_version} to content {content_id}")
        return version

    def list_content_history(self, content_id: str) -> List[VersionRecord]:
        """列出内容的所有版本"""
        record = self._contents.get(content_id)
        if not record:
            return []
        return record.versions

    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Optional[VersionDiff]:
        """
        比较两个版本的差异

        Args:
            version_id_1: 版本1 ID
            version_id_2: 版本2 ID

        Returns:
            版本差异，未找到版本返回None
        """
        v1 = self._versions.get(version_id_1)
        v2 = self._versions.get(version_id_2)

        if not v1 or not v2:
            return None

        diff = self._compute_diff(v1.content, v2.content)

        return VersionDiff(
            from_version=v1.version_number,
            to_version=v2.version_number,
            length_change=len(v2.content) - len(v1.content),
            change_ratio=len(v2.content) / max(len(v1.content), 1),
            added_lines=diff["added_lines"],
            removed_lines=diff["removed_lines"],
            similarity=diff["similarity"],
            diff_segments=self._generate_diff_segments(v1.content, v2.content)
        )

    def _generate_diff_segments(self, old: str, new: str) -> List[Dict[str, Any]]:
        """生成差异片段"""
        old_lines = old.split('\n')
        new_lines = new.split('\n')

        segments = []
        # 简化实现：按行比较
        max_len = max(len(old_lines), len(new_lines))

        for i in range(max_len):
            old_line = old_lines[i] if i < len(old_lines) else None
            new_line = new_lines[i] if i < len(new_lines) else None

            if old_line == new_line:
                segments.append({"type": "unchanged", "line": i + 1, "content": old_line})
            elif old_line is None:
                segments.append({"type": "added", "line": i + 1, "content": new_line})
            elif new_line is None:
                segments.append({"type": "removed", "line": i + 1, "content": old_line})
            else:
                segments.append({"type": "modified", "line": i + 1, "old": old_line, "new": new_line})

        return segments[:100]  # 限制返回片段数量

    def rollback_to_version(
        self,
        content_id: str,
        version_id: str,
        created_by: str = "system"
    ) -> Optional[VersionRecord]:
        """
        回滚到指定版本

        Args:
            content_id: 内容ID
            version_id: 要回滚到的版本ID
            created_by: 操作人

        Returns:
            新创建的版本记录（回滚后的当前版本）
        """
        record = self._contents.get(content_id)
        target_version = self._versions.get(version_id)

        if not record or not target_version:
            return None

        # 验证目标版本属于该内容
        if target_version.content_id != content_id:
            return None

        # 获取当前版本
        current = self._versions.get(record.current_version_id)
        current_summary = current.change_summary if current else "当前版本"

        # 创建新版本，内容为旧版本内容
        new_version = self.add_version(
            content_id=content_id,
            content=target_version.content,
            rewrite_strategy="rollback",
            change_summary=f"回滚至版本 {target_version.version_number}（原：{current_summary}）",
            created_by=created_by,
            metadata={"rollback_from": record.current_version_id}
        )

        return new_version

    def delete_content(self, content_id: str) -> bool:
        """删除内容记录（软删除）"""
        record = self._contents.get(content_id)
        if not record:
            return False

        # 从版本索引中移除
        for v in record.versions:
            self._versions.pop(v.version_id, None)

        # 从内容索引中移除
        self._contents.pop(content_id, None)

        logger.info(f"Deleted content record: {content_id}")
        return True

    def search_content(
        self,
        keyword: str,
        tags: Optional[List[str]] = None
    ) -> List[ContentRecord]:
        """搜索内容"""
        results = list(self._contents.values())

        # 按关键词搜索
        if keyword:
            kw = keyword.lower()
            results = [
                r for r in results
                if kw in r.title.lower()
                or kw in r.description.lower()
                or any(kw in v.content.lower() for v in r.versions)
            ]

        # 按标签筛选
        if tags:
            results = [r for r in results if any(tag in r.tags for tag in tags)]

        return results

    def get_statistics(self, content_id: str) -> Optional[Dict[str, Any]]:
        """获取内容统计信息"""
        record = self._contents.get(content_id)
        if not record:
            return None

        return {
            "content_id": content_id,
            "title": record.title,
            "version_count": len(record.versions),
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "versions": [
                {
                    "version_id": v.version_id,
                    "version_number": v.version_number,
                    "rewrite_strategy": v.rewrite_strategy,
                    "created_at": v.created_at
                }
                for v in record.versions
            ]
        }


# ============================================================
# 单例模式
# ============================================================

_version_service_instance: Optional[VersionManagementService] = None


def get_version_service() -> VersionManagementService:
    """获取版本管理服务单例"""
    global _version_service_instance
    if _version_service_instance is None:
        _version_service_instance = VersionManagementService()
    return _version_service_instance