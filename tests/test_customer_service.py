import json
from types import SimpleNamespace

from services.llm_service import LLMService
from services.knowledge_service import KnowledgeService


class FakeCompletions:
    def __init__(self, content: str) -> None:
        self.content = content

    def create(self, **kwargs):
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeClient:
    def __init__(self, content: str) -> None:
        completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=completions)


def create_service(content: dict) -> LLMService:
    service = LLMService()
    service.client = FakeClient(json.dumps(content, ensure_ascii=False))
    service.min_interval_seconds = 0
    return service


def test_refund() -> None:
    service = create_service(
        {
            "type": "refund",
            "need_order_info": True,
            "reason": "用户咨询退款进度",
        }
    )

    result = service.classify_intent("我已经申请退款两天了，钱还没到账，怎么回事？", "")

    assert result["type"] == "refund"
    assert result["need_order_info"] is True


def test_troubleshooting() -> None:
    service = create_service(
        {
            "type": "troubleshooting",
            "need_order_info": False,
            "reason": "用户反馈耳机故障",
        }
    )

    result = service.classify_intent("我的耳机左边没声音了，怎么办？", "")

    assert result["type"] == "troubleshooting"


def test_product() -> None:
    service = create_service(
        {
            "type": "troubleshooting",
            "need_order_info": False,
            "reason": "用户反馈耳机有问题",
        }
    )

    result = service.classify_intent("我的耳机有问题", "")

    assert result["type"] == "troubleshooting"


def test_greeting() -> None:
    service = create_service(
        {
            "type": "greeting",
            "need_order_info": False,
            "reason": "用户打招呼",
        }
    )

    result = service.classify_intent("你好", "")

    assert result["type"] == "greeting"


def test_rag() -> None:
    service = KnowledgeService()

    result = service.load_knowledge("我的耳机左边没声音了", "troubleshooting")

    assert "RAG 检索内容" in result
    assert "耳机" in result


def test_order() -> None:
    service = KnowledgeService()

    result = service.load_knowledge("帮我查一下订单 SO202606001", "logistics")

    assert "订单号 SO202606001" in result
    assert "AirSound Pro" in result
