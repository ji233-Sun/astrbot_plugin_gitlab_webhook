"""GitLab Webhook Plugin constants."""

# Default port for webhook server
DEFAULT_PORT = 8080

# Default rate limit (requests per minute)
DEFAULT_RATE_LIMIT = 10

# Default LLM timeout (seconds)
DEFAULT_LLM_TIMEOUT = 60

# GitLab event types (从 X-Gitlab-Event 头获取)
EVENT_TYPE_PUSH = "Push Hook"
EVENT_TYPE_ISSUES = "Issue Hook"
EVENT_TYPE_MERGE_REQUEST = "Merge Request Hook"
EVENT_TYPE_PING = "ping"

# Issue actions
ACTION_OPENED = "opened"
ACTION_CLOSED = "closed"
ACTION_REOPENED = "reopened"

# Merge Request actions
ACTION_MR_OPENED = "opened"
ACTION_MR_CLOSED = "closed"
ACTION_MR_REOPENED = "reopened"
ACTION_MR_MERGED = "merged"
ACTION_MR_UPDATED = "updated"