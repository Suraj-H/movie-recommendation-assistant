"""Movie recommendation agent (LLM + retrieval tool)."""
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.tools import Tool

from agent.prompt import SYSTEM_PROMPT

CHAT_MODEL = "gpt-4o-mini"


def create_movie_agent(retrieval_tool: Tool) -> Agent:
    """Build the movie agent with the given retrieval tool."""
    return Agent(
        chat_generator=OpenAIChatGenerator(model=CHAT_MODEL),
        system_prompt=SYSTEM_PROMPT,
        tools=[retrieval_tool],
    )
