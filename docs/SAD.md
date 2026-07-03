# SAD — Codebase Oracle (Memoria)
**Status:** Provisional — reasoning layer (§5) unvalidated against multi-hop requirement

## 1. Architecture Overview
```
GitHub (PRs, issues)
   → ingestion/github_client.py   (fetch raw data, rate-limit safe)
   → graph/builder.py             (format + filter + inject manual context)
   → graph/manual_context.py      (hardcoded rationale for thin-body PRs)
   → Cognee (cognify)             (builds entity/relationship graph)
   → reasoning/query_engine.py    (queries Cognee graph)
   → reasoning/llm_layer.py       (LLM composes cited natural-language answer)
   → api/ (FastAPI)               (exposes ingest + query endpoints)
   → ui/app.py (Streamlit)        (judge-facing interface)
```
Six stages. Stages 1-3 are validated and **protected — do not modify without explicit approval** (see constraints doc). Stages 4-6 are partially built or unbuilt as of this writing.

## 2. Component Status
| Component | File | Status |
|---|---|---|
| GitHub client | `ingestion/github_client.py` | Done, validated. Rate-limit retry wrapper (`_safe_call`). `get_specific_prs()` fetches by curated PR number list. |
| PR formatter | `graph/builder.py` | Done, validated. Filters CI bot noise ("docs preview"), merges body + comments, injects manual context where present. |
| Manual context | `graph/manual_context.py` | Done. Dict keyed by PR number; currently holds PR #9816 only. |
| Demo PR list | inline in `find_demo_prs.py` / `preload_demo.py` | Locked: `[9816, 14254, 14255, 14256, 12098, 14262, 15745, 15800]` |
| Cognee client | `graph/cognee_client.py` | **Not built** — all Cognee calls currently live inline in ingestion scripts. Should be centralized here so SearchType behavior changes have one point of edit. |
| Ingestion pipeline | `scripts/preload_demo.py` | In progress — sequential ingestion (one PR per call, ~35s sleep) to stay under Groq free-tier TPM. |
| Query engine | `reasoning/query_engine.py` | **Not built.** |
| LLM reasoning layer | `reasoning/llm_layer.py` | **Not built.** |
| API | `api/main.py`, `api/routes/` | **Not built.** |
| UI | `ui/app.py` | **Not built.** |
| Demo cache | `cache/demo_responses.json` | **Not built.** |

## 3. Data Model (as ingested)
Each PR is flattened into a single text document per Cognee's `add()` call, of the form:
```
Pull Request #<n>: <title>
Merged: <date>

Description:
<body or "(no description provided)">

Discussion:
<filtered comments or "(no substantive discussion)">

[optional] Additional context: <manually injected rationale>
```
Cognee's `cognify()` step extracts entities (functions, PRs, issues, people, concepts) and edges (modifies, resolves, caused_by, superseded_by) from this text — not from structured input. Graph quality is therefore bounded by text quality, which is why manual context injection exists for PR #9816.

## 4. Environment / Config
```
LLM_PROVIDER=groq
LLM_MODEL=groq/llama-3.1-8b-instant     # changed from llama-3.3-70b-versatile (TPM cap)
LLM_API_KEY=...
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=...
GITHUB_TOKEN=...                          # classic token, repo scope
```
[Certain] `.env` is config-protected except for model-string updates — structural keys should not be renamed mid-build.

## 5. Reasoning Layer — Design (provisional, not yet implemented)
This section is the part most likely to need revision once real test output exists.

**`query_engine.py` responsibilities:**
- Accept a natural-language question
- Call Cognee with `SearchType.GRAPH_COMPLETION` (primary) and fall back to `SearchType.INSIGHTS` if the former returns empty/low-confidence
- Return raw graph context (entities + relationship paths), not a final answer — keep retrieval and generation separable

**`llm_layer.py` responsibilities:**
- Take graph context + original question
- System prompt must instruct the model to: (a) answer only from the provided graph context, (b) cite specific PR/issue numbers inline, (c) explicitly say "no evidence found in the graph" rather than filling gaps from general knowledge
- [Guessing] Output format should be plain text with inline `[PR #n]` markers the UI can optionally hyperlink — not yet confirmed against what Cognee's INSIGHTS/GRAPH_COMPLETION payload actually looks like, since that test hasn't run

**Open question, must resolve before building further:** does `GRAPH_COMPLETION` actually perform multi-hop traversal (PR #14254 → Cadwyn breakage → PR #14320), or does it behave like CHUNKS with extra formatting? This determines whether `llm_layer.py` needs to do its own graph-path stitching across multiple Cognee calls, or can trust a single call's output.

## 6. API Layer (planned, unbuilt)
```
POST /ingest   → triggers preload_demo.py pipeline (admin/demo-prep use only)
POST /query    → { question: str } → { answer: str, citations: [pr_numbers] }
```
Keep `/ingest` out of the live demo path entirely — ingestion must be pre-run and committed, never triggered on stage.

## 7. UI Layer (planned, unbuilt)
Single-file Streamlit app. Input box → submit → loading state → answer with cited PR numbers rendered as text (links optional, not required for demo). No multi-page navigation, no component subfolders.

## 8. Reliability / Demo-Day Safety
- `cache/demo_responses.json`: pre-computed answers to the 3 final demo questions, keyed by exact question text
- Query engine checks cache first; live Cognee call only as a secondary/backup path during rehearsal, not during the actual demo
- Backup video recorded as final fallback if both live and cache fail

## 9. Explicit Non-Goals
No horizontal scaling, no auth beyond a single GitHub PAT, no persistence beyond Cognee's local graph DB, no multi-user support.