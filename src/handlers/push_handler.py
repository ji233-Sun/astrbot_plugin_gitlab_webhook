"""Push event handler for GitLab."""

from astrbot.api import logger

from ..formatters.push_formatter import format_push_message


async def handle_push_event(data: dict, context):
    """Handle push event from GitLab webhook."""
    try:
        # GitLab push payload 结构
        user_name = data.get("user_name", "Unknown")

        repository = data.get("repository", {})
        repo_name = repository.get("name", "Unknown")

        project = data.get("project", {})
        project_name = project.get("path_with_namespace", repo_name)

        ref = data.get("ref", "")
        branch = ref.replace("refs/heads/", "") if ref else "Unknown"

        commits = data.get("commits", [])
        if not commits:
            logger.warning("GitLab Webhook: Push event has no commits")
            return None

        # 获取最新提交信息 (GitLab 最后一个是最新的)
        commit = commits[-1]
        commit_message = commit.get("message", "No message")
        commit_url = commit.get("url", "")
        commit_id = commit.get("id", "")[:7]

        message = format_push_message(
            author_name=user_name,
            repo_name=project_name,
            branch=branch,
            commit_message=commit_message,
            commit_url=commit_url,
            commit_id=commit_id,
        )

        return message

    except Exception as e:
        logger.error(f"GitLab Webhook: Error handling push event: {e}")
        return None