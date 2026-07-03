import asyncio
from dotenv import load_dotenv
load_dotenv()

import cognee
from cognee.api.v1.search import SearchType
from ingestion.github_client import GitHubClient
from graph.builder import format_pr_for_ingestion

DEMO_PR_NUMBERS = [9816, 14254, 14255, 14256, 12098, 14262, 15745, 15800]

async def ingest_demo_repo():
    client = GitHubClient()
    repo = client.get_repo("tiangolo/fastapi")
    prs = client.get_specific_prs(repo, DEMO_PR_NUMBERS)

    print(f"Fetched {len(prs)} PRs. Formatting...")
    formatted_texts = [format_pr_for_ingestion(pr) for pr in prs]

    print("Pruning old data...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    print("Adding to Cognee...")
    await cognee.add(formatted_texts, dataset_name="fastapi_demo")

    print("Running cognify (this builds the graph, may take a few minutes for 8 PRs)...")
    await cognee.cognify()

    print("✓ Ingestion complete")

    print("\nTesting query: 'Why did FastAPI migrate to Pydantic v2?'")
    results = await cognee.search(
        query_text="Why did FastAPI migrate to Pydantic v2?",
        query_type=SearchType.CHUNKS
    )
    print(results)
    
    print("\nTesting INSIGHTS: 'Why did FastAPI migrate to Pydantic v2?'")
    insights = await cognee.search(
        query_text="Why did FastAPI migrate to Pydantic v2?",
        query_type=SearchType.INSIGHTS
    )
    print(insights)

    print("\nTesting multi-hop: 'What broke when FastAPI refactored Depends to use dataclasses?'")
    multihop = await cognee.search(
        query_text="What broke when FastAPI refactored Depends to use dataclasses?",
        query_type=SearchType.GRAPH_COMPLETION
    )
    print(multihop)

asyncio.run(ingest_demo_repo())