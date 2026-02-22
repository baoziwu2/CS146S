# Action Item Extractor

一个基于 FastAPI 和 SQLite 的 Web 应用程序，用于从自由格式的笔记中提取和管理行动项（action items）。该应用支持两种提取方式：基于启发式规则的提取和基于大语言模型（LLM）的智能提取。

## 项目概述

Action Item Extractor 是一个轻量级的任务管理工具，能够：

- **提取行动项**：从会议记录、笔记或任何文本中自动识别和提取可执行的任务
- **智能提取**：使用 Ollama LLM 进行更准确和上下文感知的提取
- **笔记管理**：保存和管理原始笔记内容
- **任务跟踪**：标记已完成的任务，跟踪待办事项

### 主要特性

- 🎯 **双重提取模式**：启发式规则提取和 LLM 驱动的智能提取
- 📝 **笔记管理**：创建、查看和列出所有保存的笔记
- ✅ **任务状态跟踪**：标记任务为已完成或待完成
- 🗄️ **SQLite 数据库**：轻量级本地数据存储
- 🌐 **Web 界面**：简洁的 HTML 前端界面
- 🧪 **单元测试**：完整的测试套件确保代码质量

## 技术栈

- **后端框架**：FastAPI
- **数据库**：SQLite
- **LLM 集成**：Ollama
- **前端**：原生 HTML/CSS/JavaScript
- **测试框架**：pytest
- **依赖管理**：Poetry

## 项目结构

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── db.py                # 数据库操作
│   ├── routers/
│   │   ├── action_items.py  # 行动项相关 API 端点
│   │   └── notes.py         # 笔记相关 API 端点
│   └── services/
│       └── extract.py       # 提取逻辑（启发式和 LLM）
├── frontend/
│   └── index.html           # Web 前端界面
├── tests/
│   └── test_extract.py      # 单元测试
├── data/
│   └── app.db               # SQLite 数据库文件（自动创建）
└── README.md
```

## 环境要求

- Python 3.8+
- Conda（用于环境管理）
- Poetry（用于依赖管理）
- Ollama（用于 LLM 功能，可选）

## 安装和设置

### 1. 激活 Conda 环境

```bash
conda activate cs146s
```

### 2. 安装依赖

确保已安装 Poetry，然后安装项目依赖：

```bash
poetry install
```

### 3. 配置 Ollama（可选，仅 LLM 提取需要）

如果使用 LLM 提取功能，需要：

1. **安装 Ollama**：
   - 访问 [Ollama 官网](https://ollama.com) 下载并安装
   - 或使用包管理器安装

2. **下载模型**：
   ```bash
   ollama pull llama3.1  # 或其他可用模型
   ```

3. **设置环境变量**：
   创建 `.env` 文件或设置环境变量：
   ```bash
   export OLLAMA_MODEL=llama3.1  # Linux/Mac
   # 或
   $env:OLLAMA_MODEL="llama3.1"  # Windows PowerShell
   ```

   或在项目根目录创建 `.env` 文件：
   ```
   OLLAMA_MODEL=llama3.1
   ```

## 运行项目

### 启动开发服务器

从项目根目录运行：

```bash
poetry run uvicorn week2.app.main:app --reload
```

服务器将在 `http://127.0.0.1:8000` 启动。

### 访问应用

在浏览器中打开：
```
http://127.0.0.1:8000
```

### API 文档

FastAPI 自动生成的交互式 API 文档：
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API 端点

### 行动项（Action Items）

#### `POST /action-items/extract`
使用启发式规则从文本中提取行动项。

**请求体**：
```json
{
  "text": "会议笔记内容...",
  "save_note": false
}
```

