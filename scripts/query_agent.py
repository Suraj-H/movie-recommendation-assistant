#!/usr/bin/env python3
"""Run the movie recommendation agent: single query or interactive loop."""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path (works when run from any CWD or via IDE)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from haystack.dataclasses import ChatMessage

from agent import build_movie_agent


def _get_final_reply_text(result: dict) -> str:
    """Extract the final assistant reply, skipping tool-call-only messages (e.g. raw JSON)."""
    messages = result.get("messages") or []
    # Walk backwards to find last assistant message with real reply text (not tool-call JSON)
    for msg in reversed(messages):
        if getattr(msg, "role", None) != "assistant":
            continue
        text = getattr(msg, "text", None) or ""
        if not text or not text.strip():
            continue
        stripped = text.strip()
        # Skip messages that look like retrieval_tool call JSON
        if stripped.startswith("{") and "metadata_filters" in stripped and "operator" in stripped:
            continue
        if stripped.startswith("```JSON") and "metadata_filters" in stripped:
            continue
        return text
    # Fallback to last_message
    last = result.get("last_message")
    return getattr(last, "text", None) or "" if last else ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the movie recommendation agent."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Single query. If omitted, run in interactive mode.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the assistant response.",
    )
    args = parser.parse_args()

    agent = build_movie_agent()

    if args.query:
        messages = [ChatMessage.from_user(args.query)]
        if args.stream:
            from haystack.components.generators.utils import print_streaming_chunk
            result = agent.run(messages, streaming_callback=print_streaming_chunk)
        else:
            result = agent.run(messages)
        print(_get_final_reply_text(result))
        return

    # Interactive
    print("Movie Recommendation Assistant. Type your request (or 'quit' to exit).")
    while True:
        try:
            line = input("\nYou: ").strip()
        except EOFError:
            break
        if not line or line.lower() in ("quit", "exit", "q"):
            break
        messages = [ChatMessage.from_user(line)]
        if args.stream:
            from haystack.components.generators.utils import print_streaming_chunk
            result = agent.run(messages, streaming_callback=print_streaming_chunk)
        else:
            result = agent.run(messages)
        print("Assistant:", _get_final_reply_text(result))


if __name__ == "__main__":
    main()
    sys.exit(0)
