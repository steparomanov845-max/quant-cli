from quant.core.config import QuantConfig
from quant.providers.lmstudio import LMStudioProvider
from quant.providers.openai   import OpenAIProvider
from quant.providers.deepseek import DeepSeekProvider
from quant.providers.ollama   import OllamaProvider
from quant.providers.base     import BaseProvider


def get_provider(cfg: QuantConfig) -> BaseProvider:
    if cfg.provider == "lmstudio":
        return LMStudioProvider(
            model=cfg.model,
            context_size=cfg.context_size,
            base_url=cfg.lmstudio_base_url,
            timeout=cfg.lmstudio_timeout,
            temperature=cfg.temperature,
        )
    elif cfg.provider == "ollama":
        return OllamaProvider(
            model=cfg.model,
            context_size=cfg.context_size,
            base_url=cfg.ollama_base_url,
            timeout=cfg.ollama_timeout,
            temperature=cfg.temperature,
        )
    elif cfg.provider == "openai":
        return OpenAIProvider(
            model=cfg.model,
            api_key=cfg.openai_api_key,
            base_url=cfg.openai_base_url,
            context_size=cfg.context_size,
            temperature=cfg.temperature,
        )
    elif cfg.provider == "deepseek":
        return DeepSeekProvider(
            model=cfg.model,
            api_key=cfg.deepseek_api_key,
            base_url=cfg.deepseek_base_url,
            context_size=cfg.context_size,
            temperature=cfg.temperature,
        )
    else:
        return LMStudioProvider(
            model=cfg.model,
            context_size=cfg.context_size,
            base_url=cfg.lmstudio_base_url,
            temperature=cfg.temperature,
        )
