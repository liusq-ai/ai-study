from pathlib import Path
from typing import Any

from services.llm_service import LLMService


class ReplyService:
    """负责加载客服回复 Prompt，并调用 LLM 生成话术。"""

    def __init__(self, llm_service: LLMService, prompt_path: str = "prompts/customer-reply.md") -> None:
        self.llm_service = llm_service
        self.prompt_path = Path(prompt_path)

    def generate_reply(
        self,
        user_message: str,
        intent: dict[str, Any],
        knowledge: str,
    ) -> str:
        template = self.prompt_path.read_text(encoding="utf-8")
        prompt = (
            template
            .replace("{{user_message}}", user_message)
            .replace("{{intent_type}}", intent["type"])
            .replace("{{need_order_info}}", str(intent["need_order_info"]))
            .replace("{{knowledge}}", knowledge)
        )
        return self.llm_service.generate_reply(prompt)
