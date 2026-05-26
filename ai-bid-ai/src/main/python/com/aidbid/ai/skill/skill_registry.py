"""预置技能库与技能注册表"""
import logging
from typing import Any, Dict, List, Optional

from .skill_engine import (
    SkillEngine,
    SkillDefinition,
    SkillParameter,
    SkillCatalog,
    PipelineDefinition,
    PipelineStage,
    SkillType,
)

logger = logging.getLogger(__name__)


# ============================================================
# 预置技能分类目录
# ============================================================

PRESET_CATALOGS = [
    SkillCatalog(
        catalog_id="cat_parser",
        code="PARSER",
        name="文档解析",
        description="招标文件解析相关技能",
        sort_order=1,
        icon="document",
    ),
    SkillCatalog(
        catalog_id="cat_generator",
        code="GENERATOR",
        name="内容生成",
        description="投标文档内容生成相关技能",
        sort_order=2,
        icon="edit",
    ),
    SkillCatalog(
        catalog_id="cat_matcher",
        code="MATCHER",
        name="资质匹配",
        description="资质评估与匹配相关技能",
        sort_order=3,
        icon="check-circle",
    ),
    SkillCatalog(
        catalog_id="cat_export",
        code="EXPORT",
        name="文档导出",
        description="文档导出相关技能",
        sort_order=4,
        icon="download",
    ),
    SkillCatalog(
        catalog_id="cat_utility",
        code="UTILITY",
        name="工具",
        description="辅助工具类技能",
        sort_order=5,
        icon="tool",
    ),
]


# ============================================================
# 预置技能处理器
# ============================================================

async def tender_parser_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """招标文件解析处理器"""
    from ..document_parser import DocumentParser

    file_path = inputs.get("file_path", "")
    file_content = inputs.get("file_content")
    file_type = inputs.get("file_type", "pdf")

    parser = DocumentParser()
    try:
        if file_path:
            result = await parser.parse(file_path)
        elif file_content:
            result = await parser.parse_bytes(file_content, file_type)
        else:
            return {"error": "No file provided"}

        return {
            "basic_info": result.basic_info,
            "scoring_method": result.scoring_method,
            "compliance_items": result.compliance_items,
            "disqualification_items": result.disqualification_items,
            "raw_text": result.raw_text[:500] if result.raw_text else "",
        }
    except Exception as e:
        logger.exception("Tender parser failed")
        return {"error": str(e)}


async def outline_generator_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """目录生成处理器"""
    from ..prompts import build_prompt, TECHNICAL_BID_OUTLINE_PROMPT
    from ..llm_gateway import LLMFactory

    project_name = inputs.get("project_name", "")
    project_type = inputs.get("project_type", "")
    bid_requirements = inputs.get("bid_requirements", "")
    scoring_criteria = inputs.get("scoring_criteria", "")

    prompt = build_prompt(
        TECHNICAL_BID_OUTLINE_PROMPT,
        project_name=project_name,
        project_type=project_type,
        bid_requirements=bid_requirements,
        scoring_criteria=scoring_criteria,
    )

    gateway = LLMFactory.get_gateway("deepseek")
    response = await gateway.chat([{"role": "user", "content": prompt}])

    return {
        "outline": response.content,
        "project_name": project_name,
        "project_type": project_type,
    }


async def content_generator_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """正文生成处理器"""
    from ..prompts import build_prompt, TECHNICAL_BID_CONTENT_PROMPT
    from ..llm_gateway import LLMFactory

    outline = inputs.get("outline", "")
    chapter = inputs.get("chapter", "")
    project_name = inputs.get("project_name", "")
    rewrite_strategy = inputs.get("rewrite_strategy", "moderate")

    prompt = build_prompt(
        TECHNICAL_BID_CONTENT_PROMPT,
        outline=outline,
        chapter=chapter,
        project_name=project_name,
    )

    gateway = LLMFactory.get_gateway("deepseek")
    response = await gateway.chat([{"role": "user", "content": prompt}])

    return {
        "content": response.content,
        "chapter": chapter,
        "word_count": len(response.content),
    }


