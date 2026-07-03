import logging
import re
import json
from typing import Any, Dict, List, Optional
from graph.cognee_client import CogneeClient
from cognee.api.v1.search import SearchType
from reasoning.llm_layer import query_llm

logger = logging.getLogger(__name__)

class QueryEngine:
    """
    Coordinates context retrieval from Cognee, compiles evidence context,
    triggers LiteLLM reasoning, and parses citations for explainability.
    """
    def __init__(self):
        self.cognee_client = CogneeClient()

    def _extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses text to extract references to PRs, Issues, and files.
        """
        citations = []
        
        # Pull Request patterns: PR #12, Pull Request #12, PR 12 (optional #)
        pr_matches = re.findall(r"(?:PR|Pull Request|PullRequest|PRs|Pull Requests)\s*#?\s*(\d+)", text, re.IGNORECASE)
        for num in set(pr_matches):
            citations.append({"type": "pull_request", "id": int(num), "label": f"PR #{num}"})
            
        # Issue patterns: Issue #34, Issue 34 (optional #)
        issue_matches = re.findall(r"(?:Issue|Issues)\s*#?\s*(\d+)", text, re.IGNORECASE)
        for num in set(issue_matches):
            citations.append({"type": "issue", "id": int(num), "label": f"Issue #{num}"})

        # File path patterns: e.g. path/to/file.py, schema.py
        file_matches = re.findall(r"\b([a-zA-Z0-9_\-/]+\.(?:py|md|txt))\b", text)
        for path in set(file_matches):
            citations.append({"type": "file", "id": path, "label": path})

        return citations

    def _extract_text_from_search_result(self, item: Any) -> str:
        if item is None:
            return ""

        if isinstance(item, str):
            return item.strip()

        if isinstance(item, dict):
            for key in ("text", "content", "answer", "payload", "data", "metadata"):
                if key in item:
                    value = item[key]
                    if isinstance(value, str):
                        return value.strip()
                    if isinstance(value, dict):
                        return self._extract_text_from_search_result(value)
            if "payload" in item and isinstance(item["payload"], dict):
                return self._extract_text_from_search_result(item["payload"])
            values = [str(v).strip() for v in item.values() if isinstance(v, str) and v.strip()]
            return "\n".join(values) if values else json.dumps(item, ensure_ascii=False)

        if hasattr(item, "dict"):
            try:
                return self._extract_text_from_search_result(item.dict())
            except Exception:
                pass

        if hasattr(item, "to_dict"):
            try:
                return self._extract_text_from_search_result(item.to_dict())
            except Exception:
                pass

        if hasattr(item, "content"):
            return str(getattr(item, "content")).strip()

        return str(item).strip()

    def _normalize_search_results(self, results: Any) -> List[str]:
        normalized = []
        if results is None:
            return normalized

        if isinstance(results, list):
            for item in results:
                text = self._extract_text_from_search_result(item)
                if text:
                    normalized.append(text)
            return normalized

        text = self._extract_text_from_search_result(results)
        return [text] if text else []

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Executes query retrieval, LLM reasoning, and parses citations.
        """
        logger.info("Executing reasoning query: '%s'", query)
        
        # Check cache/demo_responses.json for exact match
        cache_path = "cache/demo_responses.json"
        try:
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        cache = json.loads(content)
                        for cached_q, cached_val in cache.items():
                            if cached_q.strip().lower() == query.strip().lower():
                                logger.info("Cache HIT for query: '%s'", query)
                                cached_val.setdefault("retrieval_method", "CACHE_HIT")
                                return cached_val
        except Exception as ce:
            logger.warning("Failed to check cache: %s", ce)

        context_parts = []
        retrieval_method: Optional[str] = None

        # Retrieve graph-aware evidence first, then fall back to insights and RAG
        for search_type in [SearchType.GRAPH_COMPLETION, SearchType.INSIGHTS, SearchType.RAG_COMPLETION]:
            try:
                result = await self.cognee_client.search_memory(query, search_type)
                new_parts = self._normalize_search_results(result)
                if new_parts:
                    retrieval_method = search_type.name
                    logger.info("SearchType.%s returned %d context parts", search_type.name, len(new_parts))
                    context_parts.extend(new_parts)
                    break
                else:
                    logger.info("SearchType.%s returned no context. Falling back.", search_type.name)
            except Exception as se:
                logger.warning("Retrieval failed for SearchType.%s: %s", search_type.name, se)

        # Deduplicate and clean context parts
        seen_chunks = set()
        unique_context_parts = []
        for part in context_parts:
            part_str = part.strip()
            if part_str == "Got it.":
                continue
            if part_str and part_str not in seen_chunks:
                seen_chunks.add(part_str)
                unique_context_parts.append(part)

        if not unique_context_parts:
            context_text = "No direct facts found in memory."
        else:
            context_text = "\n\n".join(unique_context_parts)

        logger.info("Retrieved %d unique context chunks.", len(unique_context_parts))
        
        # Call LiteLLM query logic
        answer = await query_llm(query, context_text)
        
        # Extract citations from answer and context
        citations = self._extract_citations(answer + "\n" + context_text)

        seen = set()
        deduped_citations = []
        for cit in citations:
            key = (cit["type"], str(cit["id"]))
            if key not in seen:
                seen.add(key)
                deduped_citations.append(cit)

        return {
            "query": query,
            "answer": answer,
            "evidence": context_text,
            "citations": deduped_citations,
            "retrieval_method": retrieval_method
        }
