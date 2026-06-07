import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent


class HashEmbedding:
    """本地 Hash Embedding：轻量、免费、适合学习和 Render 部署。"""

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension

    def create_vector(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension

        for token in self.tokenize_text(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return self.normalize_vector(vector)

    def tokenize_text(self, text: str) -> list[str]:
        lowered = text.lower()
        words = re.findall(r"[a-z0-9]+", lowered)
        chars = [char for char in lowered if "\u4e00" <= char <= "\u9fff"]
        pairs = [lowered[index : index + 2] for index in range(max(len(lowered) - 1, 0))]
        return words + chars + pairs

    def normalize_vector(self, vector: list[float]) -> list[float]:
        length = math.sqrt(sum(value * value for value in vector))
        if length == 0:
            return vector
        return [value / length for value in vector]


class KnowledgeService:
    """从 Chroma RAG 知识库检索客服上下文，并从 SQLite 查询订单。"""

    collection_name = "customer_knowledge"

    def __init__(
        self,
        database_path: str | Path = BASE_DIR / "data/customer-service.db",
        schema_path: str | Path = BASE_DIR / "data/schema.sql",
        seed_path: str | Path = BASE_DIR / "data/seed.sql",
        knowledge_path: str | Path = BASE_DIR / "data/knowledge.json",
        chroma_path: str | Path = BASE_DIR / "data/chroma",
    ) -> None:
        self.database_path = Path(database_path)
        self.schema_path = Path(schema_path)
        self.seed_path = Path(seed_path)
        self.knowledge_path = Path(knowledge_path)
        self.chroma_path = Path(chroma_path)
        self.embedding = HashEmbedding()
        self.ensure_database()
        self.collection = self.ensure_chroma()

    def ensure_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self.connect_database() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))
            connection.executescript(self.seed_path.read_text(encoding="utf-8"))

    def connect_database(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def ensure_chroma(self) -> Any:
        client = self.create_chroma()
        collection = client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.upsert_chunks(collection, self.load_chunks())
        return collection

    def create_chroma(self) -> Any:
        try:
            import chromadb
        except ImportError as error:
            raise RuntimeError("未安装 Chroma，请先执行：python3 -m pip install -r requirements.txt") from error

        self.chroma_path.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(self.chroma_path))

    def load_chunks(self) -> list[dict[str, Any]]:
        return json.loads(self.knowledge_path.read_text(encoding="utf-8"))

    def upsert_chunks(self, collection: Any, chunks: list[dict[str, Any]]) -> None:
        documents = [chunk["content"] for chunk in chunks]
        embeddings = [self.embedding.create_vector(self.build_document(chunk)) for chunk in chunks]
        metadatas = [
            {
                "intent_type": chunk["intent_type"],
                "title": chunk["title"],
                "keywords": ",".join(chunk["keywords"]),
            }
            for chunk in chunks
        ]
        ids = [chunk["id"] for chunk in chunks]

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def build_document(self, chunk: dict[str, Any]) -> str:
        keywords = "，".join(chunk["keywords"])
        return f"{chunk['title']}。{chunk['content']}。关键词：{keywords}"

    def load_knowledge(self, user_message: str, intent_type: str) -> str:
        chunks = self.search_chunks(user_message, intent_type)
        order = self.load_order(user_message)

        return "\n\n".join(
            [
                self.format_chunks(chunks),
                self.format_order(order),
            ]
        )

    def search_chunks(self, user_message: str, intent_type: str, limit: int = 3) -> list[dict[str, str]]:
        query_text = f"{intent_type} {user_message}"
        result = self.collection.query(
            query_embeddings=[self.embedding.create_vector(query_text)],
            n_results=8,
            where={"intent_type": intent_type},
            include=["documents", "metadatas", "distances"],
        )
        chunks = self.parse_results(result)

        if chunks or intent_type == "other":
            return self.rerank_chunks(chunks, user_message)[:limit]

        fallback = self.collection.query(
            query_embeddings=[self.embedding.create_vector(user_message)],
            n_results=8,
            include=["documents", "metadatas", "distances"],
        )
        return self.rerank_chunks(self.parse_results(fallback), user_message)[:limit]

    def parse_results(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        return [
            {
                "intent_type": metadata["intent_type"],
                "title": metadata["title"],
                "content": document,
                "keywords": metadata["keywords"],
                "distance": distance,
            }
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

    def rerank_chunks(self, chunks: list[dict[str, Any]], user_message: str) -> list[dict[str, Any]]:
        return sorted(
            chunks,
            key=lambda chunk: (self.score_chunk(chunk, user_message), -float(chunk["distance"])),
            reverse=True,
        )

    def score_chunk(self, chunk: dict[str, Any], user_message: str) -> int:
        score = 0
        message = user_message.lower()
        keywords = [keyword.strip().lower() for keyword in chunk["keywords"].split(",")]

        for keyword in keywords:
            if keyword and keyword in message:
                score += 4

        title = chunk["title"]
        if "续航" in message and "续航" in title:
            score += 6
        if any(word in message for word in ["型号", "推荐", "哪个", "哪款", "区别", "适合"]) and "型号选择" in title:
            score += 6
        if any(word in message for word in ["保修", "质保", "售后"]) and "保修" in title:
            score += 6

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

    def format_chunks(self, chunks: list[dict[str, Any]]) -> str:
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
