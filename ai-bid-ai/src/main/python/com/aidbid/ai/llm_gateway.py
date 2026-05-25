"""LLM统一网关，支持多后端切换"""
import os
import logging
from typing import Optional, Dict, Any, List
from .config import config

logger = logging.getLogger(__name__)


class LLMGateway:
    """LLM统一网关，支持Minimax/DeepSeek/Qwen"""

    PROVIDER_CONFIGS = {
        "minimax": {
            "base_url": "https://api.minimax.chat/v1",
            "model": "abab6-chat",
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        },
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "model": "qwen-turbo",
        },
    }

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.LLM_PROVIDER
        self._client = None
        self._initialized = False

    def _get_provider_config(self) -> Dict[str, Any]:
        """获取当前provider的配置"""
        return self.PROVIDER_CONFIGS.get(self.provider, self.PROVIDER_CONFIGS["minimax"])

    def _get_api_key(self) -> Optional[str]:
        """获取API Key"""
        if self.provider == "minimax":
            return config.MINIMAX_API_KEY or os.getenv("MINIMAX_API_KEY")
        elif self.provider == "deepseek":
            return config.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
        elif self.provider == "qwen":
            return config.QWEN_API_KEY or os.getenv("QWEN_API_KEY")
        return None

    def _get_base_url(self) -> str:
        """获取Base URL"""
        if self.provider == "minimax":
            return config.MINIMAX_BASE_URL
        elif self.provider == "deepseek":
            return config.DEEPSEEK_BASE_URL
        elif self.provider == "qwen":
            return config.QWEN_BASE_URL
        return self._get_provider_config()["base_url"]

    def _get_model(self) -> str:
        """获取模型名称"""
        if self.provider == "minimax":
            return config.MINIMAX_MODEL
        elif self.provider == "deepseek":
            return config.DEEPSEEK_MODEL
        elif self.provider == "qwen":
            return config.QWEN_MODEL
        return self._get_provider_config()["model"]

    def _initialize_client(self):
        """初始化LLM客户端"""
        if self._initialized:
            return

        try:
            api_key = self._get_api_key()
            if not api_key:
                logger.warning(f"Provider {self.provider} API key not found, using mock mode")
                self._client = None
                self._initialized = True
                return

            base_url = self._get_base_url()
            model = self._get_model()

            if self.provider == "minimax":
                from langchain_community.chat_models import MiniMaxChat
                self._client = MiniMaxChat(
                    model_name=model,
                    api_key=api_key,
                    base_url=base_url
                )
            elif self.provider in ("deepseek", "qwen"):
                from langchain_community.chat_models import ChatOpenAI
                self._client = ChatOpenAI(
                    model=model,
                    openai_api_key=api_key,
                    openai_api_base=base_url
                )

            self._initialized = True
            logger.info(f"LLM Gateway initialized with provider: {self.provider}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self._client = None
            self._initialized = True

    @property
    def client(self):
        """获取LLM客户端"""
        if not self._initialized:
            self._initialize_client()
        return self._client

    def chat(self, prompt: str, **kwargs) -> str:
        """通用对话接口"""
        if self.client is None:
            return self._mock_response(prompt)

        try:
            response = self.client.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")

    def chat_with_messages(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """带消息历史的对接接口"""
        if self.client is None:
            return self._mock_response(str(messages))

        try:
            from langchain.schema import HumanMessage, SystemMessage
            langchain_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                else:
                    langchain_messages.append(HumanMessage(content=msg["content"]))

            response = self.client.invoke(langchain_messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")

    def _mock_response(self, prompt: str) -> str:
        """模拟响应（用于测试）"""
        return f"[Mock Response] 已收到请求: {prompt[:100]}..."


class LLMFactory:
    """LLM工厂类"""

    _instances: Dict[str, LLMGateway] = {}

    @classmethod
    def get_gateway(cls, provider: Optional[str] = None) -> LLMGateway:
        """获取指定provider的LLM网关实例"""
        key = provider or config.LLM_PROVIDER
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