# Architecture Map

## 核心调用链

```text
main.py
  -> CustomerService.answer_message
  -> IntentService.classify_intent
  -> KnowledgeService.load_knowledge
     -> knowledge_chunks RAG 检索
     -> orders/order_items 订单模拟数据
  -> ReplyService.generate_reply
  -> LLMService.generate_reply
```

```text
web_app.py
  -> GET /
  -> POST /api/chat
  -> CustomerService.answer_message
```

## 目录职责

- `main.py`：CLI 入口，支持连续交互和单次传参。
- `web_app.py`：Web 服务入口，提供静态页面和 Chat API。
- `web/`：前端客服工作台页面、样式和交互脚本。
- `services/`：业务编排、意图识别、知识库读取、模型调用。
- `prompts/`：意图识别和客服回复 Prompt。
- `data/`：SQLite 表结构和种子数据。
- `render.yaml`：Render 原生 Python Web Service 部署配置。
- `runtime.txt`：Render Python 运行版本。
- `tests/`：本地测试。
- `.agents/`：四层分级 agent 协作说明。
- `docs/`：可迁移上下文资产。

## 模块边界

- `CustomerService` 只做编排。
- `IntentService` 只负责加载意图 Prompt 并调用 LLM。
- `KnowledgeService` 只负责初始化 SQLite、检索 RAG 知识片段、查询订单模拟数据。
- `ReplyService` 只负责加载回复 Prompt 并调用 LLM。
- `LLMService` 只负责环境配置、智谱 SDK、限流重试和模型调用，不保留本地模拟意图或写死回复。

## 数据表

- `knowledge_chunks`：RAG 知识片段，包含意图类型、标题、内容和关键词。
- `orders`：模拟订单主表，包含订单状态、物流、退款和发票状态。
- `order_items`：模拟订单明细表，包含商品、SKU、数量和保修状态。
