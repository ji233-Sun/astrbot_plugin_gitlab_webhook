"""Merge Request event formatter for GitLab."""


def format_merge_request_message(
    action: str,
    author_name: str,
    repo_name: str,
    mr_iid: int,
    title: str,
    target_branch: str,
    source_branch: str,
    mr_url: str,
) -> str:
    """Format merge request event message."""
    action_emoji = {
        "opened": "🆕",
        "closed": "✅",
        "merged": "🔀",
        "reopened": "🔄",
        "updated": "📝",
    }.get(action, "📝")

    return (
        f"{action_emoji} GitLab Merge Request Event\n"
        f"👤 {author_name} {action} MR in {repo_name}\n"
        f"📋 MR !{mr_iid}: {title}\n"
        f"🌿 {source_branch} → {target_branch}\n"
        f"📎 {mr_url}"
    )