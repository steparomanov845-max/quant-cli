"""Tests for QUANT tools."""
from __future__ import annotations
import asyncio
import pytest
from pathlib import Path
from quant.tools.base import ToolResult, BaseTool
from quant.tools.read_file import ReadFileTool
from quant.tools.write_file import WriteFileTool, set_confirm
from quant.tools.edit_file import EditFileTool
from quant.tools.filesystem import FilesystemTool, set_working_dir, get_working_dir
from quant.tools.memory import MemoryTool
from quant.tools.datetime_tool import DatetimeTool
from quant.tools.search import SearchTool


class TestToolResult:
    def test_success(self):
        r = ToolResult(True, {"key": "value"})
        assert r.success is True
        assert r.data == {"key": "value"}
        assert r.error is None
        assert "key" in str(r)

    def test_error(self):
        r = ToolResult(False, {}, error="something broke")
        assert r.success is False
        assert "something broke" in str(r)


class TestReadFile:
    @pytest.mark.asyncio
    async def test_read_existing(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        tool = ReadFileTool()
        r = await tool.execute(path=str(f))
        assert r.success is True
        assert "hello world" in r.data["content"]

    @pytest.mark.asyncio
    async def test_read_missing(self, tmp_path):
        tool = ReadFileTool()
        r = await tool.execute(path=str(tmp_path / "nope.txt"))
        assert r.success is False

    @pytest.mark.asyncio
    async def test_read_relative_from_cwd(self, tmp_path):
        set_working_dir(tmp_path)
        f = tmp_path / "relative.txt"
        f.write_text("relative path test", encoding="utf-8")
        tool = ReadFileTool()
        r = await tool.execute(path="relative.txt")
        assert r.success is True
        assert "relative path test" in r.data["content"]
        set_working_dir(Path.cwd())


class TestWriteFile:
    @pytest.mark.asyncio
    async def test_create_new(self, tmp_path):
        set_confirm(False)
        set_working_dir(tmp_path)
        tool = WriteFileTool()
        r = await tool.execute(path="new.txt", content="new content")
        assert r.success is True
        assert r.data["created"] is True
        assert (tmp_path / "new.txt").read_text() == "new content"

    @pytest.mark.asyncio
    async def test_overwrite(self, tmp_path):
        set_confirm(False)
        set_working_dir(tmp_path)
        f = tmp_path / "existing.txt"
        f.write_text("old", encoding="utf-8")
        tool = WriteFileTool()
        r = await tool.execute(path="existing.txt", content="new")
        assert r.success is True
        assert r.data["created"] is False
        assert f.read_text() == "new"

    @pytest.mark.asyncio
    async def test_no_overwrite(self, tmp_path):
        set_confirm(False)
        set_working_dir(tmp_path)
        f = tmp_path / "existing.txt"
        f.write_text("old", encoding="utf-8")
        tool = WriteFileTool()
        r = await tool.execute(path="existing.txt", content="new", overwrite=False)
        assert r.success is False
        assert "exists" in r.error.lower()


class TestEditFile:
    @pytest.mark.asyncio
    async def test_edit(self, tmp_path):
        from quant.tools.edit_file import set_confirm as set_edit_confirm
        set_confirm(False)
        set_edit_confirm(False)
        set_working_dir(tmp_path)
        f = tmp_path / "edit.txt"
        f.write_text("hello world", encoding="utf-8")
        tool = EditFileTool()
        r = await tool.execute(path="edit.txt", old_str="world", new_str="python")
        assert r.success is True
        assert f.read_text() == "hello python"

    @pytest.mark.asyncio
    async def test_edit_not_found(self, tmp_path):
        from quant.tools.edit_file import set_confirm as set_edit_confirm
        set_confirm(False)
        set_edit_confirm(False)
        set_working_dir(tmp_path)
        f = tmp_path / "edit.txt"
        f.write_text("hello", encoding="utf-8")
        tool = EditFileTool()
        r = await tool.execute(path="edit.txt", old_str="xyz", new_str="abc")
        assert r.success is False
        assert "not found" in r.error.lower()


class TestFilesystem:
    @pytest.mark.asyncio
    async def test_cwd(self, tmp_path):
        set_working_dir(tmp_path)
        tool = FilesystemTool()
        r = await tool.execute(action="cwd")
        assert r.success is True
        assert str(tmp_path) in r.data["current_directory"]

    @pytest.mark.asyncio
    async def test_mkdir(self, tmp_path):
        set_working_dir(tmp_path)
        tool = FilesystemTool()
        r = await tool.execute(action="mkdir", path="new_dir/sub")
        assert r.success is True
        assert (tmp_path / "new_dir" / "sub").exists()

    @pytest.mark.asyncio
    async def test_list(self, tmp_path):
        set_working_dir(tmp_path)
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()
        tool = FilesystemTool()
        r = await tool.execute(action="list", path=".")
        assert r.success is True
        assert r.data["count"] == 2

    @pytest.mark.asyncio
    async def test_exists(self, tmp_path):
        set_working_dir(tmp_path)
        (tmp_path / "yes.txt").touch()
        tool = FilesystemTool()
        r = await tool.execute(action="exists", path="yes.txt")
        assert r.success is True
        assert r.data["exists"] is True

    @pytest.mark.asyncio
    async def test_delete(self, tmp_path):
        set_working_dir(tmp_path)
        f = tmp_path / "delete_me.txt"
        f.touch()
        tool = FilesystemTool()
        r = await tool.execute(action="delete", path="delete_me.txt")
        assert r.success is True
        assert not f.exists()


class TestMemory:
    @pytest.mark.asyncio
    async def test_set_get_list_delete(self, tmp_path, monkeypatch):
        from quant.tools import memory as mem
        monkeypatch.setattr(mem, "MEMORY_FILE", tmp_path / "mem.json")
        tool = MemoryTool()

        r = await tool.execute(action="set", key="test_key", value="test_value")
        assert r.success is True

        r = await tool.execute(action="get", key="test_key")
        assert r.success is True
        assert r.data["value"] == "test_value"

        r = await tool.execute(action="list")
        assert r.success is True
        assert "test_key" in r.data["keys"]

        r = await tool.execute(action="delete", key="test_key")
        assert r.success is True

        r = await tool.execute(action="get", key="test_key")
        assert r.success is False


class TestDatetime:
    @pytest.mark.asyncio
    async def test_full(self):
        tool = DatetimeTool()
        r = await tool.execute(format="full")
        assert r.success is True
        assert "datetime" in r.data
        assert "weekday" in r.data

    @pytest.mark.asyncio
    async def test_date(self):
        tool = DatetimeTool()
        r = await tool.execute(format="date")
        assert r.success is True
        assert "date" in r.data
        assert "year" in r.data

    @pytest.mark.asyncio
    async def test_timestamp(self):
        tool = DatetimeTool()
        r = await tool.execute(format="timestamp")
        assert r.success is True
        assert "unix_timestamp" in r.data


class TestSearch:
    @pytest.mark.asyncio
    async def test_search_finds_text(self, tmp_path):
        (tmp_path / "test.py").write_text("def main():\n    pass", encoding="utf-8")
        tool = SearchTool()
        r = await tool.execute(query="def main", path=str(tmp_path))
        assert r.success is True
        assert r.data["count"] >= 1
