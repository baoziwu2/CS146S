# [FEATURE] Design Document

## Current Context

* Brief overview of the existing system

  * 目前无现成系统；目标是新增一个 MCP Server 来封装 Gmail API（[https://developers.google.com/workspace/gmail/api/guides](https://developers.google.com/workspace/gmail/api/guides)），向 MCP 客户端提供工具调用能力。

* Key components and their relationships

  * **MCP Server**（工具注册与协议处理；MCP 规范参考：[https://modelcontextprotocol.io/specification/](https://modelcontextprotocol.io/specification/)）
    * 负责处理 MCP 协议通信（STDIO 模式优先），注册并暴露工具给客户端
    * 接收工具调用请求，验证参数，调用底层 Gmail Client，返回结构化结果

  * **Gmail Client**（对 Gmail REST API 的薄封装：messages.list/messages.get）
    * `list_messages`：调用 [messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list) API，支持 query 搜索、分页（nextPageToken）、结果数量限制
    * `get_message`：调用 [messages.get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get) API，获取邮件完整详情（headers、body_text、body_html）
    * 封装 HTTP 请求、重试逻辑、错误映射、超时控制

  * **Auth 模块**（OAuth2 token 获取/刷新/持久化：[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
    * **重要约束**：MCP Server 以 STDIO 后台进程运行时**无法弹出浏览器窗口**（`flow.run_local_server()` 在无头环境下会阻塞或失败），因此采用**"预授权 + token 复用"两阶段方案**：
      * **阶段 A（一次性，手动）**：提供独立的 CLI 脚本 `auth_cli.py`，开发者在有浏览器的终端中手动运行一次，完成 OAuth2 授权流程，将 refresh_token 持久化到 `.token.json`
      * **阶段 B（运行时，自动）**：MCP Server 启动时仅从 `.token.json` 读取已有的 refresh_token，调用 `creds.refresh(Request())` 获取新的 access_token；**绝不在服务进程内发起浏览器授权流程**
    * Token 安全存储（本地文件 `.token.json`，加入 `.gitignore`）
    * 自动刷新过期 access_token（基于 refresh_token），确保 API 调用可用性
    * 启动时若 `.token.json` 不存在或 refresh_token 失效，输出明确错误提示（指引用户运行 `python auth_cli.py`），而非尝试弹窗

  * **工具层**（gmail_search_messages / gmail_get_message）
    * `gmail_search_messages`：核心搜索工具，支持 Gmail query 语法（[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)），处理分页、结果补全、去重
    * `gmail_get_message`：按 message_id 获取邮件详情，支持不同格式（full/metadata）

* Pain points or gaps being addressed

  * **直接在客户端调用 Gmail API 不便**：需要处理 OAuth2 流程、token 管理、API 限流等复杂逻辑，缺乏统一封装
  * **OAuth2 浏览器授权与无头运行冲突**：标准 `run_local_server()` 方案在 MCP Server（STDIO 后台进程）中无法弹出浏览器，导致授权流程阻塞或报错（已实际踩坑验证）；需要拆分为"预授权 CLI"+"运行时 token 复用"两阶段
  * **搜索结果分页、query 语法、空结果、429 限流等边界复杂**：需要统一处理分页循环、query 组合（newer_than_days、label_ids）、空结果提示、429/5xx 重试策略（指数退避）
  * **缺乏统一校验/重试/结构化输出**：输入参数校验、错误分类映射、结构化 JSON 输出需要标准化
  * **Anaconda 环境与 Claude Desktop 部署的兼容问题**：开发使用 Anaconda `cs146s` 环境，但 Claude Desktop MCP 配置需要指定绝对 Python 解释器路径；conda 环境路径与 `.venv` 路径不同，需要明确解决方案
  * **需要展示"真实外部 API + 多工具 + 可测试性 + 文档完备"**：作为作业项目，需要体现对真实 API 集成、多工具设计、测试覆盖、文档完整性的理解

## Requirements

### Functional Requirements

* List of must-have functionality

  1. **Tool: `gmail_search_messages`** 支持 Gmail query 搜索（语法参考：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)），调用 messages.list（[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)）返回可用的 message 列表（含 id/threadId/关键头信息/snippet）
     * 支持基础 query 字符串（如 `from:example@gmail.com`、`subject:meeting`）
     * 支持可选参数组合：`newer_than_days`（转换为 `newer_than:Nd`）、`label_ids`（转换为 `label:INBOX` 等）
     * 返回结构化结果：id、thread_id、from_email、subject、date、snippet
     * 对前 K 条结果（例如前 10 条）自动补全 metadata（调用 messages.get 获取 subject/from/date），保证输出有意义

  2. **Tool: `gmail_get_message`** 按 message_id 调用 messages.get（[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)）获取详情（headers + body_text/body_html 可选）
     * 支持 `format` 参数：`full`（完整内容）或 `metadata`（仅 headers + snippet）
     * 返回结构化 JSON：headers（from/to/subject/date 等）、body_text（纯文本）、body_html（可选）

  3. **分页处理**（messages.list 的 nextPageToken），至少可配置 max_results，必要时支持 next_page_token 或内部自动翻页到上限
     * `max_results` 参数控制最终返回数量上限（建议范围 1-50，默认 10）
     * 内部自动处理分页循环：当结果超过单页限制时，使用 nextPageToken 继续拉取，直到达到 max_results 或没有更多结果
     * 去重处理：跨页可能出现重复 id，需要去重并保持顺序稳定
     * 可选：支持显式 `page_token` 参数用于手动分页（高级场景）

* Expected behaviors

  * **搜索**：输入 query → 返回稳定结构化结果；空结果返回空数组且提供建议（例如 hint 字段提示"尝试调整搜索条件"）
  * **读取**：无权限/不存在/格式不支持 → 返回明确错误（可操作建议，例如"请检查 message_id 是否正确"或"需要重新授权"）
  * **所有工具**：参数校验失败要在调用前报错（例如 query 为空、max_results 越界、message_id 非法）；外部 API 失败要有错误码映射与重试策略（建议描述 429/5xx 的处理：429 使用指数退避重试最多 3 次，5xx 重试 2 次，401 需要重新授权）

* Integration points

  * **Gmail API endpoints**：messages.list / messages.get（可选 drafts.*）
  * **OAuth2**：获取并刷新访问令牌（[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
  * **MCP client**（Claude Desktop / Cursor / 其它 MCP 客户端）

### Non-Functional Requirements

* Performance expectations

  * 搜索请求在合理网络条件下 < 2s 返回（单页结果，无补全）；分页最多拉取到 max_results 上限（例如 50 条），总耗时控制在 5-10s 内
  * 读取单条邮件详情 < 1s（format=metadata）或 < 2s（format=full）

* Scalability needs

  * 单用户 token 缓存；后续可扩展到多用户/多租户 token 存储（加密、隔离）

* Observability requirements

  * 结构化日志（stderr 或文件），包含 request_id、tool_name、latency、gmail_api_status
  * 关键指标：搜索成功率、平均延迟、分页次数分布、429 频率、补全失败率

* Security considerations

  * OAuth2 token 安全存储（最小权限 scope；OAuth2 参考：[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
  * 服务侧认证（可选；MCP 授权参考：[https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)）与敏感信息脱敏（日志不得打印 token）
  * 避免 stdout 日志污染 STDIO 传输

## Design Decisions

### 1. [Major Decision Area]（搜索实现策略）

Will implement/choose **"messages.list + 逐条补全 metadata（可选）"** because:

* **Rationale 1**：messages.list（[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)）只返回 id/threadId，需要补全 headers/snippet 才能"有意义"展示
* **Rationale 2**：可控制补全数量（仅补全前 K 条）避免性能与限流风险
* **Trade-offs considered**

  * **方案 A**：list 后对每条 get（更完整但更慢、可能触发限流）
  * **方案 B**：只返回 id（更快但输出不够"meaningful"）
  * **折中**：list → 对前 K 条做 get(metadata)（[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)）拿 subject/from/date/snippet，剩余条数仅返回 id/threadId

### 2. [Another Decision Area]（分页与结果上限）

Will implement/choose **"显式 max_results + 安全分页循环 + 去重"** because:

* **Rationale 1**：保证工具响应可控，不会无限拉取
* **Rationale 2**：分页 token（nextPageToken）处理清晰，利于测试与重放（messages.list 返回说明见：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)）
* **Alternatives considered**

  * **只返回第一分页**（实现简单但可用性不足）
  * **自动拉到所有结果**（不可控、风险高）

### 3. [Error Handling Strategy]（错误处理与重试）

Will implement/choose **"分类错误映射 + 指数退避重试"** because:

* **Rationale 1**：Gmail API 可能返回 429（限流）、5xx（临时错误）、401（授权失效），需要不同策略
* **Rationale 2**：指数退避避免加重 API 压力，同时提高成功率
* **Trade-offs considered**

  * **方案 A**：所有错误直接返回（简单但用户体验差）
  * **方案 B**：无限重试（可能导致长时间阻塞）
  * **折中**：429 重试 3 次（退避 1s/2s/4s），5xx 重试 2 次（退避 1s/2s），401 直接返回要求重新授权

### 4. [OAuth2 Headless Auth Strategy]（无头环境鉴权策略）

Will implement/choose **"预授权 CLI 脚本 + 运行时 token 复用（禁止服务内弹窗）"** because:

* **Rationale 1**：MCP Server 以 STDIO 后台进程形式被 Claude Desktop 拉起，无 TTY、无 GUI，`flow.run_local_server()` 会阻塞在 `handle_request()` 上无法完成回调（已在实际环境中验证：第一次尝试触发 `KeyboardInterrupt`）
* **Rationale 2**：将授权与运行解耦——授权是一次性操作（产出 refresh_token），运行时只需 `creds.refresh(Request())`，更安全、更可预测
* **Trade-offs considered**

  * **方案 A：服务内 `run_local_server()`**（标准 google-auth-oauthlib 示例方案）
    * 优点：代码简单、官方示例直接可用
    * **致命缺陷**：STDIO 后台进程无法打开浏览器，`handle_request()` 阻塞等待回调永远不会到达
  * **方案 B：`run_console()` 手动复制粘贴授权码**
    * 优点：不依赖浏览器回调
    * 缺陷：仍需要 stdin 交互，STDIO 模式下 stdin 已被 MCP 协议占用，同样不可行
  * **方案 C（采用）：独立 `auth_cli.py` 预授权**
    * 开发者在普通终端运行 `python auth_cli.py`，走完标准 `run_local_server()` 流程，产出 `.token.json`（含 refresh_token）
    * MCP Server 启动时仅读取 `.token.json`，调用 `creds.refresh()` 刷新 access_token
    * 若 `.token.json` 不存在或 refresh_token 失效，输出明确 stderr 错误并安全退出，不尝试交互式授权
  * **方案 D：Service Account**
    * 优点：完全无交互
    * 缺陷：Service Account 无法直接访问个人 Gmail 邮箱（除非在 Google Workspace 域内做域委派），不适用于本项目场景

### 5. [Environment Strategy]（运行环境与 Claude Desktop 部署策略）

Will implement/choose **"week3 目录内独立 .venv + Claude Desktop 指向绝对路径"** because:

* **Rationale 1**：本项目开发使用 Anaconda `cs146s` 环境，但 Claude Desktop MCP 配置（`claude_desktop_config.json`）需要指定具体的 Python 解释器绝对路径，conda 环境的 `python.exe` 路径因操作系统和 conda 安装位置不同而不稳定
* **Rationale 2**：在 `week3/` 下创建独立 `.venv`（通过 `python -m venv .venv` 或从 conda 环境构建），确保所有依赖安装在该 venv 中，Claude Desktop 配置直接指向 `.venv/Scripts/python.exe` 绝对路径，可复现性最强
* **Trade-offs considered**

  * **方案 A：直接使用 conda 环境路径**
    * 配置：`"command": "C:/Users/<user>/anaconda3/envs/cs146s/python.exe"`
    * 优点：无需额外 venv
    * 缺陷：conda 路径因用户不同而异；conda activate 的环境变量（如 `CONDA_PREFIX`）在 Claude Desktop 子进程中不会自动设置，可能导致包查找失败
  * **方案 B（采用）：week3/.venv 独立虚拟环境**
    * 使用 `python -m venv .venv` 创建（基于系统 Python 或 conda base），然后 `pip install` 所有依赖
    * Claude Desktop 配置：`"command": "E:/Users/Document/code/CS146S/CS146S/week3/.venv/Scripts/python.exe"`，配合 `"env": {"PYTHONPATH": "E:/Users/Document/code/CS146S/CS146S/week3"}`
    * README 中提供一键安装脚本（`setup_env.bat` / `setup_env.sh`），从 `requirements.txt` 安装依赖
  * **方案 C：conda 环境 + wrapper 脚本**
    * 编写 `run_server.bat`：先 `conda activate cs146s`，再 `python -m server.main`
    * Claude Desktop 配置 `"command": "run_server.bat"`
    * 缺陷：Windows 下 bat 脚本启动有额外复杂度（conda init 问题），且不利于跨平台

## Technical Design

If relevant, specify the following:

### 1. Core Components

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal, Optional, Sequence

MessageFormat = Literal["full", "metadata"]

@dataclass(frozen=True)
class SearchResultItem:
    id: str
    thread_id: str
    from_email: Optional[str]
    subject: Optional[str]
    date: Optional[str]
    snippet: Optional[str]

class GmailClient:
    """Thin wrapper around Gmail API with retries, timeouts, and typed responses.
    References:
    - messages.list: https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list
    - messages.get:  https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get
    """
    def list_messages(self, *, user_id: str, query: str, max_results: int,
                      page_token: Optional[str] = None) -> dict[str, Any]:
        """
        Call Gmail API messages.list endpoint.
        Returns: {
            "messages": [{"id": "...", "threadId": "..."}, ...],
            "nextPageToken": "..." (optional),
            "resultSizeEstimate": int
        }
        """
        raise NotImplementedError

    def get_message(self, *, user_id: str, message_id: str, fmt: MessageFormat) -> dict[str, Any]:
        """
        Call Gmail API messages.get endpoint.
        Returns: {
            "id": "...",
            "threadId": "...",
            "snippet": "...",
            "payload": {
                "headers": [...],
                "body": {...},
                "parts": [...]
            }
        }
        """
        raise NotImplementedError

class GmailMcpTools:
    """MCP tool implementations that validate inputs and return stable JSON."""
    def gmail_search_messages(self, *, query: str, max_results: int = 10,
                             newer_than_days: Optional[int] = None,
                             label_ids: Optional[Sequence[str]] = None) -> list[SearchResultItem]:
        """
        Search Gmail messages with query syntax.
        Combines query with newer_than_days and label_ids filters.
        Handles pagination, deduplication, and metadata enrichment.
        """
        raise NotImplementedError

    def gmail_get_message(self, *, message_id: str, fmt: MessageFormat = "full") -> dict[str, Any]:
        """
        Get message details by ID.
        Returns structured headers and body content.
        """
        raise NotImplementedError
```

### 2. Data Models

```python
from pydantic import BaseModel, Field, PositiveInt, conint
from typing import Optional, Sequence

class SearchParams(BaseModel):
    query: str = Field(min_length=1, description="Gmail search query syntax (see https://support.google.com/mail/answer/7190)")
    max_results: conint(ge=1, le=50) = 10
    newer_than_days: Optional[PositiveInt] = None
    label_ids: Optional[Sequence[str]] = None

class GetMessageParams(BaseModel):
    message_id: str = Field(min_length=5)
    fmt: str = Field(default="full", pattern="^(full|metadata)$")
```

### 3. Integration Points

* How this interfaces with other systems

  * **MCP client → MCP server tools → GmailClient → Gmail REST API**（[https://developers.google.com/workspace/gmail/api/guides](https://developers.google.com/workspace/gmail/api/guides)）
    * MCP client 通过 STDIO 发送 JSON-RPC 请求（tool/call）
    * MCP server 解析请求，调用对应工具方法
    * 工具方法调用 GmailClient，GmailClient 使用 OAuth2 token 调用 Gmail REST API
    * 结果返回给 MCP client

* API contracts

  * **`gmail_search_messages`**：query（语法参考：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)）+ max_results + 可选过滤 → 返回稳定字段（id/thread_id/from_email/subject/date/snippet）
  * **`gmail_get_message`**：message_id → headers + body_text（必要）+ body_html（可选）

* Data flow diagrams if needed

  * **搜索流程**：
    1. MCP client 调用 `gmail_search_messages(query="from:example", max_results=20)`
    2. 工具层组合 query：`"from:example newer_than:7d label:INBOX"`（如果提供了 newer_than_days 和 label_ids）
    3. GmailClient.list_messages 调用 messages.list API（带 query、maxResults、pageToken）
    4. 如果返回 nextPageToken 且结果数 < max_results，继续调用直到达到上限或没有更多结果
    5. 对前 K 条（例如 10 条）调用 GmailClient.get_message(message_id, fmt="metadata") 补全 metadata
    6. 聚合结果，去重，返回结构化列表
  * **读取流程**：
    1. MCP client 调用 `gmail_get_message(message_id="...", fmt="full")`
    2. GmailClient.get_message 调用 messages.get API（带 messageId、format）
    3. 解析响应，提取 headers、body_text、body_html
    4. 返回结构化 JSON

### 4. Files Changes

* Explicitly mention which files will be impacted/created in this change.
* These should be the ONLY files impacted in the change.

  * `week3/server/__init__.py` - 包初始化
  * `week3/server/main.py` - MCP server 入口，工具注册，STDIO 传输处理
  * `week3/server/auth.py` - 运行时鉴权：从 `.token.json` 加载 refresh_token → `creds.refresh()`（**不发起浏览器授权**）
  * `week3/server/auth_cli.py` - **独立预授权 CLI 脚本**：在有浏览器的终端中手动运行一次，完成 OAuth2 `run_local_server()` 流程，产出 `.token.json`
  * `week3/server/gmail_client.py` - Gmail API 封装（list_messages, get_message），重试逻辑
  * `week3/server/models.py` - 数据模型（SearchResultItem, SearchParams, GetMessageParams）
  * `week3/server/tools.py` - MCP 工具实现（gmail_search_messages, gmail_get_message）
  * `week3/server/tests/__init__.py` - 测试包初始化
  * `week3/server/tests/conftest.py` - pytest 配置、fixtures（mock GmailClient + 真实凭证 fixture）
  * `week3/server/tests/test_search.py` - 搜索工具单元测试（query 组合、分页、去重、补全、错误处理）
  * `week3/server/tests/test_get_message.py` - 读取工具单元测试
  * `week3/server/tests/test_live_search.py` - **真实 Gmail API 搜索测试**（使用已有 credentials.json + .token.json）
  * `week3/server/tests/test_live_get_message.py` - **真实 Gmail API 读取测试**
  * `week3/server/tests/test_auth.py` - 鉴权模块测试（token 加载、刷新、失效检测）
  * `week3/requirements.txt` - 依赖清单（用于 `.venv` 安装，确保与 conda 环境一致）
  * `week3/.gitignore` - 忽略 `.token.json`、`credentials.json`、`.venv/`、`__pycache__/`
  * `week3/README.md` - 项目文档：环境搭建（conda/venv 双方案）、预授权步骤、Claude Desktop 配置、运行、示例、故障排查

## Implementation Plan

1. Phase 1: [Initial Implementation]

   * **Task 0**：搭建运行环境并解决 Anaconda/venv 兼容性
     * 在 `week3/` 下创建独立 `.venv`：`python -m venv .venv`（使用系统 Python 3.10+，或通过 conda 环境的 python 创建）
     * 编写 `requirements.txt`，包含 `mcp`、`google-api-python-client`、`google-auth`、`google-auth-oauthlib`、`pydantic`、`python-dotenv` 等
     * 安装依赖：`.venv/Scripts/pip install -r requirements.txt`
     * 验证 Claude Desktop 配置（`claude_desktop_config.json`）能正确使用 `.venv` 中的 Python 解释器启动 MCP server：
       ```json
       {
         "mcpServers": {
           "gmail": {
             "command": "E:/Users/Document/code/CS146S/CS146S/week3/.venv/Scripts/python.exe",
             "args": ["-m", "server.main"],
             "env": {"PYTHONPATH": "E:/Users/Document/code/CS146S/CS146S/week3"},
             "cwd": "E:/Users/Document/code/CS146S/CS146S/week3"
           }
         }
       }
       ```
     * **注意**：开发时可继续使用 Anaconda `cs146s` 环境（`conda activate cs146s`），但需确保 `.venv` 中也安装了相同依赖；README 中提供两种环境的安装说明
   * **Task 1**：搭建 MCP server 骨架（STDIO），注册 2 个工具（参考 MCP 规范：[https://modelcontextprotocol.io/specification/](https://modelcontextprotocol.io/specification/)）
     * 使用 MCP SDK（例如 `mcp` Python 包）创建 server 实例
     * 定义工具 schema（参数类型、描述）
     * 实现工具处理函数（暂时返回 mock 数据）
   * **Task 2**：实现 OAuth2 两阶段鉴权（参考：[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
     * 实现独立 CLI 脚本 `auth_cli.py`：在有浏览器的终端中运行一次，完成 `run_local_server()` 授权流程，将含 refresh_token 的凭证保存到 `.token.json`
     * 实现 `auth.py` 运行时鉴权：从 `.token.json` 加载凭证，调用 `creds.refresh(Request())` 刷新 access_token；**绝不在服务进程内发起浏览器授权**
     * 启动时检测：若 `.token.json` 不存在或 refresh_token 失效，输出明确 stderr 错误（指引运行 `python auth_cli.py`）并安全退出
     * Token 存储到本地文件（`.token.json`，加入 `.gitignore`）
   * **Task 3**：实现 `messages.list` 与 `messages.get` 基础封装
     * 使用 `google-api-python-client` 调用 Gmail API
     * list：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
     * get：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)
     * 基础错误处理（捕获 HTTPException）
   * **Expected timeline**：预计 2-3 天完成基础框架搭建和 API 封装，确保可以成功调用 Gmail API 并返回数据

2. Phase 2: [Enhancement Phase]

   * **Task 1**：搜索增强：分页循环（nextPageToken）、max_results 上限、去重
     * 实现分页循环逻辑：检测 nextPageToken，继续调用直到达到 max_results 或没有更多结果
     * 使用 set 去重 message id，保持顺序稳定
     * 添加分页次数限制（防止无限循环，例如最多 10 页）
   * **Task 2**：输出增强：对前 K 条补全 metadata（subject/from/date），保证输出有意义
     * 对前 K 条（例如 10 条）调用 get_message(metadata) 补全信息
     * 处理补全失败情况（降级：仅返回 id/threadId）
     * 并发控制：使用 asyncio 或线程池并发补全（可选，提高性能）
   * **Task 3**：错误处理：429/5xx 重试（指数退避），明确错误分类
     * 实现重试装饰器或工具函数
     * 429 错误：重试 3 次，退避 1s/2s/4s
     * 5xx 错误：重试 2 次，退避 1s/2s
     * 401 错误：直接返回，提示重新授权
     * 错误分类映射：auth_error / rate_limited / transient / invalid_input
   * **Expected timeline**：预计 2-3 天完成增强功能，重点测试搜索工具的分页、补全、错误处理逻辑

3. Phase 3: [Production Readiness]

   * **Task 1**：完善 README：配置、运行、示例、故障排查（附外部链接）
     * 详细说明 OAuth2 配置步骤（Google Cloud Console 设置、credentials.json 获取）
     * 运行命令示例（本地 STDIO 模式）
     * 工具调用示例（输入参数、预期输出）
     * 常见问题排查（授权失败、API 限流、网络错误）
   * **Task 2**：完善日志与脱敏策略；确保 STDIO 不污染 stdout
     * 实现结构化日志（JSON 格式，输出到 stderr）
     * 日志包含：request_id、tool_name、latency_ms、gmail_api_status
     * 脱敏：不打印 token、完整邮件正文（仅打印 snippet 前 50 字符）
   * **Task 3**：（可选加分）HTTP transport + 服务侧认证（授权参考：[https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)）
     * 实现 HTTP transport（使用 FastAPI 或类似框架）
     * 实现服务侧认证（API Key 或 Bearer token 验证）
     * 部署到云平台（Vercel/Cloudflare Workers，参考 assignment.md）
   * **Expected timeline**：预计 1-2 天完成文档和日志，HTTP transport 作为加分项可额外 1-2 天

## Testing Strategy

### Unit Tests

* Key test cases（**必须把"搜索"作为最高优先级覆盖**）

  1. **Query 组合正确性**：`newer_than_days`、label_ids 与原 query 拼接是否符合预期（参考 Gmail 搜索语法：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)）
     * 测试用例：`query="from:test"` + `newer_than_days=7` → 应生成 `"from:test newer_than:7d"`
     * 测试用例：`query="subject:meeting"` + `label_ids=["INBOX", "STARRED"]` → 应生成 `"subject:meeting label:INBOX label:STARRED"`
     * 测试用例：空 query + `newer_than_days=30` → 应生成 `"newer_than:30d"`

  2. **分页正确性**：模拟多页返回（nextPageToken；list 文档：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)），确保最多拉到 max_results，且不会死循环
     * 模拟场景：第 1 页返回 10 条 + nextPageToken，第 2 页返回 5 条（无 nextPageToken），max_results=15 → 应返回 15 条
     * 模拟场景：第 1 页返回 10 条 + nextPageToken，第 2 页返回 10 条 + nextPageToken，max_results=15 → 应返回 15 条（停止分页）
     * 模拟场景：分页次数限制（最多 10 页），防止无限循环

  3. **去重正确性**：跨页重复 id 时只保留一次，顺序稳定
     * 模拟场景：第 1 页返回 id=[1,2,3]，第 2 页返回 id=[2,3,4] → 应返回 [1,2,3,4]（去重且保持顺序）

  4. **空结果**：list 返回空 messages 字段时返回空数组，并给出可行动建议字段（例如 hint）
     * 模拟场景：messages.list 返回 `{"messages": []}` → 应返回 `[]` 并包含 hint 字段提示"尝试调整搜索条件"

  5. **补全策略**：只对前 K 条做 get(metadata)（get 文档：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)）；失败时降级（仍返回 id/threadId）
     * 模拟场景：搜索返回 20 条，K=10 → 应只对前 10 条调用 get_message
     * 模拟场景：前 3 条 get_message 失败 → 应返回 id/threadId，其余 7 条正常补全

  6. **限流/重试**：模拟 429/503，验证退避重试次数与最终错误信息
     * 模拟场景：第 1 次调用返回 429，第 2 次成功 → 应重试 1 次后成功
     * 模拟场景：连续 3 次返回 429 → 应重试 3 次后返回 rate_limited 错误
     * 模拟场景：返回 503 → 应重试 2 次后返回 transient 错误

  7. **输入校验**：query 为空、max_results 越界、message_id 非法等应在调用前失败
     * 测试用例：`query=""` → 应抛出 ValidationError
     * 测试用例：`max_results=100` → 应抛出 ValidationError（超过上限 50）
     * 测试用例：`message_id=""` → 应抛出 ValidationError

* Mock strategies

  * 使用假的 GmailClient（或 requests/httpx mock）返回固定 JSON
  * 用"录制样例响应 JSON"做快照测试（确保输出结构稳定）
  * 使用 `pytest-mock` 模拟 HTTP 请求

* Coverage expectations

  * `gmail_search_messages` 相关逻辑（组合 query + 分页 + 去重 + 补全 + 错误映射）覆盖率优先达到最高（例如 >90%）

### Live API Tests（真实 Gmail API 测试，基于已有 credentials.json）

> **前置条件**：项目中已存在 `credentials.json`（Google Cloud OAuth2 客户端凭证，已 gitignore），且通过 `auth_cli.py` 预授权产出了 `.token.json`。以下测试全部使用**真实 Gmail 账户**执行，不使用 mock。

* **测试标记与运行方式**

  * 使用 `@pytest.mark.live` 标记所有真实 API 测试，默认 `pytest` 跳过（避免 CI 中无凭证时失败）
  * 手动运行：`pytest -m live -v`（需要 `.token.json` 存在且有效）
  * conftest.py 中提供 `gmail_client` fixture：自动加载 `.token.json`，构建已鉴权的 GmailClient 实例

* **搜索工具真实 API 测试**（`test_live_search.py`，最高优先级）

  1. **基础搜索可达性**：`query="in:inbox"`, `max_results=5` → 断言返回 1-5 条结果，每条包含 id/thread_id/snippet；断言 from_email、subject、date 至少部分非空
  2. **`subject:` 精确搜索**：`query="subject:<已知存在的主题>"` → 断言返回非空，首条 subject 包含目标关键词
  3. **`from:` 发件人过滤**：`query="from:<已知发件人>"` → 断言所有结果的 from_email 包含目标地址
  4. **`newer_than_days` 时间过滤**：`query=""`, `newer_than_days=3` → 断言结果的 date 均在最近 3 天内；对比 `newer_than_days=9999` 应返回更多结果
  5. **`label_ids` 标签过滤**：`query=""`, `label_ids=["INBOX"]` → 断言返回非空；`label_ids=["STARRED"]` → 验证结果与 INBOX 不同（如果有加星邮件）
  6. **分页正确性（真实）**：`query="in:anywhere"`, `max_results=25` → 断言返回 ≤25 条；再用 `max_results=5` 查同一 query → 断言返回 ≤5 条且为前者子集
  7. **去重验证**：对上述分页结果检查 id 唯一性，`len(ids) == len(set(ids))`
  8. **空结果处理**：`query="from:nonexistent_z9x8y7@fakeemail.test"` → 断言返回空列表，无异常抛出
  9. **复合查询**：`query="from:<已知发件人> subject:<关键词> newer_than:30d"` → 断言结果同时满足发件人和主题条件
  10. **max_results 边界**：`max_results=1` → 断言恰好返回 1 条；`max_results=50` → 断言返回 ≤50 条

* **读取工具真实 API 测试**（`test_live_get_message.py`）

  1. **基础读取**：先搜索获取一个 message_id，再 `gmail_get_message(message_id=..., fmt="full")` → 断言返回包含 headers（from/to/subject/date）和 body_text
  2. **metadata 格式**：同一 message_id，`fmt="metadata"` → 断言包含 headers 和 snippet，但不包含完整 body
  3. **不存在的 message_id**：`message_id="nonexistent_12345"` → 断言返回 404 错误映射，包含可操作提示
  4. **headers 完整性**：验证返回的 headers 包含 `From`、`To`、`Subject`、`Date` 字段
  5. **body 解码**：读取一封已知含中文/HTML 的邮件 → 断言 body_text 非空且不含 base64 编码残留

* **鉴权模块真实测试**（`test_auth.py`）

  1. **正常加载**：存在有效 `.token.json` → `auth.get_credentials()` 成功返回，`creds.valid` 为 True 或刷新后为 True
  2. **token 刷新**：手动将 access_token 过期时间设为过去 → 调用 `creds.refresh(Request())` → 断言成功获取新 access_token
  3. **缺失 token 文件**：临时重命名 `.token.json` → 断言 `auth.get_credentials()` 抛出明确错误（包含"请运行 auth_cli.py"提示）
  4. **损坏的 token 文件**：写入无效 JSON → 断言 `auth.get_credentials()` 抛出明确错误，不崩溃

### Integration Tests（端到端集成）

* Test scenarios（**重点：搜索在真实 Gmail 账户下端到端跑通**）

  1. **MCP 工具层端到端**：直接调用 `GmailMcpTools.gmail_search_messages()`（已注入真实 GmailClient）→ 验证从参数校验 → query 组合 → API 调用 → 分页 → 补全 → 结构化输出的完整链路
  2. **大结果集分页**：`query="in:anywhere"`, `max_results=30` → 验证分页循环正确，结果数 ≤30，日志显示多次 API 调用
  3. **错误恢复**：使用无效 token → 验证返回 auth_error 而非未捕获异常
  4. **搜索 → 读取链路**：先搜索获取 id 列表 → 取首条 id 调用 get_message → 验证搜索结果的 subject 与详情中的 Subject header 一致

* Environment needs

  * **已有**：`credentials.json`（Google Cloud OAuth2 客户端凭证，已存在于 `week3/` 目录，已 gitignore）
  * **需预授权产出**：`.token.json`（通过运行 `python server/auth_cli.py` 一次性生成）
  * 已启用 Gmail API 的 Google Cloud 项目（指南：[https://developers.google.com/workspace/gmail/api/guides](https://developers.google.com/workspace/gmail/api/guides)）
  * 环境变量（可选）：`GMAIL_CREDENTIALS_PATH`（默认 `credentials.json`）、`GMAIL_TOKEN_PATH`（默认 `.token.json`）
  * 运行环境：`week3/.venv` 或 Anaconda `cs146s` 环境均可

* Data requirements

  * 测试 Gmail 账户中应有若干邮件（不同发件人/主题/标签/日期），便于断言搜索过滤有效
  * 建议至少包含：>30 封邮件（测试分页）、≥1 封加星邮件（测试 label 过滤）、≥1 封含中文的邮件（测试编码）

> **验证要求（必须写在本节末尾，作为"手动验证清单"，且必须以"搜索"为核心）**
>
> **前置**：确保已运行 `python server/auth_cli.py` 产出 `.token.json`，且 Claude Desktop 配置正确（指向 `.venv/Scripts/python.exe`）。
>
> * **自动化验证**：运行 `pytest -m live -v`，所有 `@pytest.mark.live` 标记的真实 API 测试应全部通过（搜索 10 项 + 读取 5 项 + 鉴权 4 项）
>
> * **手动验证**：启动 Claude Desktop → 确认 gmail MCP server 连接成功 → 在对话中触发工具调用
> * 至少验证 5 条搜索用例（每条都记录"输入参数/返回条数/首条 subject-from-date"）：
>
>   * **`subject:` 精确匹配**（语法：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)）
>     * 输入：`query="subject:test meeting"`，`max_results=10`
>     * 预期：返回包含 "test meeting" 主题的邮件列表
>   * **`from:` 过滤**（语法：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)）
>     * 输入：`query="from:example@gmail.com"`，`max_results=10`
>     * 预期：返回来自该邮箱的邮件列表
>   * **`newer_than_days` 生效**（用不同日期邮件对照）
>     * 输入：`query=""`，`newer_than_days=7`，`max_results=10`
>     * 预期：仅返回最近 7 天的邮件
>   * **label_ids 生效**（INBOX/STARRED/自定义 label；结合 list 行为验证）
>     * 输入：`query=""`，`label_ids=["INBOX", "STARRED"]`，`max_results=10`
>     * 预期：返回同时属于 INBOX 和 STARRED 的邮件
>   * **大结果触发分页仍遵守 max_results**（nextPageToken）
>     * 输入：`query=""`，`max_results=30`（确保账户中有 >30 封邮件）
>     * 预期：返回 30 条结果，且分页逻辑正确（日志显示多次调用 messages.list）
>
> * **鉴权验证**：
>   * 删除 `.token.json` → 启动 server → 应在 stderr 输出明确错误（提示运行 auth_cli.py），而非弹出浏览器或崩溃
>   * 重新运行 `python server/auth_cli.py` → 浏览器授权 → `.token.json` 重新生成 → server 恢复正常

## Observability

### Logging

* Key logging points

  * **tool 调用开始/结束**（tool_name、request_id、latency_ms、result_count）
    * 示例：`{"level": "INFO", "tool": "gmail_search_messages", "request_id": "req-123", "latency_ms": 1500, "result_count": 10}`
  * **Gmail API 请求**（endpoint、status_code、retry_count）
    * 示例：`{"level": "INFO", "endpoint": "messages.list", "status_code": 200, "retry_count": 0}`
  * **错误路径**（分类：auth_error / rate_limited / transient / invalid_input）
    * 示例：`{"level": "ERROR", "error_type": "rate_limited", "message": "Gmail API rate limit exceeded", "retry_count": 3}`

* Log levels

  * **INFO**：正常调用摘要（工具调用、API 请求成功）
  * **WARNING**：重试、降级、空结果提示
  * **ERROR**：最终失败（但不输出敏感信息）

* Structured logging format

  * JSON 行日志（输出到 stderr 或文件）
  * 使用 `structlog` 或 `logging` + JSON formatter
  * 示例格式：
    ```json
    {"timestamp": "2025-01-20T10:30:00Z", "level": "INFO", "tool": "gmail_search_messages", "request_id": "req-123", "latency_ms": 1500, "result_count": 10}
    ```

### Metrics

* Key metrics to track

  * 搜索成功率（成功调用数 / 总调用数）
  * 平均延迟（p50/p95/p99）
  * 分页次数分布（1 页/2-3 页/4+ 页）
  * 429 频率（每小时 429 错误数）
  * 补全失败率（补全失败的条数 / 总补全条数）

* Collection method

  * 简化版：日志聚合统计；或本地计数器（使用 `prometheus-client` 或自定义计数器）

* Alert thresholds

  * 429 连续出现（例如 5 分钟内 >3 次）→ 警告：可能需要降低请求频率
  * 搜索延迟显著上升（p95 > 5s）→ 警告：可能存在性能问题

## Future Considerations

### Potential Enhancements

* **线程聚合**（thread view）：将同一 thread 的邮件聚合展示，提供更完整的对话上下文
* **草稿创建与发送**（双确认流程）：支持创建草稿、发送邮件，需要用户确认机制
* **缓存最近搜索结果**（降低 API 压力）：使用 LRU 缓存最近 10 次搜索结果，TTL 5 分钟
* **多用户/多租户 token 存储**（加密、隔离）：支持多个 Gmail 账户，token 加密存储，用户隔离

### Known Limitations

* **list+补全在大结果集下仍可能慢**：需严格 max_results 与 K（补全数量），建议 max_results <= 50，K <= 10
* **Gmail query 语法复杂**：只做透传与有限组合，不做完整解析器（语法参考：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)）
* **集成测试依赖真实账户与邮件数据**：需要维护测试 Gmail 账户和测试邮件，可能影响测试稳定性

## Dependencies

### Development Dependencies

* **Build tools**：Python 3.10+；开发使用 Anaconda `cs146s` 环境，部署使用 `week3/.venv` 独立虚拟环境 + `requirements.txt`（不依赖项目根目录的 Poetry/pyproject.toml，因为 week3 是独立可运行模块）
* **Test frameworks**：pytest + pytest-mock（mock 工具）+ pytest 标记系统（`@pytest.mark.live` 区分 mock 测试与真实 API 测试）
* **Development utilities**：ruff/black/mypy（项目已配置，可选但推荐）

### Runtime Dependencies

* **MCP SDK**：`mcp` Python 包（MCP server 实现）
* **Google API Client**：`google-api-python-client`、`google-auth`、`google-auth-oauthlib`（Gmail API 调用和 OAuth2）
* **HTTP Client**：`httpx` 或 `requests`（可选，用于自定义 HTTP 请求）
* **数据验证**：`pydantic`（项目已配置，用于参数校验和数据模型）
* **日志**：`structlog` 或标准 `logging`（结构化日志）

## Security Considerations

* Authentication/Authorization

  * **Gmail OAuth2**：最小 scope（`https://www.googleapis.com/auth/gmail.readonly`）；token 刷新与存储策略（[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
    * `credentials.json`（OAuth2 客户端凭证）和 `.token.json`（含 refresh_token）均添加到 `.gitignore`，不得提交到版本控制
    * 运行时仅通过 `creds.refresh(Request())` 刷新 access_token，**不在 MCP Server 进程内发起浏览器授权流程**（避免 STDIO 模式下的阻塞/安全风险）
    * 预授权通过独立 `auth_cli.py` 脚本完成，确保授权流程在用户可控的终端环境中执行
  * **服务侧可选**：API Key / Bearer token（加分项），MCP 授权参考（[https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)）
    * HTTP transport 模式下，验证请求头中的 `Authorization: Bearer <token>` 或 `X-API-Key: <key>`
    * Token 验证失败返回 401，不传递给上游 Gmail API

* Data protection

  * **日志脱敏**：不打印 token/完整正文；对 email 地址可部分遮蔽（例如 `ex***@gmail.com`）
  * **敏感信息处理**：邮件正文仅记录 snippet 前 50 字符，完整内容不记录日志

* Compliance requirements

  * 说明仅用于作业/个人测试；不做广泛分发
  * 遵循 Gmail API 使用条款和配额限制

## Rollout Strategy

1. **Development phase**
   * 本地开发环境搭建：在 `week3/` 下创建 `.venv`，安装 `requirements.txt` 依赖（开发时也可使用 Anaconda `cs146s` 环境）
   * **预授权**：运行 `python server/auth_cli.py`，在浏览器中完成一次 OAuth2 授权，产出 `.token.json`（此步骤只需执行一次）
   * 验证 Claude Desktop 配置能正确启动 MCP server（指向 `.venv/Scripts/python.exe` 绝对路径）
   * 实现 Phase 1 基础功能，确保可以成功调用 Gmail API
   * 编写单元测试 + 真实 API 测试，确保核心逻辑正确

2. **Testing phase**
   * 运行单元测试，确保覆盖率 >90%（重点搜索功能）
   * 运行集成测试，使用真实 Gmail 账户验证功能
   * 手动验证清单：执行 5+ 搜索用例，记录结果

3. **Staging deployment**
   * （可选）部署到测试环境（HTTP transport 模式）
   * 使用测试 Gmail 账户进行端到端测试
   * 验证日志、错误处理、性能指标

4. **Production deployment**
   * 本地 STDIO 模式：配置 Claude Desktop 或 Cursor，连接 MCP server
   * （可选）HTTP transport 模式：部署到云平台（Vercel/Cloudflare Workers）

5. **Monitoring period**
   * 监控日志中的错误率、延迟、429 频率
   * 收集用户反馈（如有），优化搜索性能和错误提示

## References

* Related design documents：无（或列内部 README）

* External documentation

  * **Gmail API Guides**：[https://developers.google.com/workspace/gmail/api/guides](https://developers.google.com/workspace/gmail/api/guides)
  * **Messages.list**：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
  * **Messages.get**：[https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)
  * **Gmail 搜索运算符/语法**：[https://support.google.com/mail/answer/7190](https://support.google.com/mail/answer/7190)
  * **OAuth2 协议与流程**：[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)
  * **MCP 规范**：[https://modelcontextprotocol.io/specification/](https://modelcontextprotocol.io/specification/)
  * **MCP 授权规范（服务侧认证）**：[https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

* Relevant standards

  * **OAuth 2.0**（概览在 Google OAuth2 文档中已说明：[https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)）
