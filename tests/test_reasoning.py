import pytest
from reasoning.query_engine import QueryEngine

def test_query_engine_extract_citations():
    engine = QueryEngine()
    
    sample_text = """
    We modified core/auth.py to address security concerns raised in Issue #123.
    This was done by merged Pull Request #476 which refactored auth flow.
    We also checked storage/db.txt config files.
    """
    
    citations = engine._extract_citations(sample_text)
    
    # Check PR citations
    pr_citations = [c for c in citations if c["type"] == "pull_request"]
    assert len(pr_citations) == 1
    assert pr_citations[0]["id"] == 476
    assert pr_citations[0]["label"] == "PR #476"
    
    # Check Issue citations
    issue_citations = [c for c in citations if c["type"] == "issue"]
    assert len(issue_citations) == 1
    assert issue_citations[0]["id"] == 123
    assert issue_citations[0]["label"] == "Issue #123"
    
    # Check File citations
    file_citations = [c for c in citations if c["type"] == "file"]
    assert len(file_citations) == 2
    paths = [c["id"] for c in file_citations]
    assert "core/auth.py" in paths
    assert "storage/db.txt" in paths
