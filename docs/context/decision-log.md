# Decision Log

## 2026-06-06

- 采用智谱官方 Python SDK `zai-sdk`，不再使用 OpenAI 兼容 SDK。
- 意图识别和客服最终回复都必须由模型生成，不在代码中保留本地模拟或写死话术。
- 工程采用四层分级：项目目标层、领域能力层、工程实现层、运行验证层。
- Agent 精简为 4 个：`project-owner`、`customer-domain`、`system-engineer`、`quality-operator`。
- 函数和方法名采用两段式 `动词_名词`。
- Markdown 文件命名采用小写 kebab-case，保留 `README.md` 和 `AGENTS.md` 约定。
- 上下文资产采用轻量 Markdown 资产包，放在 `docs/`。
- 知识库从 Markdown 文件迁移到 SQLite RAG；订单能力使用 SQLite 表和模拟数据，不接生产订单系统。
- Web 界面采用 Python 标准库 `http.server`，避免为学习项目引入额外 Web 框架依赖。
- 服务器发布优先使用 Render 原生 Python Web Service；Dockerfile 暂时保留，但不作为默认部署入口。
