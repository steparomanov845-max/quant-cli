"""Tests for QUANT core modules."""
from __future__ import annotations
import pytest
from pathlib import Path
from quant.core.session import Session, Message
from quant.core.config import QuantConfig, DEFAULT_CONFIG
from quant.core.context import ContextEngine


class TestSession:
    def test_add_message(self):
        s = Session()
        s.add("user", "hello")
        assert len(s.messages) == 1
        assert s.messages[0].role == "user"
        assert s.messages[0].content == "hello"

    def test_max_messages(self):
        s = Session(max_messages=3)
        for i in range(5):
            s.add("user", f"msg {i}")
        assert len(s.messages) == 3
        assert s.messages[0].content == "msg 2"

    def test_estimated_tokens_utf8(self):
        m = Message(role="user", content="привет мир")
        tokens = m.estimated_tokens()
        utf8_len = len("привет мир".encode("utf-8"))
        assert tokens == max(1, utf8_len // 4)

    def test_estimated_tokens_ascii(self):
        m = Message(role="user", content="hello world")
        tokens = m.estimated_tokens()
        assert tokens == max(1, len("hello world") // 4)

    def test_prune_no_op(self):
        s = Session(token_limit=100000)
        s.add("user", "short message")
        removed = s.prune()
        assert removed == 0
        assert len(s.messages) == 1

    def test_prune_tool_messages(self):
        s = Session(token_limit=100)
        s.add("user", "x" * 500)
        for i in range(15):
            s.add("tool", f"tool result {i}: " + "y" * 200)
        s.add("assistant", "response")
        removed = s.prune()
        assert removed > 0

    def test_to_api_format(self):
        s = Session()
        s.add("user", "hello")
        s.add("assistant", "hi")
        fmt = s.to_api_format()
        assert len(fmt) == 2
        assert fmt[0] == {"role": "user", "content": "hello"}
        assert fmt[1] == {"role": "assistant", "content": "hi"}

    def test_clear(self):
        s = Session()
        s.add("user", "hello")
        s.clear()
        assert len(s.messages) == 0


class TestConfig:
    def test_default_values(self):
        cfg = QuantConfig()
        assert cfg.provider == "lmstudio"
        assert cfg.model == "local-model"
        assert cfg.mode == "chat"
        assert cfg.lang == "en"
        assert cfg.temperature == 0.2
        assert cfg.confirm_actions is True

    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from quant.core.config import CONFIG_DIR, CONFIG_FILE
        cfg = QuantConfig()
        cfg.lang = "ru"
        cfg.mode = "agent"
        cfg.save()
        assert CONFIG_FILE.exists()

        loaded = QuantConfig.load()
        assert loaded.lang == "ru"
        assert loaded.mode == "agent"

    def test_load_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = QuantConfig.load()
        assert cfg.provider == "lmstudio"

    def test_default_config_keys(self):
        fields = QuantConfig.model_fields
        for key in DEFAULT_CONFIG:
            assert key in fields, f"Missing field: {key}"


class TestContextEngine:
    def test_build_system_context(self, tmp_path):
        ctx = ContextEngine(project_root=tmp_path)
        result = ctx.build_system_context("chat", {"model": "test", "context": 32768})
        assert "QUANT" in result
        assert "chat" in result.lower() or "CHAT" in result

    def test_read_project_files(self, tmp_path):
        (tmp_path / "QUANT.md").write_text("project context", encoding="utf-8")
        ctx = ContextEngine(project_root=tmp_path)
        result = ctx._read_project_files()
        assert "project context" in result

    def test_max_context_chars(self, tmp_path):
        ctx = ContextEngine(project_root=tmp_path, max_context_chars=100)
        assert ctx.max_context_chars == 100
