import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from api.schemas import ImportRepoRequest, StatusResponse
from ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["ingestion"])

# Simple global memory cache for tracking status of ingestion background jobs
INGESTION_STATUS = {
    "status": "idle",
    "repo_url": None,
    "details": "No active ingestion."
}

async def run_ingestion(repo_url: str):
    """
    Background job runner for repository ingestion.
    """
    global INGESTION_STATUS
    INGESTION_STATUS["status"] = "ingesting"
    INGESTION_STATUS["repo_url"] = repo_url
    INGESTION_STATUS["details"] = "Cloning repository and fetching GitHub metadata..."
    
    try:
        pipeline = IngestionPipeline()
        result = await pipeline.ingest(repo_url)
        INGESTION_STATUS["status"] = "success"
        INGESTION_STATUS["details"] = (
            f"Successfully processed repository! Ingested {result['document_count']} documents "
            f"({result['issue_count']} issues, {result['pr_count']} PRs)."
        )
        logger.info("Background ingestion success for %s", repo_url)
    except Exception as e:
        logger.error("Background ingestion failed for %s: %s", repo_url, e)
        INGESTION_STATUS["status"] = "failed"
        INGESTION_STATUS["details"] = f"Ingestion error: {str(e)}"

@router.post("/import", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_repository(payload: ImportRepoRequest, background_tasks: BackgroundTasks):
    """
    Triggers repository cloning and Cognee graph building in the background.
    """
    global INGESTION_STATUS
    
    if INGESTION_STATUS["status"] == "ingesting":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another ingestion is active for {INGESTION_STATUS['repo_url']}."
        )

    background_tasks.add_task(run_ingestion, payload.repo_url)
    
    # Update immediate state
    INGESTION_STATUS["status"] = "ingesting"
    INGESTION_STATUS["repo_url"] = payload.repo_url
    INGESTION_STATUS["details"] = "Ingestion scheduled in background tasks."
    
    return INGESTION_STATUS

@router.get("/status", response_model=StatusResponse)
async def get_ingestion_status():
    """
    Gets progress status of the current or last completed ingestion.
    """
    return INGESTION_STATUS

@router.post("/reset", response_model=StatusResponse)
async def reset_memory():
    """
    Resets/prunes Cognee memory graph database.
    """
    global INGESTION_STATUS
    try:
        from graph.cognee_client import CogneeClient
        client = CogneeClient()
        await client.prune_memory()
        
        INGESTION_STATUS = {
            "status": "idle",
            "repo_url": None,
            "details": "Database reset completed. Memory pruned."
        }
        return INGESTION_STATUS
    except Exception as e:
        logger.error("Failed to reset database: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )
