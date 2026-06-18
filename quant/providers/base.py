from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator

@dataclass
class ToolCall:
    name: str
    arguments: dict
    call_id: str = ""          # tool_call_id — требуется OpenAI-совместимыми провайдерами

@dataclass
class ChatResponse:
    type: str                  # "text" | "tool_call"
    content: str
    tool_call: ToolCall | None = None
    usage: dict = field(default_factory=dict)
    raw: str = ""

class BaseProvider(ABC):
    name: str
    model: str
    context_size: int

    @abstractmethod
    async def chat(self, messages, tools=None, system="", stream=False): ...

    @abstractmethod
    async def stream(self, messages, system=""): ...

    @abstractmethod
    async def health_check(self): ...

    def get_info(self):
        return {"provider": self.name, "model": self.model, "context": self.context_size}

    def to_openai_messages(self, messages: list[dict], system: str) -> list[dict]:
        result = []
        if system:
            result.append({"role": "system", "content": system})
        result.extend(messages)
        return result
