import logging
from typing import Any, List, Union
import cognee
from cognee.api.v1.search import SearchType
from cognee.tasks.storage.add_data_points import add_data_points
from cognee.infrastructure.engine import DataPoint

logger = logging.getLogger(__name__)

class CogneeClient:
    """
    Wrapper client for interfacing with the Cognee graph engine.
    Ensures safe initialization, dataset additions, cognitive execution, and querying.
    """
    def __init__(self):
        logger.info("Initializing Cognee Client wrapper.")

    async def prune_memory(self):
        """
        Clears all databases, vectors, and graph datasets to avoid collision.
        """
        try:
            logger.info("Pruning Cognee data and system meta-stores...")
            await cognee.prune.prune_data()
            await cognee.prune.prune_system(metadata=True)
            logger.info("✓ Cognee memory pruned successfully.")
        except Exception as e:
            logger.error("Failed to prune Cognee stores: %s", e)
            raise

    async def add_documents(self, documents: List[Union[str, Any]], dataset_name: str = "memoria_dataset"):
        """
        Adds text blobs, files, or structures to a dataset inside Cognee.
        """
        try:
            logger.info("Adding %d documents to Cognee dataset '%s'", len(documents), dataset_name)
            await cognee.add(documents, dataset_name=dataset_name)
            logger.info("✓ Documents added successfully.")
        except Exception as e:
            logger.error("Failed to add documents to Cognee: %s", e)
            raise

    async def add_structured_points(self, data_points: List[DataPoint]):
        """
        Directly inserts structured custom DataPoints (nodes & edges) to the graph.
        """
        try:
            logger.info("Adding %d structured DataPoints to Cognee...", len(data_points))
            await add_data_points(data_points)
            logger.info("✓ Structured data points added.")
        except Exception as e:
            logger.error("Failed to add structured data points: %s", e)
            raise

    async def build_graph(self):
        """
        Processes ingested inputs to build entities, relationships, embeddings, and layout configurations.
        """
        try:
            logger.info("Executing Cognee cognify graph pipeline...")
            await cognee.cognify()
            logger.info("✓ Cognee cognify pipeline completed successfully.")
        except Exception as e:
            logger.error("Cognee cognify error: %s", e)
            raise

    async def search_memory(self, query: str, search_type: SearchType = SearchType.RAG_COMPLETION) -> Any:
        """
        Queries the Cognee graph database using a specific SearchType.
        """
        try:
            logger.info("Searching Cognee memory using SearchType.%s for query: '%s'", search_type.name, query)
            results = await cognee.search(query_text=query, query_type=search_type)
            return results
        except Exception as e:
            logger.error("Cognee search failed: %s", e)
            return None
