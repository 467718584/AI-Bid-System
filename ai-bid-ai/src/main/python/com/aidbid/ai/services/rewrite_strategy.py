"""改写策略服务 - 支持多种改写策略和风格转换"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RewriteStrategy(Enum):
    """改写策略枚举"""
    CONSERVATIVE = "conservative"       # 保守改写 - 小幅调整
    MODERATE = "moderate"               # 中度改写
    AGGRESSIVE = "aggressive"           # 激进改写 - 大幅度改写
    STYLE_TRANSFER = "style_transfer"   # 风格转换
    LENGTH_ADJUST = "length_adjust"     # 长度调整


class RewriteStyle(Enum):
    """改写风格枚举"""
    PROFESSIONAL = "professional"       # 专业正式
    TECHNICAL = "technical"             # 技术详细
    CONCISE = "concise"                 # 简洁明了
    ACADEMIC = "academic"               # 学术严谨
    BUSINESS = "business"               # 商业推广
    NATURAL = "natural"                 # 自然流畅


@dataclass
class RewriteRequest:
    """改写请求"""
    content: str
    strategy: RewriteStrategy = RewriteStrategy.MODERATE
    style: Optional[RewriteStyle] = None
    target_length_ratio: float = 1.0    # 目标长度比例
    preserve_keywords: List[str] = field(default_factory=list)
    language: str = "chinese"           # chinese / english
    temperature: float = 0.7


@dataclass
class RewriteResult:
    """改写结果"""
    content: str
    strategy: str
    style: Optional[str]
    original_length: int
    rewritten_length: int
    changes_summary: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Prompt 模板
# ============================================================

CONSERVATIVE_REWRITE_PROMPT = """你是一位专业的标书改写专家。请对以下内容进行保守改写。

## 原文
{content}

## 改写要求
1. 仅对句式和表达方式进行小幅调整
2. 保持原文结构基本不变
3. 保留所有专业术语和数据
4. 提升语言的流畅性和专业性
5. 保持关键词: {preserve_keywords}

## 输出要求
直接输出改写后的内容，不要添加解释。"""

MODERATE_REWRITE_PROMPT = """你是一位专业的标书改写专家。请对以下内容进行中度改写。

## 原文
{content}

## 改写要求
1. 对句子结构进行重新组织
2. 替换同义词和专业表达
3. 优化段落逻辑顺序
4. 保持核心信息不变
5. 保持关键词: {preserve_keywords}

## 输出要求
直接输出改写后的内容，不要添加解释。"""

AGGRESSIVE_REWRITE_PROMPT = """你是一位专业的标书改写专家。请对以下内容进行大幅度改写。

## 原文
{content}

## 改写要求
1. 完全重新组织内容和结构
2. 使用全新的表达方式和句式
3. 扩展细节描述，增加说服力
4. 保持核心信息准确
5. 提升原创性和专业性
6. 保持关键词: {preserve_keywords}

## 输出要求
直接输出改写后的内容，不要添加解释。"""

STYLE_TRANSFER_PROMPT = """你是一位专业的标书改写专家。请将以下内容转换为指定的风格。

## 原文
{content}

## 目标风格
{style_description}

## 风格要求
1. 完全按照目标风格重写
2. 保持原文的核心信息和数据
3. 调整语气、用词、句式以匹配目标风格
4. 保持专业术语的准确性
5. 保持关键词: {preserve_keywords}

## 输出要求
直接输出改写后的内容，不要添加解释。"""

LENGTH_ADJUST_PROMPT = """你是一位专业的标书改写专家。请调整以下内容的长度。

## 原文
{content}

## 目标
将内容调整为目标长度的 {ratio} 倍
原文长度: {original_length} 字

## 改写要求
1. 按照目标比例扩展或压缩内容
2. 保持核心信息完整
3. 增加细节描述（扩展时）
4. 精简冗余表达（压缩时）
5. 保持关键词: {preserve_keywords}

## 输出要求
直接输出改写后的内容，不要添加解释。"""

MULTI_VERSION_PROMPT = """你是一位专业的标书改写专家。请根据同一原文生成多个不同风格的版本。

## 原文
{content}

## 需要生成的版本数量
{version_count} 个

## 各版本要求
{version_requirements}

## 共同要求
1. 每个版本都要保持原文的核心信息
2. 各版本之间要有明显差异（用词、句式、侧重点）
3. 都保持专业标书的语言规范
4. 保持关键词: {preserve_keywords}

