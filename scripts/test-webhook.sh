#!/bin/bash

# GitLab Webhook Plugin - 集成测试脚本
# 用法: ./test-webhook.sh [选项] <事件类型>

set -e

# 默认配置
DEFAULT_HOST="localhost"
DEFAULT_PORT="8080"
DEFAULT_SECRET=""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    cat << EOF
GitLab Webhook 测试脚本

用法:
    $0 [选项] <事件类型>

选项:
    -H, --host HOST       服务器地址 (默认: localhost)
    -p, --port PORT       服务器端口 (默认: 8080)
    -s, --secret SECRET   Webhook Token (默认: 无)
    -v, --verbose         详细输出
    -h, --help            显示帮助信息

事件类型:
    push              Push 事件
    issues            Issue 事件
    mr                Merge Request 事件
    ping              Ping 事件 (健康检查)

示例:
    # 发送 push 事件到默认服务器
    $0 push

    # 发送 MR 事件到指定端口
    $0 -p 6100 mr

    # 带密钥的测试
    $0 -s "my-secret" issues

    # 详细模式
    $0 -v push

EOF
}

# 解析参数
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"
SECRET="$DEFAULT_SECRET"
VERBOSE=false
EVENT_TYPE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -s|--secret)
            SECRET="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        push|issues|mr|ping)
            EVENT_TYPE="$1"
            shift
            ;;
        *)
            echo -e "${RED}错误: 未知参数或事件类型 '$1'${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 检查是否指定了事件类型
if [[ -z "$EVENT_TYPE" ]]; then
    echo -e "${RED}错误: 必须指定事件类型${NC}"
    show_help
    exit 1
fi

# 构建 Webhook URL
WEBHOOK_URL="http://${HOST}:${PORT}/webhook"

echo -e "${GREEN}=== GitLab Webhook 测试 ===${NC}"
echo "事件类型: $EVENT_TYPE"
echo "目标地址: $WEBHOOK_URL"
echo ""

# 发送请求的函数
send_request() {
    local event_type="$1"
    local payload="$2"

    # 构建 curl 命令 - 使用 GitLab 格式的头
    CURL_CMD="curl -s -X POST \"$WEBHOOK_URL\" \
        -H \"Content-Type: application/json\" \
        -H \"X-Gitlab-Event: $event_type\""

    # 如果有密钥，添加 GitLab Token 头
    if [[ -n "$SECRET" ]]; then
        CURL_CMD="$CURL_CMD \
        -H \"X-Gitlab-Token: $SECRET\""
    fi

    CURL_CMD="$CURL_CMD \
        -d '$payload'"

    if [[ "$VERBOSE" == true ]]; then
        echo -e "${YELLOW}发送请求...${NC}"
        echo "事件类型: $event_type"
        if [[ "$VERBOSE" == true ]]; then
            echo "Payload:"
            echo "$payload" | jq '.' 2>/dev/null || echo "$payload"
        fi
        echo ""
    fi

    # 执行请求
    RESPONSE=$(eval $CURL_CMD)
    EXIT_CODE=$?

    if [[ $EXIT_CODE -eq 0 ]]; then
        echo -e "${GREEN}✓ 请求发送成功${NC}"
        if [[ "$VERBOSE" == true ]]; then
            echo "响应: $RESPONSE"
        fi
    else
        echo -e "${RED}✗ 请求失败 (退出码: $EXIT_CODE)${NC}"
        if [[ "$VERBOSE" == true ]]; then
            echo "响应: $RESPONSE"
        fi
    fi

    return $EXIT_CODE
}

# 生成测试 payload - GitLab 格式
case "$EVENT_TYPE" in
    push)
        PAYLOAD='{
  "object_kind": "push",
  "ref": "refs/heads/main",
  "before": "a1b2c3d4e5f6g7h8i9j0",
  "after": "0j9i8h7g6f5e4d3c2b1a",
  "user_name": "Test User",
  "user_email": "test@example.com",
  "project": {
    "id": 123,
    "name": "test-repo",
    "path_with_namespace": "testuser/test-repo",
    "web_url": "https://gitlab.com/testuser/test-repo"
  },
  "repository": {
    "name": "test-repo",
    "url": "git@gitlab.com:testuser/test-repo.git"
  },
  "commits": [
    {
      "id": "1234567890abcdef",
      "message": "Test commit message",
      "timestamp": "2024-01-27T10:00:00Z",
      "url": "https://gitlab.com/testuser/test-repo/-/commit/1234567890abcdef",
      "author": {
        "name": "Test User",
        "email": "test@example.com"
      }
    }
  ]
}'
        send_request "Push Hook" "$PAYLOAD"
        ;;

    issues)
        PAYLOAD='{
  "object_kind": "issue",
  "user": {
    "name": "Test User",
    "username": "testuser"
  },
  "project": {
    "id": 123,
    "name": "test-repo",
    "path_with_namespace": "testuser/test-repo",
    "web_url": "https://gitlab.com/testuser/test-repo"
  },
  "object_attributes": {
    "id": 12345,
    "iid": 1,
    "title": "Test Issue",
    "description": "This is a test issue",
    "state": "opened",
    "action": "opened",
    "url": "https://gitlab.com/testuser/test-repo/-/issues/1"
  },
  "repository": {
    "name": "test-repo"
  }
}'
        send_request "Issue Hook" "$PAYLOAD"
        ;;

    mr)
        PAYLOAD='{
  "object_kind": "merge_request",
  "user": {
    "name": "Test User",
    "username": "testuser"
  },
  "project": {
    "id": 123,
    "name": "test-repo",
    "path_with_namespace": "testuser/test-repo",
    "web_url": "https://gitlab.com/testuser/test-repo"
  },
  "object_attributes": {
    "id": 98765,
    "iid": 10,
    "title": "Test Merge Request",
    "description": "This is a test MR",
    "state": "opened",
    "action": "opened",
    "source_branch": "feature-branch",
    "target_branch": "main",
    "url": "https://gitlab.com/testuser/test-repo/-/merge_requests/10"
  },
  "repository": {
    "name": "test-repo"
  }
}'
        send_request "Merge Request Hook" "$PAYLOAD"
        ;;

    ping)
        PAYLOAD='{
  "object_kind": "push",
  "test": true
}'
        send_request "Push Hook" "$PAYLOAD"
        ;;
esac

echo ""
echo -e "${GREEN}=== 测试完成 ===${NC}"