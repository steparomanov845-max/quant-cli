"""QUANT CLI — DeepSeek Provider (OpenAI-compatible API)."""
from __future__ import annotations
from quant.providers.openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    name = "deepseek"

    def __init__(self, model: str = "deepseek-coder", api_key: str = "",
                 base_url: str = "https://api.deepseek.com/v1", context_size: int = 65536,
                 temperature: float = 0.2):
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            context_size=context_size,
            temperature=temperature,
        )

    async def health_check(self) -> dict:
        if not self.api_key:
            return {"status": "error", "message": "deepseek_api_key is not set in config"}
        result = await super().health_check()
        return result
