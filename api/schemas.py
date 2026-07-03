from typing import Any, Dict, List, Optional
from pydantic import BaseModel, HttpUrl, Field

class ImportRepoRequest(BaseModel):
    """
    Schema for repository import requests.
    """
    repo_url: str = Field(..., description="The GitHub repository HTTPS URL (e.g. https://github.com/owner/repo)")

class QueryRequest(BaseModel):
    """
    Schema for QA reasoning requests.
    """
    query: str = Field(..., min_length=1, description="The query string to run reasoning over")

class CitationSchema(BaseModel):
    """
    Schema representing a reference citation.
    """
    type: str = Field(..., description="Type of citation: 'pull_request', 'issue', 'file'")
    id: Any = Field(..., description="Identifier of the cited resource (PR number, issue number, or file path)")
    label: str = Field(..., description="Human-readable citation label (e.g. 'PR #47', 'api/main.py')")

class QueryResponse(BaseModel):
    """
    Schema representing the query engine QA response.
    """
    query: str
    answer: str
    evidence: str
    citations: List[CitationSchema]

class StatusResponse(BaseModel):
    """
    Schema representing repository import job status.
    """
    status: str = Field(..., description="Status string: 'idle', 'ingesting', 'success', 'failed'")
    repo_url: Optional[str] = None
    details: Optional[str] = ""

class HealthResponse(BaseModel):
    """
    Schema representing API health checks.
    """
    status: str = "ok"
