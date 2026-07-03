# CFD — Codebase Oracle (Memoria)
Control & Context Flow Document — covers data flow, query sequence, and demo-day execution flow.

## 1. Ingestion Flow (offline, pre-demo only — never run live on stage)
```
1. scripts/preload_demo.py starts
2. github_client.get_specific_prs(repo, DEMO_PR_NUMBERS)
   → for each PR number: fetch PR + issue comments via PyGithub
   → on 403/rate-limit: _safe_call sleeps until reset, retries
3. For each fetched PR:
   builder.format_pr_for_ingestion(pr)
     → filter out CI bot comments ("docs preview")
     → merge title + body + filtered comments
     → if pr.number in MANUAL_PR_CONTEXT: append injected rationale
4. cognee.prune.prune_data() + prune_system()   [only on intentional full reset]
5. Sequential loop (NOT cognee's default concurrent batch):
   for each formatted PR text:
       cognee.add([text], dataset_name="fastapi_demo")
       cognee.cognify()
       sleep(35s)   # stay under Groq free-tier TPM ceiling
6. Log node/edge counts per PR for sanity-checking ingestion depth
7. Done — graph persists in Cognee's local DB until next explicit prune
```
[Certain] Step 4 must never run automatically inside a query-path script. Pruning is a destructive, manual-only action — the earlier session loss happened because this boundary wasn't enforced.

## 2. Query Flow (the live demo path)
```
1. User/judge types question into Streamlit UI
2. ui/app.py → POST /query { question } → api/routes/query.py
3. query_engine.py:
   a. Check cache/demo_responses.json for exact-match question
      → if hit: return cached answer immediately (no Cognee call)
   b. If miss: call cognee.search(question, SearchType.GRAPH_COMPLETION)
      → if empty/low-confidence: fall back to SearchType.INSIGHTS
      → if still empty: fall back to SearchType.CHUNKS (last resort,
        flag in response that this is similarity-only, not graph reasoning)
4. llm_layer.py:
   a. Take raw graph context from step 3
   b. Apply system prompt (answer only from context, cite PR numbers,
      say "no evidence" rather than hallucinate)
   c. Return final answer text + extracted citation list
5. api/routes/query.py returns { answer, citations } to UI
6. ui/app.py renders answer + citation list
```

## 3. Decision Points (where the system can fail, and what happens)
| Point | Failure mode | Fallback |
|---|---|---|
| GitHub fetch | Rate limit / bad token | `_safe_call` retry loop; pre-run only, never live |
| Cognee `cognify()` | LLM rate limit (Groq TPM) | Sequential ingestion + sleep; pre-run only |
| `GRAPH_COMPLETION` query | Returns empty or shallow (no real multi-hop) | Fall back to INSIGHTS, then CHUNKS — **but this changes the answer's evidentiary strength; UI/answer should not silently claim graph reasoning if it fell back to CHUNKS** |
| LLM reasoning call (live demo) | API timeout / rate limit | Cache hit (step 3a) should pre-empt this for the 3 scripted questions; for off-script judge questions, no safety net exists — accept this as a known gap |
| Live demo, total failure | Network/API down entirely | Pre-recorded backup video |

## 4. The Critical Unvalidated Path
```
PR #14254 (Depends refactor → dataclasses)
        │
        ▼  [must traverse this edge]
   downstream breakage: Cadwyn library, Depends/Security unhashable
        │
        ▼  [must traverse this edge]
   follow-up PR #14320
```
[Certain] This three-node chain is the single test that distinguishes "graph reasoning" from "search with extra steps." Run this query against `GRAPH_COMPLETION` before building anything downstream of it (query_engine, llm_layer, UI). If it fails to connect, the SAD's reasoning-layer design (§5) and this CFD's fallback chain (§3) need revision before further build time is spent.

## 5. Demo-Day Execution Sequence (Day 7, on stage)
```
1. Open pre-loaded Streamlit app (already running, repo already ingested — never ingest live)
2. Ask Q1: "Why did FastAPI migrate to Pydantic v2?" → expect cited #9816 answer
3. Ask Q2 (multi-hop): "What broke when FastAPI refactored Depends to use dataclasses?"
   → expect #14254 → Cadwyn → #14320 chain
4. Ask Q3 (TBD — third question not yet locked; pick from remaining 8 PRs
   once Q1/Q2 are confirmed reliable)
5. If any live call stalls > 5s, stated fallback: cached response plays automatically
6. Close with the one-line pitch: "Without memory, this AI is useless.
   Here's what memory unlocks."
```

## 6. Open Items Blocking This Document's Finalization
- Q3 is undecided — pick after auditing the remaining 6 PRs for which has the cleanest standalone answer
- Citation rendering format (`[PR #n]` inline vs. separate list) unconfirmed until real LLM output is seen
- No fallback defined for off-script judge questions outside the 3 cached ones — decide whether to accept this gap or build a broader cache before Day 7