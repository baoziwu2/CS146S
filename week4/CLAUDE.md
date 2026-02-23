# 现代软件开发 - 起步应用指南 (Week 4)

## 架构说明
- 这是一个全栈应用，后端使用 FastAPI + SQLite (SQLAlchemy)。
- 前端为静态文件，不需要 Node 工具链，通过 FastAPI 提供服务。
- API 路由逻辑位于 `backend/app/routers/` 目录下。
- 使用环境 `conda activate cs146s`
- 数据库模型和 Schema 位于 `backend/app/models.py` 和 `backend/app/schemas.py`。

## 开发工作流与工具链
1. **测试驱动**: 当被要求添加新功能或端点时，请先在 `backend/tests/` 中编写失败的测试用例，然后再去实现具体代码。
2. **代码检查**: 在提交代码前，必须确保代码符合格式规范。你可以使用安全的命令：
   - 运行代码格式化: `make format` (底层使用 black 和 ruff)。
   - 运行代码测试: `make test` (底层使用 pytest)。
