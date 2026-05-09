"""Library Picker agent — Phase 2 (Tavily web search via Anthropic tool use).

Architecture
------------
- LLM:           Anthropic Claude (claude-opus-4-7)
- Search tool:   Tavily, exposed to Claude via tool use
- Prompt store:  prompts/system_prompt.md  (externalized for easy iteration)
- Config:        .env (ANTHROPIC_API_KEY, TAVILY_API_KEY)

The agent loop
--------------
1. Send user query + system prompt + tavily_search tool to Claude.
2. While stop_reason == "tool_use":
     - run each tool_use block
     - feed results back as a user-turn tool_result message
3. Return the final assistant text once stop_reason == "end_turn".

Adaptive thinking is on so Claude can plan multi-step research
(query → read results → query a different angle → synthesize).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from src.tools import TAVILY_TOOL_SPEC, tavily_search

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

DEFAULT_MODEL = "claude-opus-4-7"
MAX_TOKENS = 8192
MAX_TOOL_ITERATIONS = 12


class LibraryPicker:
    """Pragmatic senior-dev agent that recommends libraries.

    Verifies every recommendation with at least one Tavily search.
    """

    def __init__(self, model: str = DEFAULT_MODEL, *, verbose: bool = True) -> None:
        load_dotenv(PROJECT_ROOT / ".env")

        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in."
            )
        if not os.getenv("TAVILY_API_KEY"):
            raise RuntimeError(
                "TAVILY_API_KEY not set. Required for Phase 2 web search."
            )

        self.client = Anthropic(api_key=anthropic_key)
        self.model = model
        self.verbose = verbose
        self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, user_input: str) -> str:
        """Take a plain-English requirement, return the final recommendation."""
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_input}]

        for iteration in range(MAX_TOOL_ITERATIONS):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=[TAVILY_TOOL_SPEC],
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": self._run_tools(response.content)})
                continue

            if response.stop_reason in ("end_turn", "stop_sequence", "max_tokens"):
                return self._extract_text(response.content)

            if response.stop_reason == "refusal":
                return f"[refusal] {self._extract_text(response.content) or 'Claude declined the request.'}"

            return f"[unexpected stop_reason={response.stop_reason}]\n{self._extract_text(response.content)}"

        return "[error] Max tool iterations reached without a final answer."

    def _run_tools(self, content) -> list[dict[str, Any]]:
        """Execute every tool_use block in `content` and return tool_result blocks."""
        results: list[dict[str, Any]] = []
        for block in content:
            if block.type != "tool_use":
                continue
            if block.name == "tavily_search":
                query = block.input.get("query", "")
                if self.verbose:
                    print(f"  [search] {query}")
                try:
                    payload = tavily_search(**block.input)
                    body = json.dumps(payload, ensure_ascii=False)
                    is_error = False
                except Exception as exc:
                    body = f"Search failed: {type(exc).__name__}: {exc}"
                    is_error = True
                    if self.verbose:
                        print(f"  [search-error] {body}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": body,
                    "is_error": is_error,
                })
            else:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Unknown tool: {block.name}",
                    "is_error": True,
                })
        return results

    @staticmethod
    def _extract_text(content) -> str:
        return "".join(block.text for block in content if block.type == "text")
