"""Issues event formatter for GitLab."""


def format_issue_message(
    action: str,
    author_name: str,
    repo_name: str,
    issue_number: int,
    title: str,
    issue_url: str,
) -> str:
    """Format issue event message."""
    action_emoji = {
        "opened": "🆕",
        "closed": "✅",
        "reopened": "🔄",
    }.get(action, "📝")

    return (
        f"{action_emoji} GitLab Issue Event\n"
        f"👤 {author_name} {action} issue in {repo_name}\n"
        f"📋 Issue #{issue_number}: {title}\n"
        f"📎 {issue_url}"
    )