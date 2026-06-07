from typing import Any

from services.intent_service import IntentService
from services.knowledge_service import KnowledgeService
from services.llm_service import LLMService
from services.reply_service import ReplyService


class CustomerService:
    """AI 客服编排服务：意图识别 -> 知识库读取 -> 回复生成。"""

    def __init__(self) -> None:
        llm_service = LLMService()
        self.intent_service = IntentService(llm_service)
        self.knowledge_service = KnowledgeService()
        self.reply_service = ReplyService(llm_service)

    def answer_message(self, user_message: str) -> dict[str, Any]:
        intent = self.intent_service.classify_intent(user_message)
        knowledge = self.knowledge_service.load_knowledge(user_message, intent["type"])
        reply = self.reply_service.generate_reply(
            user_message=user_message,
            intent=intent,
            knowledge=knowledge,
        )

        return {
            "intent": intent,
            "knowledge": knowledge,
            "reply": reply,
        }
