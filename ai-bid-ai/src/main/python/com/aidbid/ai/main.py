"""FastAPI主应用 - AI投标智能服务"""
import logging
import json
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .llm_gateway import LLMGateway, LLMFactory
from .document_parser import DocumentParser, ParsedDocument
from .document_exporter import DocumentExporter
from .prompts import (
    TECHNICAL_BID_OUTLINE_PROMPT,
    TECHNICAL_BID_CONTENT_PROMPT,
    BID_DOCUMENT_PARSE_PROMPT,
    PARAPHRASE_PROMPT,
    COMPLIANCE_CHECK_PROMPT,
    TECHNICAL_BID_PROMPT, CREDIT_BID_PROMPT, BID_REWRITE_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT, build_prompt
)

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_wrapper = AsyncLLMWrapper(provider="minimax")
document_parser = DocumentParser()
document_exporter = DocumentExporter()


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

        return {"code": 200, "data": {"content": content}}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
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
# 启动服务
# ============================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8087)