"""Request/response models for the API."""
from pydantic import BaseModel, Field

QUERY_MIN_LEN = 1
QUERY_MAX_LEN = 2000


class QueryRequest(BaseModel):
    """Body for POST /query."""

    query: str = Field(
        ...,
        min_length=QUERY_MIN_LEN,
        max_length=QUERY_MAX_LEN,
        description="Natural language movie request.",
    )

    model_config = {"str_strip_whitespace": True}


class QueryResponse(BaseModel):
    """Response for POST /query."""

    response: str = Field(..., description="Agent reply text.")
