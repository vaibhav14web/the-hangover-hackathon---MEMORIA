# API Module Documentation

## Purpose
The **API Module** serves as the public REST API surface of the Memoria engine. It exposes HTTP endpoints for triggering repository imports, tracking the status of background ingestion tasks, issuing reasoning queries, and checking service health.

## Responsibilities
- **Request Validation**: Enforcing input schemas for repository URLs and reasoning query strings.
- **Asynchronous Execution**: Scheduling repository ingestion processes to run in the background.
- **Routing & Mounting**: Hosting specific endpoints for ingestion and reasoning services.
- **CORS Handling**: Allowing connections from cross-origin clients.
- **Logging & Monitoring**: Logging start/success/failure durations for endpoints and validating health checks.

## Dependencies
- `fastapi` (Web API framework)
- `pydantic` (Input/Output data validation schemas)
- `uvicorn` (ASGI server runner)

## Components & Files

### 1. `schemas.py`
Defines validation models:
- `ImportRepoRequest`: Validates GitHub repository URLs.
- `QueryRequest`: Validates reasoning search questions.
- `CitationSchema`: Standard structure for reference references (PR/Issue numbers, File paths).
- `QueryResponse`: Formats the query execution answer and list of citations.
- `StatusResponse`: Details the status of background ingestion jobs (`idle`, `ingesting`, `success`, `failed`).
- `HealthResponse`: Standard health status confirmation.

### 2. `routes/ingest.py`
Hosts the ingestion status state machine and routes:
- `POST /repositories/import`: Starts background ingestion of a given repository. Returns `202 Accepted`.
- `GET /repositories/status`: Returns current progress info (or result details) of the ingestion system.

### 3. `routes/query.py`
Hosts the query router:
- `POST /query`: Submits query to `QueryEngine` and returns LLM-backed answers and evidence blocks.

### 4. `main.py`
- Main entry point.
- Registers standard logging, CORS middleware policies, mounts routers, and defines `GET /health`.

## Starting the API Server
Run the FastAPI application locally using uvicorn:
```powershell
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
```
