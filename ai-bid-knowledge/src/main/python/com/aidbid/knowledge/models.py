"""数据模型定义"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ChunkStatus(str, Enum):
    """知识块状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class KnowledgeBase(BaseModel):
    """知识库模型"""
    id: Optional[str] = None
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    kb_type: str = Field(default="general", description="知识库类型: general/bidding/technical")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    chunk_count: int = Field(default=0, description="知识块数量")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeChunk(BaseModel):
    """知识块模型"""
    id: Optional[str] = None
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    content: str = Field(..., description="知识块内容")
    content_hash: Optional[str] = Field(None, description="内容哈希")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    vector_ids: List[str] = Field(default_factory=list, description="向量ID列表")
    status: ChunkStatus = Field(default=ChunkStatus.ACTIVE, description="状态")
    chunk_order: int = Field(default=0, description="知识块顺序")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RetrieveRequest(BaseModel):
    """检索请求模型"""
    query: str = Field(..., description="检索查询文本")
    knowledge_base_id: Optional[str] = Field(None, description="知识库ID，不指定则检索所有")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    score_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="相似度阈值")
    filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤条件")


class RetrieveResponse(BaseModel):
    """检索响应模型"""
    query: str
    results: List[Dict[str, Any]] = Field(default_factory=list, description="检索结果")
    total: int = Field(default=0, description="结果总数")
    duration_ms: float = Field(default=0.0, description="检索耗时")


class KnowledgeBaseCreateRequest(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    kb_type: str = Field(default="general", description="知识库类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class KnowledgeBaseUpdateRequest(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class ChunkCreateRequest(BaseModel):
    """创建知识块请求"""
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    content: str = Field(..., min_length=1, description="知识块内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    chunk_order: Optional[int] = Field(None, description="知识块顺序")


class ChunkBatchCreateRequest(BaseModel):
    """批量创建知识块请求"""
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    chunks: List[ChunkCreateRequest] = Field(..., min_items=1, description="知识块列表")