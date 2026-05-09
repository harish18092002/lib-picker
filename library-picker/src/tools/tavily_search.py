"""Tavily web search — wired into the agent via Anthropic tool use.

Exports
-------
- TAVILY_TOOL_SPEC : Anthropic tool definition Claude sees
- tavily_search()  : the function the agent loop calls when Claude requests it
"""

from __future__ import annotations

import os
from typing import Any

from tavily import TavilyClient

TAVILY_TOOL_SPEC: dict[str, Any] = {
    "name": "tavily_search",
    "description": (
        "Search the web for up-to-date information about software libraries. "
        "Use this for EVERY library you consider recommending, to verify: "
        "weekly downloads, last release date, GitHub stars, bundle size, and "
        "whether the project is actively maintained. Run multiple targeted "
        "queries per library if needed (e.g., one for npm/PyPI stats, one for "
        "the GitHub repo, one for bundle size on bundlephobia)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The web search query.",
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to return (1-10). Default 5.",
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["query"],
    },
}


_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    """Lazy singleton — avoids paying the import cost when the module loads."""
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY not set in .env")
        _client = TavilyClient(api_key=api_key)
    return _client


def tavily_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Run a Tavily search; return trimmed results.

    Tavily's full payload includes scores and raw HTML. We strip down to
    title/url/content snippet to keep the agent's context window lean.
    """
    response = _get_client().search(query=query, max_results=max_results)
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        }
        for r in response.get("results", [])
    ]
