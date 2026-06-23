"""HTTP API and static file server for Alarm-AgentForIC."""

from __future__ import annotations

import json
import mimetypes
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from server.analyzer import analyze_alert, get_alert, list_alerts
from server.models import FeedbackRecord
from server.storage import list_feedback, save_feedback

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "client" / "dist"


def to_jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


class AppHandler(BaseHTTPRequestHandler):
    server_version = "AlarmAgentForIC/0.1"

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._json({"status": "ok", "version": "0.1.0"})
        if parsed.path == "/api/alerts":
            return self._json(list_alerts())
        if parsed.path.startswith("/api/alerts/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) == 3:
                alert = get_alert(parts[2])
                if alert is None:
                    return self._json({"error": "alert_not_found"}, status=404)
                return self._json(alert)
            if len(parts) == 4 and parts[3] == "analysis":
                try:
                    return self._json(analyze_alert(parts[2]))
                except KeyError:
                    return self._json({"error": "alert_not_found"}, status=404)
            if len(parts) == 4 and parts[3] == "feedback":
                return self._json(list_feedback(parts[2]))
        return self._static(parsed.path)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/alerts/") and parsed.path.endswith("/analyze"):
            alert_id = parsed.path.strip("/").split("/")[2]
            try:
                return self._json(analyze_alert(alert_id))
            except KeyError:
                return self._json({"error": "alert_not_found"}, status=404)

        if parsed.path.startswith("/api/alerts/") and parsed.path.endswith("/feedback"):
            alert_id = parsed.path.strip("/").split("/")[2]
            if get_alert(alert_id) is None:
                return self._json({"error": "alert_not_found"}, status=404)
            body = self._read_json_body()
            record = FeedbackRecord(
                feedback_id="",
                alert_id=alert_id,
                selected_cause_rank=body.get("selected_cause_rank"),
                final_root_cause=str(body.get("final_root_cause", "")).strip(),
                action_taken=str(body.get("action_taken", "")).strip(),
                recurrence_risk=body.get("recurrence_risk", "medium"),
                notes=str(body.get("notes", "")).strip(),
                created_at=datetime.now(UTC).isoformat(timespec="seconds"),
            )
            if not record.final_root_cause or not record.action_taken:
                return self._json({"error": "final_root_cause_and_action_taken_required"}, status=400)
            return self._json(save_feedback(record), status=201)

        return self._json({"error": "not_found"}, status=404)

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _json(self, payload, status: int = 200):
        body = json.dumps(to_jsonable(payload), ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path: str):
        if path in {"", "/"}:
            path = "/index.html"
        relative = Path(path.lstrip("/"))
        file_path = (PUBLIC_DIR / relative).resolve()
        if not PUBLIC_DIR.exists():
            return self._json(
                {
                    "error": "frontend_dist_not_found",
                    "hint": "Run `npm install` and `npm run build` in the client directory, or use Vite dev server on port 5173.",
                },
                status=404,
            )
        if not str(file_path).startswith(str(PUBLIC_DIR.resolve())):
            return self._json({"error": "not_found"}, status=404)
        if not file_path.exists():
            file_path = PUBLIC_DIR / "index.html"
        content = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        if file_path.suffix == ".js":
            content_type = "text/javascript"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def run(host: str = "127.0.0.1", port: int = 8000):
    httpd = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Alarm-AgentForIC running at http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
