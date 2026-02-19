# Gmail MCP Server

一个封装 Gmail API 的 Model Context Protocol (MCP) Server，提供邮件搜索和读取功能。

## 功能特性

- **`gmail_search_messages`**: 使用 Gmail 搜索语法搜索邮件，支持分页、去重、元数据补全
- **`gmail_get_message`**: 根据邮件 ID 获取完整邮件详情（headers、正文）
- **OAuth2 两阶段授权**: 预授权 CLI + 运行时 token 复用（适配无头环境）
- **错误处理与重试**: 自动处理 429 限流、5xx 错误，指数退避重试
- **分页与去重**: 自动处理多页结果，确保结果唯一性

## 前置要求

- Python 3.10+
- Google Cloud 项目（已启用 Gmail API）
- OAuth2 客户端凭证（`credentials.json`）

## 环境搭建

### 方案 A: 使用独立虚拟环境（推荐，用于 Claude Desktop 部署）

```bash
# 在 week3/ 目录下创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 方案 B: 使用 Anaconda 环境（用于开发）

```bash
# 激活 conda 环境
conda activate cs146s

# 安装依赖
pip install -r requirements.txt
```

## OAuth2 授权配置

### 1. 获取 Google Cloud OAuth2 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择项目
3. 启用 Gmail API
4. 创建 OAuth 2.0 客户端 ID 凭证（应用类型：桌面应用）
5. 下载凭证文件，保存为 `week3/credentials.json`

### 2. 预授权（一次性操作）

在**有浏览器的终端**中运行预授权脚本：

```bash
# 使用 venv
.venv\Scripts\python server\auth_cli.py

# 或使用 conda 环境
python server\auth_cli.py
```

脚本会：
1. 打开浏览器进行 OAuth2 授权
2. 将 refresh_token 保存到 `.token.json`
3. MCP Server 运行时将使用此 token 文件

**重要**: `.token.json` 已加入 `.gitignore`，不应提交到版本控制。

## Claude Desktop 配置

编辑 Claude Desktop 配置文件（位置因系统而异）：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

添加以下配置（**请将路径替换为你的实际路径**）：

```json
{
  "mcpServers": {
    "gmail": {
      "command": "E:/Users/Document/code/CS146S/CS146S/week3/.venv/Scripts/python.exe",
      "args": ["-m", "server.main"],
      "env": {
        "PYTHONPATH": "E:/Users/Document/code/CS146S/CS146S/week3",
        "GMAIL_PROJECT_ROOT": "E:/Users/Document/code/CS146S/CS146S/week3"
      },
      "cwd": "E:/Users/Document/code/CS146S/CS146S/week3"
    }
  }
}
```

**注意**: 
- `command` 路径必须是 `.venv/Scripts/python.exe` 的**绝对路径**
- `PYTHONPATH` 应指向 `week3/` 目录的绝对路径
- `cwd` 也应指向 `week3/` 目录
- **推荐**：添加 `GMAIL_PROJECT_ROOT` 环境变量指向项目根目录，确保在不同电脑上都能正确找到 `credentials.json` 和 `.token.json`

**路径查找优先级**：
1. `GMAIL_PROJECT_ROOT` 环境变量（最高优先级，推荐用于跨电脑部署）
2. 当前工作目录（如果包含 `server/` 目录和凭证文件）
3. 脚本文件位置（自动回退方案）

配置完成后，重启 Claude Desktop。

## 运行与测试

### 运行 MCP Server（本地测试）

```bash
# 使用 venv
.venv\Scripts\python -m server.main

# 或使用 conda 环境
python -m server.main
```

### 运行单元测试

```bash
# 运行所有单元测试（mock 测试）
pytest server/tests/ -v

# 运行真实 API 测试（需要 credentials.json 和 .token.json）
pytest -m live -v
```

### 测试覆盖

- **单元测试**: `test_search.py`, `test_get_message.py`, `test_auth.py`
- **真实 API 测试**: `test_live_search.py`, `test_live_get_message.py`

## 工具使用示例

### gmail_search_messages

搜索 Gmail 邮件，支持 Gmail 搜索语法。

**参数**:
- `query` (必需): Gmail 搜索查询（语法参考：[Gmail 搜索帮助](https://support.google.com/mail/answer/7190)）
- `max_results` (可选): 最大返回结果数（1-50，默认 10）
- `newer_than_days` (可选): 仅返回最近 N 天的邮件
- `label_ids` (可选): 按标签过滤（如 `["INBOX", "STARRED"]`）

**示例**:

```python
# 基础搜索
gmail_search_messages(query="from:example@gmail.com", max_results=10)

# 主题搜索
gmail_search_messages(query="subject:meeting", max_results=20)

# 组合过滤
gmail_search_messages(
    query="from:team@company.com",
    max_results=15,
    newer_than_days=7,
    label_ids=["INBOX"]
)
```

**返回格式**:

```json
{
  "results": [
    {
      "id": "msg123",
      "thread_id": "thread123",
      "from_email": "sender@example.com",
      "subject": "Test Subject",
      "date": "Mon, 1 Jan 2024 00:00:00 +0000",
      "snippet": "Email preview text..."
    }
  ],
  "total_count": 1
}
```

### gmail_get_message

获取邮件完整详情。

**参数**:
- `message_id` (必需): Gmail 邮件 ID（从搜索结果获取）
- `fmt` (可选): 格式 - `"full"`（包含正文）或 `"metadata"`（仅 headers），默认 `"full"`

**示例**:

```python
# 获取完整邮件
gmail_get_message(message_id="msg123", fmt="full")

