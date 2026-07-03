import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Ensure root of project is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import cognee
from ingestion.github_client import GitHubClient
from graph.builder import format_pr_for_ingestion

logger = logging.getLogger("memoria.preload")
logging.basicConfig(level=logging.INFO)

DEMO_PR_NUMBERS = [9816, 14254, 14255, 14256, 12098, 14262, 15745, 15800]

async def preload():
    logger.info("Initializing preloader. Pruning store...")
    try:
        # await cognee.prune.prune_data()
        # await cognee.prune.prune_system(metadata=True)
        logger.info("✓ Old data pruned.")
    except Exception as e:
        logger.warning("Prune failed (ignoring): %s", e)

    client = GitHubClient()
    repo = client.get_repo("tiangolo/fastapi")
    
    logger.info("Fetching the 8 demo PRs from GitHub...")
    prs = client.get_specific_prs(repo, DEMO_PR_NUMBERS)
    logger.info("Fetched %d PRs successfully.", len(prs))
    
    # Sort PRs by number to ingest them in historical order
    prs = sorted(prs, key=lambda x: x["number"])

    for i, pr in enumerate(prs):
        logger.info("Processing PR %d of %d (PR #%d: %s)...", i + 1, len(prs), pr["number"], pr["title"])
        formatted_text = format_pr_for_ingestion(pr)
        
        try:
            await cognee.add([formatted_text], dataset_name="fastapi_demo")
            logger.info("PR #%d added to Cognee. Running cognify...", pr["number"])
            await cognee.cognify()
            logger.info("✓ PR #%d cognified successfully.", pr["number"])
        except Exception as e:
            logger.error("Failed to ingest PR #%d: %s", pr["number"], e)
            raise e
            
        if i < len(prs) - 1:
            logger.info("Sleeping 35 seconds to avoid Groq TPM rate limits...")
            await asyncio.sleep(35)
            
    logger.info("✓ Sequential preload completed successfully!")

if __name__ == "__main__":
    asyncio.run(preload())
