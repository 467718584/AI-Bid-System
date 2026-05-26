"""主流水线类 - 整合所有阶段和执行器"""
import logging
import asyncio
from typing import Dict, Any, Optional, Callable

from .pipeline_runner import PipelineRunner, JobStatus
from .pipeline_stages import StageStatus

logger = logging.getLogger(__name__)


class BidPipeline:
    """招标文件→目录→正文全流程自动生成流水线"""

    def __init__(
        self,
        llm_wrapper,
        document_parser,
        document_exporter,
        runner: Optional["PipelineRunner"] = None
    ):
        self.llm_wrapper = llm_wrapper
        self.document_parser = document_parser
        self.document_exporter = document_exporter

        # 使用传入的runner（共享存储），或创建新runner
        self._runner = runner or PipelineRunner(
            llm_wrapper=llm_wrapper,
            document_parser=document_parser,
            document_exporter=document_exporter,
            storage=None  # 新建空dict
        )

    async def generate(
        self,
        file_content: Optional[str] = None,
        file_name: str = "tender.pdf",
        file_type: str = "pdf",
        project_name: Optional[str] = None,
        project_type: str = "工程建设",
        page_count: int = 50,
        chapters: Optional[list] = None,
        callback: Optional[Callable] = None,
        resume_from: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        启动完整流水线

        参数:
            file_content: Base64编码的招标文件内容
            file_name: 文件名
            file_type: 文件类型 (pdf/docx/doc/zf)
            project_name: 项目名称（可选，从文件解析）
            project_type: 项目类型
            page_count: 目标页数
            chapters: 自定义章节列表（可选）
            callback: 进度回调函数
            resume_from: 从指定job_id恢复

        返回:
            包含 job_id 的启动响应
        """
        # 构建初始上下文
        context = {
            "file_content": file_content,
            "file_name": file_name,
            "file_type": file_type,
            "project_name": project_name or "技术标项目",
            "project_type": project_type,
            "page_count": page_count,
            "chapters": chapters or []
        }

        # 如果有 resume_from，使用已有 job_id
        if resume_from:
            job_id = resume_from
            # 从检查点恢复上下文
            checkpoint = self._runner._load_checkpoint(job_id)
            if checkpoint:
                context = {**checkpoint, **context}
            from_stage = self._get_stage_index_from_job(job_id)
        else:
            # 创建新作业
            job_id = self._runner._create_job(context)
            from_stage = None

        logger.info(f"流水线启动: job_id={job_id}, from_stage={from_stage}")

        return {
            "job_id": job_id,
            "status": "pending",
            "message": "流水线已启动，正在异步执行"
        }

    def _get_stage_index_from_job(self, job_id: str) -> Optional[int]:
        """从已完成阶段确定恢复起点"""
        job_status = self._runner.get_job_status(job_id)
        if not job_status:
            return None

        stage_names = [
            "parse_tender",
            "extract_requirements",
            "generate_outline",
            "generate_content",
            "export_document"
        ]

        for result in reversed(job_status.get("stages", [])):
            stage_status = result.get("status")
            if stage_status == StageStatus.COMPLETED.value:
                stage_name = result.get("stage_name")
                if stage_name in stage_names:
                    return stage_names.index(stage_name) + 1

        return None

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """查询任务状态"""
        return self._runner.get_job_status(job_id)

    def get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取生成结果"""
        return self._runner.get_job_result(job_id)

    def cancel(self, job_id: str) -> bool:
        """取消任务"""
        return self._runner.cancel_job(job_id)

    def list_jobs(self) -> list:
        """列出所有任务"""
        return self._runner.list_jobs()

    async def _run_async(self, job_id: str, context: Dict[str, Any], callback=None):
        """异步执行流水线（供BackgroundTasks调用）"""
        try:
            result = await self._runner.run(
                job_id=job_id,
                context=context,
                progress_callback=callback
            )
            return result
        except Exception as e:
            logger.error(f"流水线执行失败: {e}")
            return {"job_id": job_id, "status": "failed", "error": str(e)}