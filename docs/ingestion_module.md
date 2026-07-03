# Ingestion Module Documentation

## Purpose
The **Ingestion Module** is responsible for importing raw software engineering artifacts into Memoria. It acts as the gateway of the engine, parsing local files, scraping GitHub metadata, and translating them into standard Markdown schemas designed for Cognee's ingestion layers.

## Responsibilities
- **Repository Ingestion**: Cloning local and remote Git repositories.
- **AST Code Parsing**: Traversing Python directories and extracting classes, functions, docstrings, methods, and dependencies.
- **Metadata Scraping**: Querying the GitHub API (via `PyGithub`) to download Issues and Pull Request comments.
- **PR Code Diff Extraction**: Scraping raw diff files for pull requests to identify affected modules, lines added, and lines removed.
- **Normalization**: Translating code files, AST schemas, Issues, and PR structures into highly readable Markdown pages.

## Dependencies
- `pygithub` (GitHub REST API access)
- `GitPython` (Git repository clone & pull)
- `requests` (Raw diff download)
- `cognee` (Graph & vector storage integration)

## Components & Files

### 1. `github_client.py`
- **Inputs**: Repository GitHub URL (e.g. `https://github.com/owner/repo`), optional `GITHUB_TOKEN`.
- **Outputs**: Dictionary of repository metadata, list of standard issue objects, list of pull requests.
- **Example Usage**:
```python
from ingestion.github_client import GitHubClient

client = GitHubClient(token="YOUR_GITHUB_TOKEN")
repo_info = client.get_repo_info("https://github.com/fastapi/fastapi")
issues = client.get_issues("https://github.com/fastapi/fastapi")
```

### 2. `ast_parser.py`
- **Inputs**: Absolute path to a Python source file.
- **Outputs**: Dictionary containing imports, classes (with bases and methods), and global functions.
- **Example Usage**:
```python
from ingestion.ast_parser import parse_file, format_parsed_info_to_markdown

info = parse_file("api/main.py")
markdown_doc = format_parsed_info_to_markdown(info)
```

### 3. `pipeline.py`
- **Inputs**: GitHub repository URL, optional dataset name.
- **Outputs**: Dictionary detailing the status of the run, counts of documents, issues, and PRs ingested.
- **Example Usage**:
```python
import asyncio
from ingestion.pipeline import IngestionPipeline

async def main():
    pipeline = IngestionPipeline(github_token="YOUR_TOKEN")
    result = await pipeline.ingest("https://github.com/owner/repo")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. `pr-scrapper.py`
- **Inputs**: GitHub repository URL, Pull Request number.
- **Outputs**: Markdown summary of the changes, showing additions, deletions, and diff code blocks.
- **Example Usage**:
```python
from ingestion.pr_scrapper import PRScrapper

scrapper = PRScrapper(token="YOUR_TOKEN")
summary = scrapper.summarize_pr_changes("https://github.com/owner/repo", 47)
```
