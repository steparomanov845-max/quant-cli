"""LM Studio Provider — автоопределение через v0 API (loaded model first)."""
from __future__ import annotations
import json
import uuid
from typing import AsyncGenerator
import httpx
from quant.providers.base import BaseProvider, ChatResponse, ToolCall


class LMStudioProvider(BaseProvider):
    name = "lmstudio"

    def __init__(self, model: str = "local-model", context_size: int = 32768,
                 base_url: str | None = None, timeout: int = 300, temperature: float = 0.2):
        self.model        = model
        self.context_size = context_size
        self.temperature  = temperature
        self.BASE         = (base_url.rstrip("/") + "/v1") if base_url else "http://localhost:1234/v1"
        self._timeout     = timeout
        self._client      = httpx.AsyncClient(timeout=timeout)
        self.last_usage: dict = {}
        self._context_detected: bool = False
        self._model_detected: bool = False
        self._all_models: list[dict] = []

    @property
    def _v0_base(self) -> str:
        return self.BASE.rsplit("/v1", 1)[0]

    async def _fetch_v0_models(self) -> list[dict]:
        """Получает список моделей из v0 API (там есть state, max_context_length)."""
        try:
            r = await self._client.get(f"{self._v0_base}/api/v0/models", timeout=8)
            if r.status_code == 200:
                return r.json().get("data", [])
        except Exception:
            pass
        return []

    async def health_check(self) -> dict:
        try:
            # === Шаг 1: v0 API — основной источник ===
            v0_models = await self._fetch_v0_models()
            self._all_models = v0_models

            if v0_models:
                # Ищем загруженную модель
                loaded = [m for m in v0_models if m.get("state") == "loaded"]

                if loaded:
                    best = loaded[0]
                    self.model = best["id"]
                    self._model_detected = True

                    # loaded_context_length > max_context_length
                    ctx = best.get("loaded_context_length") or best.get("max_context_length")
                    if ctx and int(ctx) > 0:
                        self.context_size = int(ctx)
                        self._context_detected = True
                    else:
                        self._context_detected = False

                    all_ids = [m["id"] for m in v0_models]
                    return {"status": "ok", "models": all_ids, "current_model": self.model}
                else:
                    # Нет загруженных — берём первый
                    best = v0_models[0]
                    self.model = best["id"]
                    self._model_detected = True
                    ctx = best.get("max_context_length")
                    if ctx and int(ctx) > 0:
                        self.context_size = int(ctx)
                        self._context_detected = True
                    all_ids = [m["id"] for m in v0_models]
                    return {"status": "ok", "models": all_ids, "current_model": self.model}

            # === Шаг 2: фоллбек на OpenAI-compat /v1/models ===
            r = await self._client.get(f"{self.BASE}/models", timeout=8)
            r.raise_for_status()
            data = r.json().get("data", [])
            models = [m["id"] for m in data]

            if not models:
                return {"status": "error", "message": "No models loaded in LM Studio"}

            if self.model in ("local-model", "", None) or self.model not in models:
                self.model = models[0]
                self._model_detected = True

            self._context_detected = False
            return {"status": "ok", "models": models, "current_model": self.model}

        except httpx.ConnectError:
            return {
                "status": "error",
                "message": "Cannot connect to LM Studio — is it running on port 1234?",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def list_models_v0(self) -> list[dict]:
        """Возвращает полную инфо из v0 API (id, state, max_context_length, capabilities)."""
        if not self._all_models:
            self._all_models = await self._fetch_v0_models()
        return self._all_models

    async def chat(self, messages, tools=None, system="", stream=False) -> ChatResponse:
        payload: dict = {
            "model":       self.model,
            "messages":    self.to_openai_messages(messages, system),
            "stream":      False,
            "temperature": self.temperature,
        }
        if tools:
            payload["tools"]       = [t.to_openai_schema() for t in tools]
            payload["tool_choice"] = "auto"

        last_error = None
        for attempt in range(3):
            try:
                resp = await self._client.post(f"{self.BASE}/chat/completions", json=payload)
                resp.raise_for_status()
                data = resp.json()
                self.last_usage = data.get("usage", {})
                break
            except Exception as e:
                last_error = e
                if attempt < 2:
                    import asyncio
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                return ChatResponse(
                    type="text",
                    content=f"Error after 3 attempts: {last_error}",
                    usage={}, raw="",
                )

        msg = data["choices"][0]["message"]

        if msg.get("tool_calls"):
            tc_raw = msg["tool_calls"][0]
            tc_id  = tc_raw.get("id") or f"call_{uuid.uuid4().hex[:8]}"
            fn     = tc_raw["function"]
            try:
                args = json.loads(fn["arguments"])
            except Exception:
                args = {}
            return ChatResponse(
                type="tool_call", content="",
                tool_call=ToolCall(name=fn["name"], arguments=args, call_id=tc_id),
                usage=self.last_usage,
                raw=json.dumps(msg),
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

    async def list_models(self) -> list[str]:
        v0 = await self.list_models_v0()
        if v0:
            return [m["id"] for m in v0]
        health = await self.health_check()
        return health.get("models", [])

    def get_info(self) -> dict:
        return {
            "provider": self.name,
            "model":    self.model,
            "context":  self.context_size,
        }

    async def close(self) -> None:
        await self._client.aclose()
