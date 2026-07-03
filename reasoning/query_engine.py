import logging
import re
import os
import json
import sqlite3
import lancedb
from typing import Any, Dict, List
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
                                return cached_val
        except Exception as ce:
            logger.warning("Failed to check cache: %s", ce)

        context_parts = []

        # Parse exact PR or Issue numbers from the query (supporting optional '#' sign)
        pr_numbers = re.findall(r"(?:PR|Pull Request|PullRequest)\s*#?\s*(\d+)", query, re.IGNORECASE)
        issue_numbers = re.findall(r"(?:Issue)\s*#?\s*(\d+)", query, re.IGNORECASE)
        
        # Direct chunk routing: If specific PRs or Issues are mentioned in the query, fetch their chunks directly from LanceDB
        if pr_numbers or issue_numbers:
            logger.info("Query mentions PRs/Issues. Performing direct LanceDB search.")
            try:
                import cognee
                cognee_dir = os.path.dirname(cognee.__file__)
                paths_to_try = [
                    os.path.join(cognee_dir, ".cognee_system", "databases", "cognee_db"),
                    os.path.expanduser("~/.cognee/databases/cognee_db"),
                    os.path.expanduser("~/.cognee_system/databases/cognee_db"),
                    os.path.abspath("venv/Lib/site-packages/cognee/.cognee_system/databases/cognee_db"),
                    os.path.abspath(".venv/Lib/site-packages/cognee/.cognee_system/databases/cognee_db")
                ]
                db_path = None
                for path in paths_to_try:
                    if os.path.exists(path):
                        db_path = path
                        break
                
                if db_path and os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT vector_database_url FROM dataset_database LIMIT 1")
                    row = cursor.fetchone()
                    if row and row[0]:
                        lancedb_path = row[0]
                        # If the absolute path stored in DB does not exist, resolve it relative to the dynamic cognee database directory
                        if not os.path.exists(lancedb_path):
                            subpath_match = re.search(r"databases[\\/](.+)$", lancedb_path)
                            if subpath_match:
                                relative_subpath = subpath_match.group(1)
                                potential_path = os.path.join(os.path.dirname(db_path), relative_subpath)
                                if os.path.exists(potential_path):
                                    lancedb_path = potential_path
                        
                        if os.path.exists(lancedb_path):
                            db = lancedb.connect(lancedb_path)
                            tbl = db.open_table("DocumentChunk_text")
                            arrow_table = tbl.to_arrow()
                            payloads = arrow_table["payload"].to_pylist()
                            
                            for p_val in payloads:
                                p_dict = eval(p_val) if isinstance(p_val, str) else p_val
                                text = p_dict.get("text", "")
                                
                                # Check for PR matches
                                for pr_num in pr_numbers:
                                    match_patterns = [f"#{pr_num}", f"PR {pr_num}", f"PR #{pr_num}", f"Pull Request #{pr_num}"]
                                    if any(pattern in text for pattern in match_patterns):
                                        context_parts.append(text)
                                        
                                # Check for Issue matches
                                for issue_num in issue_numbers:
                                    match_patterns = [f"#{issue_num}", f"Issue {issue_num}", f"Issue #{issue_num}"]
                                    if any(pattern in text for pattern in match_patterns):
                                        context_parts.append(text)
                    conn.close()
            except Exception as direct_ex:
                logger.warning("Direct LanceDB retrieval failed: %s", direct_ex)
        
        # 2. Retrieve additional context using RAG_COMPLETION and GRAPH_COMPLETION as fallback
        for search_type in [SearchType.RAG_COMPLETION, SearchType.GRAPH_COMPLETION]:
            try:
                result = await self.cognee_client.search_memory(query, search_type)
                if result:
                    if isinstance(result, list):
                        for item in result:
                            if isinstance(item, dict):
                                context_parts.append(str(item))
                            elif hasattr(item, "dict"):
                                context_parts.append(str(item.dict()))
                            else:
                                context_parts.append(str(item))
                    elif isinstance(result, dict):
                        context_parts.append(str(result))
                    else:
                        context_parts.append(str(result))
            except Exception as se:
                logger.warning("Retrieval failed for SearchType.%s: %s", search_type.name, se)

        # 3. Deduplicate and clean context parts
        seen_chunks = set()
        unique_context_parts = []
        for part in context_parts:
            part_str = part.strip()
            # Clean out useless "Got it." or similar generic LLM fallbacks from retrieved context
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
        
        # 4. Call LiteLLM query logic
        answer = await query_llm(query, context_text)
        
        # 5. Extract citations from answer and context
        citations = self._extract_citations(answer + "\n" + context_text)

        # Deduplicate citations based on type and id
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
            "citations": deduped_citations
        }
