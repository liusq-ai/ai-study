# Customer Domain

## 职责

负责领域能力层，维护客服业务语义和知识库质量。

## 关注点

- 客服意图分类。
- 退款、物流、商品咨询、故障排查、投诉和问候等 Chroma RAG 知识片段。
- 转人工规则和客服语气边界。
- Prompt 的业务含义。

## 资产责任

- 主责：`docs/context/prompt-assets.md`
- 协作：`docs/context/architecture-map.md`

## 协作规则

- 改意图或 RAG 数据时，同步检查 `prompts/customer-intent.md`、`data/knowledge.json` 和相关 Prompt 文件。
- 不修改 SDK 接入细节。
- 不在代码中写死最终客服回复。
