import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from services.customer_service import CustomerService


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


class WebHandler(BaseHTTPRequestHandler):
    """Web 客服入口：静态页面 + Chat API。"""

    service = CustomerService()

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            self.send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path == "/health":
            self.send_json({"status": "ok"})
            return

        static_path = WEB_DIR / path.lstrip("/")
        content_type = self.get_type(static_path)

        if static_path.exists() and static_path.is_file() and content_type:
            self.send_file(static_path, content_type)
            return

        self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path != "/api/chat":
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        payload = self.read_json()
        user_message = str(payload.get("message", "")).strip()

        if not user_message:
            self.send_json({"error": "用户问题不能为空"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            result = self.service.answer_message(user_message)
        except Exception as error:
            self.send_json({"error": f"模型调用失败：{error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_json(
            {
                "message": user_message,
                "intent": result["intent"],
                "reply": result["reply"],
            }
        )

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, file_path: Path, content_type: str) -> None:
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def get_type(self, file_path: Path) -> str | None:
        suffix = file_path.suffix
        return {
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".html": "text/html; charset=utf-8",
        }.get(suffix)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server() -> None:
    """启动 Web 服务。"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), WebHandler)
    print(f"AI 客服 Web 服务已启动：http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