## 输出格式
请以JSON格式输出，格式如下：
{{
  "versions": [
    {{
      "version_id": 1,
      "version_name": "版本1名称",
      "description": "版本描述",
      "content": "版本内容"
    }},
    ...
  ]
}}"""


# ============================================================
# 改写策略服务
# ============================================================

class RewriteStrategyService:
    """改写策略服务"""

    def __init__(self, llm_wrapper):
        """
        初始化改写策略服务

        Args:
            llm_wrapper: LLM异步调用包装器
        """
        self.llm = llm_wrapper
        self._style_descriptions = {
            RewriteStyle.PROFESSIONAL: "专业正式：使用规范、严谨的专业语言，适合正式投标文件",
            RewriteStyle.TECHNICAL: "技术详细：深入技术细节，使用专业术语，适合技术标书",
            RewriteStyle.CONCISE: "简洁明了：言简意赅，重点突出，适合概要说明",
            RewriteStyle.ACADEMIC: "学术严谨：逻辑严密，论证充分，适合研究报告",
            RewriteStyle.BUSINESS: "商业推广：突出优势和价值，适合商务标书",
            RewriteStyle.NATURAL: "自然流畅：语言自然，易于阅读，适合通用场景"
        }

    def _get_style_description(self, style: RewriteStyle) -> str:
        """获取风格描述"""
        return self._style_descriptions.get(style, "专业规范")

    def _estimate_time(self, content: str, version_count: int = 1) -> float:
        """估算改写耗时（秒）"""
        # 基础耗时 + 按字数计费（约100字/秒的LLM处理速度）
        base_time = 2.0
        word_count = len(content) / 2  # 中文字符约0.5词
        per_version = base_time + word_count / 100
        return per_version * version_count

    def _build_prompt(self, request: RewriteRequest) -> str:
        """构建改写Prompt"""
        preserve_keywords = ", ".join(request.preserve_keywords) if request.preserve_keywords else "无"

        if request.strategy == RewriteStrategy.CONSERVATIVE:
            return CONSERVATIVE_REWRITE_PROMPT.format(
                content=request.content,
                preserve_keywords=preserve_keywords
            )
        elif request.strategy == RewriteStrategy.MODERATE:
            return MODERATE_REWRITE_PROMPT.format(
                content=request.content,
                preserve_keywords=preserve_keywords
            )
        elif request.strategy == RewriteStrategy.AGGRESSIVE:
            return AGGRESSIVE_REWRITE_PROMPT.format(
                content=request.content,
                preserve_keywords=preserve_keywords
            )
        elif request.strategy == RewriteStrategy.STYLE_TRANSFER:
            style_desc = self._get_style_description(request.style) if request.style else "专业规范"
            return STYLE_TRANSFER_PROMPT.format(
                content=request.content,
                style_description=style_desc,
                preserve_keywords=preserve_keywords
            )
        elif request.strategy == RewriteStrategy.LENGTH_ADJUST:
            original_len = len(request.content)
            target_len = int(original_len * request.target_length_ratio)
            return LENGTH_ADJUST_PROMPT.format(
                content=request.content,
                ratio=request.target_length_ratio,
                original_length=original_len,
                preserve_keywords=preserve_keywords
            )
        else:
            return MODERATE_REWRITE_PROMPT.format(
                content=request.content,
                preserve_keywords=preserve_keywords
            )

    async def conservative_rewrite(self, content: str, **kwargs) -> RewriteResult:
        """保守改写 - 小幅调整句式和表达"""
        request = RewriteRequest(
            content=content,
            strategy=RewriteStrategy.CONSERVATIVE,
            preserve_keywords=kwargs.get("preserve_keywords", []),
            language=kwargs.get("language", "chinese")
        )
        return await self.rewrite(request)

    async def aggressive_rewrite(self, content: str, **kwargs) -> RewriteResult:
        """激进改写 - 大幅度改写内容和结构"""
        request = RewriteRequest(
            content=content,
            strategy=RewriteStrategy.AGGRESSIVE,
            preserve_keywords=kwargs.get("preserve_keywords", []),
            language=kwargs.get("language", "chinese")
        )
        return await self.rewrite(request)

    async def style_transfer(self, content: str, style: RewriteStyle, **kwargs) -> RewriteResult:
        """风格转换 - 转换为指定风格"""
        request = RewriteRequest(
            content=content,
            strategy=RewriteStrategy.STYLE_TRANSFER,
            style=style,
            preserve_keywords=kwargs.get("preserve_keywords", []),
            language=kwargs.get("language", "chinese")
        )
        return await self.rewrite(request)

    async def length_adjust(self, content: str, ratio: float, **kwargs) -> RewriteResult:
        """长度调整 - 按比例扩展或压缩内容"""
        request = RewriteRequest(
            content=content,
            strategy=RewriteStrategy.LENGTH_ADJUST,
            target_length_ratio=ratio,
            preserve_keywords=kwargs.get("preserve_keywords", []),
            language=kwargs.get("language", "chinese")
        )
        return await self.rewrite(request)

    async def rewrite(self, request: RewriteRequest) -> RewriteResult:
        """执行改写"""
        try:
            prompt = self._build_prompt(request)
            messages = [{"role": "user", "content": prompt}]

            rewritten = await self.llm.chat(
                messages,
                temperature=request.temperature
            )

            # 清理结果
            rewritten = self._clean_result(rewritten)

            return RewriteResult(
                content=rewritten,
                strategy=request.strategy.value,
                style=request.style.value if request.style else None,
                original_length=len(request.content),
                rewritten_length=len(rewritten),
                changes_summary=self._analyze_changes(request.content, rewritten)
            )
        except Exception as e:
            logger.error(f"Rewrite failed: {e}")
            raise

    async def multi_version_rewrite(
        self,
        content: str,
        version_count: int = 3,
        styles: Optional[List[RewriteStyle]] = None,
        **kwargs
    ) -> List[RewriteResult]:
        """多版本改写 - 生成多个不同风格的版本"""
        if styles is None:
            # 默认使用不同的风格组合
            default_styles = [
                RewriteStyle.PROFESSIONAL,
                RewriteStyle.TECHNICAL,
                RewriteStyle.BUSINESS,
                RewriteStyle.CONCISE,
                RewriteStyle.NATURAL,
                RewriteStyle.ACADEMIC
            ]
            styles = default_styles[:version_count]

        preserve_keywords = kwargs.get("preserve_keywords", [])
        preserve_str = ", ".join(preserve_keywords) if preserve_keywords else "无"

        # 构建各版本要求
        version_requirements = []
        for i, style in enumerate(styles[:version_count]):
            style_desc = self._get_style_description(style)
            version_requirements.append(
                f"版本{i+1}: {style_desc}"
            )

        prompt = MULTI_VERSION_PROMPT.format(
            content=content,
            version_count=version_count,
            version_requirements="\n".join(version_requirements),
            preserve_keywords=preserve_str
        )

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm.chat(messages)

            # 解析JSON响应
            import json
            result_data = json.loads(response)

            results = []
            for v in result_data.get("versions", []):
                version_content = self._clean_result(v.get("content", ""))
                results.append(RewriteResult(
                    content=version_content,
                    strategy="multi_version",
                    style=v.get("version_name"),
                    original_length=len(content),
                    rewritten_length=len(version_content),
                    changes_summary={
                        "version_id": v.get("version_id"),
                        "description": v.get("description", "")
                    }
                ))

            return results
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试逐个生成版本
            logger.warning("JSON parse failed, generating versions one by one")
            return await self._generate_versions_individually(
                content, version_count, styles[:version_count], **kwargs
            )
        except Exception as e:
            logger.error(f"Multi-version rewrite failed: {e}")
            raise

    async def _generate_versions_individually(
        self,
        content: str,
        version_count: int,
        styles: List[RewriteStyle],
        **kwargs
    ) -> List[RewriteResult]:
        """逐个生成版本（当批量生成失败时）"""
        results = []
        for i, style in enumerate(styles[:version_count]):
            request = RewriteRequest(
                content=content,
                strategy=RewriteStrategy.STYLE_TRANSFER,
                style=style,
                preserve_keywords=kwargs.get("preserve_keywords", []),
                language=kwargs.get("language", "chinese")
            )
            result = await self.rewrite(request)
            result.changes_summary["version_id"] = i + 1
            result.changes_summary["description"] = self._get_style_description(style)
            results.append(result)

        return results

    def _clean_result(self, content: str) -> str:
        """清理改写结果"""
        # 移除可能的引号包裹
        content = content.strip()
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        if content.startswith('```') and content.endswith('```'):
            # 移除markdown代码块
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)
        return content.strip()

    def _analyze_changes(self, original: str, rewritten: str) -> Dict[str, Any]:
        """分析改写前后的变化"""
        original_words = len(original)
        rewritten_words = len(rewritten)
        ratio = rewritten_words / original_words if original_words > 0 else 1.0

        # 简单统计句号数量变化
        original_sentences = original.count('。') + original.count('.')
        rewritten_sentences = rewritten.count('。') + rewritten.count('.')

        return {
            "length_ratio": round(ratio, 2),
            "original_chars": original_words,
            "rewritten_chars": rewritten_words,
            "sentence_count_change": rewritten_sentences - original_sentences,
            "expansion": "expanded" if ratio > 1.1 else "condensed" if ratio < 0.9 else "similar"
        }


# ============================================================
# 便捷函数
# ============================================================

def create_rewrite_service(llm_wrapper) -> RewriteStrategyService:
    """创建改写策略服务实例"""
    return RewriteStrategyService(llm_wrapper)