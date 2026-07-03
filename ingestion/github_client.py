import os
from github import Github, RateLimitExceededException
from datetime import datetime, timezone
import time

class GitHubClient:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        self.client = Github(token)

    def parse_repo_url(self, url: str):
        """
        Parse a GitHub repository URL and return the owner and repository name.
        Supports URLs with or without a trailing '.git'.
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != "github.com":
            raise ValueError(f"Invalid GitHub URL: {url}")
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        owner, repo = path_parts[0], path_parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo
    def get_repo(self, repo_name: str):
        return self.client.get_repo(repo_name)

    def get_pull_requests(self, repo, limit: int = 50):
        prs = []
        for pr in self._safe_call(repo.get_pulls, state="closed"):
            if pr.merged and len(prs) < limit:
                prs.append({
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body or "",
                    "merged_at": str(pr.merged_at),
                    "comments": [c.body for c in self._safe_call(pr.get_issue_comments)],
                })
            if len(prs) >= limit:
                break
        return prs

    def get_issues(self, repo, limit: int = 50):
        issues = []
        for issue in self._safe_call(repo.get_issues, state="closed"):
            if not issue.pull_request and len(issues) < limit:
                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                })
            if len(issues) >= limit:
                break
        return issues

    def _safe_call(self, func, *args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededException:
                reset = self.client.get_rate_limit().core.reset
                sleep_time = (reset - datetime.now(timezone.utc)).seconds + 10
                print(f"Rate limited. Sleeping {sleep_time}s...")
                time.sleep(sleep_time)
                
    def get_specific_prs(self, repo, pr_numbers: list[int]):
        prs = []
        for num in pr_numbers:
           pr = self._safe_call(repo.get_pull, num)
           prs.append({
            "number": pr.number,
            "title": pr.title,
            "body": pr.body or "",
            "merged_at": str(pr.merged_at),
            "comments": [c.body for c in self._safe_call(pr.get_issue_comments)],
        })
        return prs            