import json
import os
import time
from pathlib import Path
from typing import Any


def load_env(file_path: str = ".env") -> None:
    """读取项目根目录 .env，避免 IDE 运行时拿不到 shell 环境变量。"""
    env_path = Path(file_path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class LLMService:
    """LLM 服务。

    配置 ZHIPU_API_KEY 后调用智谱 GLM。
    客服回复必须由模型生成，不再使用写死话术。
    """

    def __init__(self) -> None:
        load_env()
        self.model = os.getenv("ZHIPU_MODEL", "glm-4-flash-250414")
        self.max_retries = int(os.getenv("ZHIPU_MAX_RETRIES", "3"))
        self.min_interval_seconds = float(os.getenv("ZHIPU_MIN_INTERVAL_SECONDS", "2"))
        self.last_request_time = 0.0
        self.client = self._create_client()

    def _create_client(self) -> Any | None:
        """创建智谱官方 SDK 客户端。"""
        api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("ZAI_API_KEY")
        if not api_key:
            return None

        try:
            from zai import ZhipuAiClient
        except ImportError:
            return None

        return ZhipuAiClient(api_key=api_key)

    def _wait_request(self) -> None:
        """控制请求间隔，避免连续两次模型调用过快触发限流。"""
        elapsed = time.monotonic() - self.last_request_time
        wait_seconds = self.min_interval_seconds - elapsed
        if wait_seconds > 0:
            time.sleep(wait_seconds)

    def _call_chat(self, **kwargs: Any) -> Any:
        """调用智谱接口，遇到限流时自动退避重试。"""
        if not self.client:
            raise RuntimeError(
                "未配置智谱模型。请先设置 ZHIPU_API_KEY，再调用模型能力。"
            )

        for attempt in range(self.max_retries + 1):
            self._wait_request()

            try:
                response = self.client.chat.completions.create(**kwargs)
                self.last_request_time = time.monotonic()
                return response
            except Exception as error:
                message = str(error)
                is_rate_limited = "1302" in message or "速率限制" in message

                if not is_rate_limited or attempt >= self.max_retries:
                    raise

                time.sleep(2 ** (attempt + 1))

        raise RuntimeError("智谱模型调用失败，请稍后重试。")

    def classify_intent(self, user_message: str, prompt: str) -> dict[str, Any]:
        """调用智谱 GLM 识别用户意图。"""
        response = self._call_chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你只输出合法 JSON，不要输出 Markdown 或解释。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def generate_reply(self, prompt: str) -> str:
        """调用智谱 GLM 生成客服回复。"""
        response = self._call_chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是专业、耐心、简洁的电商客服。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()
