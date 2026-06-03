"""FastAPI主应用 - AI投标智能服务"""
import logging
import json
import os
from typing import Optional, List, Dict, Any, Union
import io
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# CORS配置 - 生产环境应通过环境变量配置具体域名
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")

from .llm_gateway import LLMGateway, LLMFactory
from .document_parser import DocumentParser, ParsedDocument
from .document_exporter import DocumentExporter
from .services.image_service import ImageService, ImageResult
from .services.table_generator import TableGenerator, create_sample_data
from .prompts import (
    TECHNICAL_BID_OUTLINE_PROMPT,
    TECHNICAL_BID_CONTENT_PROMPT,
    TECHNICAL_BID_RICH_CONTENT_PROMPT,
    BID_DOCUMENT_PARSE_PROMPT,
    PARAPHRASE_PROMPT,
    COMPLIANCE_CHECK_PROMPT,
    TECHNICAL_BID_PROMPT, CREDIT_BID_PROMPT, BID_REWRITE_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT, build_prompt
)

from .pipeline import BidPipeline
from .services.rewrite_strategy import (
    RewriteStrategyService,
    RewriteStrategy,
    RewriteStyle,
    create_rewrite_service,
)
from .services.version_management import get_version_service
from .skill import get_skill_registry, SkillEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# Request/Response Models
# ============================================================

class OutlineRequest(BaseModel):
    """技术标目录生成请求"""
    projectName: str
    projectType: str
    bidRequirements: str
    scoringCriteria: str
    pageCount: int = 50
    rule: str = "MIXED"


class ContentRequest(BaseModel):
    """技术标正文生成请求"""
    projectName: str
    projectType: str
    chapterTitle: str
    chapterPath: str
    pageCount: int
    bidRequirements: str
    scoringCriteria: str
    includeImages: bool = True
    includeTables: bool = True


class ParseRequest(BaseModel):
    """文档解析请求"""
    content: str


class ParaphraseRequest(BaseModel):
    """标书改写请求"""
    content: str
    strategy: str = "ORIGINAL"
    multiplier: float = 1.0
    preserveKeywords: Optional[List[str]] = []


class ComplianceCheckRequest(BaseModel):
    """合规检测请求"""
    requirements: str
    content: str


class BidGenerateRequest(BaseModel):
    """标书生成请求"""
    bid_type: str = Field(..., description="标书类型: technical/credit")
    project_name: str
    procurement_unit: str
    deadline: Optional[str] = None
    bidding_requirements: str
    qualifications: str
    scoring_criteria: Optional[str] = None


class BidRewriteRequest(BaseModel):
    """标书改写请求"""
    original_content: str
    rewrite_requirements: str
    target_style: str = Field(default="professional")


class DocumentParseFileRequest(BaseModel):
    """文档文件解析请求（Base64编码）"""
    file_content: str  # Base64编码的文件内容
    file_name: str
    file_type: str  # pdf, docx, doc, zf


class DocumentExportRequest(BaseModel):
    """文档导出请求"""
    report_type: str = Field(..., description="报告类型: analysis/compliance/summary")
    data: Dict[str, Any]


class TableGenerateRequest(BaseModel):
    """表格生成请求"""
    table_type: str = Field(..., description="表格类型: qualification/personnel/schedule/equipment/safety")
    data: Dict[str, Any] = Field(default_factory=dict, description="表格数据")


class GanttGenerateRequest(BaseModel):
    """甘特图生成请求"""
    project_name: str = Field(default="施工进度计划", description="项目名称")
    timeline: Dict[str, Any] = Field(default_factory=dict, description="时间计划")
    output_format: str = Field(default="png", description="输出格式: png/svg")


# ============================================================
# 改写增强 - Request/Response Models
# ============================================================

class RewriteVersionsRequest(BaseModel):
    """多版本改写请求"""
    content: str
    version_count: int = Field(default=3, ge=2, le=6, description="版本数量 2-6")
    styles: Optional[List[str]] = Field(default=None, description="指定风格列表")
    preserve_keywords: Optional[List[str]] = Field(default_factory=list)


class RewriteVersionsResponse(BaseModel):
    """多版本改写响应"""
    original_length: int
    versions: List[Dict[str, Any]]


class TemplateApplyRequest(BaseModel):
    """模板应用请求"""
    content: str
    template_id: str
    variables: Optional[Dict[str, str]] = Field(default_factory=dict, description="模板变量")
    merge_strategy: str = Field(default="replace", description="合并策略: replace/prepend/append/wrap")


class TemplateApplyResponse(BaseModel):
    """模板应用响应"""
    success: bool
    applied_content: str
    template_id: str
    template_name: str
    variables_filled: int


class TemplateListRequest(BaseModel):
    """模板列表请求"""
    template_type: Optional[str] = None
    keyword: Optional[str] = None
    tags: Optional[List[str]] = None


class TemplateCreateRequest(BaseModel):
    """创建模板请求"""
    name: str
    content: str
    template_type: str = "custom"
    description: str = ""
    category: str = ""
    tags: Optional[List[str]] = None


class VersionCreateRequest(BaseModel):
    """创建内容版本请求"""
    content: str
    title: str = ""
    description: str = ""
    tags: Optional[List[str]] = None


class VersionAddRequest(BaseModel):
    """添加版本请求"""
    content: str
    rewrite_strategy: str
    change_summary: str = ""
    rewrite_style: Optional[str] = None


class VersionCompareRequest(BaseModel):
    """版本比较请求"""
    version_id_1: str
    version_id_2: str


class VersionRollbackRequest(BaseModel):
    """版本回滚请求"""
    version_id: str


# ============================================================
# 异步LLM服务包装
# ============================================================

