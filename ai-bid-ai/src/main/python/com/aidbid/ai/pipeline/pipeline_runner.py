"""流水线执行器模块"""
import logging
import uuid
import time
import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from .pipeline_stages import (
    StageResult, StageStatus,
    ParseTenderStage,
    ExtractRequirementsStage,
    GenerateOutlineStage,
    GenerateContentStage,
    ExportDocumentStage
)

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobContext:
    """流水线作业上下文"""
    job_id: str
    status: str
    created_at: str
    updated_at: str
    current_stage: Optional[str] = None
    progress_percent: float = 0.0
    stage_results: List[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.stage_results is None:
            self.stage_results = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PipelineRunner:
    """流水线执行器"""

    def __init__(
        self,
        llm_wrapper,
        document_parser,
        document_exporter,
        storage: Optional[Dict[str, JobContext]] = None
    ):
        self.llm_wrapper = llm_wrapper
        self.document_parser = document_parser
        self.document_exporter = document_exporter

        # 作业存储（内存存储，可扩展为Redis）
        # 注意：不能使用 `storage or {}`，因为空dict是falsy会导致每次创建新dict
        self._storage: Dict[str, JobContext] = {} if storage is None else storage

        # 5个阶段定义
        self._stages = [
            ParseTenderStage(document_parser),
            ExtractRequirementsStage(llm_wrapper),
            GenerateOutlineStage(llm_wrapper),
            GenerateContentStage(llm_wrapper),
            ExportDocumentStage(document_exporter),
        ]

    def _create_job(self, initial_data: Dict[str, Any]) -> str:
        """创建新作业"""
        job_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        job = JobContext(
            job_id=job_id,
            status=JobStatus.PENDING.value,
            created_at=now,
            updated_at=now,
            current_stage=None,
            progress_percent=0.0,
            stage_results=[],
            result_data=None,
            error=None
        )

        self._storage[job_id] = job
        self._save_checkpoint(job_id, initial_data)

        return job_id

    def _save_checkpoint(self, job_id: str, context: Dict[str, Any]):
        """保存检查点（中间结果缓存）"""
        if job_id in self._storage:
            job = self._storage[job_id]
            job.result_data = context.copy()
            job.updated_at = datetime.now().isoformat()

    def _load_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        """加载检查点（用于断点续传）"""
        if job_id in self._storage:
            return self._storage[job_id].result_data
        return None

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if job_id not in self._storage:
            return None

        job = self._storage[job_id]
        return {
            "job_id": job_id,
            "status": job.status,
            "current_stage": job.current_stage,
            "progress_percent": job.progress_percent,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "stages": job.stage_results,
            "error": job.error
        }

    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        if job_id not in self._storage:
            return None

        job = self._storage[job_id]
        if job.status != JobStatus.COMPLETED.value:
            return None

        return {
            "job_id": job_id,
            "status": job.status,
            "result": job.result_data
        }

    async def run(
        self,
        job_id: str,
        context: Dict[str, Any],
        from_stage: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """执行流水线"""
        stage_names = [
            "parse_tender",
            "extract_requirements",
            "generate_outline",
            "generate_content",
            "export_document"
        ]

        start_idx = from_stage if from_stage is not None else 0

        # 更新状态为运行中
        if job_id in self._storage:
            job = self._storage[job_id]
            job.status = JobStatus.RUNNING.value
            job.updated_at = datetime.now().isoformat()

        # 加载检查点上下文
        checkpoint = self._load_checkpoint(job_id)
        if checkpoint:
            context = {**checkpoint, **context}

        context["_job_id"] = job_id

        all_results = []
        total = len(self._stages)

        for idx in range(start_idx, total):
            stage = self._stages[idx]
            stage_name = stage.name

            # 更新当前阶段
            if job_id in self._storage:
                job = self._storage[job_id]
                job.current_stage = stage_name
                job.progress_percent = round((idx / total) * 100, 1)
                job.updated_at = datetime.now().isoformat()

            # 通知进度
            if progress_callback:
                try:
                    cb = progress_callback
                    if asyncio.iscoroutinefunction(cb):
                        await cb(job_id, stage_name, idx / total, f"正在执行: {stage_name}")
                    else:
                        cb(job_id, stage_name, idx / total, f"正在执行: {stage_name}")
                except Exception as e:
                    logger.warning(f"进度回调失败: {e}")

            # 执行阶段
            logger.info(f"[Job {job_id}] 执行阶段 {idx + 1}/{total}: {stage_name}")
            result = await stage.run(context)

            # 保存阶段结果
            all_results.append(result.to_dict())

            if job_id in self._storage:
                job = self._storage[job_id]
                job.stage_results = all_results
                job.updated_at = datetime.now().isoformat()

            # 检查点：每个阶段完成后保存
            self._save_checkpoint(job_id, context)

            # 失败处理
            if result.status == StageStatus.FAILED:
                logger.error(f"[Job {job_id}] 阶段 {stage_name} 失败: {result.error}")
                if job_id in self._storage:
                    job = self._storage[job_id]
                    job.status = JobStatus.FAILED.value
                    job.error = result.error
                    job.progress_percent = round((idx / total) * 100, 1)
                    job.updated_at = datetime.now().isoformat()
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "failed_stage": stage_name,
                    "error": result.error,
                    "stage_results": all_results
                }

        # 全部完成
        if job_id in self._storage:
            job = self._storage[job_id]
            job.status = JobStatus.COMPLETED.value
            job.progress_percent = 100.0
            job.result_data = context.copy()
            job.updated_at = datetime.now().isoformat()

        return {
            "job_id": job_id,
            "status": "completed",
            "stage_results": all_results,
            "document_base64": context.get("document_base64"),
            "document_file_name": context.get("document_file_name"),
            "outline": context.get("outline"),
            "chapters": context.get("generated_chapters")
        }

    def cancel_job(self, job_id: str) -> bool:
        """取消作业"""
        if job_id in self._storage:
            job = self._storage[job_id]
            if job.status in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
                job.status = JobStatus.CANCELLED.value
                job.updated_at = datetime.now().isoformat()
                return True
        return False

    def list_jobs(self) -> List[Dict[str, Any]]:
        """列出所有作业"""
        return [
            {
                "job_id": job_id,
                "status": job.status,
                "current_stage": job.current_stage,
                "progress_percent": job.progress_percent,
                "created_at": job.created_at,
                "updated_at": job.updated_at
            }
            for job_id, job in self._storage.items()
        ]