async def qualification_match_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """资质匹配处理器"""
    from ..prompts import build_prompt, COMPLIANCE_CHECK_PROMPT
    from ..llm_gateway import LLMFactory

    requirements = inputs.get("requirements", "")
    enterprise_qualifications = inputs.get("enterprise_qualifications", [])

    prompt = build_prompt(
        COMPLIANCE_CHECK_PROMPT,
        requirements=requirements,
        qualifications="\n".join([f"- {q}" for q in enterprise_qualifications]),
    )

    gateway = LLMFactory.get_gateway("deepseek")
    response = await gateway.chat([{"role": "user", "content": prompt}])

    return {
        "match_result": response.content,
        "requirements": requirements,
        "qualifications_count": len(enterprise_qualifications),
    }


async def document_export_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """文档导出处理器"""
    from ..document_exporter import DocumentExporter
    import base64

    content = inputs.get("content", "")
    title = inputs.get("title", "投标文档")
    format_type = inputs.get("format", "docx")

    exporter = DocumentExporter()
    try:
        doc = exporter.create_document(title)
        exporter.add_title(title)
        exporter.add_paragraph(content)

        if format_type == "docx":
            doc_bytes = exporter.export_to_bytes()
            return {
                "file_data": base64.b64encode(doc_bytes).decode("utf-8"),
                "format": "docx",
                "title": title,
            }
        else:
            return {"error": f"Unsupported format: {format_type}"}
    except Exception as e:
        logger.exception("Document export failed")
        return {"error": str(e)}


# ============================================================
# 预置技能定义
# ============================================================

PRESET_SKILLS = [
    # 1. 招标文件解析技能
    SkillDefinition(
        skill_id="tender_parser_skill",
        name="招标文件解析",
        description="解析PDF/Word/ZF格式招标文件，提取关键信息（基本信息、评分办法、合规项、不合格项）",
        version="1.0.0",
        skill_type=SkillType.PARSER.value,
        input_params=[
            SkillParameter(name="file_path", type="string", description="文件路径"),
            SkillParameter(name="file_content", type="string", description="文件内容(Base64)"),
            SkillParameter(name="file_type", type="string", default="pdf", description="文件类型"),
        ],
        output_schema={
            "basic_info": {"type": "object", "description": "基本信息"},
            "scoring_method": {"type": "object", "description": "评分办法"},
            "compliance_items": {"type": "array", "description": "合规项列表"},
            "disqualification_items": {"type": "array", "description": "不合格项列表"},
        },
        default_params={},
        dependencies=[],
        timeout=120,
        enabled=True,
        tags=["parser", "tender", "pdf", "word"],
        priority=10,
        handler=tender_parser_handler,
    ),
    # 2. 目录生成技能
    SkillDefinition(
        skill_id="outline_generator_skill",
        name="目录生成",
        description="根据项目信息生成投标技术标目录结构",
        version="1.0.0",
        skill_type=SkillType.GENERATOR.value,
        input_params=[
            SkillParameter(name="project_name", type="string", required=True, description="项目名称"),
            SkillParameter(name="project_type", type="string", required=True, description="项目类型"),
            SkillParameter(name="bid_requirements", type="string", description="投标要求"),
            SkillParameter(name="scoring_criteria", type="string", description="评分标准"),
        ],
        output_schema={
            "outline": {"type": "string", "description": "生成的目录"},
            "project_name": {"type": "string"},
            "project_type": {"type": "string"},
        },
        default_params={},
        dependencies=["tender_parser_skill"],
        timeout=60,
        enabled=True,
        tags=["generator", "outline", "structure"],
        priority=9,
        handler=outline_generator_handler,
    ),
    # 3. 正文生成技能
    SkillDefinition(
        skill_id="content_generator_skill",
        name="正文生成",
        description="根据目录生成投标技术标正文内容",
        version="1.0.0",
        skill_type=SkillType.GENERATOR.value,
        input_params=[
            SkillParameter(name="outline", type="string", required=True, description="目录结构"),
            SkillParameter(name="chapter", type="string", description="章节名称"),
            SkillParameter(name="project_name", type="string", description="项目名称"),
            SkillParameter(name="rewrite_strategy", type="string", default="moderate", description="改写策略"),
        ],
        output_schema={
            "content": {"type": "string", "description": "生成的内容"},
            "chapter": {"type": "string"},
            "word_count": {"type": "integer"},
        },
        default_params={"rewrite_strategy": "moderate"},
        dependencies=["outline_generator_skill"],
        timeout=180,
        enabled=True,
        tags=["generator", "content", "bid"],
        priority=8,
        handler=content_generator_handler,
    ),
    # 4. 资质匹配技能
    SkillDefinition(
        skill_id="qualification_match_skill",
        name="资质匹配",
        description="评估企业资质与招标要求的匹配程度",
        version="1.0.0",
        skill_type=SkillType.MATCHER.value,
        input_params=[
            SkillParameter(name="requirements", type="string", required=True, description="资质要求"),
            SkillParameter(name="enterprise_qualifications", type="array", description="企业资质列表"),
        ],
        output_schema={
            "match_result": {"type": "string", "description": "匹配结果"},
            "requirements": {"type": "string"},
            "qualifications_count": {"type": "integer"},
        },
        default_params={},
        dependencies=[],
        timeout=60,
        enabled=True,
        tags=["matcher", "qualification", "compliance"],
        priority=7,
        handler=qualification_match_handler,
    ),
    # 5. 文档导出技能
    SkillDefinition(
        skill_id="document_export_skill",
        name="文档导出",
        description="将内容导出为Word文档或其他格式",
        version="1.0.0",
        skill_type=SkillType.EXPORT.value,
        input_params=[
            SkillParameter(name="content", type="string", required=True, description="文档内容"),
            SkillParameter(name="title", type="string", default="投标文档", description="文档标题"),
            SkillParameter(name="format", type="string", default="docx", description="导出格式"),
        ],
        output_schema={
            "file_data": {"type": "string", "description": "文件数据(Base64)"},
            "format": {"type": "string"},
            "title": {"type": "string"},
        },
        default_params={"format": "docx"},
        dependencies=["content_generator_skill"],
        timeout=30,
        enabled=True,
        tags=["export", "document", "word"],
        priority=6,
        handler=document_export_handler,
    ),
]


