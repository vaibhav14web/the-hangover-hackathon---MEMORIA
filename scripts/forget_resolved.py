import cognee

async def prune_resolved_prs(dataset_name: str = "fastapi_demo") -> int:
    """Delete all PullRequest nodes where is_resolved == True.

    Returns the number of deleted nodes.
    """
    resolved = await cognee.datasets.query_data(
        dataset_id=dataset_name,
        filter={"is_resolved": True},
        select=["id"]
    )
    deleted = 0
    for item in resolved:
        await cognee.datasets.delete_data(
            dataset_id=dataset_name,
            data_id=item["id"]
        )
        deleted += 1
    return deleted
