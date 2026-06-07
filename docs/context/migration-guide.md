# Migration Guide

## 迁移步骤

1. 复制工程目录。
2. 安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

3. 在新环境配置 `.env`：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash-250414
ZHIPU_MIN_INTERVAL_SECONDS=3
ZHIPU_MAX_RETRIES=4
```

4. 运行编译检查：

```bash
python3 -m compileall main.py services tests
```

5. 运行客服入口：

```bash
python3 main.py "我的耳机有问题"
```

6. 运行 Web 服务：

```bash
python3 web_app.py
```

然后打开 `http://127.0.0.1:8000`。

## Render 迁移

1. 把工程推到 GitHub。
2. 在 Render 新建 `Web Service`，选择该仓库。
3. 使用原生 Python 部署：

```text
Build Command: pip install -r requirements.txt
Start Command: python3 web_app.py
Health Check Path: /health
```

4. 配置环境变量：

```text
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_MODEL=glm-4-flash
ZHIPU_MIN_INTERVAL_SECONDS=1.5
ZHIPU_MAX_RETRIES=2
```

5. 访问 `/health`，确认返回 `{"status":"ok"}`。

## 迁移检查

- `.env` 不提交到代码仓库。
- `.env.example` 只保留占位符。
- `render.yaml` 可用于 Render Blueprint，但不包含真实 API Key。
- `runtime.txt` 固定 Render Python 运行版本。
- `data/knowledge.json` 必须随工程迁移。
- `data/chroma/` 是运行时生成目录，不需要迁移。
- `data/schema.sql` 和 `data/seed.sql` 必须随工程迁移。
- `data/customer-service.db` 是运行时生成文件，不需要迁移。
- `web/` 和 `web_app.py` 必须随工程迁移。
- 服务器发布时必须配置 `ZHIPU_API_KEY` 或 `ZAI_API_KEY`。
- `docs/context/` 可说明项目背景和架构。
- `docs/runbooks/local-runbook.md` 可说明本地运行和常见错误。
