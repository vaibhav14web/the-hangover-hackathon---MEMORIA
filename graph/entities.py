from typing import Any, List, Optional
from pydantic import SkipValidation
from cognee.infrastructure.engine import DataPoint

class Developer(DataPoint):
    """
    Represents a software developer.
    """
    username: str
    email: Optional[str] = None
    
    metadata: dict = {"index_fields": ["username"]}

class Repository(DataPoint):
    """
    Represents a software repository.
    """
    name: str
    owner: str
    url: str
    description: Optional[str] = ""
    
    metadata: dict = {"index_fields": ["name", "description"]}

class PullRequest(DataPoint):
    """
    Represents a pull request.
    """
    number: int
    title: str
    state: str
    is_resolved: bool = False   # True when state.lower() in {"closed", "merged"}
    creator: SkipValidation[Developer]
    merged_at: Optional[str] = None
    base_branch: Optional[str] = ""
    head_branch: Optional[str] = ""
    
    metadata: dict = {"index_fields": ["title", "number"]}

class Issue(DataPoint):
    """
    Represents an issue.
    """
    number: int
    title: str
    state: str
    creator: SkipValidation[Developer]
    closed_at: Optional[str] = None
    
    metadata: dict = {"index_fields": ["title", "number"]}

class File(DataPoint):
    """
    Represents a code or documentation file.
    """
    path: str
    imports: Optional[List[str]] = []
    
    metadata: dict = {"index_fields": ["path"]}

class ClassEntity(DataPoint):
    """
    Represents a code Class.
    """
    name: str
    docstring: Optional[str] = ""
    bases: Optional[List[str]] = []
    methods: Optional[List[str]] = []
    file: SkipValidation[File]
    
    metadata: dict = {"index_fields": ["name", "docstring"]}

class FunctionEntity(DataPoint):
    """
    Represents a code function or class method.
    """
    name: str
    docstring: Optional[str] = ""
    args: Optional[List[str]] = []
    returns: Optional[str] = None
    is_async: Optional[bool] = False
    file: SkipValidation[File]
    class_name: Optional[str] = None
    
    metadata: dict = {"index_fields": ["name", "docstring"]}
