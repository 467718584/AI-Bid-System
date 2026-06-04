"""
增强Word导出功能 - 新增 /api/ai/export/word 端点
支持HTML表格和模板样式导出
"""

import sys
import os
sys.path.insert(0, '/home/zzy/.openclaw/workspace/workspace-bid/templates')

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 导入模板导出器
try:
    from styled_exporter import StyledDocumentExporter
    from bid_templates import get_template, list_templates, TemplateType
    TEMPLATES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Template exporter not available: {e}")
    TEMPLATES_AVAILABLE = False

router = APIRouter()

class WordExportRequest(BaseModel):
    """Word导出请求"""
    title: str = "标书文档"
    content: str  # HTML格式内容
    template_type: str = "standard"  # standard/technical/commercial/professional/simple


class WordExportResponse(BaseModel):
    """Word导出响应"""
    success: bool
    filename: str
    template_used: str


@router.post("/api/ai/export/word")
async def export_word(request: WordExportRequest):
    """使用模板导出Word文档（支持HTML表格）"""
    if not TEMPLATES_AVAILABLE:
        raise HTTPException(status_code=500, detail="模板导出器未安装")

    try:
        # 获取模板
        template_type_map = {
            "standard": TemplateType.STANDARD,
            "technical": TemplateType.TECHNICAL,
            "commercial": TemplateType.COMMERCIAL,
            "professional": TemplateType.PROFESSIONAL,
            "simple": TemplateType.SIMPLE,
        }
        template_type = template_type_map.get(request.template_type, TemplateType.STANDARD)
        template = get_template(template_type)

        # 创建带样式的文档导出器
        exporter = StyledDocumentExporter(template=template)
        doc = exporter.create_document()

        # 添加标题
        exporter.add_title(doc, request.title, level=0)

        # 添加正文内容（支持HTML表格）
        exporter.add_html_content(doc, request.content)

        # 导出
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        filename = f"{request.title}.docx"

        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
    except Exception as e:
        logger.error(f"Word export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ai/export/templates")
async def list_available_templates():
    """列出可用模板"""
    if not TEMPLATES_AVAILABLE:
        return {"templates": [], "error": "模板系统不可用"}

    templates = list_templates()
    return {
        "templates": [
            {
                "id": t.template_type.value,
                "name": t.name,
                "description": t.description,
                "theme_color": t.title_color.hex_str if hasattr(t.title_color, 'hex_str') else str(t.title_color)
            }
            for t in templates
        ]
    }


# 导出router
export_word_router = router