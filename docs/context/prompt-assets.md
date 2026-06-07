# Prompt Assets

## customer-intent.md

用途：识别用户问题所属客服类型。

输入变量：

- `{{user_message}}`

输出约束：

- 只输出 JSON。
- 必须包含 `type`、`need_order_info`、`reason`。

维护原则：

- 新增意图时，同步补充 `data/knowledge.json` 中的 Chroma RAG 知识片段。
- 模糊表达要补充示例，例如“耳机有问题”归入 `troubleshooting`。
- 产品参数、型号区别、兼容性、续航、降噪、保修和推荐类问题归入 `product_info`。
- “你是谁”“你的主人是谁”“谁创建你”等身份问题归入 `identity`。

## customer-reply.md

用途：根据用户问题、意图、RAG 检索内容和订单模拟数据生成客服回复。

输入变量：

- `{{user_message}}`
- `{{intent_type}}`
- `{{need_order_info}}`
- `{{knowledge}}`：包含 RAG 检索内容和订单模拟数据。

输出约束：

- 只输出给用户看的客服话术。
- 不输出 JSON。
- 不编造 RAG 检索内容和订单模拟数据没有的信息。

维护原则：

- 回复语气保持专业、耐心、简洁。
- 需要订单信息时要明确提醒用户提供订单号。
- 知识库无法解决时引导转人工。

## RAG 数据资产

位置：

- `data/knowledge.json`
- `data/chroma/`

维护原则：

- `data/knowledge.json` 记录客服知识片段，是 Chroma 初始化的数据来源。
- `data/chroma/` 是运行时向量库目录，不提交仓库。
- 新增产品知识或身份知识时，优先补充标题、内容和关键词，让 Hash Embedding 更容易命中。
- 新增业务能力时，不恢复 Markdown 知识库。

## 订单数据资产

位置：

- `data/schema.sql`
- `data/seed.sql`

维护原则：

- `orders` 和 `order_items` 只记录模拟订单数据。
- 订单数据用于模拟业务系统，不承担主要知识检索职责。
