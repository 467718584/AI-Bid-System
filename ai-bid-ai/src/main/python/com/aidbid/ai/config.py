"""配置管理模块"""
import os
from typing import Optional


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

    # 知识库服务配置
    KNOWLEDGE_SERVICE_URL: str = os.getenv("KNOWLEDGE_SERVICE_URL", "http://knowledge:8086")

    # 服务配置
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8087"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 标书生成配置
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))


config = Config()