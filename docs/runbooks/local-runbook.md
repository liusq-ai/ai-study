# Local Runbook

## 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 配置环境

推荐使用项目根目录 `.env`：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash-250414
ZHIPU_MIN_INTERVAL_SECONDS=3
ZHIPU_MAX_RETRIES=4
```

也兼容智谱官方环境变量：

```text
ZAI_API_KEY=你的智谱 API Key
```

## 运行

Web 界面：

```bash
python3 web_app.py
```

访问：

```text
http://127.0.0.1:8000
```

连续交互：

```bash
python3 main.py
```

单次问题：

```bash
python3 main.py "我的耳机有问题"
```

## 验证

```bash
python3 -m compileall main.py services tests
```

Web 健康检查：

```text
GET /health
```

首次运行会自动根据 `data/schema.sql` 和 `data/seed.sql` 初始化 `data/customer-service.db`。
首次运行也会根据 `data/knowledge.json` 初始化 `data/chroma/` Chroma 向量知识库。

模拟订单号：

- `SO202606001`：已发货，未申请退款。
- `SO202606002`：未发货，退款处理中。
- `SO202606003`：已签收，退款成功。

产品知识库验证：

```bash
python3 main.py "这款耳机支持苹果手机吗"
python3 main.py "AirSound Pro 续航多久"
python3 main.py "哪个型号适合打游戏"
python3 main.py "耳机保修多久"
```

## 常见错误

- 未配置智谱模型：检查 `.env` 是否存在，是否包含 `ZHIPU_API_KEY` 或 `ZAI_API_KEY`。
- 速率限制 `1302`：调大 `ZHIPU_MIN_INTERVAL_SECONDS`，例如改为 `5`。
- SDK 找不到：确认已安装 `zai-sdk`。
- Chroma 找不到：确认已执行 `python3 -m pip install -r requirements.txt`。
- RAG 结果没更新：删除 `data/chroma/` 后重启，程序会重新初始化知识库。
- 订单查不到：确认用户输入了形如 `SO202606001` 的模拟订单号。
- 页面打不开：确认 `python3 web_app.py` 正在运行，且端口没有被占用。

## 发布

Render 原生发布：

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: python3 web_app.py
Health Check Path: /health
```

Render 环境变量：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash
ZHIPU_MIN_INTERVAL_SECONDS=1.5
ZHIPU_MAX_RETRIES=2
```

仓库包含 `render.yaml`，可用于 Render Blueprint。真实 API Key 只在 Render 后台配置。

普通服务器：

```bash
python3 -m pip install -r requirements.txt
export ZHIPU_API_KEY="你的智谱 API Key"
export PORT=8000
python3 web_app.py
```

## 安全检查

- 不要把真实 API Key 写入 `.env.example`。
- 不要把真实 API Key 写入 README、AGENTS、docs 或源码。
