#!/usr/bin/env python3
"""Run the movie recommendation agent: single query or interactive loop."""
import argparse
import sys

from haystack.dataclasses import ChatMessage

from agent import build_movie_agent


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
        print(result["last_message"].text)
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
        print("Assistant:", result["last_message"].text)


if __name__ == "__main__":
    main()
    sys.exit(0)
