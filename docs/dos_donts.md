## HARD CONSTRAINT — READ BEFORE TOUCHING ANYTHING
Do NOT modify, rewrite, or "improve" these files — they are tested and working:
- ingestion/github_client.py
- graph/builder.py
- graph/manual_context.py
- find_demo_prs.py (the ingestion portion specifically — search-test additions are fine)
- .env (config values are correct, do not regenerate or restructure)

Only create NEW files for the "NOT YET BUILT" items listed above, or make 
surgical additions to find_demo_prs.py for testing new search types. If you 
believe an existing file needs a structural change, STOP and ask me first — 
do not just make the change.


Cognee already has the 8 PRs ingested in its local database (dataset_name="fastapi_demo"). 
Do not re-run cognee.prune / cognee.add / cognee.cognify unless explicitly instructed — 
querying the existing graph is sufficient for testing.

markdown# PROJECT: Codebase Oracle — Hackathon Build (The Hangover Hackathon by Cognee)

## What This Is
A forensic reasoning engine that answers WHY architectural decisions were made in a 
codebase, not just WHAT the code does. Uses Cognee's knowledge graph to enable 
multi-hop reasoning across code entities, PRs, issues, and decisions — something flat 
RAG/context-window approaches can't replicate. Built solo for a 7-day hackathon. 
2 days already used; 5 days remain.

## Tech Stack
- Backend: Python, FastAPI
- Memory/Graph: Cognee v1.2.2
- LLM: Groq (free tier) — currently using llama-3.3-70b-versatile, hitting rate 
  limits (12k TPM cap); should switch to llama-3.1-8b-instant for higher throughput
- Embeddings: OpenAI (text-embedding-3-small)
- Frontend: Streamlit (planned, not built yet)
- Platform: Windows, cmd
- GitHub API: PyGithub

## Demo Target
Repo: tiangolo/fastapi
8 hand-picked, verified-real, merged PRs covering two architectural threads:
- Pydantic v1 → v2 migration: PR #9816 (had near-empty body/comments; manually 
  enriched with real migration rationale since the actual discussion lived in a 
  linked GitHub Discussion, not the PR itself)
- Dependency injection system evolution: PRs #14254, #14255, #14256, #12098, #14262
- Router internals refactor: PR #15745
- New feature example: PR #15800

## Folder Structure (already created)
codebase-oracle/
├── ingestion/
│   ├── github_client.py      # PyGithub wrapper, rate-limit handling,
│   │                          # get_specific_prs() method DONE
│   └── pipeline.py            # NOT YET BUILT
├── graph/
│   ├── builder.py             # format_pr_for_ingestion() DONE — formats PR data,
│   │                          # filters bot noise (CI "docs preview" comments),
│   │                          # injects manual_context where needed
│   ├── manual_context.py      # MANUAL_PR_CONTEXT dict DONE — hardcoded rationale
│   │                          # for PR #9816 (Pydantic v2 migration)
│   └── cognee_client.py       # NOT YET BUILT — should centralize all Cognee calls
├── reasoning/
│   ├── query_engine.py        # NOT YET BUILT
│   └── llm_layer.py           # NOT YET BUILT
├── api/
│   ├── main.py                # NOT YET BUILT
│   └── routes/
│       ├── ingest.py          # NOT YET BUILT
│       └── query.py           # NOT YET BUILT
├── ui/
│   └── app.py                  # NOT YET BUILT — Streamlit, keep to ~150 lines
├── cache/
│   └── demo_responses.json     # NOT YET BUILT — pre-cached answers for demo safety
├── scripts/
│   └── preload_demo.py         # NOT YET BUILT — runs ingestion once, commits result
└── find_demo_prs.py            # WORKING — current ingestion + test script, ran
# successfully, ingested all 8 PRs into Cognee

## What's Confirmed Working (Day 1-2, validated)
1. Cognee account + auth working
2. .env-based config working (more reliable than programmatic config for v1.2.2):
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile  (consider switching to llama-3.1-8b-instant)
LLM_API_KEY=...
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=...
GITHUB_TOKEN=...
3. GitHub API auth working via PyGithub (classic token, repo scope)
4. All 8 demo PRs successfully fetched, formatted, and ingested into Cognee via 
   cognee.add() + cognee.cognify()
5. SearchType.CHUNKS verified working — correctly retrieves and ranks #9816 as 
   top result for "Why did FastAPI migrate to Pydantic v2?"
6. NOT yet tested: SearchType.INSIGHTS and SearchType.GRAPH_COMPLETION — this is 
   the critical next validation step since these search types are what actually 
   prove the "graph reasoning beats flat RAG" pitch, not just CHUNKS

## Known Issues / Lessons Learned
- Groq's llama-3.3-70b-versatile free tier caps at 12,000 TPM — caused repeated 
  rate-limit retries during cognify() (8 PRs took ~5 min due to backoff retries). 
  Switch to llama-3.1-8b-instant for future runs to avoid this.
- GitHub bot comments (CI "docs preview" links) pollute PR discussion data — 
  filtered out in builder.py via string matching on "docs preview"
- Some PRs have very thin bodies (just repeating the title) even when they 
  represent major decisions — e.g., PR #9816's actual rationale lived in a 
  linked GitHub Discussion (#9709), not the PR body itself. Required manual 
  research + hardcoded context injection in manual_context.py to compensate.
- A promising secondary demo question was found organically in the data: PR 
  #14254 (dependency refactor to dataclasses) broke a downstream library 
  (Cadwyn) because Depends/Security became unhashable — this is documented in 
  a PR comment and references a follow-up PR #14320. Good candidate for testing 
  multi-hop reasoning.

## Immediate Next Steps (in order)
1. Run SearchType.INSIGHTS and SearchType.GRAPH_COMPLETION queries against the 
   already-ingested data (do NOT re-run cognee.add/cognify — data is already in 
   Cognee). Validate that:
   a) "Why did FastAPI migrate to Pydantic v2?" returns reasoned output citing #9816
   b) "What broke when FastAPI refactored Depends to use dataclasses?" correctly 
      connects PR #14254 to the Cadwyn breakage and ideally to PR #14320 
      (multi-hop validation — this is the core differentiator to prove)
2. Build reasoning/query_engine.py — wraps Cognee search calls
3. Build reasoning/llm_layer.py — takes graph context, produces final cited 
   natural-language answer
4. Build api/main.py + routes — expose query endpoint via FastAPI
5. Build ui/app.py — Streamlit interface, single file, ~150 lines, just an input 
   box and answer display
6. Build scripts/preload_demo.py — formalizes the ingestion script so it can be 
   re-run cleanly once, then commit/cache the result
7. Build cache/demo_responses.json — pre-cache answers to the 3 final demo 
   questions as a live-demo safety net (judges should never see a failed API call)
8. Record a backup demo video
9. Write README.md emphasizing the problem (institutional knowledge loss in 
   codebases) before the tech stack
10. Submit with 6+ hours of buffer remaining

## Constraints / Things to NOT Do
- Don't add Tree-sitter, Docker Compose, tests/, or commit-history scraping — 
  deliberately cut scope for time
- Don't re-run ingestion (cognee.add/cognify) unnecessarily — it's slow (rate 
  limits) and data already persists in Cognee's local DB
- Don't expand the PR dataset beyond the 8 already chosen — quality over volume
- Keep ui/app.py minimal — no component subfolders, no over-engineering

## My Skill Level
Strong Python backend, limited frontend experience, working on Windows (cmd, 
not PowerShell or WSL).

---
Please pick up from step 1 of "Immediate Next Steps" above and help me continue 
the build from current state.