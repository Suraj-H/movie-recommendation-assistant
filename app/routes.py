"""API routes: /query, /query/stream, and /health."""
import asyncio
import json
import logging
import concurrent.futures
import queue
from typing import Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from haystack.dataclasses import ChatMessage

from app.schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()
AGENT_RUN_TIMEOUT_SEC = 60
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def _run_agent_with_timeout(agent: Any, messages: list, timeout: int) -> Any:
    future = _executor.submit(agent.run, messages)
    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        logger.warning("agent.run timed out after %s s", timeout)
        raise HTTPException(
            status_code=504,
            detail="Request timed out. Try a shorter query or try again.",
        )


def _run_agent_streaming(
    agent: Any, messages: list, chunk_queue: "queue.Queue[dict | None]",
) -> None:
    """Run agent with callback that pushes chunks into queue; puts None when done."""
    def streaming_callback(chunk: Any) -> None:
        content = getattr(chunk, "content", None)
        if content:
            chunk_queue.put({"type": "token", "content": content})

    try:
        agent.run(messages, streaming_callback=streaming_callback)
    finally:
        chunk_queue.put(None)


async def _stream_events(chunk_queue: "queue.Queue[dict | None]") -> Any:
    """Async generator: read from queue and yield SSE-formatted lines."""
    loop = asyncio.get_event_loop()
    while True:
        chunk = await loop.run_in_executor(_executor, chunk_queue.get)
        if chunk is None:
            break
        yield f"data: {json.dumps(chunk)}\n\n"


@router.get("/health")
def health(request: Request) -> dict:
    """Readiness: no agent call. Returns 200 if app and agent are loaded."""
    agent_loaded = getattr(request.app.state, "agent", None) is not None
    return {"status": "ok", "agent_loaded": agent_loaded}


@router.post("/query/stream")
async def query_stream(request: Request, body: QueryRequest) -> StreamingResponse:
    """Stream the agent response as Server-Sent Events (SSE). Each event: data: {\"type\":\"token\",\"content\":\"...\"}."""
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable. Agent not loaded.",
        )
    query_text = body.query.strip()
    if not query_text:
        raise HTTPException(status_code=422, detail="query must be non-empty after trim")

    chunk_queue: queue.Queue[dict | None] = queue.Queue()
    messages = [ChatMessage.from_user(query_text)]

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        _executor,
        _run_agent_streaming,
        agent,
        messages,
        chunk_queue,
    )
    return StreamingResponse(
        _stream_events(chunk_queue),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/query", response_model=QueryResponse)
def query(request: Request, body: QueryRequest) -> QueryResponse:
    """Run the movie recommendation agent on the given query."""
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        logger.error("agent not in app.state")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable. Agent not loaded.",
        )
    query_text = body.query.strip()
    if not query_text:
        raise HTTPException(status_code=422, detail="query must be non-empty after trim")
    messages = [ChatMessage.from_user(query_text)]
    try:
        result = _run_agent_with_timeout(
            agent, messages, timeout=AGENT_RUN_TIMEOUT_SEC
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("agent.run failed")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        ) from e
    text = result.get("last_message")
    if text is None:
        raise HTTPException(
            status_code=500,
            detail="Invalid agent response. Please try again.",
        )
    response_text = getattr(text, "text", None) or getattr(text, "content", "") or ""
    return QueryResponse(response=response_text)
