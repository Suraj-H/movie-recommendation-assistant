"""Haystack Tool that wraps the retrieval function for the agent."""
from typing import Callable

from haystack.tools import Tool

from data.formatters import movie_to_string
from tools.parameters import RETRIEVAL_TOOL_PARAMETERS


def create_retrieval_tool(
    retrieval_function: Callable[..., list],
) -> Tool:
    """Build the retrieval_tool for the agent."""
    return Tool(
        name="retrieval_tool",
        description="Use this tool to get movies fitting to the user criteria",
        function=retrieval_function,
        parameters=RETRIEVAL_TOOL_PARAMETERS,
        outputs_to_string={"source": "documents", "handler": movie_to_string},
    )