class AsyncLLMWrapper:
    """异步LLM调用包装器"""

    def __init__(self, provider: str = "minimax"):
        self.gateway = LLMFactory.get_gateway(provider)

    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """异步聊天"""
        return await self.gateway.chat(messages, **kwargs)

    async def chat_with_prompt(self, prompt: str, **kwargs) -> str:
        """使用prompt字符串进行聊天"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)


# ============================================================
# FastAPI应用
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("AI投标智能服务启动中...")
    yield
    logger.info("AI投标智能服务关闭...")


app = FastAPI(
    title="AI-Bid AI Service",
    description="技术标智能编制系统 - AI投标智能服务",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

llm_wrapper = AsyncLLMWrapper(provider="minimax")
document_parser = DocumentParser()
document_exporter = DocumentExporter()
image_service = ImageService()
table_generator = TableGenerator()
rewrite_service = RewriteStrategyService(llm_wrapper)
version_service = get_version_service()
skill_engine = get_skill_registry()


# ============================================================
# Skill API Request/Response Models
# ============================================================

class SkillExecuteRequest(BaseModel):
    """技能执行请求"""
    skill_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    project_id: Optional[str] = None


class SkillValidateRequest(BaseModel):
    """技能定义验证请求"""
    skill_definition: Dict[str, Any]


class PipelineExecuteRequest(BaseModel):
    """流水线执行请求"""
    pipeline_definition: Dict[str, Any]
    global_inputs: Dict[str, Any] = Field(default_factory=dict)
    project_id: Optional[str] = None


class SkillCatalogRequest(BaseModel):
    """技能分类请求"""
    code: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    sort_order: int = 0
    icon: str = ""


# ============================================================
# API Endpoints - 技能编排系统
# ============================================================

@app.get("/api/ai/skills")
async def list_skills(
    catalog_id: Optional[str] = None,
    skill_type: Optional[str] = None
):
    """技能列表"""
    skills = skill_engine.list_skills(catalog_id=catalog_id, skill_type=skill_type)
    return {"code": 200, "data": skills}


@app.get("/api/ai/skills/{skill_id}")
async def get_skill(skill_id: str):
    """获取技能详情"""
    skill = skill_engine.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
    return {"code": 200, "data": skill}


@app.post("/api/ai/skills/execute")
async def execute_skill(req: SkillExecuteRequest):
    """执行单个技能"""
    try:
        result = await skill_engine.execute_skill(
            skill_id=req.skill_id,
            inputs=req.inputs,
            project_id=req.project_id,
        )
        return {"code": 200, "data": result}
    except Exception as e:
        logger.error(f"Skill execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/skills/pipeline")
async def execute_pipeline(req: PipelineExecuteRequest):
    """执行技能流水线"""
    try:
        from .skill.skill_engine import PipelineStage, PipelineDefinition

        stages = []
        for stage_data in req.pipeline_definition.get("stages", []):
            stages.append(PipelineStage(
                skill_id=stage_data["skill_id"],
                inputs=stage_data.get("inputs", {}),
                condition=stage_data.get("condition"),
                parallel=stage_data.get("parallel", False),
            ))

        pipeline_def = PipelineDefinition(
            pipeline_id=req.pipeline_definition.get("pipeline_id", f"pipeline_{uuid.uuid4().hex[:12]}"),
            name=req.pipeline_definition.get("name", "Unnamed Pipeline"),
            description=req.pipeline_definition.get("description", ""),
            stages=stages,
            timeout=req.pipeline_definition.get("timeout", 3600),
        )

        result = await skill_engine.execute_pipeline(
            pipeline_def=pipeline_def,
            global_inputs=req.global_inputs,
            project_id=req.project_id,
        )
        return {"code": 200, "data": result}
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/skills/validate")
async def validate_skill(req: SkillValidateRequest):
    """验证技能定义"""
    try:
        from .skill.skill_engine import SkillParameter, SkillDefinition

        skill_def_dict = req.skill_definition
        input_params = []
        for param in skill_def_dict.get("input_params", []):
            input_params.append(SkillParameter(
                name=param["name"],
                type=param.get("type", "string"),
                required=param.get("required", False),
                default=param.get("default"),
                description=param.get("description", ""),
            ))

        temp_skill = SkillDefinition(
            skill_id=skill_def_dict.get("skill_id", ""),
            name=skill_def_dict.get("name", ""),
            description=skill_def_dict.get("description", ""),
            version=skill_def_dict.get("version", "1.0.0"),
            skill_type=skill_def_dict.get("skill_type", "UTILITY"),
            input_params=input_params,
            output_schema=skill_def_dict.get("output_schema", {}),
            default_params=skill_def_dict.get("default_params", {}),
            dependencies=skill_def_dict.get("dependencies", []),
            timeout=skill_def_dict.get("timeout", 300),
            enabled=skill_def_dict.get("enabled", True),
            tags=skill_def_dict.get("tags", []),
            priority=skill_def_dict.get("priority", 0),
        )

        is_valid = skill_engine.validate_skill_definition(temp_skill)
        return {
            "code": 200,
            "data": {
                "valid": is_valid,
                "skill_id": skill_def_dict.get("skill_id"),
            }
        }
    except Exception as e:
        logger.error(f"Skill validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/skills/catalogs")
async def list_skill_catalogs():
    """获取技能分类目录"""
    catalogs = skill_engine.list_catalogs()
    return {"code": 200, "data": catalogs}


@app.post("/api/ai/skills/catalogs")
async def create_skill_catalog(req: SkillCatalogRequest):
    """创建技能分类"""
    try:
        from .skill.skill_engine import SkillCatalog as SkillCatalogModel

        catalog = SkillCatalogModel(
            catalog_id=f"cat_{uuid.uuid4().hex[:8]}",
            code=req.code,
            name=req.name,
            description=req.description,
            parent_id=req.parent_id,
            sort_order=req.sort_order,
            icon=req.icon,
        )
        skill_engine.register_catalog(catalog)
        return {"code": 200, "data": catalog.to_dict()}
    except Exception as e:
        logger.error(f"Catalog creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/skills/pipelines")
async def list_pipelines():
    """获取流水线列表"""
    pipelines = skill_engine.list_pipelines()
    return {"code": 200, "data": pipelines}


@app.get("/api/ai/skills/executions")
async def list_execution_logs(
    skill_id: Optional[str] = None,
    limit: int = 100
):
    """获取技能执行日志"""
    logs = skill_engine.list_execution_logs(skill_id=skill_id, limit=limit)
    return {"code": 200, "data": logs}


# ============================================================
# API Endpoints - 技术标智能编制
# ============================================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "ai-bid-ai", "version": "1.0.0"}


@app.post("/api/ai/generate/outline")
async def generate_outline(req: OutlineRequest):
    """生成技术标目录"""
    try:
        prompt = TECHNICAL_BID_OUTLINE_PROMPT.format(
            project_name=req.projectName,
            project_type=req.projectType,
            bid_requirements=req.bidRequirements,
            scoring_criteria=req.scoringCriteria,
            page_count=req.pageCount
        )

        messages = [{"role": "user", "content": prompt}]
        response = await llm_wrapper.chat(messages)

        # 尝试解析JSON
        try:
            outline = json.loads(response)
        except:
            outline = {"title": "技术标", "raw_response": response}

        return {"code": 200, "data": outline}
    except Exception as e:
        logger.error(f"Outline generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/generate/content")
async def generate_content(req: ContentRequest):
    """生成技术标正文"""
    try:
        # 根据是否启用图文并茂选择Prompt模板
        if req.includeImages or req.includeTables:
            prompt = TECHNICAL_BID_RICH_CONTENT_PROMPT.format(
                project_name=req.projectName,
                project_type=req.projectType,
                chapter_title=req.chapterTitle,
                page_count=req.pageCount,
                bid_requirements=req.bidRequirements,
                scoring_criteria=req.scoringCriteria
            )
        else:
            prompt = TECHNICAL_BID_CONTENT_PROMPT.format(
                project_name=req.projectName,
                project_type=req.projectType,
                chapter_title=req.chapterTitle,
                page_count=req.pageCount,
                bid_requirements=req.bidRequirements,
                scoring_criteria=req.scoringCriteria
            )

        messages = [{"role": "user", "content": prompt}]
        content = await llm_wrapper.chat(messages)

        # 去除思考过程标签
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

        # 如果启用了图文并茂，解析并补充图表
        images_found = []
        tables_found = []

        if req.includeImages or req.includeTables:
            content, images_found, tables_found = _parse_and_enhance_content(
                content, req.includeImages, req.includeTables
            )

        return {
            "code": 200,
            "data": {
                "content": content,
                "images": images_found,
                "tables": tables_found,
                "includeImages": req.includeImages,
                "includeTables": req.includeTables
            }
        }
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _parse_and_enhance_content(
    content: str,
    include_images: bool,
    include_tables: bool
) -> tuple[str, List[Dict], List[Dict]]:
    """解析内容中的图表标记并生成真实图表

    Args:
        content: Markdown内容
        include_images: 是否包含图片
        include_tables: 是否包含表格

    Returns:
        增强后的内容, 图片列表, 表格列表
    """
    import re
    import json
    import io

    images_found = []
    tables_found = []
    enhanced_content = content

    # 解析 chart: 标记
    chart_pattern = re.compile(r"!\[([^\]]*)\]\(chart:([^)]+)\)")
    for match in chart_pattern.finditer(content):
        alt_text = match.group(1)
        chart_spec = match.group(2)

        try:
            parts = chart_spec.split("|")
            if len(parts) >= 2:
                chart_type = parts[0]  # bar, line, pie
                title = parts[1] if len(parts) > 1 else alt_text

                # 解析数据
                data = []
                if len(parts) > 2:
                    labels = parts[2].split(",")
                    values_str = parts[3].split(",") if len(parts) > 3 else []
                    data = [[l, v] for l, v in zip(labels, values_str)]

                # 生成图表
                chart_bytes = _generate_chart_sync(
                    chart_type, title, data
                )
                if chart_bytes:
                    # 将chart标记替换为占位说明（实际图片通过后续处理添加）
                    placeholder = f"\n\n**[图表: {title}]**\n\n"
                    enhanced_content = enhanced_content.replace(match.group(0), placeholder)
                    images_found.append({
                        "type": "chart",
                        "title": title,
                        "chartType": chart_type,
                        "data": data,
                        "placeholder": True
                    })
        except Exception as e:
            logger.warning(f"Failed to parse chart spec '{chart_spec}': {e}")

    # 解析 table: 标记
    table_pattern = re.compile(r"!\[([^\]]*)\]\(table:([^)]+)\)")
    for match in table_pattern.finditer(enhanced_content):
        alt_text = match.group(1)
        table_data_str = match.group(2)

        try:
            # 尝试解析JSON
            table_data = json.loads(table_data_str)
            headers = table_data.get("headers", [])
            rows = table_data.get("rows", [])

            if headers or rows:
                # 创建表格占位符
                table_md = _build_table_markdown(headers, rows)
                enhanced_content = enhanced_content.replace(match.group(0), table_md)
                tables_found.append({
                    "type": "table",
                    "title": alt_text,
                    "headers": headers,
                    "rows": rows
                })
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse table JSON: {table_data_str}")
        except Exception as e:
            logger.warning(f"Failed to process table: {e}")

    return enhanced_content, images_found, tables_found


def _generate_chart_sync(
    chart_type: str,
    title: str,
    data: List[List[Any]]
) -> Optional[bytes]:
    """同步生成图表（内部使用）"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        if not data:
            return None

        plt.figure(figsize=(6, 4))

        if chart_type == "bar":
            labels = [str(row[0]) for row in data]
            values = []
            for row in data:
                try:
                    values.append(float(str(row[1]).replace("%", "").replace(",", "")))
                except (ValueError, TypeError):
                    values.append(0.0)
            plt.bar(range(len(values)), values, color=["#4285f4", "#34a853", "#fbbc05", "#ea4335"])
            plt.xticks(range(len(data)), labels, rotation=45)

        elif chart_type == "line":
            values = []
            for row in data:
                try:
                    values.append(float(str(row[1]).replace("%", "").replace(",", "")))
                except (ValueError, TypeError):
                    values.append(0.0)
            plt.plot(range(len(values)), values, marker="o", color="#4285f4", linewidth=2)
            plt.grid(True, linestyle="--", alpha=0.6)

        elif chart_type == "pie":
            labels = [str(row[0]) for row in data]
            values = []
            for row in data:
                try:
                    values.append(float(str(row[1]).replace("%", "").replace(",", "")))
                except (ValueError, TypeError):
                    values.append(0.0)
            colors = ["#4285f4", "#34a853", "#fbbc05", "#ea4335", "#9c27b0"]
            plt.pie(values, labels=labels, colors=colors[:len(values)],
                    autopct="%1.1f%%", startangle=90)

        plt.title(title)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Chart generation failed: {e}")
        return None


