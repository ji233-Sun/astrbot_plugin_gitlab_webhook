"""Push event formatter for GitLab."""


def format_push_message(
    author_name: str,
    repo_name: str,
    branch: str,
    commit_message: str,
    commit_url: str,
    commit_id: str,
) -> str:
    """Format push event message."""
    return (
        f"📦 GitLab Push Event\n"
        f"👤 {author_name} pushed to {repo_name}\n"
        f"🌿 Branch: {branch}\n"
        f"💬 {commit_message}\n"
        f"🔗 Commit: {commit_id}\n"
        f"📎 {commit_url}"
    )
