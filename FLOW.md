# How the Movie Recommendation Assistant Works

This document explains the full flow so you can understand what happens from setup to answer. No prior knowledge of the codebase is required.

---

## Overview in One Paragraph

You run an **indexing script once** to load a movie dataset, turn each movie into a searchable “document” with a sparse vector and metadata (genre, rating, language), and store everything in **Qdrant**. When you **query**, an **LLM agent** reads your natural language request, decides how to search (by meaning and/or by filters), calls a **retrieval tool** that talks to Qdrant, gets back a list of movies, and then writes a friendly answer for you.

---

## Two Phases

| Phase | When | What it does |
|-------|------|----------------|
| **Indexing** | Once (or when you refresh the data) | Load movies → convert to documents → create sparse vectors → save to Qdrant |
| **Querying** | Every time you ask a question | Your question → agent → retrieval from Qdrant → LLM writes the answer |

---

## Phase 1: Indexing (One-Time Setup)

This is what runs when you execute:

```bash
python scripts/index_movies.py
```

### Step-by-step

1. **Load the dataset**  
   The script downloads the **Pablinho/movies-dataset** from Hugging Face (train split). Each row is one movie with fields like title, overview, genre, rating, language.

2. **Convert rows to documents**  
   Each movie row is turned into a **Haystack Document** with:
   - **content**: the movie overview (plot/description)
   - **meta**: title, rating (number), genre (list of strings, e.g. `["action", "drama"]`), language (e.g. `"en"`, `"ja"`)

   Text is sanitized and lengths are capped so nothing breaks later.

3. **Create sparse embeddings**  
   A **sparse embedder** (minicoil-v1) runs on each document. It uses:
   - The **content** (overview)
   - The **title** (from meta)

   so that later we can search by “meaning” (e.g. “car racing”, “courtroom drama”), not just keywords.

4. **Write to Qdrant**  
   Each document (with its sparse vector and metadata) is written to a **Qdrant** index. The index is configured so we can:
   - Search by **sparse vector** (semantic search)
   - Filter by **metadata** (genre, rating, language, etc.)

After this, the “movie database” your assistant uses is that Qdrant index.

---

## Phase 2: Querying (Every Request)

This is what runs when you execute, for example:

```bash
python scripts/query_agent.py "Find me a highly-rated action movie about car racing."
```

### Step-by-step

1. **Start the agent**  
   The script:
   - Loads settings from `.env` (OpenAI and Qdrant credentials)
   - Connects to the **same Qdrant index** (read-only, no recreate)
   - Builds a **sparse search pipeline** (embed query text → search Qdrant by vector)
   - Builds a **filter retriever** (search Qdrant by metadata only)
   - Wraps both in a single **retrieval function** and then in a **Tool** the agent can call
   - Creates the **Agent**: an LLM (e.g. gpt-4o-mini) + system prompt + that one retrieval tool

2. **You send a message**  
   Your sentence is turned into a user message and passed to the agent.

3. **Agent runs (LLM + tool)**  
   - The **LLM** reads your message and the **system prompt**. The prompt tells it:
     - It has a tool called `retrieval_tool` to get movies from the database
     - When to use a **text query** (plot/themes), when to use **metadata filters** (genre, rating, language), and when to use both
     - To output a **tool call** with parameters: `query`, `metadata_filters`, `top_k`
   - The LLM decides to call the tool and chooses parameters, e.g.:
     - `query`: `"action movie about car racing"`
     - `metadata_filters`: e.g. rating ≥ 7, genre = action
     - `top_k`: 5 (how many movies to fetch)

4. **Tool runs (retrieval)**  
   The **retrieval function** receives those parameters:
   - If there is a **query**: it embeds the query with the same sparse model, then runs a **sparse vector search** in Qdrant (optionally applying the metadata filters), and returns up to `top_k` documents.
   - If there is **no query** but only **metadata_filters**: it uses the **filter retriever** to get documents that match the filters, then returns up to `top_k` of them.

5. **Tool result → string**  
   The list of documents is turned into one string (title, overview, rating, genres per movie) by a formatter and passed back to the LLM as the **tool result**.

6. **LLM writes the answer**  
   The LLM sees your original question and the tool result (the list of movies). It then writes a natural-language reply (e.g. “Here are some highly-rated action movies about car racing: …”) and the script prints that as the assistant’s answer.

---

## Visual Flow (Query Path)

```
You type: "Find me a highly-rated action movie about car racing"
                    │
                    ▼
         ┌──────────────────────┐
         │  Movie Agent (LLM +   │
         │  retrieval_tool)      │
         └──────────┬───────────┘
                    │
                    ▼
         LLM chooses tool call:
         • query = "action movie about car racing"
         • metadata_filters = rating ≥ 7, genre = action
         • top_k = 5
                    │
                    ▼
         ┌──────────────────────┐
         │  retrieval_function  │
         └──────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Sparse pipeline          Filter retriever
  (embed query → search     (metadata only)
   Qdrant with filters)            │
        │                         │
        └───────────┬─────────────┘
                    ▼
         List of movie Documents
                    │
                    ▼
         movie_to_string() → one text block
                    │
                    ▼
         LLM reads tool result → writes final answer
                    │
                    ▼
         You see: "Here are some highly-rated action movies..."
```

---

## Where Things Live in the Project

| What you care about | Where it is |
|----------------------|-------------|
| Turning dataset rows into documents | `data/movie_to_document.py` |
| Formatting retrieved movies for the LLM | `data/formatters.py` |
| Sparse embeddings (indexing) | `indexing/embedder.py` |
| Qdrant connection and index config | `indexing/document_store.py` |
| Sparse search pipeline (query → Qdrant) | `retrieval/pipeline.py` |
| Metadata-only search | `retrieval/filter_retriever.py` |
| One function that does both types of search | `retrieval/retrieval_function.py` |
| Tool the LLM calls (name, params, formatter) | `tools/retrieval_tool.py`, `tools/parameters.py` |
| Instructions for the LLM (when to use query/filters) | `agent/prompt.py` |
| Agent (LLM + tool) | `agent/movie_agent.py` |
| Indexing entrypoint | `scripts/index_movies.py` |
| Query entrypoint | `scripts/query_agent.py` |

---

## Quick Reference: Commands

```bash
# 1. Install and set .env (see README)
pip install -r requirements.txt
# Copy .env.example to .env and fill OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

# 2. Index movies (once)
python scripts/index_movies.py

# 3. Ask the assistant
python scripts/query_agent.py "Your question here"

# Optional: stream the reply
python scripts/query_agent.py --stream "Your question here"

# Optional: interactive mode (multiple questions)
python scripts/query_agent.py
```

With this, a new user can follow the flow from “what do I run?” to “how does my question become an answer?” by reading this markdown.