def _build_table_markdown(
    headers: List[str],
    rows: List[List[str]]
) -> str:
    """构建Markdown表格"""
    if not headers and not rows:
        return ""

    lines = []

    # 表头
    if headers:
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")

    # 数据行
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join(lines)


@app.post("/api/ai/document/parse-ai")
async def parse_document_with_ai(req: ParseRequest):
    """AI辅助解析招标文件（基于LLM）"""
    try:
        prompt = BID_DOCUMENT_PARSE_PROMPT.format(content=req.content[:8000])
        messages = [{"role": "user", "content": prompt}]
        response = await llm_wrapper.chat(messages)

        try:
            result = json.loads(response)
        except:
            result = {"raw_response": response}

        return {"code": 200, "data": result}
    except Exception as e:
        logger.error(f"Document parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/rewrite")
async def paraphrase(req: ParaphraseRequest):
    """标书改写"""
    try:
        prompt = PARAPHRASE_PROMPT.format(
            original_content=req.content,
            strategy=req.strategy,
            multiplier=req.multiplier,
            preserve_keywords=", ".join(req.preserveKeywords) if req.preserveKeywords else "无"
        )

        messages = [{"role": "user", "content": prompt}]
        result = await llm_wrapper.chat(messages)

        return {
            "code": 200,
            "data": {
                "originalLength": len(req.content),
                "rewrittenContent": result,
                "rewrittenLength": len(result)
            }
        }
    except Exception as e:
        logger.error(f"Paraphrasing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/check/compliance")
