"""Issues event handler for GitLab."""

from astrbot.api import logger

from ..formatters.issues_formatter import format_issue_message


async def handle_issues_event(data: dict, context):
    """Handle issues event from GitLab webhook."""
    try:
        # GitLab issue payload 结构
        action = data.get("object_attributes", {}).get("action", "unknown")
        issue = data.get("object_attributes", {})
        repository = data.get("repository", {})

        issue_iid = issue.get("iid", 0)  # GitLab 使用 iid 作为显示编号
        title = issue.get("title", "No title")
        issue_url = issue.get("url", "")

        # 获取作者信息
        author = data.get("user", {})
        author_name = author.get("name", "Unknown")

        # 仓库名称
        repo_name = repository.get("name", "Unknown")
        project = data.get("project", {})
        project_name = project.get("path_with_namespace", repo_name)

        message = format_issue_message(
            action=action,
            author_name=author_name,
            repo_name=project_name,
            issue_number=issue_iid,
            title=title,
            issue_url=issue_url,
        )

        return message

    except Exception as e:
        logger.error(f"GitLab Webhook: Error handling issues event: {e}")
        return None