# Graph Module Documentation

## Purpose
The **Graph Module** handles structured modeling of software engineering concepts (repositories, developers, pull requests, issues, files, classes, and functions) and interfaces with the **Cognee Graph Engine**. It builds and persists the long-term relational memory of the repository context.

## Responsibilities
- **Domain Modeling**: Defining nodes and relationships representing software constructs using Pydantic schemas.
- **Data Integration**: Sending raw markdown pages or structured `DataPoint` classes to Cognee database storage.
- **Cognitive Pipeline Execution (`cognify`)**: Triggering semantic entity extraction, relation mapping, embedding generation, and graph compilation.
- **Pruning**: Clearing graph storage metadata, vectors, and relational stores.
- **Graph Retrieval**: Providing multi-hop search operations over vector and graph memory.

## Dependencies
- `cognee` (Base graph engine framework)
- `pydantic` (Data schema validations)

## Components & Files

### 1. `entities.py`
Defines standard entities that can be identified and linked inside the codebase graph context:
- `Developer`: Identifies committers, pull request creators, and issue reporters.
- `Repository`: Metadata about the root software repository.
- `PullRequest`: Standard PR details.
- `Issue`: Standard issue details.
- `File`: Path and import structures of code or text files.
- `ClassEntity`: Syntactic representation of classes (bases, methods).
- `FunctionEntity`: Syntactic representation of functions/methods (arguments, returns, async status).

### 2. `cognee_client.py`
Provides a unified client wrapper class `CogneeClient`:
- `prune_memory()`: Resets all database files.
- `add_documents(documents, dataset_name)`: Enqueues text strings for parsing.
- `add_structured_points(data_points)`: Inserts raw custom typed nodes.
- `build_graph()`: Performs entity extraction, vector embedding, and graph persistence (`cognee.cognify()`).
- `search_memory(query, search_type)`: Performs lookup using standard Cognee search types (e.g. `RAG_COMPLETION`, `GRAPH_COMPLETION`).

## Example Usage
```python
import asyncio
from graph.cognee_client import CogneeClient
from graph.entities import Developer, Repository
from cognee.api.v1.search import SearchType

async def test_graph():
    client = CogneeClient()
    
    # Reset
    await client.prune_memory()
    
    # Insert structured data
    dev = Developer(username="vaibhav-singh")
    repo = Repository(name="Memoria", owner="vaibhav-singh", url="https://github.com/vaibhav-singh/memoria")
    
    await client.add_structured_points([dev, repo])
    await client.build_graph()
    
    # Query
    result = await client.search_memory("Who is the owner of Memoria?", SearchType.RAG_COMPLETION)
    print(result)

if __name__ == "__main__":
    asyncio.run(test_graph())
```
