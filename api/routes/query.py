import json
import logging
from fastapi import APIRouter, HTTPException, status
from api.schemas import QueryRequest, QueryResponse
from reasoning.query_engine import QueryEngine

logger = logging.getLogger(__name__)
CACHE_PATH = "cache/demo_responses.json"

router = APIRouter(tags=["reasoning"])
query_engine = QueryEngine()


def _load_demo_cache() -> dict:
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


@router.post("/query", response_model=QueryResponse)
async def query_reasoning_engine(payload: QueryRequest):
    """
    Accepts user question, queries Cognee knowledge graph, structures context,
    runs LiteLLM reasoning, parses citations, and returns response.
    """
    try:
        logger.info("Received query request: '%s'", payload.query)
        result = await query_engine.execute_query(payload.query)
        return result
    except Exception as e:
        logger.error("Failed to query reasoning engine: %s", e)
        demo_cache = _load_demo_cache()
        fallback = demo_cache.get(payload.query.strip())
        if fallback:
            logger.warning("Using cached fallback answer for query: '%s'", payload.query)
            fallback.setdefault("retrieval_method", "CACHE_FALLBACK")
            return fallback
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Query reasoning failed: {str(e)}"}
        )
