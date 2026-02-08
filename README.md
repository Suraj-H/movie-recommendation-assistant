# Movie Recommendation Assistant

Uses **sparse vector search** (Qdrant + minicoil-v1), **metadata filtering**, and an **LLM agent** to answer natural language queries like “find me a highly-rated action movie about car racing” or “recommend five Japanese thrillers.”

**New here?** See **[FLOW.md](FLOW.md)** for a step-by-step explanation of how indexing and querying work so you can follow the flow yourself.

## Prerequisites

- Python 3.10+
- [Qdrant](https://qdrant.tech/) (cloud or self-hosted) with API URL and key
- [OpenAI](https://platform.openai.com/) API key

## Setup

1. **Clone and install**

   ```bash
   cd movie-recommendation-assistant
   pip install -r requirements.txt
   ```

2. **Environment**

   Copy `.env.example` to `.env` and set:

   - `OPENAI_API_KEY` – OpenAI API key
   - `QDRANT_URL` – Qdrant instance URL (e.g. `https://xxx.europe-west3-0.gcp.cloud.qdrant.io`)
   - `QDRANT_API_KEY` – Qdrant API key
   - `QDRANT_INDEX_NAME` – optional; default `movie-assistant`
   - `HF_TOKEN` – optional; [Hugging Face token](https://huggingface.co/settings/tokens) for faster dataset download when indexing

## Usage

### 1. Index movies (once)

Downloads the [Pablinho/movies-dataset](https://huggingface.co/datasets/Pablinho/movies-dataset), converts to documents, builds sparse embeddings, and writes to Qdrant.

```bash
python scripts/index_movies.py
```

- `--recreate`: recreate the index (default).
- `--no-recreate`: keep existing index and add/overwrite (use with care).
- If you see 400 errors for genre filters (e.g. sci-fi, "science fiction"), re-run indexing once so genres use the keyword-friendly format.

To free local disk space after indexing:
- Cached dataset: `./scripts/clear_dataset_cache.sh` (uses `~/.cache/huggingface/datasets/` or `HF_DATASETS_CACHE`).
- Cached embedding model (minicoil-v1): `./scripts/clear_embedding_model_cache.sh` (uses `~/.cache/huggingface/hub/` or `HUGGINGFACE_HUB_CACHE`). It will re-download on next index or query.

### 2. Query the agent

**Single query**

```bash
python scripts/query_agent.py "Find me a highly-rated action movie about car racing."
python scripts/query_agent.py "Recommend five Japanese thrillers."
```

**Streaming**

```bash
python scripts/query_agent.py --stream "Recommend five Japanese thrillers."
```

**Interactive**

```bash
python scripts/query_agent.py
# Then type your requests; type 'quit' or 'q' to exit.
```

### 3. Run the API (production / multiple users)

One process builds the agent once and serves all requests over HTTP.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or:

```bash
python scripts/run_server.py
```

- **GET /health** – readiness (no agent call). Returns `{"status": "ok", "agent_loaded": true}`.
- **POST /query** – body `{"query": "your natural language request"}`. Returns `{"response": "..."}`.

Example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Recommend one action movie"}'
```

Optional: set `ALLOWED_ORIGINS` (comma-separated) for CORS. For production, add auth (e.g. API key) and rate limiting (e.g. nginx or slowapi).

**Postman:** Import the collection from `postman/Movie_Recommendation_Assistant.postman_collection.json`. Optional: import `postman/Movie_Assistant_Local.postman_environment.json` and select it so `base_url` is `http://localhost:8000`.

## Project layout

- `config/` – env-based settings
- `data/` – dataset → Haystack documents, formatters
- `indexing/` – sparse embedder, Qdrant document store, index script
- `retrieval/` – sparse pipeline, filter retriever, unified retrieval function
- `tools/` – retrieval tool (parameters schema + Haystack Tool)
- `agent/` – system prompt, movie agent (LLM + tool)
- `app/` – FastAPI app, routes (`/query`, `/health`), schemas
- `agent/` – system prompt, movie agent, **factory** (shared by CLI and API)
- `scripts/` – `index_movies.py`, `query_agent.py`, `run_server.py`

## Sandbox / “Have I tested this?”

Run from **project root** (`movie-recommendation-assistant/`):

1. **Install:** `pip install -r requirements.txt`
2. **Imports only (no API keys):** `python scripts/verify_setup.py` – should print `OK: All imports and config load succeeded...`
3. **Env:** Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
4. **Index (once):** `python scripts/index_movies.py` – needs network + Qdrant; downloads Hugging Face dataset and writes to Qdrant
5. **Query (CLI):** `python scripts/query_agent.py "Find me a highly-rated action movie about car racing."` – needs indexed data + OpenAI + Qdrant
6. **API:** Start server (`uvicorn app.main:app --host 0.0.0.0 --port 8000`), then `curl http://localhost:8000/health` and `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"recommend one action movie"}'` – same env and indexed data

Steps 2–6 confirm end-to-end behavior in your environment.
