# Quality Operator

## 职责

负责运行验证层，保证工程可运行、可迁移、可验收。

## 关注点

- 编译检查和测试用例。
- 本地运行命令。
- 依赖安装。
- 常见错误、限流处理和迁移检查。
- 安全检查，尤其是密钥泄露。

## 资产责任

- 主责：`docs/runbooks/local-runbook.md`
- 协作：`docs/context/migration-guide.md`

## 协作规则

- 每次工程或配置变化后更新运行说明。
- 检查 `.env.example`、README 和 docs 中不得出现真实 API Key。
- 至少执行 `python3 -m compileall main.py services tests`。

