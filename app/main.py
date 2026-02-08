"""FastAPI app: agent built once at startup, reused for all requests."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent.factory import build_movie_agent
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

ALLOWED_ORIGINS_ENV = "ALLOWED_ORIGINS"
DEFAULT_ORIGINS = ""


def _cors_origins() -> list[str]:
    raw = os.environ.get(ALLOWED_ORIGINS_ENV, DEFAULT_ORIGINS).strip()
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build agent once at startup; store in app.state."""
    try:
        agent = build_movie_agent()
        app.state.agent = agent
        logger.info("Agent built and attached to app.state")
    except Exception as e:
        logger.exception("Failed to build agent at startup")
        raise RuntimeError("Startup failed: agent could not be built") from e
    yield
    # Shutdown: uvicorn waits for in-flight requests; no extra teardown here


app = FastAPI(
    title="Movie Recommendation Assistant API",
    description="Query the movie recommendation agent via HTTP.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, tags=["query"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Log and return generic 500; avoid leaking internals. Let HTTPException through."""
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
