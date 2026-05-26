"""AI服务模块 - 图文并茂相关服务"""
from .image_service import ImageService, ImageResult
from .image_service import get_image_service, close_image_service
from .table_generator import TableGenerator, create_sample_data
from .rewrite_strategy import (
    RewriteStrategyService,
    RewriteStrategy,
    RewriteStyle,
    RewriteRequest,
    RewriteResult,
    create_rewrite_service,
)
from .version_management import (
    VersionManagementService,
    VersionRecord,
    ContentRecord,
    VersionDiff,
    get_version_service,
)

__all__ = [
    # 原有服务
    "ImageService",
    "ImageResult",
    "get_image_service",
    "close_image_service",
    "TableGenerator",
    "create_sample_data",
    # 改写策略服务
    "RewriteStrategyService",
    "RewriteStrategy",
    "RewriteStyle",
    "RewriteRequest",
    "RewriteResult",
    "create_rewrite_service",
    # 版本管理服务
    "VersionManagementService",
    "VersionRecord",
    "ContentRecord",
    "VersionDiff",
    "get_version_service",
]