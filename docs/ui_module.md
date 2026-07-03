# UI Module Documentation

## Purpose
The **UI Module** provides an interactive, dark-themed Streamlit dashboard for developer interaction. It integrates with the FastAPI endpoints, providing search fields, log stream visibility, visual graphs, and administrator reset controls.

## Responsibilities
- **Question & Answering Interface**: Interactive chat rendering with foldable cards for evidence details and references.
- **Relational Map Visualizer**: Generating topological graphs using `networkx` and `matplotlib` to illustrate files, issues, and PR connections.
- **Job Status Polling**: Querying background worker progress indicators and printing active operations.
- **Control Center Management**: Triggering database reset routines via standard POST calls.

## Dependencies
- `streamlit` (App dashboard runner)
- `networkx` (Network graph models)
- `matplotlib` (Graph plotting visualization)
- `requests` (Communication with FastAPI routes)

## Components & Files

### 1. `app.py`
Exposes the single-page wide layout dividing features into tabs:
- **Sidebar Diagnostics**: Confirms API connectivity status and displays active LLM models.
- **Tab 1: Chat Interface**: Supports query inputs, maintains session-based chat history, and highlights citations.
- **Tab 2: Graph Explorer**: Dynamically drafts visual graphs mapping files, issues, PRs, and developers.
- **Tab 3: Control Center**: Input field for importing a repository, a button to poll import jobs, and a memory prune trigger.

## Launching the UI App
Start the Streamlit dashboard server:
```powershell
.\venv\Scripts\streamlit.exe run ui/app.py --server.port 8501
```
The dashboard will open automatically in your browser at `http://localhost:8501`.
