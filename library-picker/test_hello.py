"""Phase 1 smoke test — confirms API key works and the persona loads."""

from src.agent import LibraryPicker


def main() -> None:
    agent = LibraryPicker()
    response = agent.run("Hello, introduce yourself in one sentence.")
    print(response)


if __name__ == "__main__":
    main()