# ============================================================
# 预置流水线定义
# ============================================================

PRESET_PIPELINES = [
    PipelineDefinition(
        pipeline_id="full_bid_pipeline",
        name="完整投标文档生成",
        description="从招标文件解析到文档导出的完整流程",
        stages=[
            PipelineStage(skill_id="tender_parser_skill", inputs={"file_path": "$file_path"}),
            PipelineStage(skill_id="outline_generator_skill", inputs={"project_name": "$project_name", "project_type": "$project_type", "bid_requirements": "$bid_requirements", "scoring_criteria": "$scoring_criteria"}),
            PipelineStage(skill_id="content_generator_skill", inputs={"outline": "$outline_generator_skill.outline", "project_name": "$project_name"}),
            PipelineStage(skill_id="document_export_skill", inputs={"content": "$content_generator_skill.content", "title": "$project_name"}),
        ],
        timeout=600,
    ),
    PipelineDefinition(
        pipeline_id="quick_bid_pipeline",
        name="快速投标文档生成",
        description="不解析招标文件，直接生成目录和内容",
        stages=[
            PipelineStage(skill_id="outline_generator_skill", inputs={"project_name": "$project_name", "project_type": "$project_type"}),
            PipelineStage(skill_id="content_generator_skill", inputs={"outline": "$outline_generator_skill.outline", "project_name": "$project_name"}),
            PipelineStage(skill_id="document_export_skill", inputs={"content": "$content_generator_skill.content", "title": "$project_name"}),
        ],
        timeout=300,
    ),
]


# ============================================================
# 技能注册表单例
# ============================================================

class SkillRegistry:
    """技能注册表管理器"""

    _instance: Optional["SkillRegistry"] = None
    _engine: Optional[SkillEngine] = None

    @classmethod
    def get_instance(cls) -> "SkillRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化注册表，加载预置技能"""
        self._engine = SkillEngine()

        # 注册分类目录
        for catalog in PRESET_CATALOGS:
            self._engine.register_catalog(catalog)

        # 注册预置技能
        for skill in PRESET_SKILLS:
            try:
                self._engine.register_skill(skill)
            except Exception as e:
                logger.warning(f"Failed to register skill {skill.skill_id}: {e}")

        # 注册预置流水线
        for pipeline in PRESET_PIPELINES:
            self._engine.register_pipeline(pipeline)

        logger.info(f"SkillRegistry initialized with {len(PRESET_SKILLS)} skills")

    @property
    def engine(self) -> SkillEngine:
        return self._engine


def get_skill_registry() -> SkillEngine:
    """获取技能引擎实例"""
    return SkillRegistry.get_instance().engine