from pathlib import Path
from typing import Any

from services.llm_service import LLMService


class IntentService:
    """负责加载意图识别 Prompt，并调用 LLM 做分类。"""

    def __init__(self, llm_service: LLMService, prompt_path: str = "prompts/customer-intent.md") -> None:
        self.llm_service = llm_service
        self.prompt_path = Path(prompt_path)

    def classify_intent(self, user_message: str) -> dict[str, Any]:
        template = self.prompt_path.read_text(encoding="utf-8")
        prompt = template.replace("{{user_message}}", user_message)
        return self.llm_service.classify_intent(user_message=user_message, prompt=prompt)
