"""QUANT Agent — ReAct loop with streaming and loop detection."""
from __future__ import annotations
import json
import uuid
from quant.providers.base import BaseProvider
from quant.tools.base import BaseTool, ToolResult


class QuantAgent:
    MAX_ITERATIONS = 25

    def __init__(self, provider: BaseProvider, tools: list[BaseTool],
                 mode: str = "agent", on_tool=None, on_token=None, model_name: str = ""):
        self.provider   = provider
        self.tools      = {t.name: t for t in tools}
        self.mode       = mode
        self.on_tool    = on_tool
        self.on_token   = on_token
        self.model_name = model_name

    async def _execute_tool(self, tc, messages: list) -> str:
        tool = self.tools.get(tc.name)
        call_id = tc.call_id or f"call_{uuid.uuid4().hex[:8]}"

        if tool:
            result: ToolResult = await tool.execute(**tc.arguments)
            if self.on_tool:
                self.on_tool(tc.name, tc.arguments, result)
            result_str = str(result)
        else:
            result_str = f"ERROR: Unknown tool '{tc.name}'. Available: {list(self.tools.keys())}"

        assistant_msg = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id":       call_id,
                    "type":     "function",
                    "function": {
                        "name":      tc.name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                    },
                }
            ],
        }
        messages.append(assistant_msg)
        messages.append({
            "role":         "tool",
            "tool_call_id": call_id,
            "name":         tc.name,
            "content":      result_str,
        })
        return result_str

    async def run(self, task: str, history: list[dict], system: str) -> str:
        messages = list(history)
        messages.append({"role": "user", "content": task})

        recent_calls: list[str] = []
        use_streaming = self.on_token and hasattr(self.provider, "stream_chat")

        for iteration in range(self.MAX_ITERATIONS):
            if use_streaming:
                full_text = ""
                tool_call_result = None

                async for event_type, event_data in self.provider.stream_chat(
                    messages=messages,
                    tools=list(self.tools.values()),
                    system=system,
                ):
                    if event_type == "token":
                        full_text += event_data
                        self.on_token(event_data)
                    elif event_type == "tool_call":
                        tool_call_result = event_data
                    elif event_type == "error":
                        return f"Error: {event_data}"
                    elif event_type == "done":
                        full_text = event_data

                if tool_call_result:
                    tc = tool_call_result
                    call_sig = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                    recent_calls.append(call_sig)
                    if len(recent_calls) > 5:
                        recent_calls.pop(0)
                    if len(recent_calls) >= 3 and len(set(recent_calls[-3:])) == 1:
                        return "Loop detected: same tool called 3 times with same args."
                    await self._execute_tool(tc, messages)
                    continue

                if full_text:
                    messages.append({"role": "assistant", "content": full_text})
                    return full_text
                return ""
            else:
                response = await self.provider.chat(
                    messages=messages,
                    tools=list(self.tools.values()),
                    system=system,
                    stream=False,
                )

                if response.type == "text":
                    full = response.content
                    if self.on_token:
                        self.on_token(full)
                    messages.append({"role": "assistant", "content": full})
                    return full

                if response.type == "tool_call" and response.tool_call:
                    tc = response.tool_call
                    call_sig = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                    recent_calls.append(call_sig)
                    if len(recent_calls) > 5:
                        recent_calls.pop(0)
                    if len(recent_calls) >= 3 and len(set(recent_calls[-3:])) == 1:
                        return "Loop detected: same tool called 3 times with same args."
                    await self._execute_tool(tc, messages)

        return "Max iterations reached."
