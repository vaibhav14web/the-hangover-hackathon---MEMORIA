from graph.manual_context import MANUAL_PR_CONTEXT

def format_pr_for_ingestion(pr: dict) -> str:
    comments_text = "\n".join(
        f"Comment: {c}" for c in pr['comments']
        if c.strip() and "docs preview" not in c.lower()
    )

    extra = ""
    if pr['number'] in MANUAL_PR_CONTEXT:
        extra = MANUAL_PR_CONTEXT[pr['number']]

    return f"""
Pull Request #{pr['number']}: {pr['title']}
Merged: {pr['merged_at']}

Description:
{pr['body'] if pr['body'].strip() else '(no description provided)'}

Discussion:
{comments_text if comments_text else '(no substantive discussion)'}
{extra}
"""