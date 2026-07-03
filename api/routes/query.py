import logging
from fastapi import APIRouter, HTTPException, status
from api.schemas import QueryRequest, QueryResponse
from reasoning.query_engine import QueryEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reasoning"])
query_engine = QueryEngine()

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
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Query reasoning failed: {str(e)}"}
        )
