"""QUANT CLI — WEB_SEARCH tool (duckduckgo-search library)."""
from __future__ import annotations
from quant.tools.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    name = "WEB_SEARCH"
    description = (
        "Search the web using DuckDuckGo. Returns titles, URLs and snippets. "
        "IMPORTANT: After searching, always use READ_URL on the most relevant result "
        "to get the full content. Snippets alone are not enough for accurate answers. "
        "Use for: documentation, tutorials, error solutions, package info, news."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Max results to return (default: 8, max: 15)"
            },
            "region": {
                "type": "string",
                "description": "Region for search results (default: wt-wt for worldwide). "
                               "Examples: us-en, ru-ru, de-de"
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, max_results: int = 8, region: str = "wt-wt", **kwargs) -> ToolResult:
        max_results = min(max_results, 15)
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results, region=region):
                    results.append({
                        "title":   r.get("title", "")[:150],
                        "url":     r.get("href", ""),
                        "snippet": r.get("body", "")[:500],
                    })

            if not results:
                return ToolResult(True, {
                    "query":   query,
                    "results": [],
                    "note":    "No results found. Try rephrasing or using READ_URL on known documentation.",
                })

            output = {
                "query":   query,
                "count":   len(results),
                "results": results,
                "hint":    "Use READ_URL on the most relevant URL to get full content before answering.",
            }

            return ToolResult(True, output)

        except ImportError:
            return ToolResult(False, {}, error="duckduckgo-search not installed. Run: pip install duckduckgo-search")
        except Exception as e:
            return ToolResult(False, {}, error=f"Search failed: {e}")