# 仅获取元数据
gmail_get_message(message_id="msg123", fmt="metadata")
```

**返回格式**:

```json
{
  "id": "msg123",
  "thread_id": "thread123",
  "headers": {
    "From": "sender@example.com",
    "To": "recipient@example.com",
    "Subject": "Test Subject",
    "Date": "Mon, 1 Jan 2024 00:00:00 +0000"
  },
  "body_text": "Plain text email body...",
  "body_html": "<p>HTML email body...</p>",
  "snippet": "Email preview..."
}
```

## 跨电脑部署

### 方法 1：使用环境变量（推荐）

在不同电脑上部署时，推荐使用 `GMAIL_PROJECT_ROOT` 环境变量指定项目根目录：

**Windows (Claude Desktop 配置)**：
```json
{
  "mcpServers": {
    "gmail": {
      "command": "C:/path/to/week3/.venv/Scripts/python.exe",
      "args": ["-m", "server.main"],
      "env": {
        "PYTHONPATH": "C:/path/to/week3",
        "GMAIL_PROJECT_ROOT": "C:/path/to/week3"
      },
      "cwd": "C:/path/to/week3"
    }
  }
}
```

**macOS/Linux (Claude Desktop 配置)**：
```json
{
  "mcpServers": {
    "gmail": {
      "command": "/path/to/week3/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "PYTHONPATH": "/path/to/week3",
        "GMAIL_PROJECT_ROOT": "/path/to/week3"
      },
      "cwd": "/path/to/week3"
    }
  }
}
```

### 方法 2：使用绝对路径

如果不想使用环境变量，确保 `cwd` 设置为项目根目录，代码会自动从当前工作目录查找文件。

### 路径查找优先级

代码按以下优先级查找项目根目录：

1. **`GMAIL_PROJECT_ROOT` 环境变量**（最高优先级，推荐用于跨电脑部署）
2. **当前工作目录**（如果包含 `server/` 目录和凭证文件）
3. **脚本文件位置**（自动回退方案，基于 `server/auth.py` 的位置）

### 部署步骤

1. 将整个 `week3/` 目录复制到新电脑
2. 在新电脑上创建虚拟环境并安装依赖：
   ```bash
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt  # Windows
   # 或
   .venv/bin/pip install -r requirements.txt      # macOS/Linux
   ```
3. 复制 `credentials.json` 和 `.token.json` 到项目根目录
4. 更新 Claude Desktop 配置中的路径（使用新电脑的绝对路径）
5. 添加 `GMAIL_PROJECT_ROOT` 环境变量（推荐）

## 故障排查

### 1. 授权失败

**错误**: `Token file not found` 或 `Failed to refresh access token`

**解决**:
1. 确保已运行 `python server/auth_cli.py` 完成预授权
2. 检查 `.token.json` 文件是否存在
3. 如果 refresh_token 已过期，删除 `.token.json` 并重新运行 `auth_cli.py`

### 2. Claude Desktop 无法连接

**错误**: MCP server 未出现在 Claude Desktop 中

**解决**:
1. 检查 `claude_desktop_config.json` 中的路径是否正确（使用绝对路径）
2. 确保 `.venv` 已创建且依赖已安装
3. 检查 Python 解释器路径是否正确
4. 查看 Claude Desktop 日志（通常在应用数据目录）

### 3. API 限流错误

**错误**: `rate_limited` 或 429 错误

**解决**:
- Gmail API 有配额限制，等待一段时间后重试
- 减少 `max_results` 参数值
- 避免频繁调用

### 4. 搜索结果为空

**可能原因**:
- 搜索条件过于严格
- 账户中确实没有匹配的邮件

**解决**:
- 尝试更宽泛的搜索条件（如 `in:inbox`）
- 检查 Gmail 搜索语法是否正确

## 项目结构

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP Server 入口
│   ├── auth.py              # 运行时鉴权
│   ├── auth_cli.py          # 预授权 CLI
│   ├── gmail_client.py      # Gmail API 客户端
│   ├── models.py            # 数据模型
│   ├── tools.py             # MCP 工具实现
│   └── tests/               # 测试文件
│       ├── conftest.py
│       ├── test_search.py
│       ├── test_get_message.py
│       ├── test_auth.py
│       ├── test_live_search.py
│       └── test_live_get_message.py
├── requirements.txt         # Python 依赖
├── .gitignore              # Git 忽略规则
├── DESIGN.md               # 设计文档
└── README.md               # 本文档
```

## 开发说明

### 代码规范

- 使用类型提示（type hints）
- 遵循 PEP 8 代码风格
- 使用 Pydantic 进行参数验证

### 日志

- 所有日志输出到 `stderr`（避免污染 STDIO 传输）
- 结构化日志格式（JSON）
- 敏感信息脱敏（不打印 token、完整邮件正文）

### 错误处理

- **429 (Rate Limit)**: 指数退避重试 3 次（1s/2s/4s）
- **5xx (Server Error)**: 指数退避重试 2 次（1s/2s）
- **401 (Auth Error)**: 直接返回，提示重新授权
- **404 (Not Found)**: 返回明确错误信息

## 参考文档

- [Gmail API 指南](https://developers.google.com/workspace/gmail/api/guides)
- [Messages.list API](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
- [Messages.get API](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)
- [Gmail 搜索语法](https://support.google.com/mail/answer/7190)
- [OAuth2 协议](https://developers.google.com/identity/protocols/oauth2)
- [MCP 规范](https://modelcontextprotocol.io/specification/)

## 许可证

本项目仅用于课程作业，不用于商业用途。

