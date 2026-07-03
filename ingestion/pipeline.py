import os
import shutil
import logging
import asyncio
from typing import Any, Dict, List, Optional
import git
import cognee
from dotenv import load_dotenv
from github import Github

from ingestion.ast_parser import parse_file, format_parsed_info_to_markdown

logger = logging.getLogger(__name__)

# Directory where repositories are cloned
CACHE_REPOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "repos"))

class IngestionPipeline:
    """
    Coordinates repository cloning, AST parsing, GitHub issues/PR metadata retrieval,
    normalizing data to a single Markdown document, and uploading it to Cognee.
    """
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.github_token)
        
        # Ensure cache directory exists
        os.makedirs(CACHE_REPOS_DIR, exist_ok=True)

    def parse_repo_url(self, repo_url: str):
        """
        Extracts owner and repo name from GitHub URL or name string.
        """
        url_str = repo_url.replace("https://github.com/", "").replace("http://github.com/", "")
        parts = [p for p in url_str.split("/") if p]
        if len(parts) >= 2:
            return parts[0], parts[1]
        return "", ""

    def _clone_repo(self, repo_url: str) -> str:
        """
        Clones repository locally. If it exists, pulls the latest changes.
        """
        owner, repo_name = self.parse_repo_url(repo_url)
        local_path = os.path.join(CACHE_REPOS_DIR, f"{owner}_{repo_name}")
        
        if os.path.exists(local_path):
            try:
                logger.info("Repository exists locally. Attempting pull at %s", local_path)
                repo = git.Repo(local_path)
                repo.remotes.origin.pull()
                logger.info("Successfully pulled latest changes.")
            except Exception as e:
                logger.warning("Pull failed: %s. Cleaning up and re-cloning...", e)
                shutil.rmtree(local_path, ignore_errors=True)
                if os.path.exists(local_path):
                    import subprocess
                    subprocess.run(f'rmdir /s /q "{local_path}"', shell=True)
                git.Repo.clone_from(repo_url, local_path)
                logger.info("Successfully re-cloned repository.")
        else:
            logger.info("Cloning repository to %s", local_path)
            git.Repo.clone_from(repo_url, local_path)
            logger.info("Clone completed.")
        
        return local_path

    def _fetch_metadata(self, repo_url: str):
        """
        Synchronously fetches repository metadata, issues, and PR history.
        """
        owner, repo_name = self.parse_repo_url(repo_url)
        repo_fullname = f"{owner}/{repo_name}"
        
        issues = []
        pulls = []
        repo_info = {}
        
        try:
            logger.info("Fetching repository metadata from GitHub: %s", repo_fullname)
            repo_obj = self.github.get_repo(repo_fullname)
            repo_info = {
                "full_name": repo_obj.full_name,
                "description": repo_obj.description or "",
                "owner": owner,
                "stars": repo_obj.stargazers_count,
                "forks": repo_obj.forks_count,
                "default_branch": repo_obj.default_branch,
                "url": repo_obj.html_url
            }
            
            # Fetch closed issues (limit to 5 issues, scanning up to 30 items)
            logger.info("Fetching closed issues...")
            issue_count = 0
            for idx, issue in enumerate(repo_obj.get_issues(state="closed")):
                if issue_count >= 5 or idx >= 30:
                    break
                if not issue.pull_request:
                    comments = []
                    try:
                        for c in issue.get_comments():
                            comments.append({
                                "user": c.user.login,
                                "created_at": str(c.created_at),
                                "body": c.body or ""
                            })
                    except Exception:
                        pass
                    issues.append({
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "creator": issue.user.login,
                        "state": issue.state,
                        "created_at": str(issue.created_at),
                        "closed_at": str(issue.closed_at),
                        "url": issue.html_url,
                        "comments": comments
                    })
                    issue_count += 1
                        
            # Fetch closed PRs (limit to 10 PRs, scanning up to 30 items)
            logger.info("Fetching closed PRs...")
            pr_count = 0
            for idx, pr in enumerate(repo_obj.get_pulls(state="closed")):
                if pr_count >= 10 or idx >= 30:
                    break
                comments = []
                try:
                    for c in pr.get_issue_comments():
                        comments.append({
                            "user": c.user.login,
                            "created_at": str(c.created_at),
                            "body": c.body or ""
                        })
                except Exception:
                    pass
                pulls.append({
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body or "",
                    "creator": pr.user.login,
                    "state": pr.state,
                    "is_resolved": pr.state.lower() in {"closed", "merged"},
                    "created_at": str(pr.created_at),
                    "merged_at": str(pr.merged_at) if pr.merged else "N/A",
                    "merged_by": pr.merged_by.login if pr.merged_by else "N/A",
                    "base_branch": pr.base.ref,
                    "head_branch": pr.head.ref,
                    "url": pr.html_url,
                    "comments": comments
                })
                pr_count += 1
        except Exception as e:
            logger.error("Failed to fetch repository metadata/issues/pulls: %s", e)

        return issues, pulls, repo_info

    async def ingest(self, repo_url: str, dataset_name: str = "memoria_dataset") -> Dict[str, Any]:
        """
        Runs the full ingestion pipeline:
        1. Clones repo.
        2. Retrieves Issues & PRs.
        3. Formulates a single comprehensive Markdown document.
        4. Sends the document to Cognee.
        """
        logger.info("Starting ingestion pipeline for %s", repo_url)
        
        # 1. Clone (non-blocking thread execution)
        local_path = await asyncio.to_thread(self._clone_repo, repo_url)
        
        # 2. Get Issues and PRs (non-blocking thread execution)
        issues, pulls, repo_info = await asyncio.to_thread(self._fetch_metadata, repo_url)
        
        owner, repo_name = self.parse_repo_url(repo_url)
        repo_fullname = f"{owner}/{repo_name}"

        # 3. Formulate Repo Description Document (Single document pattern for maximum token efficiency)
        repo_md = f"""# Repository: {repo_info.get('full_name', repo_fullname)}
Description: {repo_info.get('description', '')}
Owner: {repo_info.get('owner', owner)}
Stars: {repo_info.get('stars', 0)} | Forks: {repo_info.get('forks', 0)}
Default Branch: {repo_info.get('default_branch', 'main')}
URL: {repo_info.get('url', repo_url)}

## Recent Closed Issues
"""
        for issue in issues:
            comments_str = ""
            if issue.get("comments"):
                comments_str = " | Comments: " + ", ".join(f"@{c['user']}: {c['body'][:50]}" for c in issue["comments"])
            repo_md += f"- **Issue #{issue['number']}**: '{issue['title']}' created by @{issue['creator']} (state: {issue['state']}, closed: {issue['closed_at']}){comments_str}\n"

        repo_md += "\n## Recent Closed Pull Requests\n"
        for pr in pulls:
            comments_str = ""
            if pr.get("comments"):
                comments_str = " | Comments: " + ", ".join(f"@{c['user']}: {c['body'][:50]}" for c in pr["comments"])
            repo_md += f"- **Pull Request #{pr['number']}**: '{pr['title']}' created by @{pr['creator']} (state: {pr['state']}, base: {pr['base_branch']}, head: {pr['head_branch']}){comments_str}\n"

        # List repository files to give context to Cognee
        repo_md += "\n## Repository Files\n"
        file_count = 0
        for root, dirs, files in os.walk(local_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', 'node_modules', '__pycache__')]
            for file in files:
                if file_count >= 15:
                    break
                rel_path = os.path.relpath(os.path.join(root, file), local_path)
                repo_md += f"- `{rel_path}`\n"
                file_count += 1

        documents_to_add = [repo_md]

        # 4. Ingest into Cognee
        logger.info("Adding 1 document containing repository metadata and PR history to Cognee dataset '%s'", dataset_name)
        await cognee.add(documents_to_add, dataset_name=dataset_name)
        logger.info("Added document to Cognee. Running cognify...")
        
        await cognee.cognify()
        logger.info("Cognify completed successfully.")

        return {
            "status": "success",
            "repo_info": repo_info,
            "document_count": 1,
            "issue_count": len(issues),
            "pr_count": len(pulls)
        }
