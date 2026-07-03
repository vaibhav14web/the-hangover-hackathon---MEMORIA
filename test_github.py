from dotenv import load_dotenv
load_dotenv()
from ingestion.github_client import GitHubClient

client = GitHubClient()
repo = client.get_repo("tiangolo/fastapi")
prs = client.get_pull_requests(repo, limit=5)

for pr in prs:
    print(f"#{pr['number']}: {pr['title']}")
    print(pr['body'][:200])
    print("---")