import json
from pathlib import Path
from types import SimpleNamespace

from services.llm_service import LLMService
from services.knowledge_service import KnowledgeService


BASE_DIR = Path(__file__).resolve().parent.parent


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


def test_identity() -> None:
    service = create_service(
        {
            "type": "identity",
            "need_order_info": False,
            "reason": "用户询问 AI 客服助手身份",
        }
    )

    result = service.classify_intent("你的主人是谁？", "")

    assert result["type"] == "identity"
    assert result["need_order_info"] is False


def create_knowledge(tmp_path: Path) -> KnowledgeService:
    return KnowledgeService(
        database_path=tmp_path / "customer-service.db",
        schema_path=BASE_DIR / "data/schema.sql",
        seed_path=BASE_DIR / "data/seed.sql",
        knowledge_path=BASE_DIR / "data/knowledge.json",
        chroma_path=tmp_path / "chroma",
    )


def test_rag(tmp_path: Path) -> None:
    service = create_knowledge(tmp_path)

    result = service.load_knowledge("我的耳机左边没声音了", "troubleshooting")

    assert "RAG 检索内容" in result
    assert "耳机" in result


def test_order(tmp_path: Path) -> None:
    service = create_knowledge(tmp_path)

    result = service.load_knowledge("帮我查一下订单 SO202606001", "logistics")

    assert "订单号 SO202606001" in result
    assert "AirSound Pro" in result


def test_product_rag(tmp_path: Path) -> None:
    service = create_knowledge(tmp_path)

    result = service.load_knowledge("AirSound Pro 续航多久", "product_info")

    assert "AirSound Pro 续航" in result
    assert "32 小时" in result


def test_product_recommend(tmp_path: Path) -> None:
    service = create_knowledge(tmp_path)

    result = service.load_knowledge("哪个型号适合打游戏", "product_info")

    assert "型号选择建议" in result
    assert "AirSound Pro" in result


def test_identity_rag(tmp_path: Path) -> None:
    service = create_knowledge(tmp_path)

    result = service.load_knowledge("你的主人是谁？", "identity")

    assert "AI 身份信息" in result
    assert "主人是小白" in result
