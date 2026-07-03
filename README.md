# Codebase Oracle (Memoria)

> Forensic reasoning over FastAPI's architecture using Cognee Knowledge Graphs.

---

## 1. The Problem
Codebases accumulate institutional knowledge in PRs and issues. Current tools (Cursor, Copilot) see **WHAT** the code is, not **WHY** decisions were made. When engineers leave, that **WHY** is lost forever.

## 2. The Solution
Codebase Oracle captures the historical context of a repository using a knowledge graph. By ingesting issues, pull request threads, and metadata into **Cognee**, it enables multi-hop reasoning across decisions, relationships, and code changes rather than performing flat vector chunk search.

## 3. Why Cognee Specifically
Traditional RAG relies on pure semantic embeddings, which fail when trying to connect disparate pieces of historical evidence. Cognee builds deterministic entity-relationship graphs. For example, when asking *"What broke when FastAPI refactored Depends to use dataclasses?"*, Cognee traverses:
$$\text{PR \#14254 (Depends dataclass refactor)} \longrightarrow \text{Cadwyn library breakage (Depends/Security unhashable)} \longrightarrow \text{PR \#14320 (Restored hashability fix)}$$
all in a single query. It is the entity connections that enable true "forensic reasoning" over codebases.

---

## 4. Architecture Diagram

```
                 +-------------------+
                 |    GitHub PRs     |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Ingestion Pipeline| (PR Scraping & Formatting)
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |   Cognee Graph    | (90 Nodes, 120 Edges, SQLite/LanceDB)
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |   Query Engine    | (Hybrid direct/graph routing)
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |    LLM Layer      | (LiteLLM with Rate-Limit retries)
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |   User Interface  | (Streamlit Frontend)
                 +-------------------+
```

---

## 5. Setup & Execution

### Prerequisites
* Python 3.11.7
* SQLite3

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file in the root directory:
```env
LLM_MODEL=groq/llama-3.3-70b-versatile
LLM_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

### Step 3: Run the API Server (Globally accessible on port 8000)
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Run the Streamlit Interface (Globally accessible on port 8501)
```bash
python -m streamlit run ui/app.py --server.address 0.0.0.0 --server.port 8501
```

---

## 6. Demo Questions & Expected Answers

1. **"Why did FastAPI migrate to Pydantic v2?"**
   * *Expected Answer*: FastAPI migrated to Pydantic v2 to gain major performance improvements due to Pydantic's Rust core, while introducing a backward compatibility layer (`pydantic.v1`) to prevent downstream breakage.
   * *Source*: `PR #9816`

2. **"What broke when FastAPI refactored Depends to use dataclasses?"**
   * *Expected Answer*: The `Cadwyn` library broke because `Depends` and `Security` were no longer hashable after the dataclass refactoring, which was subsequently fixed by restoring hashability.
   * *Source*: `PR #14254`

3. **"What new capabilities does PR 15745 unlock for FastAPI users?"**
   * *Expected Answer*: Refactors FastAPI internals to preserve `APIRouter` and `APIRoute` instances rather than copying/cloning them. This enables adding routes dynamically after a router is included, including subrouters before their routes are defined, custom request matching using `.matches()` and `.handle()`, and unblocks future per-router middleware/exceptions/dependencies.
   * *Source*: `PR #15745`

---

## 7. Tech Stack
* **Knowledge Graph Engine**: Cognee v1.2.2 (LanceDB + SQLite)
* **LLM Reasoning**: LiteLLM (Groq Llama 3.3 70B with auto-fallback to Llama 3.1 8B on token rate limits)
* **Backend Web Framework**: FastAPI
* **Frontend Web Framework**: Streamlit

