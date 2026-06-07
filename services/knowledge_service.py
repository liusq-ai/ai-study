import re
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class KnowledgeService:
    """从 SQLite RAG 知识库检索客服上下文。"""

    def __init__(
        self,
        database_path: str | Path = BASE_DIR / "data/customer-service.db",
        schema_path: str | Path = BASE_DIR / "data/schema.sql",
        seed_path: str | Path = BASE_DIR / "data/seed.sql",
    ) -> None:
        self.database_path = Path(database_path)
        self.schema_path = Path(schema_path)
        self.seed_path = Path(seed_path)
        self.ensure_database()

    def ensure_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self.connect_database() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))
            connection.executescript(self.seed_path.read_text(encoding="utf-8"))

    def connect_database(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def load_knowledge(self, user_message: str, intent_type: str) -> str:
        chunks = self.search_chunks(user_message, intent_type)
        order = self.load_order(user_message)

        return "\n\n".join(
            [
                self.format_chunks(chunks),
                self.format_order(order),
            ]
        )

    def search_chunks(self, user_message: str, intent_type: str, limit: int = 3) -> list[sqlite3.Row]:
        with self.connect_database() as connection:
            rows = connection.execute(
                """
                SELECT intent_type, title, content, keywords
                FROM knowledge_chunks
                """
            ).fetchall()

        ranked_rows = sorted(
            rows,
            key=lambda row: self.score_chunk(row, user_message, intent_type),
            reverse=True,
        )
        return [row for row in ranked_rows if self.score_chunk(row, user_message, intent_type) > 0][:limit]

    def score_chunk(self, row: sqlite3.Row, user_message: str, intent_type: str) -> int:
        score = 3 if row["intent_type"] == intent_type else 0
        keywords = [keyword.strip() for keyword in row["keywords"].split(",")]

        for keyword in keywords:
            if keyword and keyword in user_message:
                score += 2

        if row["intent_type"] == "other":
            score += 1

        return score

    def extract_order(self, user_message: str) -> str | None:
        match = re.search(r"[A-Z]{2}\d{9}", user_message.upper())
        return match.group(0) if match else None

    def load_order(self, user_message: str) -> dict[str, object] | None:
        order_id = self.extract_order(user_message)
        if not order_id:
            return None

        with self.connect_database() as connection:
            order = connection.execute(
                """
                SELECT *
                FROM orders
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchone()

            if not order:
                return {"order_id": order_id, "found": False}

            items = connection.execute(
                """
                SELECT product_name, sku, quantity, warranty_status
                FROM order_items
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchall()

        return {"order": order, "items": items, "found": True}

    def format_chunks(self, chunks: list[sqlite3.Row]) -> str:
        if not chunks:
            return "RAG 检索内容：暂无匹配知识片段。"

        lines = ["RAG 检索内容："]
        for index, chunk in enumerate(chunks, start=1):
            lines.append(f"{index}. [{chunk['intent_type']}] {chunk['title']}：{chunk['content']}")

        return "\n".join(lines)

    def format_order(self, order_data: dict[str, object] | None) -> str:
        if not order_data:
            return "订单模拟数据：用户未提供订单号。"

        if not order_data["found"]:
            return f"订单模拟数据：未找到订单 {order_data['order_id']}。"

        order = order_data["order"]
        items = order_data["items"]
        item_text = "；".join(
            f"{item['product_name']}({item['sku']}) x{item['quantity']}，{item['warranty_status']}"
            for item in items
        )

        return (
            "订单模拟数据："
            f"订单号 {order['order_id']}，客户 {order['customer_name']}，手机号尾号 {order['phone_tail']}，"
            f"状态 {order['status']}，付款时间 {order['paid_at']}，发货时间 {order['shipped_at'] or '未发货'}，"
            f"承运商 {order['carrier'] or '暂无'}，物流单号 {order['tracking_no'] or '暂无'}，"
            f"退款状态 {order['refund_status']}，退款金额 {order['refund_amount']}，"
            f"发票状态 {order['invoice_status']}，商品：{item_text}。"
        )