**响应**：
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "设置数据库"},
    {"id": 2, "text": "实现 API 端点"}
  ]
}
```

#### `POST /action-items/extract-llm`
使用 LLM 从文本中提取行动项（需要配置 Ollama）。

**请求体**：同 `/extract`

**响应**：同 `/extract`

#### `GET /action-items`
获取所有行动项，或按笔记 ID 筛选。

**查询参数**：
- `note_id` (可选): 筛选特定笔记的行动项

**响应**：
```json
[
  {"id": 1, "text": "设置数据库"},
  {"id": 2, "text": "实现 API 端点"}
]
```

#### `POST /action-items/{action_item_id}/done`
标记行动项为已完成或未完成。

**请求体**：
```json
{
  "done": true
}
```

**响应**：
```json
{
  "id": 1,
  "done": true
}
```

### 笔记（Notes）

#### `POST /notes`
创建新笔记。

**请求体**：
```json
{
  "content": "笔记内容..."
}
```

**响应**：
```json
{
  "id": 1,
  "content": "笔记内容...",
  "created_at": "2024-01-01 12:00:00"
}
```

#### `GET /notes`
获取所有笔记（按创建时间倒序）。

**响应**：
```json
[
  {
    "id": 1,
    "content": "笔记内容...",
    "created_at": "2024-01-01 12:00:00"
  }
]
```

#### `GET /notes/{note_id}`
根据 ID 获取单个笔记。

**响应**：
```json
{
  "id": 1,
  "content": "笔记内容...",
  "created_at": "2024-01-01 12:00:00"
}
```

## 前端功能

Web 界面提供以下功能：

1. **文本输入**：在文本框中粘贴或输入笔记内容
2. **保存选项**：可选择是否将输入保存为笔记
3. **提取按钮**：
   - **Extract**：使用启发式规则提取
   - **Extract LLM**：使用 LLM 智能提取
4. **任务管理**：勾选复选框标记任务完成状态
5. **笔记列表**：点击 "List Notes" 查看所有保存的笔记

## 运行测试

项目使用 `pytest` 作为测试框架。

### 运行所有测试

```bash
poetry run pytest
```

### 运行特定测试文件

```bash
poetry run pytest tests/test_extract.py
```

### 运行测试并显示详细输出

```bash
poetry run pytest -v
```

### 测试覆盖

当前测试套件包括：

- `test_extract_action_items_llm_basic`：测试 LLM 提取基本功能
- `test_extract_bullets_and_checkboxes`：测试启发式提取器识别项目符号和复选框
- `test_extract_action_items_llm_empty_input`：测试空输入处理
- `test_extract_action_items_llm_with_bullets`：测试 LLM 提取包含项目符号的文本

## 提取算法

### 启发式提取（`extract_action_items`）

基于规则的提取器识别以下模式：

- **项目符号**：`-`, `*`, `•`, 或数字列表（如 `1.`）
- **关键词前缀**：`todo:`, `action:`, `next:`
- **复选框标记**：`[ ]`, `[todo]`
- **命令式语句**：以特定动词开头的句子（如 "add", "create", "implement" 等）

### LLM 提取（`extract_action_items_llm`）

使用 Ollama LLM 进行上下文感知的智能提取：

- 利用大语言模型理解文本语义
- 返回结构化的 JSON 数组
- 能够识别更复杂和隐含的行动项

## 数据库架构

### Notes 表
- `id` (INTEGER PRIMARY KEY)
- `content` (TEXT NOT NULL)
- `created_at` (TEXT DEFAULT datetime('now'))

### Action Items 表
- `id` (INTEGER PRIMARY KEY)
- `note_id` (INTEGER, FOREIGN KEY)
- `text` (TEXT NOT NULL)
- `done` (INTEGER DEFAULT 0)
- `created_at` (TEXT DEFAULT datetime('now'))

## 开发说明

### 代码组织

- **路由层** (`app/routers/`)：处理 HTTP 请求和响应
- **服务层** (`app/services/`)：业务逻辑和提取算法
- **数据层** (`app/db.py`)：数据库操作和连接管理
- **前端** (`frontend/`)：静态 HTML 界面

### 添加新功能

1. 在相应的路由文件中添加新的端点
2. 在服务层实现业务逻辑
3. 更新数据库模式（如需要）
4. 添加单元测试
5. 更新前端界面（如需要）

## 故障排除

### LLM 提取失败

- 确保 Ollama 服务正在运行：`ollama serve`
- 检查 `OLLAMA_MODEL` 环境变量是否正确设置
- 验证模型是否已下载：`ollama list`

### 数据库错误

- 确保 `data/` 目录存在且可写
- 检查 SQLite 数据库文件权限
- 删除 `data/app.db` 以重新初始化数据库（会丢失所有数据）

### 端口冲突

如果 8000 端口被占用，可以指定其他端口：

```bash
poetry run uvicorn week2.app.main:app --reload --port 8001
```

## 许可证

本项目为课程作业项目。

## 贡献

本项目为 CS146S 课程作业，不对外接受贡献。

---

**注意**：使用 LLM 提取功能需要本地运行 Ollama 服务。确保在运行应用前已正确配置 Ollama 环境。
