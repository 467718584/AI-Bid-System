"""流水线阶段定义模块"""
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class StageStatus(str, Enum):
    """阶段状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """阶段执行结果"""
    stage_name: str
    status: StageStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    elapsed_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "retry_count": self.retry_count,
            "elapsed_ms": self.elapsed_ms
        }


class PipelineStage:
    """流水线阶段基类"""

    name: str = "base_stage"
    max_retries: int = 3
    timeout_seconds: int = 90

    def __init__(self):
        self._callbacks: List[Callable] = []

    def add_callback(self, cb: Callable):
        """添加进度回调函数"""
        self._callbacks.append(cb)

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """执行阶段（子类实现）"""
        raise NotImplementedError

    async def run(self, context: Dict[str, Any]) -> StageResult:
        """运行阶段，包含重试和超时逻辑"""
        import time
        start = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"[{self.name}] 开始执行 (尝试 {attempt + 1}/{self.max_retries + 1})")
                result = await asyncio.wait_for(
                    self.execute(context),
                    timeout=self.timeout_seconds
                )
                elapsed = int((time.time() - start) * 1000)
                result.elapsed_ms = elapsed
                logger.info(f"[{self.name}] 完成，耗时 {elapsed}ms")
                return result
            except asyncio.TimeoutError:
                error_msg = f"阶段超时 ({self.timeout_seconds}s)"
                logger.warning(f"[{self.name}] {error_msg}")
                if attempt == self.max_retries:
                    return StageResult(
                        stage_name=self.name,
                        status=StageStatus.FAILED,
                        error=error_msg,
                        retry_count=attempt + 1,
                        elapsed_ms=int((time.time() - start) * 1000)
                    )
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"[{self.name}] 执行失败: {error_msg} (尝试 {attempt + 1}/{self.max_retries + 1})")
                if attempt == self.max_retries:
                    return StageResult(
                        stage_name=self.name,
                        status=StageStatus.FAILED,
                        error=error_msg,
                        retry_count=attempt + 1,
                        elapsed_ms=int((time.time() - start) * 1000)
                    )
                await asyncio.sleep(2 ** attempt)  # 指数退避

        # 不应该走到这里
        return StageResult(stage_name=self.name, status=StageStatus.FAILED, error="未知错误")

    async def _notify_callbacks(self, progress: float, message: str, data: Optional[Dict] = None):
        """通知所有回调"""
        for cb in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(self.name, progress, message, data)
                else:
                    cb(self.name, progress, message, data)
            except Exception as e:
                logger.warning(f"回调执行失败: {e}")


# ============================================================
# Stage 1: 解析招标文件
# ============================================================

class ParseTenderStage(PipelineStage):
    """Stage 1: 解析招标文件"""

    name = "parse_tender"
    max_retries = 3
    timeout_seconds = 120

    def __init__(self, document_parser):
        super().__init__()
        self.parser = document_parser

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """解析招标文件（PDF/Word）"""
        file_content_b64 = context.get("file_content")
        file_name = context.get("file_name", "tender.pdf")
        file_type = context.get("file_type", "pdf")

        if not file_content_b64:
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                error="缺少文件内容 (file_content)"
            )

        import base64
        file_content = base64.b64decode(file_content_b64)

        parsed = await self.parser.parse(file_content, file_name, file_type)

        context["parsed_document"] = parsed
        context["project_name"] = parsed.basic_info.get("project_name", "未命名项目")
        context["tender_content"] = parsed.content
        context["scoring_method"] = parsed.scoring_method
        context["compliance_items"] = parsed.compliance_items

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            data={
                "file_name": parsed.file_name,
                "content_length": len(parsed.content),
                "basic_info": parsed.basic_info,
                "scoring_method": parsed.scoring_method
            }
        )


# ============================================================
# Stage 2: 提取关键需求
# ============================================================

class ExtractRequirementsStage(PipelineStage):
    """Stage 2: 提取关键需求"""

    name = "extract_requirements"
    max_retries = 3
    timeout_seconds = 90

    def __init__(self, llm_wrapper):
        super().__init__()
        self.llm_wrapper = llm_wrapper

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """使用AI提取关键需求"""
        tender_content = context.get("tender_content", "")
        project_name = context.get("project_name", "")

        if not tender_content:
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                error="缺少招标文件内容"
            )

        # 使用已有的 AI 解析 prompt
        from ..prompts import BID_DOCUMENT_PARSE_PROMPT
        prompt = BID_DOCUMENT_PARSE_PROMPT.format(
            content=tender_content[:12000]
        )

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_wrapper.chat(messages)

        try:
            requirements = json.loads(response)
        except json.JSONDecodeError:
            requirements = {"raw_response": response}

        context["requirements"] = requirements
        context["bid_requirements"] = requirements.get("raw_response", tender_content[:4000])

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            data={
                "requirements_summary": requirements.get("basic_info", {}),
                "scoring_method": requirements.get("scoring_method", {}),
                "compliance_items": requirements.get("compliance_items", [])
            }
        )


# ============================================================
# Stage 3: 生成技术标目录
# ============================================================

class GenerateOutlineStage(PipelineStage):
    """Stage 3: 生成技术标目录"""

    name = "generate_outline"
    max_retries = 3
    timeout_seconds = 90

    def __init__(self, llm_wrapper):
        super().__init__()
        self.llm_wrapper = llm_wrapper

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """生成技术标章节目录"""
        project_name = context.get("project_name", "")
        bid_requirements = context.get("bid_requirements", context.get("tender_content", "")[:4000])
        scoring_method = context.get("scoring_method", {})
        project_type = context.get("project_type", "工程建设")

        # 构建评分标准描述
        scoring_criteria = ""
        if scoring_method:
            scoring_criteria = json.dumps(scoring_method, ensure_ascii=False)

        page_count = context.get("page_count", 50)

        from ..prompts import TECHNICAL_BID_OUTLINE_PROMPT
        prompt = TECHNICAL_BID_OUTLINE_PROMPT.format(
            project_name=project_name,
            project_type=project_type,
            bid_requirements=bid_requirements[:3000],
            scoring_criteria=scoring_criteria[:2000] if scoring_criteria else "按招标文件要求",
            page_count=page_count
        )

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm_wrapper.chat(messages)

        try:
            outline = json.loads(response)
        except json.JSONDecodeError:
            # 尝试从响应中提取JSON
            try:
                import re
                json_match = re.search(r"\{[\s\S]+\}", response)
                if json_match:
                    outline = json.loads(json_match.group())
                else:
                    outline = {"title": "技术标", "raw_response": response}
            except Exception:
                outline = {"title": "技术标", "raw_response": response}

        context["outline"] = outline
        context["chapters"] = outline.get("children", [])

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            data={
                "title": outline.get("title", "技术标"),
                "total_pages": outline.get("totalPages", page_count),
                "chapter_count": len(outline.get("children", [])),
                "outline": outline
            }
        )


# ============================================================
# Stage 4: 生成各章节正文
# ============================================================

class GenerateContentStage(PipelineStage):
    """Stage 4: 生成各章节正文（批量并行）"""

    name = "generate_content"
    max_retries = 3
    timeout_seconds = 90  # 每章节超时

    def __init__(self, llm_wrapper):
        super().__init__()
        self.llm_wrapper = llm_wrapper

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """批量生成各章节正文（并行）"""
        chapters = context.get("chapters", [])
        project_name = context.get("project_name", "")
        project_type = context.get("project_type", "工程建设")
        bid_requirements = context.get("bid_requirements", "")
        scoring_criteria = context.get("scoring_criteria", "")
        bid_requirements_text = bid_requirements if isinstance(bid_requirements, str) else ""

        if not chapters:
            # 如果没有预定义目录，自动创建章节
            chapters = [
                {"title": "第一章 项目概况", "pageCount": 3},
                {"title": "第二章 施工方案", "pageCount": 15},
                {"title": "第三章 质量保证措施", "pageCount": 8},
                {"title": "第四章 施工进度计划", "pageCount": 5},
                {"title": "第五章 安全文明施工", "pageCount": 4},
                {"title": "第六章 项目管理机构", "pageCount": 4},
                {"title": "第七章 售后服务", "pageCount": 3},
                {"title": "第八章 附图附表", "pageCount": 8},
            ]
            context["chapters"] = chapters

        from ..prompts import TECHNICAL_BID_CONTENT_PROMPT

        async def generate_single_chapter(chapter: Dict[str, Any], index: int) -> Dict[str, Any]:
            chapter_title = chapter.get("title", f"第{index + 1}章")
            page_count = chapter.get("pageCount", 5)
            chapter_path = chapter.get("path", chapter_title)

            prompt = TECHNICAL_BID_CONTENT_PROMPT.format(
                project_name=project_name,
                project_type=project_type,
                chapter_title=chapter_title,
                page_count=page_count,
                bid_requirements=bid_requirements_text[:3000],
                scoring_criteria=scoring_criteria[:2000] if scoring_criteria else ""
            )

            messages = [{"role": "user", "content": prompt}]
            content = await self.llm_wrapper.chat(messages)

            return {
                "index": index,
                "title": chapter_title,
                "path": chapter_path,
                "page_count": page_count,
                "content": content
            }

        # 并行生成所有章节
        tasks = [
            generate_single_chapter(chapter, idx)
            for idx, chapter in enumerate(chapters)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        generated_chapters = []
        failed_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"章节生成失败: {result}")
                failed_count += 1
                generated_chapters.append({
                    "index": i,
                    "title": chapters[i].get("title", f"第{i + 1}章"),
                    "content": f"[生成失败: {str(result)}]",
                    "status": "failed"
                })
            else:
                generated_chapters.append(result)

        # 按顺序排序
        generated_chapters.sort(key=lambda x: x["index"])

        context["generated_chapters"] = generated_chapters
        context["total_chapters"] = len(generated_chapters)
        context["failed_chapters"] = failed_count

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            data={
                "total": len(generated_chapters),
                "failed": failed_count,
                "chapters": [
                    {"title": c["title"], "status": c.get("status", "completed")}
                    for c in generated_chapters
                ]
            }
        )


# ============================================================
# Stage 5: 导出最终标书
# ============================================================

class ExportDocumentStage(PipelineStage):
    """Stage 5: 导出最终标书"""

    name = "export_document"
    max_retries = 2
    timeout_seconds = 60

    def __init__(self, document_exporter):
        super().__init__()
        self.exporter = document_exporter

    async def execute(self, context: Dict[str, Any]) -> StageResult:
        """导出Word文档"""
        chapters = context.get("generated_chapters", [])
        project_name = context.get("project_name", "技术标")
        outline = context.get("outline", {})

        if not chapters:
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                error="没有可导出的章节内容"
            )

        doc = self.exporter.create_document()

        # 添加标题
        self.exporter.add_title(doc, project_name, level=0)

        # 添加目录信息
        self.exporter.add_paragraph(doc, f"总页数: {outline.get('totalPages', 'N/A')}")
        self.exporter.add_paragraph(doc, f"生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph()  # 空行

        # 添加各章节内容
        for chapter in chapters:
            title = chapter.get("title", "未命名章节")
            content = chapter.get("content", "")

            self.exporter.add_title(doc, title, level=1)

            # 将 Markdown 内容转换为 Word 段落
            if content:
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        doc.add_paragraph()
                        continue
                    # 处理 Markdown 标题
                    if line.startswith("# "):
                        self.exporter.add_paragraph(doc, line[2:], bold=True, font_size=14)
                    elif line.startswith("## "):
                        self.exporter.add_paragraph(doc, line[3:], bold=True, font_size=12)
                    elif line.startswith("- ") or line.startswith("* "):
                        self.exporter.add_paragraph(doc, line[2:])
                    else:
                        self.exporter.add_paragraph(doc, line)

        # 保存到内存
        import io
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        doc_bytes = buffer.read()

        # 转为 Base64
        import base64
        doc_base64 = base64.b64encode(doc_bytes).decode("utf-8")

        context["document_bytes"] = doc_bytes
        context["document_base64"] = doc_base64
        context["document_file_name"] = f"{project_name}.docx"

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            data={
                "file_name": f"{project_name}.docx",
                "file_size": len(doc_bytes),
                "chapter_count": len(chapters)
            }
        )