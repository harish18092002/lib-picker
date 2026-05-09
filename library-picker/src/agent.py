"""Library Picker agent — Phase 1 scaffold (persona + environment only).

Architecture
------------
- LLM:           Anthropic Claude (claude-opus-4-7 by default)
- Search tool:   Tavily (wired in Phase 2 via Anthropic tool use)
- Prompt store:  prompts/system_prompt.md  (externalized for easy iteration)
- Config:        .env (ANTHROPIC_API_KEY, TAVILY_API_KEY)

Phase 1 contract
----------------
LibraryPicker.run(user_input) -> str
    Single-turn chat with the persona loaded as `system`. No tools yet.

Phase 2 contract (planned)
--------------------------
The agent will expose a `tavily_search` tool to Claude. The model decides
when to call it; we run the loop until `stop_reason != "tool_use"`. Every
library it recommends must be backed by at least one search result.
"""

from __future__ import annotations

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

# Latest Opus model. Override via LibraryPicker(model=...) for evals or A/B tests.
DEFAULT_MODEL = "claude-opus-4-7"
MAX_TOKENS = 1024


class LibraryPicker:
    """Pragmatic senior-dev agent that recommends libraries.

    Phase 1: persona-only chat (no tools).
    Phase 2: Tavily web search wired in as an Anthropic tool — every
    recommendation must be verified via search before it's returned.
    """

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        load_dotenv(PROJECT_ROOT / ".env")

        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in."
            )

        # Tavily key isn't required in Phase 1, but warn early so Phase 2 isn't blocked.
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_key:
            print("[warn] TAVILY_API_KEY not set — required for Phase 2 web search.")

        self.client = Anthropic(api_key=anthropic_key)
        self.model = model
        self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, user_input: str) -> str:
        """Send a single user message to Claude with the Library Picker persona."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_input}],
        )
        return "".join(block.text for block in response.content if block.type == "text")
