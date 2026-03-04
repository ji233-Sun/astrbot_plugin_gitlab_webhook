# 安装指南

本文档介绍如何安装和配置 AstrBot GitLab Webhook Plugin。

## 前置要求

- 已安装并运行的 AstrBot
- 有访问 AstrBot 插件目录的权限
- （推荐）可访问公网的服务器或内网穿透工具

## 安装步骤

### 1. 克隆插件到 AstrBot 插件目录

```bash
cd AstrBot/data/plugins
git clone https://github.com/TatsukiMengChen/astrbot_plugin_gitlab_webhook.git
```

### 2. 安装依赖

```bash
cd astrbot_plugin_gitlab_webhook
pip install -r requirements.txt
```

或使用 AstrBot 推荐的包管理器（如 uv）：

```bash
uv pip install -r requirements.txt
```

### 3. 配置插件

在 AstrBot WebUI 中配置插件，或编辑配置文件：

`data/config/astrbot_plugin_gitlab_webhook_config.json`

```json
{
  "port": 8080,
  "target_umo": "platform_id:GroupMessage:群号",
  "webhook_secret": "your_gitlab_webhook_token",
  "rate_limit": 10
}
```

配置项说明详见 [配置文档](02-configuration.md)。

### 4. 重启 AstrBot

重启 AstrBot 以加载插件：

```bash
# 如果使用 systemd
sudo systemctl restart astrbot

# 或手动重启
# Ctrl+C 停止后重新运行
```

查看日志确认插件已加载：

```
[INFO] GitLab Webhook server started on port 8080
```

## 配置 GitLab Webhook

### 1. 打开 GitLab 项目设置

进入你的 GitLab 项目 → **Settings** → **Webhooks**

### 2. 配置 Webhook

- **URL**: `http://你的服务器IP:配置的端口/webhook`
  - 例如：`http://123.45.67.89:8080/webhook`
- **Secret Token** (强烈推荐): 配置 Webhook 密钥用于验证
  1. 在插件配置中设置 `webhook_secret` 字段
  2. 将此处生成的密钥复制到 GitLab Webhook 设置
  3. 用于验证请求来源，防止伪造请求
  4. 留空则禁用验证（生产环境不推荐）
- **Trigger**: 选择需要触发的事件
  - 建议勾选：`Push events`, `Issues events`, `Merge request events`
- **SSL verification**: 如果使用 HTTP 可以取消勾选

### 3. 点击 "Add webhook"

GitLab 会发送测试请求，检查 AstrBot 日志确认收到：

```
[INFO] GitLab Webhook: Received event type: Push Hook
```

## 获取目标 UMO

1. 加入目标群组
2. 在群组中发送命令：`/sid`
3. AstrBot 会返回当前会话的 UMO，例如：
   ```
   UMO: 「default:GroupMessage:1078537517」 此值可用于设置白名单。
   ```
4. 将此 UMO 填入插件的 `target_umo` 配置项

## 下一步

- [配置详解](02-configuration.md) - 了解所有配置选项
- [使用示例](03-usage.md) - 查看消息格式
- [部署指南](04-deployment.md) - 防火墙、Docker 配置