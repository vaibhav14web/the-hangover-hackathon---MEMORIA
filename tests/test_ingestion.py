import pytest
from ingestion.ast_parser import parse_file, format_parsed_info_to_markdown
from ingestion.github_client import GitHubClient

MOCK_CODE = """
import os
from sys import path

class MyBase:
    pass

class Calculator(MyBase):
    \"\"\"Perform addition operations.\"\"\"
    def add(self, a: int, b: int) -> int:
        \"\"\"Adds a and b.\"\"\"
        return a + b
        
    async def get_async(self):
        return True

def global_func():
    return None
"""

def test_ast_parser_extracts_structures():
    parsed = parse_file("dummy.py", code_content=MOCK_CODE)
    
    assert parsed["file_path"] == "dummy.py"
    assert "os" in parsed["imports"]
    assert "sys.path" in parsed["imports"]
    
    # Classes
    assert len(parsed["classes"]) == 2
    calc_class = [c for c in parsed["classes"] if c["name"] == "Calculator"][0]
    assert calc_class["bases"] == ["MyBase"]
    assert calc_class["docstring"] == "Perform addition operations."
    
    # Methods
    methods = calc_class["methods"]
    assert len(methods) == 2
    add_method = [m for m in methods if m["name"] == "add"][0]
    assert add_method["args"] == ["self", "a", "b"]
    assert add_method["docstring"] == "Adds a and b."
    assert add_method["returns"] == "int"
    
    async_method = [m for m in methods if m["name"] == "get_async"][0]
    assert async_method["is_async"] is True
    
    # Global Functions
    assert len(parsed["functions"]) == 1
    assert parsed["functions"][0]["name"] == "global_func"

def test_markdown_formatter():
    parsed = parse_file("dummy.py", code_content=MOCK_CODE)
    md = format_parsed_info_to_markdown(parsed)
    
    assert "## Classes" in md
    assert "Class: `Calculator`" in md
    assert "`add(self, a, b) -> int`" in md
    assert "## Functions" in md
    assert "Function: `global_func()`" in md

def test_github_client_url_parser():
    client = GitHubClient()
    owner, repo = client.parse_repo_url("https://github.com/owner/repository")
    assert owner == "owner"
    assert repo == "repository"
    
    owner, repo = client.parse_repo_url("https://github.com/another-owner/repo.git")
    assert owner == "another-owner"
    assert repo == "repo"
    
    with pytest.raises(ValueError):
        client.parse_repo_url("https://invalid.com/owner/repo")