async def check_compliance(req: ComplianceCheckRequest):
    """合规检测"""
    try:
        prompt = COMPLIANCE_CHECK_PROMPT.format(
            requirements=req.requirements[:4000],
            content=req.content[:4000]
        )

        messages = [{"role": "user", "content": prompt}]
        response = await llm_wrapper.chat(messages)

        try:
            result = json.loads(response)
        except:
            result = {"raw_response": response}

        return {"code": 200, "data": result}
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# API Endpoints - 改写增强（多版本/模板/版本管理）
# ============================================================

@app.post("/api/ai/rewrite/versions", response_model=RewriteVersionsResponse)
async def rewrite_multi_versions(req: RewriteVersionsRequest):
    """多版本改写 - 同一内容生成多个不同风格版本"""
    try:
        # 解析指定风格
        style_enums = None
        if req.styles:
            style_enums = []
            for s in req.styles:
                try:
                    style_enums.append(RewriteStyle(s))
                except ValueError:
                    pass

        # 执行多版本改写
        results = await rewrite_service.multi_version_rewrite(
            content=req.content,
            version_count=req.version_count,
            styles=style_enums,
            preserve_keywords=req.preserve_keywords
        )

        versions = []
        for i, r in enumerate(results):
            versions.append({
                "version_id": i + 1,
                "version_name": r.style or f"版本{i+1}",
                "description": r.changes_summary.get("description", ""),
                "content": r.content,
                "length": r.rewritten_length,
                "change_summary": r.changes_summary
            })

        return {
            "code": 200,
            "data": {
                "original_length": len(req.content),
                "versions": versions
            }
        }
    except Exception as e:
        logger.error(f"Multi-version rewrite failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/template/apply")
async def apply_template(req: TemplateApplyRequest):
    """应用模板到内容"""
    try:
        from ai_bid_material.template_service import get_template_service
        template_service = get_template_service()

        result = template_service.apply_template(
            content=req.content,
            template_id=req.template_id,
            variables=req.variables,
            merge_strategy=req.merge_strategy
        )

        return {
            "code": 200,
            "data": {
                "success": result.success,
                "applied_content": result.applied_content,
                "template_id": result.template_id,
                "template_name": result.template_name,
                "variables_filled": result.variables_filled,
                "warnings": result.warnings
            }
        }
    except Exception as e:
        logger.error(f"Template apply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/template/list")
