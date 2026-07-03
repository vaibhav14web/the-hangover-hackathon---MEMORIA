# Testing & Utilities Documentation

## Purpose
This suite provides unit tests to verify AST code parse extraction accuracy, citation regex matches, and diagnostic utilities to preload mock datasets without requiring remote API access.

## Responsibilities
- **Syntactic Parsing Verification**: Mocking Python source code strings and testing import, base class, async method, and global function extractions.
- **Reference Extraction Verification**: Validating that issue/PR tags and relative file paths are identified inside response texts.
- **Mock Preloading**: Providing automated scripts to load local developer schemas into the Cognee graph database for validation.

## Dependencies
- `pytest` (Testing executor framework)
- `cognee` (Graph indexing verification)

## Components & Files

### 1. `tests/test_ingestion.py`
Contains:
- `test_ast_parser_extracts_structures()`: Validates code classes, bases, methods, and functions.
- `test_markdown_formatter()`: Confirms AST structures are formatted correctly to Markdown.
- `test_github_client_url_parser()`: Validates regex matches on repository ownership endpoints.

### 2. `tests/test_reasoning.py`
Contains:
- `test_query_engine_extract_citations()`: Tests regex logic for recognizing `PR #\d+`, `Issue #\d+`, and local paths.

### 3. `scripts/preload_demo.py`
Executes:
- Formats mock Markdown documents simulating a load-balancer issue (#23) and migration pull request (#47).
- Wipes Cognee caches.
- Runs `cognee.add` and `cognee.cognify` to initialize the database with standard data.

## Running Tests & Preload Utility
Run the test suite:
```powershell
.\venv\Scripts\python.exe -m pytest tests/
```

Preload the mock database:
```powershell
.\venv\Scripts\python.exe scripts/preload_demo.py
```
