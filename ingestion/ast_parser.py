import ast
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ASTParser(ast.NodeVisitor):
    """
    AST Parser to extract imports, classes, methods, and functions from Python files.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: List[str] = []
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.current_class: Optional[Dict[str, Any]] = None

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}" if module else alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "bases": [self._get_base_name(base) for base in node.bases],
            "methods": []
        }
        
        # Save reference to current class for method visitor
        prev_class = self.current_class
        self.current_class = class_info
        
        # Visit child nodes (methods, class attributes, etc.)
        self.generic_visit(node)
        
        self.classes.append(class_info)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Extract arguments
        args = [arg.arg for arg in node.args.args]
        
        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "args": args,
            "returns": self._get_return_annotation(node.returns) if node.returns else None
        }

        if self.current_class:
            self.current_class["methods"].append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        args = [arg.arg for arg in node.args.args]
        
        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "args": args,
            "returns": self._get_return_annotation(node.returns) if node.returns else None,
            "is_async": True
        }

        if self.current_class:
            self.current_class["methods"].append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)

    def _get_base_name(self, node: ast.AST) -> str:
        """Helper to get class base names as strings."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return "Unknown"

    def _get_return_annotation(self, node: ast.AST) -> str:
        """Helper to get return annotations as strings."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"

def parse_file(file_path: str, code_content: Optional[str] = None) -> Dict[str, Any]:
    """
    Parses a single python file path or code string and returns structure info.
    """
    try:
        if code_content is None:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()

        tree = ast.parse(code_content, filename=file_path)
        parser = ASTParser(file_path)
        parser.visit(tree)
        
        return {
            "file_path": file_path,
            "imports": parser.imports,
            "classes": parser.classes,
            "functions": parser.functions
        }
    except Exception as e:
        logger.error("Failed to parse file %s: %s", file_path, e)
        return {
            "file_path": file_path,
            "imports": [],
            "classes": [],
            "functions": [],
            "error": str(e)
        }

def format_parsed_info_to_markdown(parsed_info: Dict[str, Any]) -> str:
    """
    Formates python parsed structure dictionary into a clean markdown document.
    """
    md = []
    md.append(f"# Code Structure: `{parsed_info['file_path']}`\n")
    
    if parsed_info.get("error"):
        md.append(f"> [!WARNING]\n> Failed to parse AST: {parsed_info['error']}\n")
        return "\n".join(md)

    if parsed_info["imports"]:
        md.append("## Imports")
        for imp in parsed_info["imports"]:
            md.append(f"- `{imp}`")
        md.append("")

    if parsed_info["classes"]:
        md.append("## Classes")
        for cls in parsed_info["classes"]:
            md.append(f"### Class: `{cls['name']}`")
            if cls["bases"]:
                bases_str = ", ".join(f"`{b}`" for b in cls["bases"])
                md.append(f"- **Bases**: {bases_str}")
            if cls["docstring"]:
                md.append(f"\n> {cls['docstring']}\n")
            if cls["methods"]:
                md.append("#### Methods")
                for method in cls["methods"]:
                    args_str = ", ".join(method["args"])
                    ret_str = f" -> {method['returns']}" if method.get("returns") else ""
                    is_async = "async " if method.get("is_async") else ""
                    md.append(f"- `{is_async}{method['name']}({args_str}){ret_str}`")
                    if method["docstring"]:
                        md.append(f"  - **Doc**: {method['docstring']}")
            md.append("")

    if parsed_info["functions"]:
        md.append("## Functions")
        for func in parsed_info["functions"]:
            args_str = ", ".join(func["args"])
            ret_str = f" -> {func['returns']}" if func.get("returns") else ""
            is_async = "async " if func.get("is_async") else ""
            md.append(f"### Function: `{is_async}{func['name']}({args_str}){ret_str}`")
            if func["docstring"]:
                md.append(f"\n> {func['docstring']}\n")
            md.append("")

    return "\n".join(md)
