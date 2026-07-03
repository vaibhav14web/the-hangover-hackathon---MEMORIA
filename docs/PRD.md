# PRD — Codebase Oracle (Memoria)
**Hackathon:** The Hangover Hackathon by Cognee
**Status:** Draft — core reasoning layer unvalidated as of writing

## 1. Problem
Existing AI coding tools (Cursor, Copilot, Cody, Continue) answer "what does this code do" via semantic search over files. None answer "why is it written this way," "what broke when this changed," or "what did we already try and reject." That knowledge lives in PRs, issue threads, and review comments, and decays as people leave or memory fades. Flat RAG / large-context approaches can't reason across multi-hop chains of decisions because they retrieve by similarity, not by relationship.

## 2. Solution
A forensic reasoning engine that ingests a repo's PRs and issues, builds a Cognee knowledge graph connecting code entities to decisions and rationale, and answers natural-language questions with cited, multi-hop reasoning — e.g., tracing from a bug, to the PR that introduced it, to the architectural decision that made it inevitable.

## 3. Target User (for the demo)
A judge or engineer unfamiliar with a codebase's history, who wants to ask "why" questions a current tool would hallucinate or refuse.

## 4. Differentiator / Moat
[Certain] Context windows are flat; Cognee's graph is relational. The product must demonstrably traverse 2-3 hops of reasoning (decision → consequence → follow-up) without stuffing the entire repo into a prompt. If a question can be answered as well by "paste repo into GPT-4 with full context," the product has failed its core pitch.

## 5. Scope (Locked)
**In scope:**
- Single demo repo: `tiangolo/fastapi`
- 8 hand-picked, verified, merged PRs covering two real architectural threads (Pydantic v1→v2 migration; dependency-injection internals refactor) plus 2 standalone PRs
- PR body + filtered discussion comments + manually-injected supplementary context (for PRs with thin bodies) as ingestion source
- Natural-language Q&A over the resulting graph, via Streamlit UI calling a FastAPI backend
- 3 pre-scripted, cache-backed demo questions

**Explicitly out of scope (cut for time):**
- Commit history scraping
- Tree-sitter / full AST parsing (deferred to Python's built-in `ast` module if used at all)
- Multi-repo support
- IDE integration
- Automated tests
- Docker packaging
- Live, un-ingested repo input during the demo

## 6. Success Criteria
1. [Must] A question about the Pydantic v2 migration returns an answer citing PR #9816 with real rationale, not a restated title.
2. [Must] A multi-hop question ("what broke when FastAPI refactored Depends to use dataclasses") correctly connects PR #14254 to the downstream Cadwyn breakage and ideally PR #14320 — this is the single test that validates the core pitch.
3. [Should] The Streamlit demo runs twice in a row without crashing or hitting a live rate limit, using cached responses as fallback.
4. [Should] The submission write-up leads with the problem, not the stack.

## 7. Risks (carried from planning, not yet all retired)
| Risk | Status |
|---|---|
| Groq free-tier rate limits during ingestion | Mitigated — switched to `llama-3.1-8b-instant`, sequential ingestion with delay |
| Thin/empty PR bodies producing weak answers | Mitigated for #9816 via manual context injection; not yet audited for other PRs beyond accepting them as-is |
| GRAPH_COMPLETION / multi-hop reasoning may not actually work as pitched | **Unretired** — this is the highest-severity open risk; if it fails, the product degrades to "RAG with extra steps," which is explicitly the failure mode this project was designed to avoid |
| Live demo API failure | Mitigated via planned response cache, not yet built |

## 8. Out-of-the-box question for the team (i.e., you)
[Guessing] If GRAPH_COMPLETION underperforms CHUNKS on the multi-hop test, do you have a fallback pitch — e.g., reframing around INSIGHTS-level relational retrieval rather than full multi-hop chains? Decide this before Day 5, not during the demo.