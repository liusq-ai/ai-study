# AI Customer Service Engineering Guide

本工程是一个 AI 客服学习项目，目标是用简洁、易懂、好维护的方式实践 Prompt Engineering、知识库检索、智谱 GLM 接入、Web 界面和工程化协作。

## 四层分级

1. 项目目标层：定义目标、边界、成功标准和关键决策。
2. 领域能力层：定义客服意图、知识库、回复策略和转人工规则。
3. 工程实现层：定义代码结构、命名、配置读取、模型接入和异常处理。
4. 运行验证层：定义测试、验收、安全检查、依赖安装和迁移验证。

## Agent 协作

本工程使用 4 个见名知意的 agent，配置在 `.agents/`：

- `project-owner.md`：项目目标层，负责目标、边界、成功标准和关键决策。
- `customer-domain.md`：领域能力层，负责意图分类、知识库、转人工规则和客服语气。
- `system-engineer.md`：工程实现层，负责 Python 代码、智谱 SDK、配置读取、限流重试和目录结构。
- `quality-operator.md`：运行验证层，负责测试、验收、安全检查、依赖说明和迁移检查。

协作顺序：

```text
project-owner -> customer-domain -> system-engineer -> quality-operator
```

## 代码规范

- 实现必须简洁、易懂、好维护。
- 函数和方法名使用两段式 `动词_名词`。
- 私有方法允许 `_` 前缀，但语义仍必须是两段式，例如 `_create_client`。
- 推荐命名：`load_prompt`、`create_client`、`classify_intent`、`generate_reply`。
- 避免命名：`load_env_file`、`_create_zhipu_client`、`process_data`。
- Python 魔术方法如 `__init__` 不受两段式约束。
- 注释使用中文，只解释业务意图或复杂逻辑。
- 意图识别和客服回复必须由模型生成，不允许在代码中保留本地模拟或写死最终客服话术。

## Markdown 命名

- Markdown 文件使用小写 kebab-case，例如 `project-brief.md`。
- `README.md` 和 `AGENTS.md` 作为社区约定保留大写。
- Agent 文件名必须见名知意，不使用过短缩写，不使用 `*-agent.md` 重复后缀。
- RAG 数据文件使用小写 kebab-case，Chroma 和 SQLite 运行库文件不得提交。

## 资产沉淀

工程上下文资产放在 `docs/`：

- `docs/context/project-brief.md`：项目目标、当前能力、非目标、成功标准。
- `docs/context/architecture-map.md`：目录结构、核心调用链、模块职责。
- `docs/context/decision-log.md`：关键决策和原因。
- `docs/context/migration-guide.md`：工程迁移检查清单。
- `docs/context/prompt-assets.md`：Prompt 用途、变量、输出约束和修改原则。
- `docs/runbooks/local-runbook.md`：本地运行、常见错误、限流处理和验收场景。

资产更新规则：

- 改目标或边界：更新 `project-brief.md` 和 `decision-log.md`。
- 改意图、Chroma 知识资产、订单种子数据、Prompt：更新 `prompt-assets.md`。
- 改代码结构、SDK、环境变量、数据库初始化：更新 `architecture-map.md` 和 `migration-guide.md`。
- 改依赖、运行方式、测试方式：更新 `local-runbook.md` 和 `migration-guide.md`。

## 安全约束

- API Key 只允许放在 `.env` 或系统环境变量中。
- `.env.example`、README、AGENTS、docs 和源码中不得出现真实密钥。
- `.env` 必须保持在 `.gitignore` 中。

## 验证命令

修改后至少运行：

```bash
python3 -m compileall main.py services tests
```

涉及真实模型调用时再运行：

```bash
python3 main.py "我的耳机有问题"
```

涉及 Web 服务时运行：

```bash
python3 web_app.py
```
