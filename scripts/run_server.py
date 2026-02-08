#!/usr/bin/env python3
"""Run the FastAPI server (agent built once at startup)."""
import sys
from pathlib import Path

# Project root on path so "app" resolves when run from any CWD
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
