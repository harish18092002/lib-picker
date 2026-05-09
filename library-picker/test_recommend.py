"""Phase 2 live demo — real library recommendation with Tavily web search.

Usage:
    python test_recommend.py
    python test_recommend.py "your requirement here"
"""

import sys

from src.agent import LibraryPicker


def main() -> None:
    query = " ".join(sys.argv[1:]) or "lightweight charting in React, no D3"

    print("=" * 70)
    print(f"Library Picker — query: {query}")
    print("=" * 70)
    print()

    agent = LibraryPicker(verbose=True)
    print("Researching...")
    response = agent.run(query)

    print()
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print()
    print(response)


if __name__ == "__main__":
    main()
