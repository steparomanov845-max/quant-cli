"""QUANT CLI — OpenAI Provider с правильным tool_call_id."""
from __future__ import annotations
import json
import uuid
from typing import AsyncGenerator
import httpx
from quant.providers.base import BaseProvider, ChatResponse, ToolCall


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o", api_key: str = "",
                 base_url: str = "https://api.openai.com/v1", context_size: int = 128000,
                 temperature: float = 0.2):
        self.model        = model
        self.api_key      = api_key
        self.temperature  = temperature
        self.BASE         = base_url.rstrip("/")
        self.context_size = context_size
        self._client      = httpx.AsyncClient(
            timeout=120,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        self.last_usage: dict = {}

    async def health_check(self) -> dict:
        if not self.api_key:
            return {"status": "error", "message": "openai_api_key is not set in config"}
        try:
            r = await self._client.get(f"{self.BASE}/models", timeout=8)
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
            return {"status": "ok", "models": models}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def chat(self, messages, tools=None, system="", stream=False) -> ChatResponse:
        payload: dict = {
            "model":       self.model,
            "messages":    self.to_openai_messages(messages, system),
            "temperature": self.temperature,
        }
        if tools:
            payload["tools"]       = [t.to_openai_schema() for t in tools]
            payload["tool_choice"] = "auto"

        resp = await self._client.post(f"{self.BASE}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        self.last_usage = data.get("usage", {})

        msg = data["choices"][0]["message"]

        if msg.get("tool_calls"):
            tc_raw = msg["tool_calls"][0]
            call_id = tc_raw.get("id") or f"call_{uuid.uuid4().hex[:8]}"
            fn      = tc_raw["function"]
            try:
                args = json.loads(fn["arguments"])
            except Exception:
                args = {}
            return ChatResponse(
                type="tool_call", content="",
                tool_call=ToolCall(name=fn["name"], arguments=args, call_id=call_id),
                usage=self.last_usage, raw=json.dumps(msg),
            )

        return ChatResponse(
            type="text", content=msg.get("content", "") or "",
            usage=self.last_usage, raw=json.dumps(msg),
        )

    async def stream(self, messages, system="") -> AsyncGenerator[str, None]:
        payload = {
            "model":       self.model,
            "messages":    self.to_openai_messages(messages, system),
            "stream":      True,
            "temperature": self.temperature,
        }
        async with self._client.stream("POST", f"{self.BASE}/chat/completions", json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    token = json.loads(chunk)["choices"][0]["delta"].get("content") or ""
                    if token:
                        yield token
                except Exception:
                    continue

    async def stream_chat(
        self, messages, tools=None, system=""
    ) -> AsyncGenerator[tuple, None]:
        payload = {
            "model":       self.model,
            "messages":    self.to_openai_messages(messages, system),
            "stream":      True,
            "temperature": self.temperature,
        }
        if tools:
            payload["tools"]       = [t.to_openai_schema() for t in tools]
            payload["tool_choice"] = "auto"

        tool_calls_buf: dict[int, dict] = {}
        text_buf = ""
        usage = {}

        try:
            async with self._client.stream(
                "POST", f"{self.BASE}/chat/completions", json=payload
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        parsed = json.loads(chunk)
                        choice = parsed["choices"][0]
                        delta  = choice.get("delta", {})

                        if parsed.get("usage"):
                            usage = parsed["usage"]

                        content = delta.get("content")
                        if content:
                            text_buf += content
                            yield ("token", content)

                        for tc_delta in delta.get("tool_calls", []):
                            idx = tc_delta.get("index", 0)
                            if idx not in tool_calls_buf:
                                tool_calls_buf[idx] = {
                                    "id": "", "name": "", "arguments": ""
                                }
                            buf = tool_calls_buf[idx]
                            if tc_delta.get("id"):
                                buf["id"] = tc_delta["id"]
                            fn = tc_delta.get("function", {})
                            if fn.get("name"):
                                buf["name"] = fn["name"]
                            if fn.get("arguments"):
                                buf["arguments"] += fn["arguments"]
                    except Exception:
                        continue
        except Exception as e:
            yield ("error", str(e))
            return

        self.last_usage = usage

        if tool_calls_buf:
            tc = list(tool_calls_buf.values())[0]
            try:
                args = json.loads(tc["arguments"]) if tc["arguments"] else {}
            except Exception:
                args = {}
            yield ("tool_call", ToolCall(
                name=tc["name"], arguments=args, call_id=tc["id"]
            ))
        elif text_buf:
            yield ("done", text_buf)
        else:
            yield ("done", "")

    def get_info(self) -> dict:
        return {"provider": self.name, "model": self.model, "context": self.context_size}
