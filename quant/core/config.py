from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings
import yaml

CONFIG_DIR  = Path(".quant")
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "provider":           "lmstudio",
    "model":              "local-model",
    "context_size":       32768,
    "mode":               "chat",
    "lang":               "en",
    "lmstudio_base_url":  "http://localhost:1234",
    "lmstudio_timeout":   300,
    "ollama_base_url":    "http://localhost:11434",
    "ollama_timeout":     300,
    "openai_api_key":     "",
    "openai_base_url":    "https://api.openai.com/v1",
    "deepseek_api_key":   "",
    "deepseek_base_url":  "https://api.deepseek.com/v1",
    "confirm_actions":    True,
    "safe_mode":          True,
    "temperature":        0.2,
    "max_context_chars":  12000,
}

class QuantConfig(BaseSettings):
    provider:           str  = "lmstudio"
    model:              str  = "local-model"
    context_size:       int  = 32768
    mode:               str  = "chat"
    lang:               str  = "en"
    lmstudio_base_url:  str  = "http://localhost:1234"
    lmstudio_timeout:   int  = 300
    ollama_base_url:    str  = "http://localhost:11434"
    ollama_timeout:     int  = 300
    openai_api_key:     str  = ""
    openai_base_url:    str  = "https://api.openai.com/v1"
    deepseek_api_key:   str  = ""
    deepseek_base_url:  str  = "https://api.deepseek.com/v1"
    confirm_actions:    bool = True
    safe_mode:          bool = True
    temperature:        float = 0.2
    max_context_chars:  int  = 12000

    class Config:
        env_prefix = "QUANT_"

    @classmethod
    def load(cls) -> "QuantConfig":
        if CONFIG_FILE.exists():
            try:
                raw   = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
                valid = cls.model_fields.keys()
                raw   = {k: v for k, v in raw.items() if k in valid}
                return cls(**raw)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(
            yaml.dump(self.model_dump(), allow_unicode=True),
            encoding="utf-8",
        )
