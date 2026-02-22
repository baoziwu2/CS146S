**Model Context Protocol (MCP)** 是一个用于标准化大型语言模型（LLMs）与外部系统/数据源/工具之间交互的开放协议，使得 LLM 在不同模型或平台之间保持一致的集成方式下访问实时数据和服务
和调用外部函数或接口。

### 结构
MCP 是一个 Client-Server 架构，存在三个主要角色：
- MCP host: 与用户直接交互的 ai 应用（e.g. Cursor, Claude Desktop, Windsurf）
- MCP client: 嵌入在 host 内部的组件，与具体的 MCP Server 握手、维护连接并处理协议层的数据转换
- MCP server: 运行在外部（本地或云端），暴露 Tools / Resources / Prompts
	Tools 就是可以使用的工具，如一些函数这样。有输入参数 schema （通常 JSON schema），返回结构化的结果
	Resources 提供上下文信息，如本地文件，日志信息，当 LLM 需要时通过 client 塞入上下文中
	Prompt 是 server 提供的预定义 prompt 模板
由于 MCP 具有统一性，集成复杂度从 $O(n \times m)$ 下降到 $O(n + m)$

### 流程
MCP 流程的伪代码如下:
```javascript
// 1. Send user prompt to LLM with available tools context
const response = await anthropicClient.complete({
  prompt: "User: Can you list my projects?\nAssistant: ",
  model: "claude-3.5",
  tools: tools // list of tools from MCP server
});
for (const msg of response.messages) {
  if (msg.type === 'tool_use') {
    // 2. LLM decided to use a tool
    const { name, args } = msg;
    // 3. Call the tool via MCP
    const toolRes = await mcpClient.request({ method: 'tools/call', params: { name, arguments: args } });
    // 4. Inject tool result and resume LLM
    await anthropicClient.send({ role: 'system', content: `Tool result: ${toolRes.result}` });
  } else {
    // 5. Handle normal LLM reply (tool result likely integrated)
    console.log("Assistant:", msg.content);
  }
}
```

传输层还有 stdio 和 http 的区别：stdio 是 Host 应用直接启动 Server 的可执行程序，并将其作为一个子进程；http 则是 Server 作为一个独立的 Web 服务运 Client 通过 `POST` 请求发送消息。 Server 通过一个持久的 `GET` 连接将响应推送回 Client

### 局限
MCP 目前还不是万能的，现在 ai 还不能使用太多工具（窗口有限），而且这样做 token 消耗很快
目前有两种解决方案
### 动态工具搜索
将工具的 `Description`（描述）视为“文档”，通过 RAG 的方式按需注入。
1. **索引期**：将所有 MCP Server 提供的工具名称和描述存入向量数据库（如 Chroma, Pinecone）。
2. **检索期**：当用户输入请求时，先由一个轻量级模型（或 Embedding 模型）计算用户意图与工具描述的余弦相似度。
3. **注入期**：只挑选评分最高的 **Top-K** 个工具说明放入当前的上下文窗口。
可以发现这种方案很有效，但是语义描述一定要足够精确
### 分级智能体架构
利用层级结构分摊上下文压力。
Superior Agent：不直接连接任何 MCP 工具，只负责理解任务并“派发”给下级
Specialist Agents：每个专家只挂载特定领域的 MCP Server
实现流程：
1. 上级 Agent 收到任务：“分析数据并写一份报告”。
2. 上级判断需要“数据专家”。
3. 下级拿到请求，因为工具较少上下文干净，决策更准。
4. 下级返回结果，上级总结。
除了决策更准还可以并行

### 认证，权限和安全
MCP 有 http 传输方式，这意味着是有必要做认证和安全性的，同时我们也要控制 LLM 的权限

MCP 的认证机制通常采用 OAuth 2.1 或 JWT，即在MCP Client 在请求 MCP Server 之前，需要先通过 OAuth 授权流程获得访问令牌（access token），该令牌代表客户端身份和授权范围
**基本认证流程**
1. MCP Client 发起请求 → 若无令牌或令牌不合法，MCP Server 返回 `401 Unauthorized`。
2. Client 启动 OAuth 授权流程（通常包括授权码流程 + PKCE）。
3. 授权服务器颁发访问令牌。
4. Client 使用该令牌调用 MCP Server。
5. Server 验证令牌合法性后才执行业务逻辑

**通过 scope 控制权限**
 授权服务器在颁发访问令牌时，会嵌入客户端请求的 scopes（例如 `read:files`, `write:files`） MCP Server 根据 scopes 判断客户端是否被授权执行特定操作。如 Server 可以返回 `403 Forbidden` + `insufficient_scope` 来提示需要更高权限。

**安全原则**
最小权限原则（Least Privilege）：客户端在获取 token 时应只请求完成当前任务所需的最小 scopes，避免不必要权限扩散。
零信任设计：不轻信任何未经验证的输入或 session 状态，每次请求都应重新验证身份与权限

### MCP Registry
MCP registry 是一个列出了所有 公开可用的 MCP 服务器 的中心目录，且每个服务器都有对应的元数据，并提供 REST API。
MCP registry 不托管服务器代码或二进制，只储存向实际服务器发布位置的元数据