async def list_templates(
    template_type: Optional[str] = None,
    keyword: Optional[str] = None,
    tags: Optional[str] = None
):
    """模板列表"""
    try:
        from ai_bid_material.template_service import get_template_service, TemplateType
        template_service = get_template_service()

        # 解析类型
        t_type = None
        if template_type:
            try:
                t_type = TemplateType(template_type)
            except ValueError:
                pass

        # 解析标签
        tag_list = tags.split(",") if tags else None

        templates = template_service.list_templates(
            template_type=t_type,
            keyword=keyword,
            tags=tag_list
        )

        return {
            "code": 200,
            "data": {
                "total": len(templates),
                "templates": [
                    {
                        "template_id": t.template_id,
                        "name": t.name,
                        "description": t.description,
                        "template_type": t.template_type.value,
                        "category": t.category,
                        "tags": t.tags,
                        "current_version": t.current_version,
                        "usage_count": t.usage_count
                    }
                    for t in templates
                ]
            }
        }
    except Exception as e:
        logger.error(f"List templates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/template/create")
async def create_template(req: TemplateCreateRequest):
    """创建模板"""
    try:
        from ai_bid_material.template_service import get_template_service, TemplateType
        template_service = get_template_service()

        t_type = TemplateType.CUSTOM
        if req.template_type:
            try:
                t_type = TemplateType(req.template_type)
            except ValueError:
                t_type = TemplateType.CUSTOM

        template = template_service.create_template(
            name=req.name,
            content=req.content,
            template_type=t_type,
            description=req.description,
            category=req.category,
            tags=req.tags
        )

        return {
            "code": 200,
            "data": {
                "template_id": template.template_id,
                "name": template.name,
                "created_at": template.created_at
            }
        }
    except Exception as e:
        logger.error(f"Create template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/template/{template_id}")
async def get_template(template_id: str):
    """获取模板详情"""
    try:
        from ai_bid_material.template_service import get_template_service
        template_service = get_template_service()

        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "code": 200,
            "data": template.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/version/content")
async def create_content_version(req: VersionCreateRequest):
    """创建内容版本记录"""
    try:
        record = version_service.create_content(
            content=req.content,
            title=req.title,
            description=req.description,
            tags=req.tags
        )

        return {
            "code": 200,
            "data": {
                "content_id": record.content_id,
                "version_id": record.current_version_id,
                "created_at": record.created_at
            }
        }
    except Exception as e:
        logger.error(f"Create content version failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/version/{content_id}/add")
