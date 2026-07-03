import logging
import sys
import os
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ingest, query, maintenance
from api.schemas import HealthResponse

# Set up logging formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("memoria.api")

app = FastAPI(
    title="Memoria AI Institutional Memory Engine",
    description="REST API server backing Memoria's Cognee graph indexing and LiteLLM reasoning.",
    version="1.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(maintenance.router)

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    API Health status check endpoint.
    """
    logger.info("Health check ping received.")
    return {"status": "ok"}
