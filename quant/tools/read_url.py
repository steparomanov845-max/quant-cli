"""QUANT CLI — READ_URL tool (fetch webpage as plain text)."""
from __future__ import annotations
import re
import urllib.request
import urllib.parse
from quant.tools.base import BaseTool, ToolResult


def _html_to_text(html: str) -> str:
    """Простой HTML → текст без зависимостей."""
    # Убираем скрипты, стили, комментарии
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>",  " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    # Заголовки → текст с переносами
    html = re.sub(r"<h[1-6][^>]*>", "\n\n## ", html, flags=re.IGNORECASE)
    html = re.sub(r"</h[1-6]>",     "\n",       html, flags=re.IGNORECASE)
    # Параграфы, br, li
    html = re.sub(r"<br\s*/?>", "\n",     html, flags=re.IGNORECASE)
    html = re.sub(r"<p[^>]*>",  "\n",     html, flags=re.IGNORECASE)
    html = re.sub(r"<li[^>]*>", "\n• ",   html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>",   " ",      html)
    # HTML entities
    html = html.replace("&nbsp;", " ").replace("&amp;", "&").replace(
        "&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    # Убираем лишние пробелы/переносы
    lines = [line.strip() for line in html.splitlines()]
    lines = [l for l in lines if l]
    text  = "\n".join(lines)
    text  = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class ReadURLTool(BaseTool):
    name = "READ_URL"
    description = (
        "Fetch and read the content of any URL as plain text. "
        "Use for: reading documentation pages, GitHub READMEs, articles, API docs, "
        "Stack Overflow answers, PyPI package info. "
        "Returns the text content of the page (HTML stripped)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL to fetch (https://...)"
            },
            "max_chars": {
                "type": "integer",
                "description": "Max characters to return (default: 8000)"
            },
        },
        "required": ["url"],
    }

    async def execute(self, url: str, max_chars: int = 8000, **kwargs) -> ToolResult:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent":      "Mozilla/5.0 (compatible; QUANT-CLI/2.0)",
                    "Accept":          "text/html,text/plain,*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                content_type = resp.headers.get("Content-Type", "")
                raw          = resp.read(512_000)  # max 512KB

            # Определяем кодировку
            encoding = "utf-8"
            m = re.search(r"charset=([\w-]+)", content_type)
            if m:
                encoding = m.group(1)

            text = raw.decode(encoding, errors="replace")

            # Если HTML — конвертируем в текст
            if "html" in content_type.lower() or text.strip().startswith("<"):
                text = _html_to_text(text)

            truncated = len(text) > max_chars
            text      = text[:max_chars]

            return ToolResult(True, {
                "url":       url,
                "length":    len(text),
                "truncated": truncated,
                "content":   text,
            })

        except urllib.error.HTTPError as e:
            return ToolResult(False, {}, error=f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            return ToolResult(False, {}, error=f"Cannot reach URL: {e.reason}")
        except Exception as e:
            return ToolResult(False, {}, error=str(e))
