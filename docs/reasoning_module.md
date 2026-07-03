# Reasoning Module Documentation

## Purpose
The **Reasoning Module** performs query comprehension, evidence aggregation, and response formulation. It coordinates with the graph layers to extract relevant entities/context, passes them into LiteLLM (prompting Groq's Llama 3.3-70b model), enforces anti-hallucination guardrails, and extracts reference citations.

## Responsibilities
- **Context Synthesis**: Gathering and formatting graph and vector outputs into unified retrieved contexts.
- **Explainable Answering**: Prompting the LLM using zero-temperature parameters for deterministic, evidence-grounded answers.
- **Citation Extraction**: Scanning response strings and retrieved contexts for code filenames (`*.py`), Issue numbers (`#\d+`), and PR numbers (`#\d+`) to map them to discrete objects.
- **Anti-Hallucination Guardrails**: Forcing the LLM to output "I do not have enough evidence to answer confidently." when the graph has no related records.

## Dependencies
- `litellm` (LLM communication abstraction layer)
- `cognee` (Graph semantic lookup context)
- `re` (Regex-based citation parser)

## Components & Files

### 1. `llm_layer.py`
- **Inputs**: Query string, formatted retrieved context string, optional model override.
- **Outputs**: Plain text answer returned by the LLM.
- **Example Usage**:
```python
import asyncio
from reasoning.llm_layer import query_llm

async def run():
    ans = await query_llm("Why did we use JWT?", "PR #47 changed authentication to JWT because sessions do not scale.")
    print(ans)

if __name__ == "__main__":
    asyncio.run(run())
```

### 2. `query_engine.py`
Provides `QueryEngine` class:
- `execute_query(query)`: High-level execution step.
  1. Searches graph memory using multiple types (`GRAPH_COMPLETION`, `RAG_COMPLETION`).
  2. Synthesizes search output.
  3. Invokes LLM reasoning via `llm_layer.py`.
  4. Parses, structures, and deduplicates citations.
  5. Returns structured dictionary containing `query`, `answer`, `evidence`, and `citations`.
- **Example Usage**:
```python
import asyncio
from reasoning.query_engine import QueryEngine

async def run():
    engine = QueryEngine()
    result = await engine.execute_query("Why did authentication change to JWT?")
    print("Answer:", result["answer"])
    print("Citations:", result["citations"])

if __name__ == "__main__":
    asyncio.run(run())
```