async def add_version(content_id: str, req: VersionAddRequest):
    """为内容添加新版本"""
    try:
        version = version_service.add_version(
            content_id=content_id,
            content=req.content,
            rewrite_strategy=req.rewrite_strategy,
            change_summary=req.change_summary,
            rewrite_style=req.rewrite_style
        )

        if not version:
            raise HTTPException(status_code=404, detail="Content not found")

        return {
            "code": 200,
            "data": {
                "version_id": version.version_id,
                "version_number": version.version_number,
                "created_at": version.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add version failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/version/{content_id}/history")
async def get_version_history(content_id: str):
    """获取内容版本历史"""
    try:
        history = version_service.list_content_history(content_id)

        return {
            "code": 200,
            "data": {
                "content_id": content_id,
                "versions": [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "rewrite_strategy": v.rewrite_strategy,
                        "rewrite_style": v.rewrite_style,
                        "change_summary": v.change_summary,
                        "created_at": v.created_at
                    }
                    for v in history
                ]
            }
        }
    except Exception as e:
        logger.error(f"Get version history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/version/{version_id}/content")
async def get_version_content(version_id: str):
    """获取特定版本内容"""
    try:
        version = version_service.get_version(version_id)

        if not version:
            raise HTTPException(status_code=404, detail="Version not found")

        return {
            "code": 200,
            "data": {
                "version_id": version.version_id,
                "version_number": version.version_number,
                "content": version.content,
                "rewrite_strategy": version.rewrite_strategy,
                "change_summary": version.change_summary,
                "created_at": version.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get version content failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/version/compare")
async def compare_versions(req: VersionCompareRequest):
    """比较两个版本的差异"""
    try:
        diff = version_service.compare_versions(
            version_id_1=req.version_id_1,
            version_id_2=req.version_id_2
        )

        if not diff:
            raise HTTPException(status_code=404, detail="Version not found")

        return {
            "code": 200,
            "data": {
                "from_version": diff.from_version,
                "to_version": diff.to_version,
                "length_change": diff.length_change,
                "change_ratio": diff.change_ratio,
                "added_lines": diff.added_lines,
                "removed_lines": diff.removed_lines,
                "similarity": diff.similarity,
                "diff_segments": diff.diff_segments[:50]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compare versions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/version/{content_id}/rollback")
async def rollback_version(content_id: str, req: VersionRollbackRequest):
    """回滚到指定版本"""
    try:
        new_version = version_service.rollback_to_version(
            content_id=content_id,
            version_id=req.version_id
        )

        if not new_version:
            raise HTTPException(status_code=404, detail="Content or version not found")

        return {
            "code": 200,
            "data": {
                "success": True,
                "new_version_id": new_version.version_id,
                "new_version_number": new_version.version_number,
                "message": f"已回滚到版本 {new_version.version_number}"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rollback version failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# API Endpoints - 兼容原有接口
# ============================================================

@app.post("/api/v1/bid/generate")
async def generate_bid(request: BidGenerateRequest):
    """生成投标文件"""
    try:
        if request.bid_type == "technical":
            prompt = build_prompt(
                TECHNICAL_BID_PROMPT,
                project_name=request.project_name,
                procurement_unit=request.procurement_unit,
                deadline=request.deadline or "未指定",
                bidding_requirements=request.bidding_requirements,
                qualifications=request.qualifications,
                scoring_criteria=request.scoring_criteria or "参考招标文件",
                reference_docs="（无参考文档）"
            )
        else:
            prompt = build_prompt(
                CREDIT_BID_PROMPT,
                project_name=request.project_name,
                procurement_unit=request.procurement_unit,
                qualifications=request.qualifications,
                case_studies="（无业绩案例）",
                financial_info="（无财务信息）",
                honors_and_certifications="（无荣誉资质）"
            )

        messages = [{"role": "user", "content": prompt}]
        content = await llm_wrapper.chat(messages)

        return {
            "code": 200,
            "data": {
                "success": True,
                "bid_type": request.bid_type,
                "content": content,
                "word_count": len(content)
            }
        }
    except Exception as e:
        logger.error(f"Bid generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/bid/rewrite")
async def rewrite_bid(request: BidRewriteRequest):
    """改写投标文件"""
    try:
        prompt = build_prompt(
            BID_REWRITE_PROMPT,
            original_content=request.original_content,
            rewrite_requirements=request.rewrite_requirements,
            target_style=request.target_style
        )

        messages = [{"role": "user", "content": prompt}]
        content = await llm_wrapper.chat(messages)

        return {
            "code": 200,
            "data": {
                "success": True,
                "original_length": len(request.original_content),
                "rewritten_length": len(content),
                "content": content
            }
        }
    except Exception as e:
        logger.error(f"Bid rewrite failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# API Endpoints - 文档解析与导出
# ============================================================

@app.post("/api/ai/document/parse")
async def parse_document_file(req: DocumentParseFileRequest):
    """解析文档文件（PDF/Word）"""
    try:
        import base64

        # 解码Base64内容
        file_content = base64.b64decode(req.file_content)

        # 解析文档
        parsed = await document_parser.parse(
            file_content=file_content,
            file_name=req.file_name,
            file_type=req.file_type
        )

        return {
            "code": 200,
            "data": {
                "file_name": parsed.file_name,
                "file_type": parsed.file_type,
                "content_length": len(parsed.content),
                "basic_info": parsed.basic_info,
                "scoring_method": parsed.scoring_method,
                "compliance_items": parsed.compliance_items,
                "disqualification_items": parsed.disqualification_items,
                "preview": parsed.content[:500] if parsed.content else ""
            }
        }
    except Exception as e:
        logger.error(f"Document file parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/document/export")
async def export_document(req: DocumentExportRequest):
    """导出Word文档"""
    try:
        report_type = req.report_type.lower()
        data = req.data

        if report_type == "analysis":
            content = document_exporter.export_analysis_report(data)
        elif report_type == "compliance":
            content = document_exporter.export_compliance_report(data)
        elif report_type == "summary":
            content = document_exporter.export_bid_summary(data)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        import base64
        return {
            "code": 200,
            "data": {
                "file_content": base64.b64encode(content).decode("utf-8"),
                "file_name": f"{report_type}_report.docx"
            }
        }
    except Exception as e:
        logger.error(f"Document export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/document/parse-ai")
async def parse_document_with_ai(req: ParseRequest):
    """AI辅助解析招标文件（基于LLM）"""
    try:
        prompt = BID_DOCUMENT_PARSE_PROMPT.format(content=req.content[:8000])
        messages = [{"role": "user", "content": prompt}]
        response = await llm_wrapper.chat(messages)

        try:
            result = json.loads(response)
        except:
            result = {"raw_response": response}

        return {"code": 200, "data": result}
    except Exception as e:
        logger.error(f"Document parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# API Endpoints - 表格生成
# ============================================================

@app.post("/api/ai/table/generate")
async def generate_table(req: TableGenerateRequest):
    """生成指定类型表格

    支持的表格类型:
    - qualification: 资质要求对照表
    - personnel: 项目人员配置表
    - schedule: 施工进度计划表
    - equipment: 设备清单表
    - safety: 安全措施检查表
    """
    try:
        table_type = req.table_type.lower()
        data = req.data

        # 如果没有提供数据，使用示例数据
        if not data:
            sample_data = create_sample_data()
            if table_type == "qualification":
                data = sample_data.get("qualification_requirements", [])
            elif table_type == "personnel":
                data = sample_data.get("personnel_config", {}).get("positions", [])
            elif table_type == "schedule":
                data = sample_data.get("schedule_timeline", {})
            elif table_type == "equipment":
                data = sample_data.get("equipment_list", [])
            elif table_type == "safety":
                data = sample_data.get("safety_measures", [])

        # 根据类型生成表格
        if table_type == "qualification":
            table_data = table_generator.generate_qualification_table(data)
        elif table_type == "personnel":
            table_data = table_generator.generate_personnel_table(data)
        elif table_type == "schedule":
            table_data = table_generator.generate_schedule_table(data)
        elif table_type == "equipment":
            table_data = table_generator.generate_equipment_table(data)
        elif table_type == "safety":
            table_data = table_generator.generate_safety_table(data)
        else:
            raise ValueError(f"Unsupported table type: {table_type}")

        return {
            "code": 200,
            "data": {
                "table_type": table_type,
                "table_data": table_data,
                "row_count": len(table_data) - 1,
                "column_count": len(table_data[0]) if table_data else 0
            }
        }
    except Exception as e:
        logger.error(f"Table generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/table/generate-word")
async def generate_table_word(req: TableGenerateRequest):
    """生成表格并导出为Word文档"""
    try:
        table_type = req.table_type.lower()
        data = req.data

        # 获取表格数据
        table_req = TableGenerateRequest(table_type=table_type, data=data)
        table_result = await generate_table(table_req)

        table_data = table_result["data"]["table_data"]

        # 生成Word文档
        table_titles = {
            "qualification": "资质要求对照表",
            "personnel": "项目人员配置表",
            "schedule": "施工进度计划表",
            "equipment": "设备清单表",
            "safety": "安全措施检查表"
        }
        title = table_titles.get(table_type, "表格")

        word_content = table_generator.export_table_to_word(
            table_data,
            title=title,
            header_style="BLUE"
        )

        import base64
        return {
            "code": 200,
            "data": {
                "file_content": base64.b64encode(word_content).decode("utf-8"),
                "file_name": f"{table_type}_table.docx",
                "table_type": table_type
            }
        }
    except Exception as e:
        logger.error(f"Table Word export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/table/generate-gantt")
async def generate_gantt(req: GanttGenerateRequest):
    """生成施工进度甘特图

    Args:
        project_name: 项目名称
        timeline: 时间计划，包含 phases 列表
        output_format: 输出格式 (png/svg)
    """
    try:
        timeline = req.timeline

        # 如果没有提供数据，使用示例数据
        if not timeline:
            sample_data = create_sample_data()
            timeline = sample_data.get("schedule_timeline", {})

        timeline["project_name"] = req.project_name

        # 生成甘特图
        gantt_image = table_generator.generate_gantt_chart(
            timeline=timeline,
            output_format=req.output_format
        )

        import base64
        return {
            "code": 200,
            "data": {
                "image_content": base64.b64encode(gantt_image).decode("utf-8"),
                "format": req.output_format,
                "project_name": req.project_name
            }
        }
    except Exception as e:
        logger.error(f"Gantt generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/table/generate-gantt-word")
async def generate_gantt_word(req: GanttGenerateRequest):
    """生成甘特图并导出为Word文档"""
    try:
        timeline = req.timeline

        # 如果没有提供数据，使用示例数据
        if not timeline:
            sample_data = create_sample_data()
            timeline = sample_data.get("schedule_timeline", {})

        timeline["project_name"] = req.project_name

        # 生成甘特图
        gantt_image = table_generator.generate_gantt_chart(
            timeline=timeline,
            output_format="png"
        )

        # 生成Word文档
        word_content = table_generator.export_gantt_to_word(
            gantt_image,
            title=req.project_name,
            doc_title=f"{req.project_name} - 施工进度计划（甘特图）"
        )

        import base64
        return {
            "code": 200,
            "data": {
                "file_content": base64.b64encode(word_content).decode("utf-8"),
                "file_name": f"{req.project_name}_gantt.docx",
                "project_name": req.project_name
            }
        }
    except Exception as e:
        logger.error(f"Gantt Word export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Pipeline - 全文生成流水线
# ============================================================

# 全局流水线存储（所有runner共享）
_pipeline_storage: Dict[str, Any] = {}

# 创建执行器（共享存储）
from .pipeline import PipelineRunner
_pipeline_runner = PipelineRunner(
    llm_wrapper=llm_wrapper,
    document_parser=document_parser,
    document_exporter=document_exporter,
    storage=_pipeline_storage
)

bid_pipeline = BidPipeline(
    llm_wrapper=llm_wrapper,
    document_parser=document_parser,
    document_exporter=document_exporter,
    runner=_pipeline_runner
)


class PipelineGenerateRequest(BaseModel):
    """流水线生成请求"""
    file_content: Optional[str] = None  # Base64编码的招标文件
    file_name: str = "tender.pdf"
    file_type: str = "pdf"  # pdf, docx, doc, zf
    project_name: Optional[str] = None
    project_type: str = "工程建设"
    page_count: int = 50
    chapters: Optional[List[Dict[str, Any]]] = None
    resume_from: Optional[str] = None  # 从指定job_id恢复


@app.post("/api/ai/pipeline/generate")
async def pipeline_generate(req: PipelineGenerateRequest):
    """启动完整流水线 - 招标文件→目录→正文全流程自动生成"""
    try:
        start_result = await bid_pipeline.generate(
            file_content=req.file_content,
            file_name=req.file_name,
            file_type=req.file_type,
            project_name=req.project_name,
            project_type=req.project_type,
            page_count=req.page_count,
            chapters=req.chapters,
            resume_from=req.resume_from
        )

        job_id = start_result["job_id"]

        import asyncio

        async def run_pipeline():
            context = {
                "file_content": req.file_content,
                "file_name": req.file_name,
                "file_type": req.file_type,
                "project_name": req.project_name or "技术标项目",
                "project_type": req.project_type,
                "page_count": req.page_count,
                "chapters": req.chapters or []
            }
            await _pipeline_runner.run(job_id=job_id, context=context)

        asyncio.create_task(run_pipeline())

        return {
            "code": 200,
            "data": {
                "job_id": job_id,
                "status": "pending",
                "message": "流水线已启动，正在异步执行",
                "status_url": f"/api/ai/pipeline/status/{job_id}",
                "result_url": f"/api/ai/pipeline/result/{job_id}"
            }
        }
    except Exception as e:
        logger.error(f"Pipeline start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/pipeline/status/{job_id}")
async def pipeline_status(job_id: str):
    """查询任务状态"""
    status = _pipeline_runner.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return {"code": 200, "data": status}


@app.get("/api/ai/pipeline/result/{job_id}")
async def pipeline_result(job_id: str):
    """获取生成结果"""
    result = _pipeline_runner.get_job_result(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Job not found or not completed: {job_id}")
    return {"code": 200, "data": result}


@app.get("/api/ai/pipeline/jobs")
async def pipeline_list_jobs():
    """列出所有任务"""
    return {"code": 200, "data": _pipeline_runner.list_jobs()}


@app.post("/api/ai/pipeline/cancel/{job_id}")
async def pipeline_cancel(job_id: str):
    """取消任务"""
    success = _pipeline_runner.cancel_job(job_id)
    return {"code": 200 if success else 400, "data": {"job_id": job_id, "cancelled": success}}


@app.post("/api/ai/pipeline/resume/{job_id}")
async def pipeline_resume(job_id: str):
    """从断点恢复任务"""
    status = _pipeline_runner.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    if status["status"] not in ["failed", "cancelled"]:
        return {"code": 400, "data": {"error": "只能恢复失败或取消的任务"}}

    start_result = await bid_pipeline.generate(file_content=None, resume_from=job_id)
    job_id_new = start_result["job_id"]

    import asyncio

    async def run_resume():
        context = {}
        checkpoint = _pipeline_runner._load_checkpoint(job_id)
        if checkpoint:
            context = checkpoint

        from_stage = None
        for i, result in enumerate(status.get("stages", [])):
            if result.get("status") != "completed":
                from_stage = i
                break

        await _pipeline_runner.run(job_id=job_id_new, context=context, from_stage=from_stage)

    asyncio.create_task(run_resume())

    return {
        "code": 200,
        "data": {
            "job_id": job_id_new,
            "status": "resuming",
            "message": f"从任务 {job_id} 恢复执行",
            "status_url": f"/api/ai/pipeline/status/{job_id_new}"
        }
    }


@app.post("/api/ai/export/html-to-word")
async def export_html_to_word(request: Request):
    """将HTML内容导出为Word文档
    
    Request body:
        {
            "html": "<h1>标题</h1><p>内容...</p>",
            "title": "标书标题",  // 可选
            "template": "standard"  // 可选: standard/technical/commercial/professional/simple
        }
    
    Returns:
        Word document file download
    """
    try:
        body = await request.json()
        html_content = body.get("html", "")
        doc_title = body.get("title", "标书文档")
        template_type = body.get("template", "standard")
        
        if not html_content:
            raise HTTPException(status_code=400, detail="HTML内容不能为空")
        
        # 导入模板系统
        import sys
        sys.path.insert(0, '/home/zzy/.openclaw/workspace/workspace-bid/templates')
        from bid_templates import get_template, list_templates
        from styled_exporter import StyledDocumentExporter
        
        # 获取模板
        template = get_template(template_type)
        exporter = StyledDocumentExporter(template)
        doc = exporter.create_document()
        
        # 添加文档标题
        exporter.add_title(doc, doc_title, level=0)
        
        # 解析HTML内容并添加
        exporter.add_html_content(doc, html_content)
        
        # 导出
        doc_bytes = exporter.export_to_bytes(doc)
        
        # 返回文件
        from fastapi.responses import StreamingResponse
        import urllib.parse
        
        encoded_filename = urllib.parse.quote(doc_title + '.docx')
        
        return StreamingResponse(
            io.BytesIO(doc_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        logger.error(f"HTML to Word export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/export/templates")
async def list_export_templates():
    """列出所有可用的导出模板"""
    import sys
    sys.path.insert(0, '/home/zzy/.openclaw/workspace/workspace-bid/templates')
    from bid_templates import list_templates
    return {"code": 200, "data": list_templates()}


def _add_html_content_to_doc(doc, html_content: str, exporter: DocumentExporter):
    """解析HTML内容并添加到Word文档"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for element in soup.children:
        if element.name is None:  # 文本节点
            continue
            
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            text = element.get_text().strip()
            if text:
                exporter.add_title(doc, text, level=level if level <= 6 else 6)
                
        elif element.name == 'p':
            text = element.get_text().strip()
            if text:
                # 检查是否加粗
                strong = element.find('strong')
                exporter.add_paragraph(doc, text, bold=strong is not None)
                
        elif element.name == 'div':
            # 递归处理div（可能是章节块）
            div_html = str(element)
            _add_html_content_to_doc(doc, div_html, exporter)
            
        elif element.name == 'strong' or element.name == 'b':
            text = element.get_text().strip()
            if text:
                exporter.add_paragraph(doc, text, bold=True)
                
        elif element.name == 'table':
            _add_html_table_to_doc(doc, element, exporter)
            
        elif element.name == 'ul':
            for li in element.find_all('li', recursive=False):
                text = li.get_text().strip()
                if text:
                    para = doc.add_paragraph(style='List Bullet')
                    para.add_run(text)
                    
        elif element.name == 'ol':
            for li in element.find_all('li', recursive=False):
                text = li.get_text().strip()
                if text:
                    para = doc.add_paragraph(style='List Number')
                    para.add_run(text)
                    
        elif element.name == 'hr':
            # 分隔线 - 添加空行
            doc.add_paragraph()


def _add_html_table_to_doc(doc, table_element, exporter: DocumentExporter):
    """将HTML表格转换为Word表格"""
    from bs4 import BeautifulSoup
    
    rows = table_element.find_all('tr')
    if not rows:
        return
    
    # 获取表头
    header_row = rows[0] if rows else None
    headers = []
    if header_row:
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text().strip())
    
    # 获取数据行
    data_rows = []
    for tr in rows[1:]:
        row_data = []
        for td in tr.find_all('td'):
            row_data.append(td.get_text().strip())
        if row_data:
            data_rows.append(row_data)
    
    # 添加表格
    if headers or data_rows:
        exporter.add_styled_table(doc, data_rows, headers if headers else None)


# ============================================================
# 启动服务
# ============================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8087)