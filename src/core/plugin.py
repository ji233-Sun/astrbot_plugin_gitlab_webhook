"""GitLab Webhook Plugin core implementation."""

import json
from aiohttp import web

from astrbot.api import all as api
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star
from astrbot.api import logger

from .config import PluginConfig
from .constants import DEFAULT_PORT
from ..handlers.issues_handler import handle_issues_event
from ..handlers.merge_request_handler import handle_merge_request_event
from ..handlers.push_handler import handle_push_event
from ..utils.rate_limiter import RateLimiter
from ..utils.verify_signature import verify_token


class GitLabWebhookPlugin(Star):
    """GitLab Webhook receiver plugin."""

    def __init__(self, context: Context, config):
        super().__init__(context)
        self.app = web.Application()
        self.app.router.add_post("/webhook", self.handle_webhook)
        self.runner = None
        self.site = None
        self.cfg = PluginConfig(config)

        if self.cfg.rate_limit > 0:
            self.rate_limiter = RateLimiter(max_requests=self.cfg.rate_limit)
        else:
            self.rate_limiter = None

    async def start_server(self):
        # Clean up any existing server instance
        if self.site:
            await self.site.stop()
            logger.info("GitLab Webhook: Cleaned up existing server instance")
        if self.runner:
            await self.runner.cleanup()
            logger.info("GitLab Webhook: Cleaned up existing runner")

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "0.0.0.0", self.cfg.port)
        await self.site.start()
        logger.info(f"GitLab Webhook: Server started on port {self.cfg.port}")

    async def handle_webhook(self, request: web.Request):
        # GitLab 使用 X-Gitlab-Event 头，事件名格式为 "Push Hook" 等
        event_type = request.headers.get("X-Gitlab-Event", "unknown")
        token = request.headers.get("X-Gitlab-Token", "")

        # Rate limiting check
        if self.rate_limiter:
            is_allowed, retry_after = await self.rate_limiter.is_allowed()
            if not is_allowed:
                current, max_req = self.rate_limiter.get_usage()
                logger.warning(
                    f"GitLab Webhook: Rate limit exceeded "
                    f"({current}/{max_req} requests/minute)"
                )
                return web.Response(
                    status=429,
                    text=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(max_req),
                        "X-RateLimit-Remaining": str(max_req - current),
                        "X-RateLimit-Reset": str(retry_after),
                    },
                )

        # Read payload
        try:
            payload_bytes = await request.read()
            data = json.loads(payload_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"GitLab Webhook: Failed to parse JSON: {e}")
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            logger.error(f"GitLab Webhook: Failed to read request body: {e}")
            return web.Response(status=400, text="Failed to read request")

        # Token verification (GitLab 使用简单 token 验证)
        if self.cfg.webhook_secret and token:
            if not verify_token(token, self.cfg.webhook_secret):
                logger.warning("GitLab Webhook: Invalid token - request rejected")
                return web.Response(status=401, text="Invalid token")

        logger.info(f"GitLab Webhook: Received event type: {event_type}")

        if event_type == "ping":
            return web.Response(text="Pong")

        message = None

        try:
            # GitLab 事件类型: Push Hook, Issue Hook, Merge Request Hook
            if event_type == "Push Hook":
                message = await handle_push_event(data, self.context)
            elif event_type == "Issue Hook":
                message = await handle_issues_event(data, self.context)
            elif event_type == "Merge Request Hook":
                message = await handle_merge_request_event(data, self.context)
            else:
                logger.info(f"GitLab Webhook: Event type '{event_type}' not handled")
        except Exception as e:
            logger.error(f"GitLab Webhook: Error processing event: {e}", exc_info=True)
            return web.Response(status=500, text="Internal server error")

        if message:
            if self.cfg.enable_agent:
                from ..services.llm_service import send_with_agent

                await send_with_agent(self, message, data, event_type)
            else:
                await self.send_message(message)

        return web.Response(status=200, text="OK")

    async def send_message(self, message: str):
        if not self.cfg.target_umo:
            logger.error(
                "GitLab Webhook: Cannot send message - target_umo not configured"
            )
            return

        try:
            message_chain = api.MessageChain([Plain(message)])
            result = await self.context.send_message(self.cfg.target_umo, message_chain)
            logger.info(
                f"GitLab Webhook: Message sent to {self.cfg.target_umo}, result: {result}"
            )
            if not result:
                logger.warning(
                    f"GitLab Webhook: Platform not found for {self.cfg.target_umo}"
                )
        except Exception as e:
            # 记录完整错误信息但不传播异常
            logger.error(f"GitLab Webhook: Failed to send message: {e}")
            logger.error(f"GitLab Webhook: Error type: {type(e).__name__}")
            logger.error(f"GitLab Webhook: Error details: {str(e)}")

    async def terminate(self):
        logger.info("GitLab Webhook: Shutting down server...")
        if self.site:
            await self.site.stop()
            logger.info("GitLab Webhook: Server stopped")
        if self.runner:
            await self.runner.cleanup()
            logger.info("GitLab Webhook: Runner cleaned up")