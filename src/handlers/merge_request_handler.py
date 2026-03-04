"""Merge Request event handler for GitLab."""

from astrbot.api import logger

from ..formatters.merge_request_formatter import format_merge_request_message


async def handle_merge_request_event(data: dict, context):
    """Handle merge request event from GitLab webhook."""
    try:
        # GitLab MR payload 结构
        action = data.get("object_attributes", {}).get("action", "unknown")
        merge_request = data.get("object_attributes", {})
        repository = data.get("repository", {})

        mr_iid = merge_request.get("iid", 0)  # GitLab 使用 iid 作为显示编号
        title = merge_request.get("title", "No title")
        mr_url = merge_request.get("url", "")

        # 获取作者信息
        author = data.get("user", {})
        author_name = author.get("name", "Unknown")
        author_username = author.get("username", "")

        # 仓库名称
        repo_name = repository.get("name", "Unknown")
        project = data.get("project", {})
        project_name = project.get("path_with_namespace", repo_name)

        # 分支信息
        source_branch = merge_request.get("source_branch", "unknown")
        target_branch = merge_request.get("target_branch", "unknown")

        # MR 状态
        state = merge_request.get("state", "unknown")

        message = format_merge_request_message(
            action=action,
            author_name=author_name,
            repo_name=project_name,
            mr_iid=mr_iid,
            title=title,
            target_branch=target_branch,
            source_branch=source_branch,
            mr_url=mr_url,
        )

        return message

    except Exception as e:
        logger.error(f"GitLab Webhook: Error handling merge request event: {e}")
        return None