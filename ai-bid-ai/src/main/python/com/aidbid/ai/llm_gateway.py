"""LLM统一网关，支持多后端切换"""
import os
import logging
from typing import Optional, Dict, Any, List
import httpx

from .config import config

logger = logging.getLogger(__name__)


class LLMGateway:
    """LLM统一网关"""

    def __init__(self, provider: str = "minimax"):
        self.provider = provider
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.model = self._get_model()

    def _get_api_key(self) -> str:
        if self.provider == "minimax":
            return config.MINIMAX_API_KEY or os.getenv("MINIMAX_API_KEY") or "sk-cp-ZpS3_cdjkZ282Ux41yYKpAT6uOmYqQ6L3f7rqJ81HFLsVcLC1xeJ5UaUgu5p3BzRqdDVYtTLDxtMuLKZfyiqd_eYuPrHaJzPMRA_BIevVROCws1zs0JsAH4"
        elif self.provider == "deepseek":
            return config.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", "")
        elif self.provider == "qwen":
            return config.QWEN_API_KEY or os.getenv("QWEN_API_KEY", "")
        return ""

    def _get_base_url(self) -> str:
        if self.provider == "minimax":
            return config.MINIMAX_BASE_URL
        elif self.provider == "deepseek":
            return config.DEEPSEEK_BASE_URL
        elif self.provider == "qwen":
            return config.QWEN_BASE_URL
        return "https://api.minimax.chat/v1"

    def _get_model(self) -> str:
        if self.provider == "minimax":
            return config.MINIMAX_MODEL
        elif self.provider == "deepseek":
            return config.DEEPSEEK_MODEL
        elif self.provider == "qwen":
            return config.QWEN_MODEL
        return "abab6-chat"

    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 8192)
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """获取文本嵌入向量"""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "embo01",
            "input": texts
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return [item["embedding"] for item in result["data"]]


class LLMFactory:
    """LLM工厂类"""

    _instances: Dict[str, LLMGateway] = {}

    @classmethod
    def get_gateway(cls, provider: Optional[str] = None) -> LLMGateway:
        """获取指定provider的LLM网关实例"""
        key = provider or "minimax"
        if key not in cls._instances:
            cls._instances[key] = LLMGateway(provider=key)
        return cls._instances[key]

    @classmethod
    def create_minimax_gateway(cls) -> LLMGateway:
        """创建Minimax网关"""
        return cls.get_gateway("minimax")

    @classmethod
    def create_deepseek_gateway(cls) -> LLMGateway:
        """创建DeepSeek网关"""
        return cls.get_gateway("deepseek")

    @classmethod
    def create_qwen_gateway(cls) -> LLMGateway:
        """创建Qwen网关"""
        return cls.get_gateway("qwen")