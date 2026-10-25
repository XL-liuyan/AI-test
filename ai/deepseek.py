"""DeepSeek LLM 客户端：OpenAI 兼容 /chat/completions，直接走 requests（无额外依赖）。"""
import logging

import requests

from config import settings

logger = logging.getLogger("ai")

API_URL = "https://api.deepseek.com/chat/completions"


class DeepSeekLLM:
    """极简封装：向 DeepSeek 发聊天请求，返回回复文本。"""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat", timeout: float = 120.0):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.model = model
        self.timeout = timeout
        if not self.api_key:
            raise RuntimeError(
                "未找到 DEEPSEEK_API_KEY：请在系统环境变量或项目 .env 中配置后重试。"
            )

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """messages 形如 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]。"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info("-> DeepSeek %s (messages=%d)", self.model, len(messages))
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        logger.info("<- DeepSeek 回复 %d 字符", len(content))
        return content
