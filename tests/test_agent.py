"""Tests for QUANT agent."""
from __future__ import annotations
import json
import pytest
from quant.agent.agent import QuantAgent
from quant.providers.base import BaseProvider, ChatResponse, ToolCall
from quant.tools.base import BaseTool, ToolResult


class MockTool(BaseTool):
    name = "MOCK_TOOL"
    description = "Mock tool for testing"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string"},
        },
        "required": ["input"],
    }

    async def execute(self, input: str = "", **kwargs) -> ToolResult:
        return ToolResult(True, {"echo": input})


class MockProvider(BaseProvider):
    name = "mock"
    model = "mock-model"
    context_size = 4096

    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.call_count = 0
        self.last_usage = {}

    async def chat(self, messages, tools=None, system="", stream=False):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return ChatResponse(type="text", content="Done.")

    async def stream(self, messages, system=""):
        yield "mock response"

    async def stream_chat(self, messages, tools=None, system=""):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            if resp.type == "tool_call":
                yield ("tool_call", resp.tool_call)
            else:
                for ch in resp.content:
                    yield ("token", ch)
                yield ("done", resp.content)
        else:
            yield ("done", "Done.")

    async def health_check(self):
        return {"status": "ok"}

    async def close(self):
        pass


class TestAgent:
    @pytest.mark.asyncio
    async def test_simple_text_response(self):
        provider = MockProvider([
            ChatResponse(type="text", content="Hello!"),
        ])
        agent = QuantAgent(provider=provider, tools=[])
        result = await agent.run("hi", history=[], system="test")
        assert result == "Hello!"

    @pytest.mark.asyncio
    async def test_tool_call_then_text(self):
        provider = MockProvider([
            ChatResponse(
                type="tool_call",
                content="",
                tool_call=ToolCall(name="MOCK_TOOL", arguments={"input": "test"}, call_id="c1"),
            ),
            ChatResponse(type="text", content="Done!"),
        ])
        agent = QuantAgent(provider=provider, tools=[MockTool()])
        result = await agent.run("do something", history=[], system="test")
        assert result == "Done!"
        assert provider.call_count == 2

    @pytest.mark.asyncio
    async def test_loop_detection(self):
        responses = []
        for i in range(5):
            responses.append(ChatResponse(
                type="tool_call",
                content="",
                tool_call=ToolCall(
                    name="MOCK_TOOL",
                    arguments={"input": "same"},
                    call_id=f"c{i}",
                ),
            ))
        provider = MockProvider(responses)
        agent = QuantAgent(provider=provider, tools=[MockTool()])
        result = await agent.run("loop", history=[], system="test")
        assert "Loop detected" in result

    @pytest.mark.asyncio
    async def test_on_token_callback(self):
        provider = MockProvider([
            ChatResponse(type="text", content="Hello!"),
        ])
        tokens = []
        agent = QuantAgent(
            provider=provider, tools=[],
            on_token=lambda t: tokens.append(t),
        )
        result = await agent.run("hi", history=[], system="test")
        assert result == "Hello!"
        assert "".join(tokens) == "Hello!"

    @pytest.mark.asyncio
    async def test_on_tool_callback(self):
        provider = MockProvider([
            ChatResponse(
                type="tool_call",
                content="",
                tool_call=ToolCall(name="MOCK_TOOL", arguments={"input": "x"}, call_id="c1"),
            ),
            ChatResponse(type="text", content="ok"),
        ])
        tool_calls = []
        agent = QuantAgent(
            provider=provider, tools=[MockTool()],
            on_tool=lambda name, args, result: tool_calls.append(name),
        )
        await agent.run("test", history=[], system="test")
        assert "MOCK_TOOL" in tool_calls

    @pytest.mark.asyncio
    async def test_max_iterations(self):
        responses = [
            ChatResponse(
                type="tool_call",
                content="",
                tool_call=ToolCall(
                    name="MOCK_TOOL",
                    arguments={"input": str(i)},
                    call_id=f"c{i}",
                ),
            )
            for i in range(30)
        ]
        provider = MockProvider(responses)
        agent = QuantAgent(provider=provider, tools=[MockTool()])
        result = await agent.run("many tools", history=[], system="test")
        assert "Max iterations" in result
