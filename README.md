# AI 客服学习案例

这是一个最小可运行的 AI 客服案例，用来学习 Prompt Engineering 在真实应用里的落地方式。

核心流程：

```text
用户问题 / Web 页面请求
  -> 意图识别 Prompt
  -> Chroma RAG 检索客服知识
  -> SQLite 查询订单模拟数据
  -> 客服回复 Prompt
  -> 返回客服话术
```

## 目录结构

```text
.
├── main.py
├── web_app.py
├── web/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/
│   ├── schema.sql
│   ├── seed.sql
│   └── knowledge.json
├── prompts/
│   ├── customer-intent.md
│   └── customer-reply.md
├── services/
│   ├── customer_service.py
│   ├── intent_service.py
│   ├── knowledge_service.py
│   ├── llm_service.py
│   └── reply_service.py
├── docs/
│   ├── context/
│   └── runbooks/
└── tests/
    └── test_customer_service.py
```

## 运行

Web 界面：

```bash
python3 web_app.py
```

打开：

```text
http://127.0.0.1:8000
```

连续交互：

```bash
python3 main.py
```

启动后可以反复输入用户问题，输入 `exit` / `quit` / `q` / `退出` 结束。

或者直接传入用户问题：

```bash
python3 main.py "我已经申请退款两天了，钱还没到账，怎么回事？"
```

## 接入智谱 GLM

本项目默认支持两种模式：

1. 未配置 `ZHIPU_API_KEY`：无法调用模型能力，程序会提示补充配置。
2. 已配置 `ZHIPU_API_KEY`：调用智谱官方 Python SDK，由模型识别意图并生成客服回复。

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

配置 API Key：

```bash
export ZHIPU_API_KEY="你的智谱 API Key"
```

如果你在 PyCharm / IDEA 里运行，推荐在项目根目录新建 `.env`：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash-250414
```

项目会自动读取 `.env`。`.env` 已加入 `.gitignore`，不要提交到代码仓库。

智谱官方文档推荐的环境变量名是 `ZAI_API_KEY`，本项目也兼容：

```text
ZAI_API_KEY=你的智谱 API Key
```

可选：指定模型，默认使用免费版 `glm-4-flash-250414`：

```bash
export ZHIPU_MODEL="glm-4-flash-250414"
```

如果遇到速率限制，可以调大请求间隔：

```bash
export ZHIPU_MIN_INTERVAL_SECONDS="3"
export ZHIPU_MAX_RETRIES="4"
```

`.env` 中也可以这样写：

```text
ZHIPU_MIN_INTERVAL_SECONDS=3
ZHIPU_MAX_RETRIES=4
```

运行真实模型测试：

```bash
python3 main.py "我买了之后不想要了，钱什么时候能退回来？"
```

运行 Web 服务测试：

```bash
python3 web_app.py
```

真实调用代码在：

```text
services/llm_service.py
```

其中：

- `classify_intent`：调用智谱 GLM 做意图识别，要求返回 JSON。
- `generate_reply`：调用智谱 GLM 根据用户问题、意图和知识库生成客服回复。
- `KnowledgeService`：初始化 Chroma 知识库、检索 RAG 片段，并从 SQLite 拼接模拟订单数据。

## Chroma RAG 知识库

本项目使用 Chroma 模拟产品和客服知识库：

```text
data/knowledge.json
  -> 本地 Hash Embedding
  -> data/chroma/
  -> Chroma collection: customer_knowledge
```

Hash Embedding 是本地 Python 计算，不下载模型、不调用额外 API，适合 Render 免费部署和学习 RAG 流程。

订单数据仍然使用 SQLite：

```text
data/schema.sql
data/seed.sql
data/customer-service.db
```

可以测试这些产品咨询：

```bash
python3 main.py "这款耳机支持苹果手机吗"
python3 main.py "AirSound Pro 续航多久"
python3 main.py "哪个型号适合打游戏"
python3 main.py "耳机保修多久"
```

## 服务器发布

本项目推荐使用 Render 原生 Python Web Service，不使用 Dockerfile 作为默认发布入口。

### Render 发布

先把项目推到 GitHub，然后在 Render 新建 `Web Service`，选择该仓库。

手动配置：

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: python3 web_app.py
Health Check Path: /health
```

环境变量：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash
ZHIPU_MIN_INTERVAL_SECONDS=1.5
ZHIPU_MAX_RETRIES=2
```

也可以使用仓库里的 `render.yaml` 创建 Render Blueprint。`ZHIPU_API_KEY` 不会写入仓库，需要在 Render 后台填写。

部署完成后访问：

```text
https://你的服务名.onrender.com
```

健康检查：

```text
https://你的服务名.onrender.com/health
```

### 普通服务器发布

```bash
python3 -m pip install -r requirements.txt
export ZHIPU_API_KEY="你的智谱 API Key"
export PORT=8000
python3 web_app.py
```

支持 `PORT` 环境变量，适配 Render 等平台；`Procfile` 已提供：

```text
web: python3 web_app.py
```

本项目使用智谱官方 Python SDK：

```python
from zai import ZhipuAiClient
```

## 学习重点

1. 意图识别使用 JSON 输出，方便程序判断下一步。
2. 客服回复使用自然语言输出，直接给用户看。
3. Prompt 和代码分离，方便后续调整和版本管理。
4. 知识库使用 Chroma RAG，不再使用写死 Markdown 知识库。
5. 订单模拟数据继续使用 SQLite，方便区分知识库和业务数据。
