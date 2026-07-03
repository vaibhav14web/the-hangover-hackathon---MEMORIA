from fastapi import APIRouter, Header, HTTPException, Depends
import os
from scripts.forget_resolved import prune_resolved_prs

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

def verify_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("MAINTENANCE_API_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@router.post("/forget_resolved")
async def forget_resolved(payload: dict = {}, authorized: bool = Depends(verify_api_key)):
    """Delete resolved pull requests from a Cognee dataset.
    Payload may contain optional "dataset_name" (default: "fastapi_demo").
    """
    dataset_name = payload.get("dataset_name", "fastapi_demo")
    deleted = await prune_resolved_prs(dataset_name)
    return {"status": "ok", "deleted": deleted}
