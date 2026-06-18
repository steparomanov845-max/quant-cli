"""QUANT CLI — Ollama Provider (local models via Ollama API)."""
from __future__ import annotations
import json
import uuid
from typing import AsyncGenerator
import httpx
from quant.providers.base import BaseProvider, ChatResponse, ToolCall


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, model: str = "llama3", context_size: int = 4096,
                 base_url: str = "http://localhost:11434", timeout: int = 300,
                 temperature: float = 0.2):
        self.model        = model
        self.context_size = context_size
        self.temperature  = temperature
        self.BASE         = base_url.rstrip("/")
        self._timeout     = timeout
        self._client      = httpx.AsyncClient(timeout=timeout)
        self.last_usage: dict = {}
        self._model_detected: bool = False
        self._context_detected: bool = False

    async def health_check(self) -> dict:
        try:
            r = await self._client.get(f"{self.BASE}/api/tags", timeout=8)
            r.raise_for_status()
            data = r.json()
            models = [m["name"] for m in data.get("models", [])]

            if not models:
                return {"status": "error", "message": "No models found in Ollama. Pull a model first: ollama pull llama3"}

            if self.model in ("local-model", "", None) or self.model not in models:
                self.model = models[0]
                self._model_detected = True

            return {"status": "ok", "models": models, "current_model": self.model}

        except httpx.ConnectError:
            return {
                "status": "error",
                "message": "Cannot connect to Ollama — is it running on port 11434?",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def chat(self, messages, tools=None, system="", stream=False) -> ChatResponse:
        ollama_msgs = []
        if system:
            ollama_msgs.append({"role": "system", "content": system})
        for m in messages:
            ollama_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        payload = {
            "model":    self.model,
            "messages": ollama_msgs,
            "stream":   False,
            "options":  {"temperature": self.temperature},
        }

        if tools:
            ollama_tools = []
            for t in tools:
                schema = t.to_openai_schema()
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": schema["function"]["name"],
                        "description": schema["function"]["description"],
                        "parameters": schema["function"]["parameters"],
                    }
                })
            payload["tools"] = ollama_tools

        last_error = None
        for attempt in range(3):
            try:
                resp = await self._client.post(f"{self.BASE}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
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

        msg = data.get("message", {})
        self.last_usage = {
            "prompt_tokens":     data.get("prompt_eval_count", 0),
            "completion_tokens": data.get("eval_count", 0),
            "total_tokens":      data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
        }

        if msg.get("tool_calls"):
            tc_raw = msg["tool_calls"][0]
            fn     = tc_raw.get("function", {})
            tc_id  = f"call_{uuid.uuid4().hex[:8]}"
            try:
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    args = json.loads(args)
            except Exception:
                args = {}
            return ChatResponse(
                type="tool_call", content="",
                tool_call=ToolCall(name=fn.get("name", ""), arguments=args, call_id=tc_id),
                usage=self.last_usage, raw=json.dumps(msg),
            )

        return ChatResponse(
            type="text", content=msg.get("content", "") or "",
            usage=self.last_usage, raw=json.dumps(msg),
        )

    async def stream(self, messages, system="") -> AsyncGenerator[str, None]:
        ollama_msgs = []
        if system:
            ollama_msgs.append({"role": "system", "content": system})
        for m in messages:
            ollama_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        payload = {
            "model":    self.model,
            "messages": ollama_msgs,
            "stream":   True,
            "options":  {"temperature": self.temperature},
        }

        async with self._client.stream("POST", f"{self.BASE}/api/chat", json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    delta = chunk.get("message", {}).get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    continue

    async def stream_chat(
        self, messages, tools=None, system=""
    ) -> AsyncGenerator[tuple, None]:
        ollama_msgs = []
        if system:
            ollama_msgs.append({"role": "system", "content": system})
        for m in messages:
            ollama_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        payload = {
            "model":    self.model,
            "messages": ollama_msgs,
            "stream":   True,
            "options":  {"temperature": self.temperature},
        }

        if tools:
            ollama_tools = []
            for t in tools:
                schema = t.to_openai_schema()
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": schema["function"]["name"],
                        "description": schema["function"]["description"],
                        "parameters": schema["function"]["parameters"],
                    }
                })
            payload["tools"] = ollama_tools

        text_buf = ""
        tool_calls_buf = None

        try:
            async with self._client.stream("POST", f"{self.BASE}/api/chat", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        msg = chunk.get("message", {})

                        content = msg.get("content", "")
                        if content:
                            text_buf += content
                            yield ("token", content)

                        if msg.get("tool_calls"):
                            tool_calls_buf = msg["tool_calls"][0].get("function", {})

                        if chunk.get("done"):
                            self.last_usage = {
                                "prompt_tokens":     chunk.get("prompt_eval_count", 0),
                                "completion_tokens": chunk.get("eval_count", 0),
                                "total_tokens":      chunk.get("prompt_eval_count", 0) + chunk.get("eval_count", 0),
                            }
                    except Exception:
                        continue
        except Exception as e:
            yield ("error", str(e))
            return

        if tool_calls_buf:
            try:
                args = tool_calls_buf.get("arguments", {})
                if isinstance(args, str):
                    args = json.loads(args)
            except Exception:
                args = {}
            yield ("tool_call", ToolCall(
                name=tool_calls_buf.get("name", ""),
                arguments=args,
                call_id=f"call_{uuid.uuid4().hex[:8]}",
            ))
        elif text_buf:
            yield ("done", text_buf)
        else:
            yield ("done", "")

    async def list_models(self) -> list[str]:
        try:
            r = await self._client.get(f"{self.BASE}/api/tags", timeout=8)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    def get_info(self) -> dict:
        return {
            "provider": self.name,
            "model":    self.model,
            "context":  self.context_size,
        }

    async def close(self) -> None:
        await self._client.aclose()
