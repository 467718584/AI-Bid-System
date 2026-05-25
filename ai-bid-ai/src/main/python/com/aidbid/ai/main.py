"""FastAPI主应用 - AI投标智能服务"""
import logging
import hashlib
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import io

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import config
from .llm_gateway import LLMGateway, LLMFactory
from .prompts import (
    TECHNICAL_BID_PROMPT, CREDIT_BID_PROMPT, BID_REWRITE_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT, COMPLIANCE_CHECK_PROMPT,
    DOCUMENT_SUMMARY_PROMPT, build_prompt
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# 请求/响应模型
# ============================================================

class DocumentParseRequest(BaseModel):
    """文档解析请求"""
    content: Optional[str] = None
    file_url: Optional[str] = None
    parse_options: Dict[str, Any] = Field(default_factory=dict)


class DocumentParseResponse(BaseModel):
    """文档解析响应"""
    success: bool
    content: str
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class BidGenerateRequest(BaseModel):
    """标书生成请求"""
    bid_type: str = Field(..., description="标书类型: technical/credit")
    project_name: str
    procurement_unit: str
    deadline: Optional[str] = None
    bidding_requirements: str
    qualifications: str
    scoring_criteria: Optional[str] = None
    case_studies: Optional[str] = None
    financial_info: Optional[str] = None
    honors: Optional[str] = None
    reference_docs: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    use_rag: bool = Field(default=True, description="是否使用RAG增强")


class BidGenerateResponse(BaseModel):
    """标书生成响应"""
    success: bool
    bid_type: str
    content: str
    word_count: int
    sections: List[str]
    generated_at: str


class BidRewriteRequest(BaseModel):
    """标书改写请求"""
    original_content: str
    rewrite_requirements: str
    target_style: str = Field(default="professional")


class BidRewriteResponse(BaseModel):
    """标书改写响应"""
    success: bool
    original_length: int
    rewritten_length: int
    content: str
    changes: List[Dict[str, str]] = Field(default_factory=list)


class ComplianceCheckRequest(BaseModel):
    """合规检测请求"""
    bid_document: str
    bidding_requirements: str
    legal_requirements: Optional[str] = None


class ComplianceIssue(BaseModel):
    """合规问题"""
    severity: str
    category: str
    description: str
    location: str
    suggestion: str


class ComplianceCheckResponse(BaseModel):
    """合规检测响应"""
    success: bool
    score: int
    total_issues: int
    severe_count: int
    general_count: int
    hint_count: int
    issues: List[ComplianceIssue]


class CompetitorAnalysisRequest(BaseModel):
    """竞品分析请求"""
    bid_content: str
    bidding_requirements: str
    scoring_criteria: Optional[str] = None


class CompetitorAnalysisResponse(BaseModel):
    """竞品分析响应"""
    success: bool
    advantages: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    strategy: str


# ============================================================
# 文档解析服务
# ============================================================

class DocumentParser:
    """文档解析服务"""

    def __init__(self):
        self.llm_gateway = LLMFactory.get_gateway()

    async def parse_document(self, file: UploadFile, options: Dict[str, Any] = None) -> DocumentParseResponse:
        """解析上传的文档（PDF/DOCX/TXT）"""
        try:
            content = await self._read_file(file)
            return await self._parse_content(content, file.filename, options or {})

        except Exception as e:
            logger.error(f"文档解析失败: {e}")
            raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")

    async def _read_file(self, file: UploadFile) -> str:
        """读取文件内容"""
        content = await file.read()

        if file.filename.endswith('.pdf'):
            return self._parse_pdf(content)
        elif file.filename.endswith('.docx'):
            return self._parse_docx(content)
        elif file.filename.endswith('.txt'):
            return content.decode('utf-8')
        else:
            return content.decode('utf-8', errors='ignore')

    def _parse_pdf(self, content: bytes) -> str:
        """解析PDF"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.io.BytesIO(content) as pdf:
                with pdfplumber.open(pdf) as pdf_reader:
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            return content.decode('utf-8', errors='ignore')

    def _parse_docx(self, content: bytes) -> str:
        """解析DOCX"""
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"DOCX解析失败: {e}")
            return content.decode('utf-8', errors='ignore')

    async def _parse_content(self, content: str, filename: str, options: Dict[str, Any]) -> DocumentParseResponse:
        """解析文本内容"""
        # 提取元数据
        metadata = {
            "filename": filename,
            "length": len(content),
            "parsed_at": datetime.now().isoformat()
        }

        # 简单清理
        clean_content = self._clean_text(content)

        # 生成摘要
        summary = None
        if options.get("generate_summary", True) and len(clean_content) > 500:
            summary = await self._generate_summary(clean_content[:5000], options)

        # 提取结构化数据
        extracted_data = self._extract_structured_data(clean_content, filename)

        return DocumentParseResponse(
            success=True,
            content=clean_content,
            summary=summary,
            metadata=metadata,
            extracted_data=extracted_data
        )

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        return text.strip()

    async def _generate_summary(self, content: str, options: Dict[str, Any]) -> str:
        """生成摘要"""
        try:
            prompt = f"请用3-5句话总结以下文档的主要内容：\n\n{content[:3000]}"
            return self.llm_gateway.chat(prompt)
        except Exception as e:
            logger.warning(f"摘要生成失败: {e}")
            return None

    def _extract_structured_data(self, content: str, filename: str) -> Dict[str, Any]:
        """提取结构化数据"""
        data = {
            "filename": filename,
            "has_tables": False,
            "has_images": False,
            "key_terms": []
        }

        # 提取关键词
        keywords = ["投标", "报价", "技术方案", "资质", "工期", "服务"]
        for keyword in keywords:
            if keyword in content:
                data["key_terms"].append(keyword)

        return data


# ============================================================
# 标书生成服务
# ============================================================

class BidGenerator:
    """标书生成服务"""

    def __init__(self):
        self.llm_gateway = LLMFactory.get_gateway()
        self._rag_client = None

    def _get_rag_context(self, query: str, kb_id: str, top_k: int = 5) -> str:
        """从知识库获取RAG上下文"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"{config.KNOWLEDGE_SERVICE_URL}/api/v1/retrieve"
                payload = {
                    "query": query,
                    "knowledge_base_id": kb_id,
                    "top_k": top_k
                }
                async with session.post(url, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("results"):
                            contexts = []
                            for r in result["results"]:
                                contexts.append(f"- {r.get('content', '')[:500]}")
                            return "\n".join(contexts)
        except Exception as e:
            logger.warning(f"RAG上下文获取失败: {e}")
        return "（知识库无可用参考信息）"

    async def generate_technical_bid(self, request: BidGenerateRequest) -> BidGenerateResponse:
        """生成技术标"""
        # 获取RAG上下文
        reference_docs = request.reference_docs or ""
        if request.use_rag and request.knowledge_base_id:
            rag_context = self._get_rag_context(
                f"{request.project_name} {request.bidding_requirements}",
                request.knowledge_base_id
            )
            reference_docs = f"{reference_docs}\n\n## 知识库参考：\n{rag_context}"

        # 构建Prompt
        prompt = build_prompt(
            TECHNICAL_BID_PROMPT,
            project_name=request.project_name,
            procurement_unit=request.procurement_unit,
            deadline=request.deadline or "未指定",
            bidding_requirements=request.bidding_requirements,
            qualifications=request.qualifications,
            scoring_criteria=request.scoring_criteria or "参考招标文件",
            reference_docs=reference_docs or "（无参考文档）"
        )

        # 调用LLM生成
        content = self.llm_gateway.chat(prompt, max_tokens=config.MAX_TOKENS)

        # 提取章节
        sections = self._extract_sections(content)

        return BidGenerateResponse(
            success=True,
            bid_type="technical",
            content=content,
            word_count=len(content),
            sections=sections,
            generated_at=datetime.now().isoformat()
        )

    async def generate_credit_bid(self, request: BidGenerateRequest) -> BidGenerateResponse:
        """生成资信标"""
        # 构建Prompt
        prompt = build_prompt(
            CREDIT_BID_PROMPT,
            project_name=request.project_name,
            procurement_unit=request.procurement_unit,
            qualifications=request.qualifications,
            case_studies=request.case_studies or "（无业绩案例）",
            financial_info=request.financial_info or "（无财务信息）",
            honors_and_certifications=request.honors or "（无荣誉资质）"
        )

        # 调用LLM生成
        content = self.llm_gateway.chat(prompt, max_tokens=config.MAX_TOKENS)

        # 提取章节
        sections = self._extract_sections(content)

        return BidGenerateResponse(
            success=True,
            bid_type="credit",
            content=content,
            word_count=len(content),
            sections=sections,
            generated_at=datetime.now().isoformat()
        )

    def _extract_sections(self, content: str) -> List[str]:
        """提取章节标题"""
        sections = []
        # 匹配Markdown标题
        for line in content.split('\n'):
            line = line.strip()
            if re.match(r'^#{1,3}\s+.+', line):
                sections.append(line.lstrip('#').strip())
        return sections


# ============================================================
# 标书改写服务
# ============================================================

class Rewriter:
    """标书改写服务"""

    def __init__(self):
        self.llm_gateway = LLMFactory.get_gateway()

    async def rewrite(self, request: BidRewriteRequest) -> BidRewriteResponse:
        """改写标书"""
        original_length = len(request.original_content)

        prompt = build_prompt(
            BID_REWRITE_PROMPT,
            original_content=request.original_content,
            rewrite_requirements=request.rewrite_requirements,
            target_style=request.target_style
        )

        content = self.llm_gateway.chat(prompt, max_tokens=config.MAX_TOKENS)
        rewritten_length = len(content)

        # 分析变更
        changes = self._analyze_changes(request.original_content, content)

        return BidRewriteResponse(
            success=True,
            original_length=original_length,
            rewritten_length=rewritten_length,
            content=content,
            changes=changes
        )

    def _analyze_changes(self, original: str, rewritten: str) -> List[Dict[str, str]]:
        """分析改写变更"""
        changes = []

        # 简单对比分析
        orig_words = set(original.split())
        new_words = set(rewritten.split())

        added = new_words - orig_words
        removed = orig_words - new_words

        if added:
            changes.append({
                "type": "addition",
                "count": len(added),
                "description": f"新增词汇 {len(added)} 个"
            })

        if removed:
            changes.append({
                "type": "removal",
                "count": len(removed),
                "description": f"移除词汇 {len(removed)} 个"
            })

        return changes


# ============================================================
# 合规检测服务
# ============================================================

class ComplianceChecker:
    """合规检测服务"""

    def __init__(self):
        self.llm_gateway = LLMFactory.get_gateway()

    async def check(self, request: ComplianceCheckRequest) -> ComplianceCheckResponse:
        """检测合规性"""
        prompt = build_prompt(
            COMPLIANCE_CHECK_PROMPT,
            bid_document=request.bid_document,
            bidding_requirements=request.bidding_requirements,
            legal_requirements=request.legal_requirements or "适用招投标相关法律法规"
        )

        result = self.llm_gateway.chat(prompt, max_tokens=config.MAX_TOKENS)

        # 解析结果
        try:
            # 尝试解析JSON格式结果
            if '{' in result and '}' in result:
                json_str = result[result.find('{'):result.rfind('}')+1]
                parsed = json.loads(json_str)
                return self._build_response_from_parsed(parsed)
        except:
            pass

        # 降级处理：返回原始文本分析
        return self._build_response_from_text(result, request.bid_document)

    def _build_response_from_parsed(self, parsed: Dict[str, Any]) -> ComplianceCheckResponse:
        """从解析结果构建响应"""
        issues = []
        for item in parsed.get("issues", []):
            issues.append(ComplianceIssue(
                severity=item.get("severity", "hint"),
                category=item.get("category", "general"),
                description=item.get("description", ""),
                location=item.get("location", "unknown"),
                suggestion=item.get("suggestion", "")
            ))

        return ComplianceCheckResponse(
            success=True,
            score=parsed.get("score", 80),
            total_issues=len(issues),
            severe_count=len([i for i in issues if i.severity == "severe"]),
            general_count=len([i for i in issues if i.severity == "general"]),
            hint_count=len([i for i in issues if i.severity == "hint"]),
            issues=issues
        )

    def _build_response_from_text(self, result: str, original: str) -> ComplianceCheckResponse:
        """从文本构建响应"""
        # 基础合规检查
        issues = []
        score = 100

        # 检查基本要求
        if len(original) < 500:
            issues.append(ComplianceIssue(
                severity="severe",
                category="content",
                description="标书内容过少",
                location="全文",
                suggestion="建议增加详细内容，至少500字以上"
            ))
            score -= 30

        # 检查关键词
        required_terms = ["投标", "报价", "质量"]
        missing_terms = [t for t in required_terms if t not in original]
        if missing_terms:
            issues.append(ComplianceIssue(
                severity="general",
                category="content",
                description=f"缺少必要关键词: {', '.join(missing_terms)}",
                location="全文",
                suggestion="确保包含所有必要关键词"
            ))
            score -= 10

        return ComplianceCheckResponse(
            success=True,
            score=max(0, score),
            total_issues=len(issues),
            severe_count=len([i for i in issues if i.severity == "severe"]),
            general_count=len([i for i in issues if i.severity == "general"]),
            hint_count=len([i for i in issues if i.severity == "hint"]),
            issues=issues
        )


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
    title="AI投标智能服务",
    description="提供投标文档智能生成、解析、改写、合规检测等能力",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
document_parser = DocumentParser()
bid_generator = BidGenerator()
rewriter = Rewriter()
compliance_checker = ComplianceChecker()


# ============================================================
# 文档解析接口
# ============================================================

@app.post("/api/v1/parse/document", response_model=DocumentParseResponse)
async def parse_document(
    file: UploadFile = File(...),
    generate_summary: bool = True,
    extract_tables: bool = False
):
    """解析投标文档（PDF/DOCX/TXT）"""
    options = {
        "generate_summary": generate_summary,
        "extract_tables": extract_tables
    }
    return await document_parser.parse_document(file, options)


@app.post("/api/v1/parse/text", response_model=DocumentParseResponse)
async def parse_text(request: DocumentParseRequest):
    """解析文本内容"""
    if not request.content and not request.file_url:
        raise HTTPException(status_code=400, detail="content或file_url必须提供其一")

    content = request.content
    if request.file_url:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(request.file_url) as resp:
                if resp.status == 200:
                    content = await resp.text()

    return await document_parser._parse_content(
        content, "text", request.parse_options
    )


# ============================================================
# 标书生成接口
# ============================================================

@app.post("/api/v1/bid/generate", response_model=BidGenerateResponse)
async def generate_bid(request: BidGenerateRequest):
    """生成投标文件"""
    if request.bid_type == "technical":
        return await bid_generator.generate_technical_bid(request)
    elif request.bid_type == "credit":
        return await bid_generator.generate_credit_bid(request)
    else:
        raise HTTPException(status_code=400, detail="不支持的标书类型")


# ============================================================
# 标书改写接口
# ============================================================

@app.post("/api/v1/bid/rewrite", response_model=BidRewriteResponse)
async def rewrite_bid(request: BidRewriteRequest):
    """改写投标文件"""
    return await rewriter.rewrite(request)


# ============================================================
# 合规检测接口
# ============================================================

@app.post("/api/v1/bid/compliance", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """检测标书合规性"""
    return await compliance_checker.check(request)


# ============================================================
# 竞品分析接口
# ============================================================

@app.post("/api/v1/bid/competitor-analysis", response_model=CompetitorAnalysisResponse)
async def analyze_competitor(request: CompetitorAnalysisRequest):
    """竞品分析"""
    prompt = build_prompt(
        COMPETITOR_ANALYSIS_PROMPT,
        bid_content=request.bid_content,
        bidding_requirements=request.bidding_requirements,
        scoring_criteria=request.scoring_criteria or "参考招标文件"
    )

    result = LLMGateway().chat(prompt)

    # 简单解析（生产应使用更可靠的解析方法）
    return CompetitorAnalysisResponse(
        success=True,
        advantages=["差异化优势待分析"],
        weaknesses=["不足之处待分析"],
        suggestions=["优化建议待分析"],
        strategy=result[:500] if len(result) > 500 else result
    )


# ============================================================
# 健康检查接口
# ============================================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-bid-ai",
        "version": "1.0.0",
        "llm_provider": config.LLM_PROVIDER
    }


if __name__ == "__main__":
    uvicorn.run(
        "com.aidbid.ai.main:app",
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
        reload=True
    )