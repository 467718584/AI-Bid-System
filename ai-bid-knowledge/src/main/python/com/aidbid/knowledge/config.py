"""配置管理模块"""
import os
import httpx
import asyncio
import logging
import hashlib
import math
from typing import Optional, List

logger = logging.getLogger(__name__)


class Config:
    """配置管理类，从环境变量读取配置"""

    # LLM 配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "minimax")
    MINIMAX_API_KEY: Optional[str] = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL: str = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
    MINIMAX_MODEL: str = os.getenv("MINIMAX_MODEL", "abab6-chat")

    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-turbo")

    # 向量数据库配置
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))

    # Embedding 模型配置
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "embo01")
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    USE_LOCAL_EMBEDDING: bool = os.getenv("USE_LOCAL_EMBEDDING", "false").lower() == "true"

    # 服务配置
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8086"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()


class SimpleEmbeddingModel:
    """简单的基于词频的嵌入模型（不需要网络）"""

    def __init__(self, dim: int = 384):
        self.dim = dim
        # 常用词表
        self.vocab = [
            "的", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看",
            "好", "自己", "这", "中", "大", "来", "为", "得", "之", "以", "于", "从",
            "人工智能", "机器", "学习", "深度", "网络", "神经", "模型", "数据", "算法",
            "系统", "技术", "方法", "应用", "招标", "投标", "采购", "工程", "项目",
            "建设", "施工", "监理", "设计", "咨询", "服务", "供应", "资格", "审查",
            "评审", "评分", "中标", "合同", "文件", "公告", "招标人", "投标人",
            "公开", "透明", "公平", "公正", "竞争", "市场", "价格", "质量", "工期"
        ]

    def _hash(self, text: str) -> int:
        """生成哈希值"""
        h = hashlib.md5(text.encode('utf-8')).hexdigest()
        return int(h[:8], 16)

    def encode(self, texts: List[str]) -> List[List[float]]:
        """将文本编码为向量"""
        vectors = []
        for text in texts:
            vec = self._text_to_vector(text)
            vectors.append(vec)
        return vectors

    def _text_to_vector(self, text: str) -> List[float]:
        """将文本转换为向量"""
        vector = [0.0] * self.dim

        # 分词（简单按字符）
        words = []
        current = ""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                if current:
                    words.append(current)
                    current = ""
                words.append(char)
            elif char.isspace() or char in ',，。.。!！?？':
                if current:
                    words.append(current)
                    current = ""
            else:
                current += char.lower()

        if current:
            words.append(current)

        # 词频统计
        word_freq = {}
        for w in words:
            if len(w) >= 1:
                word_freq[w] = word_freq.get(w, 0) + 1

        # 更新向量
        for word, freq in word_freq.items():
            hash_idx = self._hash(word) % self.dim
            vector[hash_idx] = freq * 0.1

        # 归一化
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector

    def get_sentence_embedding_dimension(self) -> int:
        return self.dim


# 全局简单嵌入模型
_simple_model: Optional[SimpleEmbeddingModel] = None


def get_simple_embedding_model() -> SimpleEmbeddingModel:
    """获取简单嵌入模型"""
    global _simple_model
    if _simple_model is None:
        _simple_model = SimpleEmbeddingModel()
        logger.info("Simple embedding model initialized")
    return _simple_model


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """获取文本嵌入向量，优先MiniMax API，失败则使用简单模型"""
    api_key = config.MINIMAX_API_KEY

    # 如果配置了使用本地模型，直接使用
    if config.USE_LOCAL_EMBEDDING or not api_key:
        return _simple_embed_texts(texts)

    url = f"{config.MINIMAX_BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "embo01",
        "texts": texts,
        "type": "dbqa"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            vectors = result.get("vectors", [])
            if vectors:
                return [v.get("embedding", v) if isinstance(v, dict) else v for v in vectors]

            # API返回错误，检查是否是余额不足
            error_msg = result.get("base_resp", {}).get("status_msg", "")
            if "insufficient" in error_msg.lower():
                logger.warning(f"MiniMax API insufficient balance, using simple fallback")
                return _simple_embed_texts(texts)

            logger.error(f"MiniMax API error: {error_msg}")
            return _simple_embed_texts(texts)

    except Exception as e:
        logger.warning(f"MiniMax embedding failed: {e}, using simple fallback")
        return _simple_embed_texts(texts)


def _simple_embed_texts(texts: List[str]) -> List[List[float]]:
    """使用简单模型进行嵌入"""
    model = get_simple_embedding_model()
    return model.encode(texts)


async def embed_text(text: str) -> List[float]:
    """获取单个文本的嵌入向量"""
    embeddings = await embed_texts([text])
    if embeddings:
        return embeddings[0]
    raise RuntimeError("Failed to generate embedding")