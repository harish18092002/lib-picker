"""Interactive Library Picker — loads project context, accepts terminal queries.

Flow:
1. Reads `context.md` (project description: stack, constraints, conventions).
2. Loops on stdin: each line is a library requirement.
3. For each requirement, the agent uses Tavily to verify everything before
   returning the top-3 picks scoped to your stack.
4. Type 'exit', 'quit', or hit Ctrl-D to leave.

Usage:
    python demo.py
"""

import sys
from pathlib import Path

from src.agent import LibraryPicker

PROJECT_ROOT = Path(__file__).resolve().parent
CONTEXT_PATH = PROJECT_ROOT / "context.md"

BANNER = "=" * 70
PROMPT = "\n> "


def main() -> None:
    if not CONTEXT_PATH.exists():
        print(f"[error] {CONTEXT_PATH.name} not found in {PROJECT_ROOT}.")
        sys.exit(1)

    context = CONTEXT_PATH.read_text(encoding="utf-8").strip()

    print(BANNER)
    print("Library Picker — interactive demo")
    print(BANNER)
    print(f"Loaded {CONTEXT_PATH.name} ({len(context):,} chars)")
    print()
    print("Project context preview:")
    preview = "\n".join("  " + line for line in context.splitlines()[:8])
    print(preview)
    print("  ...")
    print()
    print("Ask for any library you need. Recommendations will be scoped to the stack above.")
    print("Type 'exit' (or Ctrl-D) to quit.")

    agent = LibraryPicker(verbose=True)

    while True:
        try:
            query = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return

        if not query:
            continue
        if query.lower() in {"exit", "quit", ":q"}:
            print("bye.")
            return

        framed = (
            "I'm working on the project below. Recommend libraries that fit this "
            "stack and constraints — match the language, framework, ecosystem, "
            "license, and bundle-size limits. Don't recommend anything listed "
            "under 'Already chosen'.\n\n"
            f"--- PROJECT CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
            f"Requirement: {query}"
        )

        print("\nResearching...")
        try:
            response = agent.run(framed)
        except Exception as exc:
            print(f"\n[error] {type(exc).__name__}: {exc}")
            continue

        print()
        print(BANNER)
        print(response)
        print(BANNER)


if __name__ == "__main__":
    main()
