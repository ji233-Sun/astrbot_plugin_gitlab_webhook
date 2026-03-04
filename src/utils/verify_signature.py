"""Webhook token verification utilities for GitLab."""

import hmac
import hashlib


def verify_token(token_header: str, secret: str) -> bool:
    """
    Verify GitLab webhook token.

    GitLab 使用简单的 token 验证方式，通过 X-Gitlab-Token 头传递。

    Args:
        token_header: X-Gitlab-Token header value
        secret: Webhook secret from GitLab

    Returns:
        True if token matches, False otherwise
    """
    if not secret or not token_header:
        return False

    # GitLab 使用简单的字符串比较
    # 使用常量时间比较以防止时序攻击
    return hmac.compare_digest(token_header, secret)


def verify_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
) -> bool:
    """
    Verify webhook signature using HMAC-SHA256 (保留用于兼容性)。

    注意：GitLab 默认使用 token 验证，此函数保留用于可能的扩展场景。

    Args:
        payload: Raw request body bytes
        signature_header: Signature header value
        secret: Webhook secret

    Returns:
        True if signature is valid, False otherwise
    """
    if not secret or not signature_header:
        return False

    # 移除可能的前缀
    if signature_header.startswith("sha256="):
        signature = signature_header[7:]
    else:
        signature = signature_header

    # 计算期望的签名
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    # 使用常量时间比较以防止时序攻击
    return hmac.compare_digest(expected_signature, signature)