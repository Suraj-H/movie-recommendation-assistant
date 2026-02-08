"""JSON Schema for the retrieval tool (agent tool call parameters)."""
from typing import Any

RETRIEVAL_TOOL_PARAMETERS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "top_k": {
            "type": "integer",
            "description": "number of movies to get",
            "default": 5,
        },
        "query": {
            "type": "string",
            "description": "query to retrieve movies based on semantic similarity of the description",
        },
        "metadata_filters": {
            "type": "object",
            "description": "metadata filters to filter the movies based on user's preference",
            "properties": {
                "operator": {
                    "type": "string",
                    "enum": ["AND", "OR", "NOT"],
                    "default": "AND",
                    "description": "operator to combine the conditions",
                },
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {
                                "type": "string",
                                "enum": [
                                    "meta.title",
                                    "meta.rating",
                                    "meta.genre",
                                    "meta.language",
                                ],
                            },
                            "operator": {
                                "type": "string",
                                "enum": ["==", "!=", ">", "<", ">=", "<=", "not in"],
                            },
                            "value": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "integer"},
                                    {"type": "array", "items": {"type": "string"}},
                                ]
                            },
                        },
                        "required": ["field", "operator", "value"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["operator", "conditions"],
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}
